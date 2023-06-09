"""JMUTestCase class and related code.

The ``JMUTestCase`` is a subclass of ``unittest.TestCase`` with the following
features:

* Some useful assertions for autograding.
* Guaranteed test method execution order based on definition order.
* ``@required`` annotation that can be used to make a particular test a requirement for all subsequent tests.

"""
import types
import unittest
import tempfile
import subprocess
import os
import shutil
import re
from pathlib import Path
from functools import wraps
from . import utils
import sys
from importlib import import_module

_TEST_ORDER = {}


def _order(f):
    global _TEST_ORDER
    _TEST_ORDER[f.__name__] = len(_TEST_ORDER)
    return f


def test_compare(a, b):
    if a in _TEST_ORDER and b in _TEST_ORDER:
        return [1, -1][_TEST_ORDER[a] < _TEST_ORDER[b]]
    elif a in _TEST_ORDER:
        return -1
    elif b in _TEST_ORDER:
        return 1
    else:
        return [1, -1][a < b]


def _check_required(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if hasattr(self.__class__, '_FAILED_REQUIRED_TEST'):
            self.fail("Failed required test: {}".format(self._FAILED_REQUIRED_TEST))
            result = None
        else:
            result = func(self, *args, **kwargs)
        return result

    return wrapper


def required():
    """Used to decorate required test method.  If a required method is
    failed then all of the following methods will fail as well.

    """

    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                result = func(self, *args, **kwargs)
            except Exception as e:
                self.__class__._FAILED_REQUIRED_TEST = func.__doc__
                result = None
                raise e.__class__(str(e) + "\n This test was required.  All of the following tests will fail automatically.")
            return result

        return wrapper

    return decorator


# https://stackoverflow.com/questions/8245135/python-decorate-all-methods-of-subclass-and-provide-means-to-override

class OrderAllTestsMeta(type):
    """Decorate every method so that they will be ordered during testing,
    and they will respect the 'required' decorator.

    """

    def __new__(cls, name, bases, local):

        for attr in local:
            value = local[attr]
            if isinstance(value, types.FunctionType):
                local[attr] = _check_required(_order(value))
        return type.__new__(cls, name, bases, local)


class _JmuTestCase(unittest.TestCase):
    """Additional useful assertions for grading.

    This is the superclass for ``JmuTestCase``.  Users should subclass
    ``JmuTestCase`` in their test code. """

    # counts the number of dynamic modules created
    module_count = 0

    def getScriptOutput(self, filename, string_in, variables=None, args="",
                        msg=None, processor=None, only_output=False, from_file=False):
        """Get output for the provided Python script.
        Changed June 2023 - look for file without leading paths in source only

        Args:
            filename (str): The name of the Python file to test
            string_in (str): A string that will be fed to stdin for the script
            variables (dict): A dictionary mapping from variable names to
                values. The script will be edited with these
                substitutions before it is executed.
            args (str):  Command line arguments that will be passed to the script.
            msg (str):  Error message that will be printed if the assertion fails.
            processor (func):  A function mapping from string to string that will
                process the script output before it is returned.
            only_output (bool): Return only the stdout (rather than also the stderr).
            from_file (bool): Interpret string_in as a file name rather than a string.
                The file should be stored in the scaffolding folder.

        Returns:
            dict: keys include 'stdout', and 'msg' as well as 'stderr' if there
            there was any output on stderr. 'stdout' and 'stderr' are the script
            output and 'msg' is a formatted string describing any execution errors
            as well as the inputs to the script.

        """
        tmpdir = None
        filenameNoPath = Path(filename).name
        try:
            tmpdir, new_file_name = utils.replace_variables(filename,
                                                            variables)

            # Make a clean backup of the original submission:
            shutil.copy(utils.full_source_path(filename),
                        os.path.join(tmpdir, "__tmp_backup.py"))

            # Replace the original submission in source:
            shutil.copy(new_file_name, utils.full_source_path(filename))

            command = [sys.executable, utils.full_source_path(filename)]
            command.extend(args.split())

            proc = subprocess.Popen(command,
                                    stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)

            if from_file:
                with open(utils.full_source_path(string_in), 'r') as f:
                    string_in = f.read()

            actual, stderr = proc.communicate(input=string_in.encode())
            actual_text = actual.decode()

            if processor:
                actual_text = processor(actual_text)
                if only_output:
                    return {"stdout": actual_text}
            stderr_text = stderr.decode()

            if len(stderr) > 0:
                stderr_text = stderr_text.replace(utils.full_source_path() + "/", '')
                err_msg = "Error during script execution:\n{}".format(stderr_text)
                out_msg = "\nOutput before failure:\n{}".format(actual_text)
                return {"stdout": actual_text, "stderr": stderr_text, "msg": err_msg + out_msg}

            show_in = string_in.encode('unicode_escape').decode()
            message = "Input was: '{}'".format(show_in)
            if len(args) > 0:
                message += "\nCommand line arguments: {}".format(args)
            if msg is not None:
                message += "\n" + msg
            return {"stdout": actual_text, "msg": message}
        finally:
            if tmpdir is not None:
                # Restore the original submission in source:
                shutil.copy(os.path.join(tmpdir, "__tmp_backup.py"),
                            utils.full_source_path(filename))
                shutil.rmtree(tmpdir)

    def assertScriptOutputEqual(self, filename, string_in, expected,
                                variables=None, args="", msg=None,
                                processor=None):
        """Deprecated wrapper for :meth:`~jmu_gradescope_utils.jmu_test_case._JmuTestCase.assertOutputEqual`."""
        self.assertOutputEqual(filename, string_in, expected, variables, args,
                               msg, processor)

    def assertOutputEqual(self, filename, string_in, expected,
                          variables=None, args="", msg=None,
                          processor=None, from_files=False):
        """Assert correct output for the provided Python script.

        Args:
            filename (str): The name of the Python file to test
            string_in (str): A string that will be fed to stdin for the script
            expected (str): Expected stdout
            variables (dict): A dictionary mapping from variable names to
                values. The script will be edited with these
                substitutions before it is executed.
            args (str):  Command line arguments that will be passed to the script.
            msg (str):  Error message that will be printed if the assertion fails.
            processor (func):  A function mapping from string to string that will
                process the script output before it is compared
                to the expected output.
            from_files (bool): Interpret string_in and expected as a file names rather
                than strings.  The files should be stored in the scaffolding folder.
        Raises:
            AssertionError: If the expected output doesn't match the actual
                output.

        """
        result = self.getScriptOutput(filename, string_in, variables=variables,
                                      args=args, msg=msg, processor=processor,
                                      from_file=from_files)
        if "stderr" in result:
            self.fail(result["msg"])

        if from_files:
            with open(utils.full_source_path(expected), 'r') as f:
                expected = f.read()

        self.assertEqual(result["stdout"], expected, result["msg"])

    def assertOutputNotEqual(self, filename, string_in, expected,
                             variables=None, args="", msg=None,
                             processor=None, from_files=False):
        """Assert script output is NOT equal to the indicated string.

        See :meth:`~jmu_gradescope_utils.jmu_test_case._JmuTestCase.assertOutputEqual` for
        description of arguments.
        """
        result = self.getScriptOutput(filename, string_in, variables=variables,
                                      args=args, msg=msg, processor=processor,
                                      from_file=from_files)
        if "stderr" in result:
            self.fail(result["msg"])

        if from_files:
            with open(utils.full_source_path(expected), 'r') as f:
                expected = f.read()

        self.assertNotEqual(result["stdout"], expected, result["msg"])

    def assertInOutput(self, filename, string_in, expected,
                       variables=None, args="", msg=None,
                       processor=None, from_files=False):
        """Assert script output contains the indicated string.

        See :meth:`~jmu_gradescope_utils.jmu_test_case._JmuTestCase.assertOutputEqual` for
        description of arguments.
        """
        result = self.getScriptOutput(filename, string_in, variables=variables,
                                      args=args, msg=msg, processor=processor,
                                      from_file=from_files)
        if "stderr" in result:
            self.fail(result["msg"])

        if from_files:
            with open(utils.full_source_path(expected), 'r') as f:
                expected = f.read()

        self.assertIn(expected, result["stdout"], result["msg"])

    def assertNotInOutput(self, filename, string_in, expected,
                          variables=None, args="", msg=None,
                          processor=None, from_files=False):
        """Assert script output does not contain the indicated string.

        See :meth:`~jmu_gradescope_utils.jmu_test_case._JmuTestCase.assertOutputEqual` for
        description of arguments.
        """
        result = self.getScriptOutput(filename, string_in, variables=variables,
                                      args=args, msg=msg, processor=processor,
                                      from_file=from_files)
        if "stderr" in result:
            self.fail(result["msg"])

        if from_files:
            with open(utils.full_source_path(expected), 'r') as f:
                expected = f.read()

        self.assertNotIn(expected, result["stdout"], result["msg"])

    def assertNoLoops(self, filename, msg=None):
        """ Assert that the provided script has no for or while loops.

        Comments will be ignored.

        Args:
            filename (str): The name of the Python file to test
            msg (str):  Error message that will be printed if the assertion fails.

        Raises:
            AssertionError: If the file contains a loop.

        """
        loop_regex = "(^|(\r\n?|\n))\s*(for|while).*:\s*(#.*)*($|(\r\n?|\n))"
        count = utils.count_regex_matches(loop_regex, filename)
        message = f"It looks like the file {filename} contains at least one loop."
        if msg is not None:
            message += f"\n{msg}"
        if count > 0:
            self.fail(message)

    def assertNoForLoops(self, filename, msg=None):
        """ Assert that the provided script has no for loops.

        Comments will be ignored.

        Args:
            filename (str): The name of the Python file to test
            msg (str):  Error message that will be printed if the assertion fails.

        Raises:
            AssertionError: If the file contains a for loop.

        """
        loop_regex = "(^|(\r\n?|\n))\s*(for).*:\s*(#.*)*($|(\r\n?|\n))"
        count = utils.count_regex_matches(loop_regex, filename)
        message = f"It looks like the file {filename} contains at least one for loop."
        if msg is not None:
            message += f"\n{msg}"
        if count > 0:
            self.fail(message)

    def assertNoWhileLoops(self, filename, msg=None):
        """ Assert that the provided script has no while loops.

        Comments will be ignored.

        Args:
            filename (str): The name of the Python file to test
            msg (str):  Error message that will be printed if the assertion fails.

        Raises:
            AssertionError: If the file contains a while loop.

        """
        loop_regex = "(^|(\r\n?|\n))\s*(while).*:\s*(#.*)*($|(\r\n?|\n))"
        count = utils.count_regex_matches(loop_regex, filename)
        message = f"It looks like the file {filename} contains at least one while loop."
        if msg is not None:
            message += f"\n{msg}"
        if count > 0:
            self.fail(message)

    def assertNoConditionals(self, filename, msg=None):
        """ Assert that the provided script has no conditional statements.

        Comments will be ignored.  ``if __name__ == "__main__":`` will be ignored.

        Args:
            filename (str): The name of the Python file to test
            msg (str):  Error message that will be printed if the assertion fails.

        Raises:
            AssertionError: If the file contains an if.

        """
        if_regex = "(^|(\r\n?|\n))\s*if.*:\s*(#.*)*($|(\r\n?|\n))"
        main_regex = "(^|(\r\n?|\n))\s*if\s*__name__.*:\s*(#.*)*($|(\r\n?|\n))"
        count = utils.count_regex_matches(if_regex, filename)
        main_count = utils.count_regex_matches(main_regex, filename)
        message = f"It looks like the file {filename} contains at least one if statement."
        if msg is not None:
            message += f"\n{msg}"
        if count > main_count:
            self.fail(message)

    def assertPassesPep8(self, filename):
        """Assert that there are no formatting errors as discovered by flake8.

        This will use the config file flake8.cfg included in the autograder
        folder.

        Args:
            filename (str): The name of the Python file to test

        Raises:
            AssertionError: If flake8 produces any output.

        """
        output = utils.run_flake8(filename)
        if len(output) != 0:
            self.fail("Submission does not pass pep8 checks:\n" + output)
        print('Submission passes all formatting checks!')

    def assertDocstringsCorrect(self, filename):
        """Assert that there are no formatting errors as discovered by flake8.

        This will use the config file docstring.cfg included in the autograder
        folder.

        Args:
            filename (str): The name of the Python file to test

        Raises:
            AssertionError: If flake8 produces any output.

        """
        output = utils.run_flake8_docstring(filename)
        if len(output) != 0:
            self.fail("Submission does not pass docstring checks:\n" + output)
        print('Submission passes all docstring checks!')

    def assertRequiredFilesPresent(self, required_files):
        """Assert that all files in the provided list were submitted.

        Note that this assertion won't get a chance to run if the test file
        attempts to import a missing file. One workaround is to do the
        imports inside the test methods.

        Args:
            required_files (list): A list of Python file names.

        Raises:
            AssertionError: If any of the indicated files are missing.

        """
        missing_files = utils.check_submitted_files(required_files)
        for path in missing_files:
            print('Missing {0}'.format(path))
        self.assertEqual(len(missing_files), 0, 'Missing some required files!')
        print('All required files submitted!')

    def assertOutputCorrect(self, filename, string_in, expected,
                            variables=None, processor=None):
        """ Wrapper for assertOutputEqual.

        I'm not sure why this exists. -NRS

        """
        self.assertOutputEqual(filename, string_in, expected,
                               variables=variables, processor=processor)
        print('Correct output:\n' + expected)

    def run_with_substitution(self, filename, variables, func):
        """substitute variable values, then load a module and execute the given function `func`"""
        _JmuTestCase.module_count = _JmuTestCase.module_count + 1
        short_filename = filename
        if filename[-3:] == '.py':
            short_filename = filename[0:-3]
        new_module_name = short_filename + "_" + str(_JmuTestCase.module_count)
        (tmpdir, new_file_name) = utils.replace_variables(filename,
                                                          variables=variables,
                                                          new_name=new_module_name + ".py")
        # insert the new temporary directory into the system module load path
        sys.path.insert(1, tmpdir)
        # load the module
        dynamic_module = import_module(new_module_name)
        func(dynamic_module)

    def assertMatchCount(self, filename, regex, num_matches, msg=None):
        """Assert that the regex matches exactly the correct number of times.

        Ignores comments and docstrings.

        Could be used if the problem instructions say something like:
        "Your program must use exactly one while loop."

        Args:
            filename (str): The name of the Python file to test
            regex (str): A Python regular expression.
            num_matches (str):  The expected number of matches.
            msg (str):  Error message that will be printed if the assertion fails.

        Raises:
            AssertionError: If the count doesn't match.

        """
        count = utils.count_regex_matches(regex, filename)
        self.assertEqual(num_matches, count, msg=msg)


class JmuTestCase(_JmuTestCase, metaclass=OrderAllTestsMeta):
    """Test methods declared within subclasses will be executed in the
    order they are declared as long as the ``sortTestMethodUsing`` attribute
    of the defaultTestLoader has been set::
        unittest.defaultTestLoader.sortTestMethodsUsing = test_compare

    They will also respect the ``@required`` decorator.

    """
    pass

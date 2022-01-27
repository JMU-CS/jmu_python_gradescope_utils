import types
import unittest
import tempfile
import subprocess
import os
import shutil
import re
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
    """ Additional useful assertions for grading. """

    # counts the number of dynamic modules created
    module_count = 0

    def assertScriptOutputEqual(self, filename, string_in, expected,
                                variables=None, msg=None, processor=None):
        tmpdir = None
        try:
            tmpdir, new_file_name = utils.replace_variables(filename, variables)

            proc = subprocess.Popen(['python3', new_file_name],
                                    stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE)
            actual = proc.communicate(input=string_in.encode())[0]

            show_in = string_in.encode('unicode_escape').decode()
            message = "Input was: '{}'".format(show_in)
            if msg is not None:
                message += "\n" + msg
            actual_text = actual.decode()
            if processor:
                actual_text = processor(actual_text)
            self.assertEqual(actual_text, expected, message)
        finally:
            if tmpdir is not None:
                shutil.rmtree(tmpdir)


    def assertPassesPep8(self, filename):
        output = utils.run_flake8(filename)
        if len(output) != 0:
            self.fail("Submission does not pass pep8 checks:\n" + output)
        print('Submission passes all formatting checks!')

    def assertRequiredFilesPresent(self, required_files):
        missing_files = utils.check_submitted_files(required_files)
        for path in missing_files:
            print('Missing {0}'.format(path))
        self.assertEqual(len(missing_files), 0, 'Missing some required files!')
        print('All required files submitted!')

    def assertOutputCorrect(self, filename, string_in, expected,
                            variables=None, processor=None):
        self.assertScriptOutputEqual(filename, string_in, expected,
                                     variables=variables, processor=processor)
        print('Correct output:\n' + expected)

    def run_with_substitution(self, filename, variables, func):
        """substitute variable values, then load a module and execute the given function `func`"""
        _JmuTestCase.module_count = _JmuTestCase.module_count + 1
        short_filename = filename
        if filename[-3:] == '.py':
            short_filename = filename[0:-3]
        new_module_name = short_filename + "_" + str(_JmuTestCase.module_count)
        (tmpdir, new_file_name) = utils.replace_variables(filename, variables=variables, new_name=new_module_name + ".py")
        # insert the new temporary directory into the system module load path
        sys.path.insert(1, tmpdir)
        # load the module
        dynamic_module = import_module(new_module_name)
        func(dynamic_module)

    def assertMatchCount(self, filename, regex, num_matches, msg=None):
        count = utils.count_regex_matches(regex, filename)
        self.assertEqual(num_matches, count, msg=msg)


class JmuTestCase(_JmuTestCase, metaclass=OrderAllTestsMeta):
    """Test methods declared within subclasses will be executed in the
    order they are declared as long as the sortTestMethodUsing attrute
    of the defaultTestLoader has been set::

    unittest.defaultTestLoader.sortTestMethodsUsing = test_compare

    They will also respect the @required decorator.

    """
    pass

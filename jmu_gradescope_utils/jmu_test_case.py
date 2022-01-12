import types
import unittest
import tempfile
import subprocess
import os
import shutil
import re
from functools import wraps
from . import utils


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

    def assertScriptOutputEqual(self, filename, string_in, expected,
                                variables=None, msg=None):

        tmpdir = tempfile.mkdtemp()
        try:
            new_file_name = os.path.join(tmpdir, os.path.basename(filename))
            with open(utils.full_submission_path(filename), 'r') as f:
                new_file = f.read()

            if variables is not None:

                for var in variables:
                    regexp = '(^|\n)( *){}\s*(?=\=)(?!==).*(\n|$)'.format(var)
                    replace = "\\1\\2{} = {}\\3".format(var, repr(variables[var]))
                    new_file = re.sub(regexp, replace, new_file)

            with open(os.path.join(new_file_name), 'w') as f:
                f.write(new_file)

            proc = subprocess.Popen(['python3', new_file_name],
                                    stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE)
            actual = proc.communicate(input=string_in.encode())[0]

            show_in = string_in.encode('unicode_escape').decode()
            message = "Input was: '{}'".format(show_in)
            if msg is not None:
                message += "\n" + msg
            self.assertEqual(actual.decode(), expected, message)
        finally:
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
                            variables=None):
        self.assertScriptOutputEqual(filename, string_in, expected,
                                     variables=variables)
        print('Correct output:\n' + expected)


class JmuTestCase(_JmuTestCase, metaclass=OrderAllTestsMeta):
    """Test methods declared within subclasses will be executed in the
    order they are declared as long as the sortTestMethodUsing attrute
    of the defaultTestLoader has been set::

    unittest.defaultTestLoader.sortTestMethodsUsing = test_compare

    They will also respect the @required decorator.

    """
    pass

import subprocess
import types
import unittest
import os
import re
import contextlib
import io
import sys
from . import remove_comments

SUBMISSION_BASE = '/autograder/submission'

# The code below provides a subclass of unittest.TestCase that includes
# some additional assertions for grading and ensures that tests will
# be executed in the order they are declared.

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


# https://stackoverflow.com/questions/8245135/python-decorate-all-methods-of-subclass-and-provide-means-to-override

class OrderAllTestsMeta(type):
    def __new__(cls, name, bases, local):
        for attr in local:
            value = local[attr]
            if isinstance(value, types.FunctionType):
                local[attr] = _order(value)
        return type.__new__(cls, name, bases, local)


class _JmuTestCase(unittest.TestCase):
    """ Additional useful assertions for grading. """

    def assertScriptOutputEqual(self, filename, string_in, expected,
                                msg=None):
        oldstdin = sys.stdin
        sys.stdin = io.StringIO(string_in)

        try:
            f = io.StringIO()
            with contextlib.redirect_stdout(f):
                exec(open(full_submission_path(filename)).read())
            actual = f.getvalue()
            show_in = string_in.encode('unicode_escape').decode()
            message = "Input was: '{}'".format(show_in)
            if msg is not None:
                message += "\n" + msg
            self.assertEqual(actual, expected, message)
        finally:
            sys.stdin = oldstdin


class JmuTestCase(_JmuTestCase, metaclass=OrderAllTestsMeta):
    """Test methods declared within subclasses will be executed in the
    order they are declared as long as the sortTestMethodUsing attrute
    of the defaultTestLoader has been set::

    unittest.defaultTestLoader.sortTestMethodsUsing = test_compare

    """
    pass

def full_submission_path(filename):

    if os.path.dirname(filename) == SUBMISSION_BASE:
        return filename
    elif os.path.dirname(filename) == '':
        return os.path.join(SUBMISSION_BASE, filename)
    else:
        raise ValueError("bad submission file path: " + filename)


def count_regexp_matches_in_file(regexp, filename, strip_comments=True):
    full_path = full_submission_path(filename)
    if not os.path.exists(full_path):
        raise FileNotFoundError("no such file: " + full_path)

    if strip_comments:
        contents = remove_comments.remove_comments(full_path)
    else:
        with open(full_path, 'r') as f:
            contents = f.read()

    matches = re.findall(regexp, contents)
    return len(matches)


def run_flake8(filename):
    full_path = full_submission_path(filename)
    if not os.path.exists(full_path):
        raise FileNotFoundError("no such file: " + full_path)

    proc = subprocess.Popen(['flake8',
                             '--config=/autograder/source/flake8.cfg',
                             full_path],
                            stdout=subprocess.PIPE)
    proc.wait()
    return proc.stdout.read().decode().strip()


if __name__ == "__main__":

    print(count_regexp_matches_in_file('open', 'jmu_gradescope_utils.py'))
    print(full_submission_path('/autograder/submission/tree.py'))

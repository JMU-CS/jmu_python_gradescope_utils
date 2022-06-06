import subprocess
import os
import re
from . import remove_comments
import tempfile
import io
import sys
from contextlib import contextmanager

if 'JMU_GRADESCOPE_BASE' in os.environ:
    GRADESCOPE_BASE = os.environ['JMU_GRADESCOPE_BASE']
else:
    GRADESCOPE_BASE = '/autograder'

SUBMISSION_BASE = os.path.join(GRADESCOPE_BASE, 'submission')
SOURCE_BASE = os.path.join(GRADESCOPE_BASE, 'source')

def full_submission_path(filename=None):

    if filename is None:
        return SUBMISSION_BASE
    elif os.path.dirname(filename) == SUBMISSION_BASE:
        return filename
    elif os.path.dirname(filename) == '':
        return os.path.join(SUBMISSION_BASE, filename)
    else:
        raise ValueError("bad submission file path: " + filename)


def full_source_path(filename=None):

    if filename is None:
        return SOURCE_BASE
    elif os.path.dirname(filename) == SOURCE_BASE:
        return filename
    elif os.path.dirname(filename) == '':
        return os.path.join(SOURCE_BASE, filename)
    else:
        raise ValueError("bad source file path: " + filename)


def count_regex_matches(regex, filename, strip_comments=True):
    full_path = full_submission_path(filename)
    if not os.path.exists(full_path):
        raise FileNotFoundError("no such file: " + full_path)

    if strip_comments:
        contents = remove_comments.remove_comments(full_path)
    else:
        with open(full_path, 'r') as f:
            contents = f.read()

    matches = re.findall(regex, contents)
    return len(matches)


def run_flake8(filename, config='flake8.cfg'):
    """Return the output of executing flake8.  Should be an empty string
    if no formatting issues were found.

    """
    full_path = full_submission_path(filename)
    if not os.path.exists(full_path):
        raise FileNotFoundError("no such file: " + full_path)

    config_path = os.path.join(GRADESCOPE_BASE, 'source', config)
    proc = subprocess.Popen(['python3', '-m', 'flake8',
                             '--config={}'.format(config_path),
                             full_path],
                            stdout=subprocess.PIPE)
    proc.wait()
    return proc.stdout.read().decode().strip()


def run_flake8_docstring(filename):
    return run_flake8(filename, config='docstring.cfg')


def replace_variables(filename, variables=None, new_name=None):
    tmpdir = tempfile.mkdtemp()
    if new_name is not None:
        new_file_name = os.path.join(tmpdir, new_name)
    else:
        new_file_name = os.path.join(tmpdir, os.path.basename(filename))
    with open(full_submission_path(filename), 'r') as f:
        new_file = f.read()

    if variables is not None:

        for var in variables:
            regexp = '(^|\n)( *){}\s*(?=\=)(?!==).*(\n|$)'.format(var)
            replace = "\\1\\2{} = {}\\3".format(var, repr(variables[var]))
            new_file = re.sub(regexp, replace, new_file)

    with open(os.path.join(new_file_name), 'w') as f:
        f.write(new_file)

    return (tmpdir, new_file_name)


# This is copied directly from:
# https://github.com/gradescope/gradescope-utils/blob/master/gradescope_utils/autograder_utils/files.py
# Copied here so that SUBMISSION_BASE default will respect
# 'JMU_GRADESCOPE_BASE'

def check_submitted_files(paths, base=SUBMISSION_BASE):
    """Checks that the files in the given list exist in the student's submission.

    Returns a list of missing files.

    eg. check_submitted_files(['src/calculator.py'])
    """
    missing_files = []
    for path in paths:
        target_path = os.path.join(base, path)
        if not os.path.isfile(target_path):
            missing_files.append(path)
    return missing_files

@contextmanager
def suppress_IO(in_string):
    """
    Suppresses standard io when running a block of code, feeding in the given in_string as input
    and squelching all output. Use as

    ```with suppress_IO("desired input"):
            # my code block
    ```
    """
    text_in = io.StringIO(in_string)
    text_out = io.StringIO()
    oldout = sys.stdout
    oldin = sys.stdin
    sys.stdout = text_out
    sys.stdin = text_in
    yield
    sys.stdout = oldout
    sys.stdin = oldin

class IOContext:
    """
    Context manager that allows specifying simulated keyboard input, and captures text output.

    Use like so::

        context = IOContext("program input")
        with context:
            # my code block
        output = context.output
    """
    def __init__(self, in_string):
        self.text_in = io.StringIO(in_string)
        self.text_out = io.StringIO()

    def __enter__(self):
        self.oldout = sys.stdout
        self.oldin = sys.stdin
        sys.stdout = self.text_out
        sys.stdin = self.text_in

    def __exit__(self, exc_type, exc_value, traceback):
        sys.stdout = self.oldout
        sys.stdin = self.oldin
        self.output = self.text_out.getvalue()

if __name__ == "__main__":

    print(count_regex_matches_in_file('open', 'jmu_gradescope_utils.py'))
    print(full_submission_path('/autograder/submission/tree.py'))

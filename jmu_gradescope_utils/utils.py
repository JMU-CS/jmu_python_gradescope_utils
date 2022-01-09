import subprocess
import os
import re
from . import remove_comments

SUBMISSION_BASE = '/autograder/submission'

def full_submission_path(filename):

    if os.path.dirname(filename) == SUBMISSION_BASE:
        return filename
    elif os.path.dirname(filename) == '':
        return os.path.join(SUBMISSION_BASE, filename)
    else:
        raise ValueError("bad submission file path: " + filename)


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


def run_flake8(filename):
    """Return the output of executing flake8.  Should be an empty string
    if no formatting issues were found.

    """
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

    print(count_regex_matches_in_file('open', 'jmu_gradescope_utils.py'))
    print(full_submission_path('/autograder/submission/tree.py'))

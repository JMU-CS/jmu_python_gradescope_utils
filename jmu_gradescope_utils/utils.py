import subprocess
import os
import re
from . import remove_comments

if 'JMU_GRADESCOPE_BASE' in os.environ:
    GRADESCOPE_BASE = os.environ['JMU_GRADESCOPE_BASE']
else:
    GRADESCOPE_BASE = '/autograder'

SUBMISSION_BASE = os.path.join(GRADESCOPE_BASE, 'submission')

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

    config_path = os.path.join(GRADESCOPE_BASE, 'source', 'flake8.cfg')
    proc = subprocess.Popen(['flake8',
                             '--config={}'.format(config_path),
                             full_path],
                            stdout=subprocess.PIPE)
    proc.wait()
    return proc.stdout.read().decode().strip()



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


if __name__ == "__main__":

    print(count_regex_matches_in_file('open', 'jmu_gradescope_utils.py'))
    print(full_submission_path('/autograder/submission/tree.py'))

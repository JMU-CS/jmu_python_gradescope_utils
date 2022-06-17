#!/usr/bin/env python
"""This script can be used to test-run the Gradescope autograder
scripts locally. (As long as those scripts respect the
'JMU_GRADESCOPE_BASE' environment variable.)

Run it as follows::

python test_autograder.py /path/to/sample/submission/

If all goes well it will produce an output file named
test_results.json containing the autograder output.

"""

import sys
import shutil
import jmu_gradescope_utils.build_utils as build_utils

def main():

    if len(sys.argv) < 2:
        print("Usage:")
        print("test_autograder.py /path/to/submission/folder/")
        print("\nScript must be run from within the autograder folder.")
        return

    result_json_loc, code = build_utils.test_autograder('./', sys.argv[1])
    shutil.move(result_json_loc, './test_results.json')
    sys.exit(code)

if __name__ == "__main__":
    main()

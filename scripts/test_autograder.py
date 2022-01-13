#!/usr/bin/env python
"""This script can be used to test-run the Gradescope autograder
scripts locally. (As long as those scripts respect the
'JMU_GRADESCOPE_BASE' environment variable.)

Run it as follows::

python test_autograder.py /path/to/sample/submission/

If all goes well it will produce an output file named
test_results.json containing the autograder output.

"""

import tempfile
import sys
import subprocess
import os
import shutil

def main():

    if len(sys.argv) < 2:
        print("Usage:")
        print("test_autograder.py /path/to/submission/folder/")
        print("\nScript must be run from within the autograder folder.")
        return

    tmpdir = tempfile.mkdtemp()

    shutil.copytree(sys.argv[1], os.path.join(tmpdir, 'submission')) 
    shutil.copytree('./', os.path.join(tmpdir, 'source')) 
    os.mkdir(os.path.join(tmpdir, 'results'))

    my_env = os.environ.copy()
    my_env["JMU_GRADESCOPE_BASE"] = tmpdir

    p = subprocess.Popen('./run_autograder', env=my_env)
    p.wait()

    shutil.copy(os.path.join(tmpdir, 'results', 'results.json'),
                './test_results.json')

    shutil.rmtree(tmpdir)
    
    sys.exit(p.returncode)

if __name__ == "__main__":
    main()

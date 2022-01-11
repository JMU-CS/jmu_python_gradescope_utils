import unittest
import os
from gradescope_utils.autograder_utils.json_test_runner import JSONTestRunner
import jmu_gradescope_utils

if 'JMU_GRADESCOPE_BASE' in os.environ:
    GRADESCOPE_BASE = os.environ['JMU_GRADESCOPE_BASE']
else:
    GRADESCOPE_BASE = '/autograder'

unittest.defaultTestLoader.sortTestMethodsUsing = jmu_gradescope_utils.test_compare

if __name__ == '__main__':
    suite = unittest.defaultTestLoader.discover('tests')
    outfile = os.path.join(GRADESCOPE_BASE, 'results', 'results.json')

    with open(outfile, 'w') as f:
        JSONTestRunner(visibility='visible', stream=f).run(suite)

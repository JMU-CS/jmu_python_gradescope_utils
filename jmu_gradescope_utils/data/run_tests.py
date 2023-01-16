#!/usr/bin/env python
import sys
from jmu_gradescope_utils import run_utils

run_utils.setup_autograder()
num_errors_and_failures = run_utils.run_tests()
sys.exit(num_errors_and_failures)

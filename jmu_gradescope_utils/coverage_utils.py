"""Utilities for running student tests and checking code coverage."""
import unittest
import json
import os
import tempfile
import sys
import importlib
import logging
import traceback
from pathlib import Path
from coverage import Coverage

def get_gradescope_base():
    if 'JMU_GRADESCOPE_BASE' in os.environ:
        return os.environ['JMU_GRADESCOPE_BASE']
    else:
        return '/autograder'

def run_student_tests(print_feedback=True, show_traces=True,
                      success_required=True):
    """Run a suite of student submitted tests.

    Tests must be located in /autograder/source/student_tests/

    Args:
        print_feedback (bool): Print success or failure message
        show_traces (bool): Show failure/error stack traces
        success_required (bool): If True, this function will raise an
                                 AssertionError if any student tests fail.

    Returns:
        bool: True if all tests pass, False otherwise

    Raises:
        AssertionError if success_required is true and any test fails.

    """
    logging.info("Running student tests...")
    try:
        source_base = os.path.join(get_gradescope_base(), 'source')
        suite = unittest.defaultTestLoader.discover('student_tests',
                                                    top_level_dir=source_base)
        result = unittest.TestResult()
        suite.run(result)
    except:
        logging.error(f"Error running student tests:\n {traceback.format_exc()}")

    logging.info("Tests have run.")

    succeeded = len(result.failures) == 0 and len(result.errors) == 0

    if not succeeded:
        if print_feedback:
            print(
                "It looks like your submission is not passing your own tests:")
            if len(result.errors) > 0:
                print("Errors:")
                for error in result.errors:
                    print(error[0]._testMethodName)
                    if show_traces:
                        print(error[1])
            if len(result.failures) > 0:
                print("Failures:")
                for failure in result.failures:
                    print(failure[0]._testMethodName)
                    if show_traces:
                        print(failure[1])
        if success_required:
            raise AssertionError("Student tests failed.")
    else:
        if print_feedback:
            print("Submission passes student tests.")

    return succeeded


def check_coverage(checked_files, branch=False, target_percentage=100.0,
                   print_feedback=True,
                   show_details=True, success_required=True):
    """Check code coverage for student-submitted unit tests.

    Args:
        checked_files (list): A list of file names for the files that should
                              be covered by the tests.
        target_percentage (float): The target coverage percentage for each
                                   file.
        branch (bool): True if branch coverage should be checked, False for
                       statement coverage only.
        print_feedback (bool): True if success or failure message should be
                               printed.
        show_details (bool): True if a detailed coverage report should be
                             printed in the case that coverage is less than
                             target.
        success_required: True if an AssertionError should be raised in the
                          case of insufficient coverage.

    Returns:
        bool: True if coverage hits target, False otherwise.

    Raises:
        AssertionError if success_required, and coverage is below target.

    """
    logging.info("Checking coverage...")
    
    source_base = os.path.join(get_gradescope_base(), 'source')
    try:
        # Run the tests while checking coverage...
        cov = Coverage(branch=branch)
        cov.start()

        # Make sure the tested modules are imported during coverage
        # monitoring so that the definition lines are covered.
        for name in checked_files:
            module = Path(name).stem
            if module in sys.modules:
                del sys.modules[module]
            importlib.import_module(module)

        run_student_tests(print_feedback=False, success_required=False)
        cov.stop()

        # Get coverage data as a dictionary...
        tmp_json = tempfile.mkstemp(suffix='.json', text=True)[1]
        cov.json_report(outfile=tmp_json)
        with open(tmp_json, 'r') as f:
            data = json.load(f)
        os.remove(tmp_json)

        adequate_coverage = True
        full_coverage = True
        for checked_file in checked_files:
            checked_file = os.path.join(source_base, checked_file)
            if data['files'][checked_file]['summary']['percent_covered'] < target_percentage:
                adequate_coverage = False
            if data['files'][checked_file]['summary']['percent_covered_display'] != '100':
                full_coverage = False

        # Get the coverage report in table form.
        if show_details:
            tmp_report = tempfile.mkstemp(suffix='.txt', text=True)[1]
            with open(tmp_report, 'w') as f:
                cov.report(morfs=checked_files, file=f)
            with open(tmp_report, 'r') as f:
                report_txt = f.read()
            os.remove(tmp_report)

    except:
        logging.error(f"Error running student tests:\n {traceback.format_exc()}")

    if print_feedback:
        files_str = ", ".join(checked_files)
        if full_coverage:
            if branch:
                print(f"100% statement and branch coverage of: {files_str}")
            else:
                print(f"100% statement coverage of: {files_str}")

        elif adequate_coverage:
            if branch:
                print(f"Sufficient statement and branch coverage of: {files_str}")
            else:
                print(f"Sufficient statement coverage of: {files_str}")

            if show_details:
                print(report_txt)

        else:
            if len(checked_files) > 1:
                print(f"Test coverage is less than target of {target_percentage}% for at least one file.")
            else:
                print(f"Test coverage is less than target of {target_percentage}%.")

            if show_details:
                print(report_txt)

    if success_required and not adequate_coverage:
        raise AssertionError("Coverage failed.")

    return adequate_coverage


if __name__ == "__main__":
    run_student_tests(show_traces=False)
    #check_coverage(['store_inventory.py'], success_required=True,
    #               show_details=True)

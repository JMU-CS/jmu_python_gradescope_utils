"""Utilities for running student tests and checking code coverage."""
import unittest
import json
import os
import tempfile
import sys
import importlib
from pathlib import Path
from coverage import Coverage


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
    suite = unittest.defaultTestLoader.discover('student_tests',
                                                top_level_dir="./")
    result = unittest.TestResult()
    suite.run(result)

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


def check_coverage(checked_files, branch=False, print_feedback=True,
                   show_details=True, success_required=True):
    """Check code coverage for student-submitted unit tests.

    Args:
        checked_files (list): A list of file names for the files that should
                              be covered by the tests.
        branch (bool): True if branch coverage should be checked, False for
                       statement coverage only.
        print_feedback (bool): True if success or failure message should be
                               printed.
        show_details (bool): True if a detailed coverage report should be
                             printed in the case that coverage is not 100%.
        success_required: True if an AssertionError should be raised in the
                          case of insufficient coverage.

    Returns:
        bool: True if full coverage, False otherwise.

    Raises:
        AssertionError if success_required, and less than full coverage.

    """

    # Run the tests while checking coverage...
    cov = Coverage(branch=branch)
    cov.start()

    # Make sure the tested modules are imported during coverage
    # monitoring so that the definition lines are covered.
    for name in checked_files:
        module = Path(name).stem
        del sys.modules[module]
        importlib.import_module(module)

    passed_tests = run_student_tests(print_feedback=False,
                                     success_required=False)
    cov.stop()

    # Now check the coverage...
    tmp_json = tempfile.mkstemp(suffix='.json', text=True)[1]
    cov.json_report(outfile=tmp_json)
    with open(tmp_json, 'r') as f:
        data = json.load(f)
    os.remove(tmp_json)

    full_coverage = True
    for checked_file in checked_files:
        if data['files'][checked_file]['summary']['percent_covered_display'] != '100':
            full_coverage = False

    if not full_coverage:
        if print_feedback:
            print("Test coverage is less than 100%.")
            if show_details:
                tmp_report = tempfile.mkstemp(suffix='.txt', text=True)[1]
                with open(tmp_report, 'w') as f:
                    cov.report(morfs=checked_files, file=f)
                with open(tmp_report, 'r') as f:
                    print(f.read())
                os.remove(tmp_report)
        if success_required:
            raise AssertionError("Coverage failed.")
    else:
        if print_feedback and branch:
            print("100% statement and branch coverage of: " +
                  ", ".join(checked_files))
        elif print_feedback:
            print("100% statement coverage of: " +
                  ", ".join(checked_files))
            
    return full_coverage


if __name__ == "__main__":
    run_student_tests(show_traces=False)
    #check_coverage(['store_inventory.py'], success_required=True,
    #               show_details=True)

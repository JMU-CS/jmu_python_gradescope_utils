"""Code for actually executing the autograder on the server."""

import shutil
import os
from pathlib import Path
import configparser
import logging
import unittest
import jmu_gradescope_utils
from gradescope_utils.autograder_utils.json_test_runner import JSONTestRunner

def get_gradescope_base():
    if 'JMU_GRADESCOPE_BASE' in os.environ:
        return os.environ['JMU_GRADESCOPE_BASE']
    else:
        return '/autograder'


def parse_file_list(config_str):
    files = [x.strip() for x in config_str.split(',')]
    files = [x for x in files if len(x) > 0]
    return files

def setup_autograder():
    logging.basicConfig(level=logging.INFO)
    gradescope_base = get_gradescope_base()
    logging.info("Configuring autograder...")
    source_base = Path(gradescope_base) / 'source'
    config_path = source_base / 'config.ini'
    config = configparser.ConfigParser()
    config.read(config_path)

    if not config_path.exists():
        logging.error(f"Missing config file: {config_path}")
        return

    submit_code_files = parse_file_list(config['SUBMIT']['code'])
    submit_test_files = parse_file_list(config['SUBMIT']['tests'])

    # COPY STUDENT SUBMITTED CODE
    submission_base = Path(gradescope_base) / 'submission'
    for name in submit_code_files:
        logging.info(f"Copying student submitted file: {name} to {source_base/name}")
        shutil.copy(submission_base / name,  source_base / name)

    # COPY STUDENT SUBMITTED TESTS
    student_test_dir = source_base / 'student_tests'
    student_test_dir.mkdir()
    (student_test_dir / '__init__.py').touch()

    for name in submit_test_files:
        logging.info(f"Copying student submitted test file: {name} to {student_test_dir/name}")
        shutil.copy(submission_base / name,  student_test_dir / name)

def run_tests():
    logging.basicConfig(level=logging.INFO)
    logging.info("Running autograder...")
    gradescope_base = get_gradescope_base()
    unittest.defaultTestLoader.sortTestMethodsUsing = jmu_gradescope_utils.test_compare
    source_base = Path(gradescope_base) / 'source'
    suite = unittest.defaultTestLoader.discover(str(source_base / 'tests'),
                                                top_level_dir=str(source_base))
    outfile = os.path.join(gradescope_base, 'results', 'results.json')

    with open(outfile, 'w') as f:
        result = JSONTestRunner(visibility='visible', stream=f).run(suite)

    return len(result.errors + result.failures)

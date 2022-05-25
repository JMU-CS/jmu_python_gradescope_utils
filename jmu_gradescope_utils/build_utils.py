"""Code for generating and testing Gradescope autograder uploads."""

import logging
import zipfile
import shutil
import os
import pkg_resources
import configparser
from pathlib import Path
import tempfile
import subprocess
import stat


def test_autograder(autograder_folder, sample_folder,
                    delete_tmp_folder=True):
    return_loc = None
    try:
        tmpdir = Path(tempfile.mkdtemp())
        sourcedir = tmpdir / 'source'

        zip_location = tmpdir / 'tmp.zip'
        logging.info(f"Creating zip file {str(zip_location)} for testing...")
        build_zip(autograder_folder, zip_location)

        logging.info("Unzipping into the test folder...")

        with zipfile.ZipFile(zip_location, 'r') as zip_obj:
            zip_obj.extractall(path=sourcedir)

        logging.info(f"Copying sample submission from {sample_folder}")
        shutil.copytree(sample_folder, os.path.join(tmpdir, 'submission'))

        my_env = os.environ.copy()
        my_env["JMU_GRADESCOPE_BASE"] = tmpdir

        os.makedirs(tmpdir / 'results')

        autograder_path = str(sourcedir / 'run_autograder')

        # Make executable
        st = os.stat(autograder_path)
        os.chmod(autograder_path, st.st_mode | stat.S_IEXEC)

        logging.info("Running the autograder...")
        p = subprocess.Popen(str(autograder_path),
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             env=my_env)
        stdout, stderr = p.communicate()
        if len(stdout) > 0:
            logging.error("stdout for run_autograder:\n" + stdout.decode())
        if len(stderr) > 0:
            logging.error("stderr for run_autograder:\n" + stderr.decode())

        return_loc = Path(tempfile.mkdtemp()) / 'results.json'
        shutil.copy(tmpdir / 'results' / 'results.json', return_loc)

    finally:
        if delete_tmp_folder:
            shutil.rmtree(tmpdir)
        return return_loc


def build_zip(autograder_folder, zip_location):
    # These just need to be copied in.
    files_to_copy = ['run_tests.py',
                     'setup.sh', 'requirements.txt']

    # These need to be copied in unless the user provides an alternate
    # version
    config_files = ['flake8.cfg', 'docstring.cfg']

    autograder_template = 'run_autograder_template'

    config_path = Path(autograder_folder) / 'config.ini'
    if not config_path.exists():
        logging.error(f"Missing file: {config_path}")
        return

    # if autograder.zip already exists for this hw, back it up
    if os.path.exists(zip_location):
        bak_location = zip_location + '.bak'
        shutil.copy(zip_location, bak_location)
        logging.info(f"Backing up existing zip file to {bak_location}")

    zip_file = zipfile.ZipFile(zip_location, mode='w')

    # Set up the official tests folder...
    tests_path = Path(autograder_folder) / 'tests'
    for path in tests_path.glob('*'):
        logging.info(f"Adding {path.name} to zip file")
        zip_file.write(path, arcname=os.path.join('tests', path.name))
    zip_file.writestr(os.path.join('tests', '__init__.py'), '')

    # Add scaffolding code
    scaffold_path = Path(autograder_folder) / 'scaffolding'
    for path in scaffold_path.glob('*'):
        logging.info(f"Adding {path.name} to zip file")
        zip_file.write(path, arcname=path.name)

    # Add the files that just need to be added...
    for file_name in files_to_copy:
        path = pkg_resources.resource_filename('jmu_gradescope_utils',
                                               os.path.join('data', file_name))
        logging.info(f"Adding {file_name} to zip file")
        zip_file.write(path, arcname=file_name)

    # Add config files...
    for file_name in config_files:
        path = os.path.join(autograder_folder, 'configurations', file_name)
        if os.path.exists(path):
            logging.info(f"Adding user provided {file_name} to zip file")
            zip_file.write(path, arcname=file_name)
        else:
            path = pkg_resources.resource_filename('jmu_gradescope_utils',
                                                   os.path.join('data',
                                                                file_name))
            logging.info(f"Adding default {file_name} to zip file")
            zip_file.write(path, arcname=file_name)

    # Update the run_autograder script and add it
    config = configparser.ConfigParser()
    config.read(config_path)

    submit_code_files = [x.strip() for x in config['SUBMIT']['code'].split(',')]
    submit_test_files = [x.strip() for x in
                         config['SUBMIT']['tests'].split(',')]
    submit_code_files_str = ' '.join(submit_code_files)
    submit_test_files_str = ' '.join(submit_test_files)
    logging.info(f'Student submitted code files: {submit_code_files_str}')
    if len(submit_test_files_str) > 0:
        logging.info(f'Student submitted test files: {submit_test_files_str}')

    template_path = os.path.join('data', autograder_template)
    autograder_str = pkg_resources.resource_string('jmu_gradescope_utils',
                                                   template_path).decode(
        'utf-8')
    autograder_str = autograder_str.replace('__SOURCE_FILES__',
                                            submit_code_files_str)
    autograder_str = autograder_str.replace('__TEST_FILES__',
                                            submit_test_files_str)

    logging.info(f'Adding run_autograder to zip file.')
    zip_file.writestr('run_autograder', autograder_str)

    zip_file.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # build_zip('../examples/hello_world_with_coverage/', 'tmp.zip')
    loc = test_autograder(
        '/home/spragunr/jmu_python_gradescope_utils/examples/hello_world_new/',
        '/home/spragunr/jmu_python_gradescope_utils/examples/hello_world_new/sample/')

    subprocess.run(['xdg-open', str(loc)])

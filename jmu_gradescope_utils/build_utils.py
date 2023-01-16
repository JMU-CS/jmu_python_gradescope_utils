"""Code for generating and testing Gradescope autograder uploads."""

import logging
import zipfile
import shutil
import os
import pkg_resources
from pathlib import Path
import tempfile
import subprocess
import traceback
import sys

def create_template(folder):
    path = Path(folder)
    if path.exists():
        logging.error(f"Cannot create folder {path.name} already exists.")
        return False

    source = pkg_resources.resource_filename('jmu_gradescope_utils',
                                             os.path.join('data', 'template'))
    shutil.copytree(source, path)
    # Can't have empty folders in the template...
    (path / 'scaffolding').mkdir(exist_ok=True)
    logging.info(f'Created {path}')
    return True


def test_autograder(autograder_folder, sample_folder,
                    delete_tmp_folder=True):
    return_loc = None
    return_code = 1
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
        os.makedirs(tmpdir / 'results')

        my_env = os.environ.copy()
        my_env["JMU_GRADESCOPE_BASE"] = str(tmpdir)

        script_path = str(sourcedir / 'run_tests.py')

        p = subprocess.Popen([sys.executable, script_path],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             env=my_env)
        stdout, stderr = p.communicate()
        return_code = p.returncode
        # Raise an exception if there was a problem so we can see the stack.
        if len(stdout) > 0:
            logging.error("stdout for run_tests.py:\n" + stdout.decode())
        if len(stderr) > 0:
            logging.error("stderr for run_tests.py:\n" + stderr.decode())

        logging.info("Autograder finished.")

        # Give a .txt extension so it will be opened in a text
        # editor by default.
        return_loc = Path(tempfile.mkdtemp()) / 'results.json.txt'
        shutil.copy(tmpdir / 'results' / 'results.json', return_loc)

    except:
        logging.error(f"Error testing autograder:\n {traceback.format_exc()}")

    finally:
        if delete_tmp_folder:
            shutil.rmtree(tmpdir)
        logging.info(f"Autograder result: {return_loc}")
        return return_loc, return_code


def build_zip(autograder_folder, zip_location):
    # These just need to be copied in.
    files_to_copy = ['run_autograder', 'setup.sh', 'run_tests.py']

    # These need to be copied in unless the user provides an alternate
    # version
    config_files = ['flake8.cfg', 'docstring.cfg', 'requirements.txt']

    # if autograder.zip already exists for this hw, back it up
    if os.path.exists(zip_location):
        bak_location = zip_location + '.bak'
        shutil.copy(zip_location, bak_location)
        logging.info(f"Backing up existing zip file to {bak_location}")

    zip_file = zipfile.ZipFile(zip_location, mode='w')

    config_path = Path(autograder_folder) / 'config.ini'
    if not config_path.exists():
        logging.error(f"Missing file: {config_path}")
        return
    zip_file.write(config_path, 'config.ini')

    # Set up the official tests folder...
    tests_path = Path(autograder_folder) / 'tests'
    for path in tests_path.glob('*'):
        logging.info(f"Adding {path.name} to zip file")
        zip_file.write(path, arcname=os.path.join('tests', path.name))
    zip_file.writestr(os.path.join('tests', '__init__.py'), '')

    # Add scaffolding code
    scaffold_path = Path(autograder_folder) / 'scaffolding'
    for path in scaffold_path.glob('**/*'):
        lname = str(path).split(str(scaffold_path) + os.sep)[1]
        logging.info(f"Adding  {lname} to zip file")
        zip_file.write(path, arcname=lname)

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
            source = os.path.join('data', 'template', 'configurations', file_name)
            path = pkg_resources.resource_filename('jmu_gradescope_utils', source)
            logging.warning(f"{file_name} not provided. Adding default to zip file.")
            zip_file.write(path, arcname=file_name)

    zip_file.close()
    logging.info(f'Zip file {zip_location} created.')


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # build_zip('../examples/hello_world_with_coverage/', 'tmp.zip')
    #loc = test_autograder(
    #    '/home/spragunr/jmu_python_gradescope_utils/examples/hello_world_new/',
    #    '/home/spragunr/jmu_python_gradescope_utils/examples/hello_world_new/sample/')

    #subprocess.run(['xdg-open', str(loc)])
    create_template(sys.argv[1])

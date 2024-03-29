from setuptools import setup
import os
import logging

# https://stackoverflow.com/a/36693250
def package_files(directory):
    paths = []
    for (path, _, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths

extra_files = package_files('jmu_gradescope_utils/data')

setup(
    name='jmu_gradescope_utils',
    version='0.2',
    packages=['jmu_gradescope_utils'],
    url='',
    license='',
    author='Nathan Sprague',
    author_email='nathan.r.sprague@gmail.com',
    description='Python Gradescope utilities',
    install_requires=[
        'gradescope-utils>=0.4',
        'flake8',
        'coverage>=6.0',
        'pep8-naming',
        'flake8-docstrings',
        'flake8-rst-docstrings',
        'darglint',
        'tk',
        'importlib_metadata>=4.2',
    ],
    scripts=['scripts/test_autograder.py',
             'scripts/jmu_gradescope_builder.py'],
    include_package_data=True,
    package_data={'': extra_files},
)

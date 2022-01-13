from setuptools import setup

setup(
    name='jmu_gradescope_utils',
    version='0.1',
    packages=['jmu_gradescope_utils'],
    url='',
    license='',
    author='Nathan Sprague',
    author_email='nathan.r.sprague@gmail.com',
    description='Python Gradescope utilities',
    install_requires=[
        'flake8',
        'pep8-naming'
    ],
    scripts=['scripts/test_autograder.py']

)

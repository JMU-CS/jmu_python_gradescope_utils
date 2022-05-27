from setuptools import setup

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
        'flake8',
        'coverage',
        'pep8-naming',
        'flake8-docstrings',
        'flake8-rst-docstrings',
        'darglint',
        'tk',
        'gradescope_utils',
    ],
    scripts=['scripts/test_autograder.py',
             'scripts/jmu_gradescope_builder.py'],
    include_package_data=True,
    package_data={'jmu_gradescope_utils': ['data/*']},
)

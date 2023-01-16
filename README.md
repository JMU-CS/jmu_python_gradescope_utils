# jmu_python_gradescope_utils

This is a library that adds some useful functionality to the default
Python autograder scripts available from
<https://github.com/gradescope/gradescope-utils>.

Features include: 

*   `JmuTestCase`, a subclass of `unittest.TestCase` that:
    * guarantees tests will be executed in the order they are declared.
    * provides a `@required` annotation that makes a test required, so
      that subsequent tests will automatically fail if it fails.
    * provide several additional assertion methods, including an
      `assertOutputEqual` method that makes it possible to specify
      stdin input and check for correct stdout output for a Python
      script.
*    Some additional utility functions for checking PEP 8 compliance
     and applying regex searches to submitted source files.
*    A script that makes it possible to test the autograder logic
     locally before uploading to the Gradescope server:
     `test_autograder.py`
*    A graphical tool for testing autograders and building autograder zip
     files.
	 
API Documentation can be found here: <https://jmu-cs.github.io/jmu_python_gradescope_utils/>

## Installation

```
pip3 install wheel
pip3 install git+https://github.com/JMU-CS/jmu_python_gradescope_utils.git
```

On Linux, this will probably add the GUI script to your PATH so that it can be executed as:

```
$ jmu_gradescope_builder.py
```

If that doesn't work, you may need to execute the script using the Python interpreter:

```
python3 wherever/on/your/system/bin/jmu_gradescope_builder.py
```

Note that the GUI uses tk, which should be available in Windows, Linux
and OSX. Unfortunately, the tk library distributed with some versions
of OSX is broken, resulting in a blank black window. There are some
reports that upgrading Python to 3.10 resolves the issue.

## Autograder Format

See `examples/hello_world/` and `hello_world_w_coverage` for a sample autograders.

Autograder folders are organized as follows:

```
hello_world/
│
├── config.ini
│
├── configurations/
│   ├── flake8.cfg
│   ├── docstring.cfg
│   └── requirements.txt
│
├── sample/
│   └── hello_world.py
│
└── scaffolding/
│
└── tests/
    └── test_hello.py
```


### `config.ini`

This specifies the files that must be submitted by the student:

```
[SUBMIT]
code: hello_world.py
tests:
```

The `test` field should contain the names of student test files for assignments that require student-submitted unit tests.

### `flake8.cfg`

This is the `flake8` configuration file that will be used by
[assertPassesPep8](https://jmu-cs.github.io/jmu_python_gradescope_utils/jmu_test_case.html#jmu_gradescope_utils.jmu_test_case._JmuTestCase.assertPassesPep8).

The [flake8](https://flake8.pycqa.org/en/latest/index.html) tool is
used by our library for Python style checking.  The possible error
codes are listed in the following locations:

* [pycodestyle error codes](https://pycodestyle.pycqa.org/en/latest/intro.html#error-codes)
* [flake8 error codes](https://flake8.pycqa.org/en/latest/user/error-codes.html)


The current default looks like this:
```
[flake8]
select = E, F, C90
ignore = W, E226, E123, W504, N818, E704, E24, E121, E126
max-line-length = 100
```

### `docstring.cfg`
This is the `flake8` configuration file that will be used by [assertDocstringsCorrect](https://jmu-cs.github.io/jmu_python_gradescope_utils/jmu_test_case.html#jmu_gradescope_utils.jmu_test_case._JmuTestCase.assertDocstringsCorrect).  The current default looks like this:

```
[flake8]
select = D,DAR
ignore = D401

[pydocstyle]
convention=google

[darglint]
docstring_style=google
```

The available error codes for the two plugins can be found here:

* `pydocstyle`: <http://www.pydocstyle.org/en/stable/error_codes.html>
* `darglint`: <https://github.com/terrencepreilly/darglint#error-codes>


### `requirements.txt`

This file should list any python packages that are required for this
assignment. They will be pip installed on the server by the autograder
script. 

### sample/

This folder should contain a reference solution.  This isn't strictly
necessary, but the autograder testing utility will expect to find a
solution at this location.

### scaffolding/

Any files in this folder will be copied into the same folder as the
student submission before testing.  This could be data files or Python
modules.

### tests/

Instructor unit tests.


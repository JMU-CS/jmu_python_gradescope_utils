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
      `assertScriptOutputEqual` method that makes it possible to specify
      stdin input and check for correct stdout output for a Python
      script.
*    Some additional utility functions for checking PEP 8 compliance
     and applying regex searches to submitted source files.
*    A script that makes it possible to test the autograder logic
     locally before uploading to the Gradescope server:
     `test_autograder.py`

## Installation

```
pip3 install git+https://github.com/JMU-CS/jmu_python_gradescope_utils.git
```

This will automatically install all dependencies except
`gradescope-utils` which can be installed as:

```
pip3 install gradescope-utils>=0.3.1
```

## Instructions

See `examples/hello_world_autograder/` for a sample autograder.

To perform a test run: 

```bash
$ cd /your/autograder
$ test_autograder.py /path/to/sample/submission/folder
```

The output of the test will be stored in a file named
`test_results.json`.

Once everything is working correctly, just zip the contents of the
autograder folder and upload to Gradescope:

```bash
$ cd /your/autograder
$ zip -r autograder.zip .
```

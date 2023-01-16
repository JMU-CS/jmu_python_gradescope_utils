import unittest
from gradescope_utils.autograder_utils.decorators import weight, number
from jmu_gradescope_utils import JmuTestCase, required
import jmu_gradescope_utils

FILENAME = 'hello_world.py'

class TestHelloWorld(JmuTestCase):

    @required()
    @weight(0)
    def test_submitted_files(self):
        """Check submitted files"""
        self.assertRequiredFilesPresent([FILENAME])

    @weight(2)
    def test_pep8(self):
        """PEP 8 checks. """
        self.assertPassesPep8(FILENAME)

    @weight(8)
    def test_functionality(self):
        """Test for correct output."""

        string_in = ""
        expected = "Hello World!\n"
        self.assertOutputEqual('hello_world.py', string_in, expected)
        print('Correct output:\n' + expected)
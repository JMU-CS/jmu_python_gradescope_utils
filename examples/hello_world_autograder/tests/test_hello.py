import unittest
from gradescope_utils.autograder_utils.decorators import weight, number
from jmu_gradescope_utils import JmuTestCase, required, check_submitted_files
import jmu_gradescope_utils


class TestHelloWorld(JmuTestCase):

    FILENAME = 'hello_world.py'

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
    def test_output(self):
        """hello_world.py output checks. """
        string_in = ""
        expected = "Hello World!\n"
        self.assertOutputCorrect(FILENAME, string_in, expected)




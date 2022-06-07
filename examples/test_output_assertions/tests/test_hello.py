import unittest
from gradescope_utils.autograder_utils.decorators import weight, number
from jmu_gradescope_utils import JmuTestCase, required, check_submitted_files
import jmu_gradescope_utils

def to_lower(s):
    return s.lower()

class TestHelloWorld(JmuTestCase):


    @required()
    @weight(0)
    def test_submitted_files(self):
        """Check submitted files"""
        missing_files = check_submitted_files(['hello_world.py'])
        for path in missing_files:
            print('Missing {0}'.format(path))
        self.assertEqual(len(missing_files), 0, 'Missing some required files!')
        print('All required files submitted!')
    
    @required()
    @weight(1)
    def test_output_retrieved(self):
        """hello_world.py output retrieved. """
        string_in = ""
        expected = "Hello World!\n"
        actual = self.result('hello_world.py', string_in)
        self.assertEqual(expected, actual["stdout"], "didn't get expected result from script")
        print('Correct output equal:\n' + expected)
        
    @weight(1)
    def test_output_exactly(self):
        """hello_world.py output equal. """
        string_in = ""
        expected = "Hello World!\n"
        self.assertOutputEqual('hello_world.py', string_in, expected)
        print('Correct output equal:\n' + expected)

    @weight(1)
    def test_output_not_equal(self):
        """hello_world.py output not equal. """
        string_in = ""
        expected = "Incorrect\n"
        self.assertOutputNotEqual('hello_world.py', string_in, expected)
        print('Correct output not equal:\n' + expected)
        
    @weight(1)
    def test_output_contains(self):
        """hello_world.py output contains. """
        string_in = ""
        expected = "hello"
        self.assertInOutput('hello_world.py', string_in, expected, processor=to_lower)
        print('Correct output contains:\n' + expected)
        
    @weight(1)
    def test_output_not_containing(self):
        """hello_world.py output not contains. """
        string_in = ""
        expected = "hola"
        self.assertNotInOutput('hello_world.py', string_in, expected)
        print('Correct output not containing:\n' + expected)
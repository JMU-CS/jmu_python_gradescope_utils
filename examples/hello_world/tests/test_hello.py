import unittest
from gradescope_utils.autograder_utils.decorators import weight, number
from jmu_gradescope_utils import JmuTestCase, required, check_submitted_files
import jmu_gradescope_utils


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

    
    @weight(2)
    def test_pep8(self):
        """PEP 8 checks. """
        output = jmu_gradescope_utils.run_flake8('hello_world.py')
        if len(output) != 0:
            self.fail("Submission does not pass pep8 checks:\n" + output)
        print('Submission passes all formatting checks!')
        
    @weight(8)
    def test_output(self):
        """hello_world.py output checks. """
        string_in = ""
        expected = "Hello World!\n"
        self.assertOutputEqual('hello_world.py', string_in, expected)
        print('Correct output:\n' + expected)




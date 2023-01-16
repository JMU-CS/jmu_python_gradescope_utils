import unittest
from gradescope_utils.autograder_utils.decorators import weight, number
from jmu_gradescope_utils import JmuTestCase, required, check_submitted_files
import jmu_gradescope_utils

FILENAME = 'hello_world.py'

class TestHelloWorld(JmuTestCase):

    @required()
    @weight(0)
    def test_submitted_files(self):
        """Check submitted files."""
        self.assertRequiredFilesPresent([FILENAME, 'test_hello.py'])

    @weight(2)
    def test_pep8(self):
        """PEP 8 checks."""
        self.assertPassesPep8(FILENAME)

    @weight(0)
    @required()
    def test_passes_student_tests(self):
        """Check that submission passes student tests."""
        jmu_gradescope_utils.run_student_tests()

    @weight(4)
    @required()
    def test_student_coverage(self):
        """Check student test coverage."""
        jmu_gradescope_utils.check_coverage(['hello_world.py'])

    @weight(4)
    def test_functionality(self):
        """Test hello_func."""
        import hello_world
        self.assertEquals(hello_world.hello_func(), "Hello World")

import unittest
from gradescope_utils.autograder_utils.decorators import weight, number
from jmu_gradescope_utils import JmuTestCase, required
import jmu_gradescope_utils

FILENAME = 'submission_template.py'

class TestDefault(JmuTestCase):

    @required()
    @weight(0)
    def test_submitted_files(self):
        """Check submitted files"""
        self.assertRequiredFilesPresent([FILENAME])

    @required()
    @weight(0)
    def test_docstrings(self):
        """Docstring checks. """
        self.assertDocstringsCorrect(FILENAME)

    @weight(2)
    def test_pep8(self):
        """PEP 8 checks. """
        self.assertPassesPep8(FILENAME)

    @weight(8)
    def test_functionality(self):
        """Test student code funtionality."""
        self.assertEqual(1, 1)

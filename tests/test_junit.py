from io import StringIO
from unittest import TestCase

from unittest.mock import patch

from mlx.warnings import WarningsPlugin


class TestJUnitFailures(TestCase):
    def setUp(self):
        self.warnings = WarningsPlugin(verbose=True)
        self.warnings.activate_checker_name('junit')

    def test_no_warning(self):
        with open('tests/test_in/junit_no_fail.xml', 'r') as xmlfile:
            self.warnings.check(xmlfile.read())
        self.assertEqual(self.warnings.return_count(), 0)

    def test_single_warning(self):
        with open('tests/test_in/junit_single_fail.xml', 'r') as xmlfile:
            with patch('sys.stdout', new=StringIO()) as fake_out:
                self.warnings.check(xmlfile.read())
        self.assertEqual(self.warnings.return_count(), 1)
        self.assertRegex(fake_out.getvalue(), 'myfirstfai1ure')

    def test_dual_warning(self):
        with open('tests/test_in/junit_double_fail.xml', 'r') as xmlfile:
            with patch('sys.stdout', new=StringIO()) as fake_out:
                self.warnings.check(xmlfile.read())
        self.assertEqual(self.warnings.return_count(), 2)
        self.assertRegex(fake_out.getvalue(), 'myfirstfai1ure')
        self.assertRegex(fake_out.getvalue(), 'mysecondfai1ure')

    def test_invalid_xml(self):
        self.warnings.check('this is not xml')
        self.assertEqual(self.warnings.return_count(), 0)

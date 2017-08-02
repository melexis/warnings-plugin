from unittest import TestCase

from mlx.warnings import WarningsPlugin
from xml.etree.ElementTree import ParseError


class TestJUnitFailures(TestCase):
    def setUp(self):
        self.warnings = WarningsPlugin(False, False, True)

    def test_no_warning(self):
        with open('tests/junit_no_fail.xml') as xmlfile:
            self.warnings.check(xmlfile.read())
        self.assertEqual(self.warnings.return_count(), 0)

    def test_single_warning(self):
        with open('tests/junit_single_fail.xml') as xmlfile:
            self.warnings.check(xmlfile.read())
        self.assertEqual(self.warnings.return_count(), 1)

    def test_dual_warning(self):
        with open('tests/junit_double_fail.xml') as xmlfile:
            self.warnings.check(xmlfile.read())
        self.assertEqual(self.warnings.return_count(), 2)

    def test_invalid_xml(self):
        with self.assertRaises(ParseError):
            self.warnings.check('this is not xml')
        self.assertEqual(self.warnings.return_count(), 0)


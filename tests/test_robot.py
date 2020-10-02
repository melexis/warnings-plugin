from io import StringIO
from unittest import TestCase

from mlx.warnings import WarningsPlugin, RobotSuiteChecker
from mock import patch


class TestRobotWarnings(TestCase):
    def setUp(self):
        self.warnings = WarningsPlugin(verbose=True)
        self.dut = self.warnings.activate_checker_name('robot')
        self.suite1 = 'Suite One'
        self.suite2 = 'Suite Two'
        self.dut.checkers = [
            RobotSuiteChecker(self.suite1),
            RobotSuiteChecker(self.suite2),
        ]

    def test_no_warning(self):
        with open('tests/junit_no_fail.xml', 'r') as xmlfile:
            self.warnings.check(xmlfile.read())
        self.assertEqual(self.warnings.return_count(), 0)

    def test_single_warning(self):
        with open('tests/robot_single_fail.xml', 'r') as xmlfile:
            with patch('sys.stdout', new=StringIO()) as fake_out:
                self.warnings.check(xmlfile.read())
                count = self.warnings.return_count()
        stdout_log = fake_out.getvalue()

        self.assertEqual(count, 1)
        self.assertIn("Suite {!r}: 1 warnings found".format(self.suite1), stdout_log)
        self.assertIn("Suite {!r}: 0 warnings found".format(self.suite2), stdout_log)

    def test_double_warning(self):
        with open('tests/robot_double_fail.xml', 'r') as xmlfile:
            with patch('sys.stdout', new=StringIO()) as fake_out:
                self.warnings.check(xmlfile.read())
                count = self.warnings.return_count()
        stdout_log = fake_out.getvalue()

        self.assertEqual(count, 2)
        self.assertIn("Suite {!r}: 1 warnings found".format(self.suite1), stdout_log)
        self.assertIn("Suite {!r}: 1 warnings found".format(self.suite2), stdout_log)

    def test_invalid_xml(self):
        self.warnings.check('this is not xml')
        self.assertEqual(self.warnings.return_count(), 0)

    def test_testsuites_root(self):
        self.dut.checkers = [
            RobotSuiteChecker('test_warn_plugin_double_fail'),
            RobotSuiteChecker('test_warn_plugin_no_double_fail'),
        ]
        with open('tests/junit_double_fail.xml', 'r') as xmlfile:
            self.warnings.check(xmlfile.read())
            count = self.warnings.return_count()
        self.assertEqual(count, 2)

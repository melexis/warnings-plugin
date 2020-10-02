from io import StringIO
from unittest import TestCase

from unittest.mock import patch

from mlx.robot_checker import RobotSuiteChecker
from mlx.warnings import WarningsPlugin


class TestRobotWarnings(TestCase):
    def setUp(self):
        self.warnings = WarningsPlugin(verbose=True)
        self.dut = self.warnings.activate_checker_name('robot')
        self.suite1 = 'Suite One'
        self.suite2 = 'Suite Two'
        self.dut.checkers = [
            RobotSuiteChecker(self.suite1, verbose=True),
            RobotSuiteChecker(self.suite2, verbose=True),
        ]

    def test_no_warning(self):
        with open('tests/test_in/junit_no_fail.xml', 'r') as xmlfile:
            self.warnings.check(xmlfile.read())
        self.assertEqual(self.warnings.return_count(), 0)

    def test_single_warning(self):
        with open('tests/test_in/robot_single_fail.xml', 'r') as xmlfile:
            with patch('sys.stdout', new=StringIO()) as fake_out:
                self.warnings.check(xmlfile.read())
                count = self.warnings.return_count()
        stdout_log = fake_out.getvalue()

        self.assertEqual(count, 1)
        self.assertIn("Suite {!r}: 1 warnings found".format(self.suite1), stdout_log)
        self.assertIn("Suite {!r}: 0 warnings found".format(self.suite2), stdout_log)

    def test_double_warning_and_verbosity(self):
        with open('tests/test_in/robot_double_fail.xml', 'r') as xmlfile:
            with patch('sys.stdout', new=StringIO()) as fake_out:
                self.warnings.check(xmlfile.read())
                count = self.warnings.return_count()
        stdout_log = fake_out.getvalue()

        self.assertEqual(count, 2)
        self.assertEqual(
            '\n'.join([
                "Suite One &amp; Suite Two.Suite One.First Test",
                "Suite One &amp; Suite Two.Suite Two.Another test",
                "Suite {!r}: 1 warnings found".format(self.suite1),
                "Suite {!r}: 1 warnings found".format(self.suite2),
            ]) + '\n',
            stdout_log
        )

    def test_invalid_xml(self):
        self.warnings.check('this is not xml')
        self.assertEqual(self.warnings.return_count(), 0)

    def test_testsuites_root(self):
        self.dut.checkers = [
            RobotSuiteChecker('test_warn_plugin_double_fail'),
            RobotSuiteChecker('test_warn_plugin_no_double_fail'),
        ]
        with open('tests/test_in/junit_double_fail.xml', 'r') as xmlfile:
            self.warnings.check(xmlfile.read())
            count = self.warnings.return_count()
        self.assertEqual(count, 2)

import unittest

import pytest

from mlx.warnings import RobotSuiteChecker, WarningsPlugin, warnings_wrapper


class TestRobotWarnings(unittest.TestCase):
    @pytest.fixture(autouse=True)
    def caplog(self, caplog):
        self.caplog = caplog

    def setUp(self):
        self.warnings = WarningsPlugin()
        self.dut = self.warnings.activate_checker_name('robot', True)
        self.suite1 = 'Suite One'
        self.suite2 = 'Suite Two'
        self.dut.checkers = [
            RobotSuiteChecker(self.suite1),
            RobotSuiteChecker(self.suite2),
        ]

    def test_no_warning(self):
        with open('tests/test_in/junit_no_fail.xml') as xmlfile:
            self.warnings.check(xmlfile.read())
        self.assertEqual(self.warnings.return_count(), 0)

    def test_single_warning(self):
        with open('tests/test_in/robot_single_fail.xml') as xmlfile:
            self.warnings.check(xmlfile.read())
            count = self.warnings.return_count()
        self.assertEqual(count, 1)
        self.assertEqual(["Suite One &amp; Suite Two.Suite One.First Test"], self.caplog.messages)

    def test_double_warning_and_verbosity(self):
        retval = warnings_wrapper(['--verbose',
                                    '--robot',
                                    'tests/test_in/robot_double_fail.xml'])
        self.assertEqual(
            ["Suite One &amp; Suite Two.Suite One.First Test",
             "Suite One &amp; Suite Two.Suite Two.Another test",
             "number of warnings (2) is higher than the maximum limit (0).",
             "Robot: Returning error code 2."],
            self.caplog.messages
        )
        self.assertEqual(retval, 2)

    def test_invalid_xml(self):
        self.warnings.check('this is not xml')
        self.assertEqual(self.warnings.return_count(), 0)

    def test_testsuites_root(self):
        self.dut.checkers = [
            RobotSuiteChecker('test_warn_plugin_double_fail'),
            RobotSuiteChecker('test_warn_plugin_no_double_fail'),
        ]
        with open('tests/test_in/junit_double_fail.xml') as xmlfile:
            self.warnings.check(xmlfile.read())
            count = self.warnings.return_count()
        self.assertEqual(count, 2)

    def test_check_suite_name(self):
        self.dut.checkers = [
            RobotSuiteChecker('nonexistent_suite_name', check_suite_name=True),
        ]
        with open('tests/test_in/robot_double_fail.xml') as xmlfile:
            with self.assertRaises(SystemExit) as c_m:
                self.warnings.check(xmlfile.read())
        self.assertEqual(c_m.exception.code, -1)

    def test_robot_version_5(self):
        self.dut.checkers = [
            RobotSuiteChecker('Empty Flash Product Id', check_suite_name=True),
        ]
        with open('tests/test_in/robot_version_5.xml') as xmlfile:
            self.warnings.check(xmlfile.read())
            count = self.warnings.return_count()
        self.assertEqual(count, 6)


if __name__ == '__main__':
    unittest.main()

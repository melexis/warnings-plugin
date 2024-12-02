import unittest

from mlx.warnings import RobotSuiteChecker, WarningsPlugin


class TestRobotWarnings(unittest.TestCase):
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
            with self.assertLogs(level="INFO") as fake_out:
                self.warnings.check(xmlfile.read())
                count = self.warnings.return_count()
        stdout_log = fake_out.output

        self.assertEqual(count, 1)
        self.assertIn("INFO:root:Suite One &amp; Suite Two.Suite One.First Test", stdout_log)

    def test_double_warning_and_verbosity(self):
        with open('tests/test_in/robot_double_fail.xml', 'r') as xmlfile:
            with self.assertLogs(level="INFO") as fake_out:
                self.warnings.check(xmlfile.read())
                count = self.warnings.return_count()
        stdout_log = fake_out.output

        self.assertEqual(count, 2)
        self.assertEqual(
            [
                "INFO:root:Suite One &amp; Suite Two.Suite One.First Test",
                "INFO:root:Suite One &amp; Suite Two.Suite Two.Another test",
            ],
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

    def test_check_suite_name(self):
        self.dut.checkers = [
            RobotSuiteChecker('nonexistent_suite_name', check_suite_name=True),
        ]
        with open('tests/test_in/robot_double_fail.xml', 'r') as xmlfile:
            with self.assertRaises(SystemExit) as c_m:
                self.warnings.check(xmlfile.read())
        self.assertEqual(c_m.exception.code, -1)

    def test_robot_version_5(self):
        self.dut.checkers = [
            RobotSuiteChecker('Empty Flash Product Id', check_suite_name=True),
        ]
        with open('tests/test_in/robot_version_5.xml', 'r') as xmlfile:
            self.warnings.check(xmlfile.read())
            count = self.warnings.return_count()
        self.assertEqual(count, 6)


if __name__ == '__main__':
    unittest.main()

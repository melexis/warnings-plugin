from io import StringIO
from unittest import TestCase

from unittest.mock import patch

from mlx.warnings import warnings_wrapper


class TestIntegration(TestCase):

    def test_help(self):
        with self.assertRaises(SystemExit) as ex:
            warnings_wrapper(['--help'])
        self.assertEqual(0, ex.exception.code)

    def test_version(self):
        with self.assertRaises(SystemExit) as ex:
            warnings_wrapper(['--version'])
        self.assertEqual(0, ex.exception.code)

    def test_no_parser_selection(self):
        with self.assertRaises(SystemExit) as ex:
            warnings_wrapper([])
        self.assertEqual(2, ex.exception.code)

    min_ret_val_on_failure = 1
    junit_warning_cnt = 3

    def test_single_argument(self):
        retval = warnings_wrapper(['--junit', 'tests/test_in/junit_single_fail.xml'])
        self.assertEqual(1, retval)

    def test_single_defect_coverity(self):
        retval = warnings_wrapper(['--coverity', 'tests/test_in/coverity_single_defect.txt'])
        self.assertEqual(1, retval)

    def test_two_arguments(self):
        retval = warnings_wrapper(['--junit', 'tests/test_in/junit_single_fail.xml', 'tests/test_in/junit_double_fail.xml'])
        self.assertEqual(1 + 2, retval)

    def test_non_existing_logfile(self):
        retval = warnings_wrapper(['--sphinx', 'not-exist.log'])
        self.assertEqual(1, retval)
        retval = warnings_wrapper(['--xmlrunner', 'not-exist.log'])
        self.assertEqual(1, retval)

    def test_single_command_argument(self):
        retval = warnings_wrapper(['--junit', '--command', 'cat', 'tests/test_in/junit_single_fail.xml'])
        self.assertEqual(1, retval)

    def test_two_command_arguments(self):
        retval = warnings_wrapper(['--sphinx', '--command', 'cat', 'tests/test_in/sphinx_single_warning.txt', 'tests/test_in/sphinx_double_warning.txt'])
        self.assertEqual(1 + 2, retval)

    def test_command_with_its_own_arguments(self):
        retval = warnings_wrapper(['--sphinx', '--command', 'cat', '-A', 'tests/test_in/sphinx_single_warning.txt', 'tests/test_in/sphinx_double_warning.txt'])
        self.assertEqual(1 + 2, retval)

    def test_command_to_stderr(self):
        retval = warnings_wrapper(['--sphinx', '--command', 'cat', 'tests/test_in/sphinx_single_warning.txt', '>&2'])
        self.assertEqual(1, retval)

    def test_faulty_command(self):
        with self.assertRaises(OSError):
            warnings_wrapper(['--sphinx', '--command', 'blahahahaha', 'tests/test_in/sphinx_single_warning.txt'])

    def test_command_revtal_err(self):
        retval = warnings_wrapper(['--sphinx', '--command', 'false'])
        self.assertEqual(1, retval)

    def test_command_revtal_err_supress(self):
        retval = warnings_wrapper(['--sphinx', '--ignore-retval', '--command', 'false'])
        self.assertEqual(0, retval)

    def test_wildcarded_arguments(self):
        # note: no shell expansion simulation (e.g. as in windows)
        retval = warnings_wrapper(['--junit', 'tests/test_in/junit*.xml'])
        self.assertEqual(self.junit_warning_cnt, retval)

    def test_max(self):
        retval = warnings_wrapper(['--junit', '--maxwarnings', '2', 'tests/test_in/junit*.xml'])
        self.assertEqual(self.junit_warning_cnt, retval)

    def test_max_but_still_ok(self):
        retval = warnings_wrapper(['--junit', '--maxwarnings', '100', 'tests/test_in/junit*.xml'])
        self.assertEqual(0, retval)

    def test_min(self):
        retval = warnings_wrapper(['--junit', '--maxwarnings', '100', '--minwarnings', '100', 'tests/test_in/junit*.xml'])
        self.assertEqual(self.junit_warning_cnt, retval)

    def test_min_but_still_ok(self):
        retval = warnings_wrapper(['--junit', '--max-warnings', '100', '--min-warnings', '2', 'tests/test_in/junit*.xml'])
        self.assertEqual(0, retval)

    def test_exact_sphinx(self):
        retval = warnings_wrapper(['--sphinx', '--exact-warnings', '2', 'tests/test_in/sphinx_double_warning.txt'])
        self.assertEqual(0, retval)

    def test_exact_too_few(self):
        retval = warnings_wrapper(['--sphinx', '--exact-warnings', '3', 'tests/test_in/sphinx_double_warning.txt'])
        self.assertEqual(2, retval)

    def test_exact_too_many(self):
        retval = warnings_wrapper(['--sphinx', '--exact-warnings', '1', 'tests/test_in/sphinx_double_warning.txt'])
        self.assertEqual(2, retval)

    def test_exact_junit(self):
        retval = warnings_wrapper(['--junit', '--exact-warnings', '3', 'tests/test_in/junit*.xml'])
        self.assertEqual(0, retval)

    def test_exact_with_min(self):
        with self.assertRaises(SystemExit):
            warnings_wrapper(['--junit', '--exact-warnings', '3', '--min-warnings', '3', 'tests/test_in/junit*.xml'])

    def test_exact_with_max(self):
        with self.assertRaises(SystemExit):
            warnings_wrapper(['--junit', '--exact-warnings', '3', '--max-warnings', '3', 'tests/test_in/junit*.xml'])

    def test_configfile_ok(self):
        retval = warnings_wrapper(['--config', 'tests/test_in/config_example.json', 'tests/test_in/junit_single_fail.xml'])
        self.assertEqual(0, retval)

    def test_configfile_exclude_commandline(self):
        with self.assertRaises(SystemExit) as ex:
            warnings_wrapper(['--config', 'tests/test_in/config_example.json', '--junit', 'tests/test_in/junit_single_fail.xml'])
        self.assertEqual(2, ex.exception.code)

    def test_sphinx_deprecation(self):
        retval = warnings_wrapper(['--sphinx', 'tests/test_in/sphinx_double_deprecation_warning.txt'])
        self.assertEqual(0, retval)

    def test_exclude_sphinx_deprecation(self):
        retval = warnings_wrapper(['--sphinx', '--include-sphinx-deprecation', 'tests/test_in/sphinx_double_deprecation_warning.txt'])
        self.assertEqual(2, retval)

    def test_ignore_sphinx_deprecation_flag(self):
        retval = warnings_wrapper(['--junit', '--include-sphinx-deprecation', 'tests/test_in/junit*.xml'])
        self.assertEqual(self.junit_warning_cnt, retval)

    def test_multiple_checkers_ret_val(self):
        retval = warnings_wrapper(['--sphinx', '--junit', 'tests/test_in/junit*.xml'])
        self.assertEqual(self.junit_warning_cnt, retval)

    def test_non_zero_ret_val_on_failure(self):
        retval = warnings_wrapper(['--sphinx', '--exact-warnings', '2', 'tests/test_in/junit*.xml'])
        self.assertEqual(self.min_ret_val_on_failure, retval)

    def test_various_sphinx_warnings(self):
        ''' Use the output log of the example documentation of mlx.traceability as input.

        The input file contains 18 Sphinx warnings, but exactly 19 are required to pass.
        The number of warnings (18) must be returned as return code.
        '''
        retval = warnings_wrapper(['--sphinx', '--exact-warnings', '19', 'tests/test_in/sphinx_traceability_output.txt'])
        self.assertEqual(18, retval)

    def test_robot_with_name_arg(self):
        retval = warnings_wrapper(['--robot', '--name', "Suite Two", 'tests/test_in/robot_double_fail.xml'])
        self.assertEqual(1, retval)

    def test_robot_default_name_arg(self):
        ''' If no suite name is configured, all suites must be taken into account '''
        retval = warnings_wrapper(['--robot', 'tests/test_in/robot_double_fail.xml'])
        self.assertEqual(2, retval)

    def test_robot_verbose(self):
        ''' If no suite name is configured, all suites must be taken into account '''
        with patch('sys.stdout', new=StringIO()) as fake_out:
            retval = warnings_wrapper(['--verbose', '--robot', '--name', 'Suite Two', 'tests/test_in/robot_double_fail.xml'])
        stdout_log = fake_out.getvalue()

        self.assertEqual(1, retval)
        self.assertEqual(
            '\n'.join([
                "Suite One &amp; Suite Two.Suite Two.Another test",
                "Suite 'Suite Two': 1 warnings found",
                "Counted failures for test suite 'Suite Two'.",
                "Number of warnings (1) is higher than the maximum limit (0). Returning error code 1.",
            ]) + '\n',
            stdout_log
        )

    def test_robot_config(self):
        with patch('sys.stdout', new=StringIO()) as fake_out:
            retval = warnings_wrapper(['--config', 'tests/test_in/config_example_robot.json', 'tests/test_in/robot_double_fail.xml'])
        stdout_log = fake_out.getvalue()

        self.assertEqual(
            '\n'.join([
                "Config parsing for robot completed",
                "Suite 'Suite One': 1 warnings found",
                "2 warnings found",
                "Suite 'Suite Two': 1 warnings found",
                "Counted failures for test suite 'Suite One'.",
                "Number of warnings (1) is between limits 0 and 1. Well done.",
                "Counted failures for all test suites.",
                "Number of warnings (2) is higher than the maximum limit (1). Returning error code 2.",
                "Counted failures for test suite 'Suite Two'.",
                "Number of warnings (1) is between limits 1 and 2. Well done.",
            ]) + '\n',
            stdout_log
        )
        self.assertEqual(2, retval)

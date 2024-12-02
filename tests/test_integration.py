import filecmp
import os
from io import StringIO
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from mlx.warnings import Finding, WarningsConfigError, exceptions, warnings_wrapper

TEST_IN_DIR = Path(__file__).parent / 'test_in'
TEST_OUT_DIR = Path(__file__).parent / 'test_out'


class TestIntegration(TestCase):
    def setUp(self):
        Finding.fingerprints = {}
        if not TEST_OUT_DIR.exists():
            TEST_OUT_DIR.mkdir()

    def tearDown(self):
        for var in ('FIRST_ENVVAR', 'SECOND_ENVVAR', 'MIN_SPHINX_WARNINGS', 'MAX_SPHINX_WARNINGS'):
            if var in os.environ:
                del os.environ[var]

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
        os.environ['MIN_SPHINX_WARNINGS'] = '0'
        os.environ['MAX_SPHINX_WARNINGS'] = '0'
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
        with self.assertLogs(level="INFO") as fake_out:
            retval = warnings_wrapper(['--verbose', '--robot', '--name', 'Suite Two', 'tests/test_in/robot_double_fail.xml'])
        stdout_log = fake_out.output

        self.assertEqual(1, retval)
        self.assertIn("INFO:root:Suite One &amp; Suite Two.Suite Two.Another test", stdout_log)

    def test_robot_config(self):
        os.environ['MIN_ROBOT_WARNINGS'] = '0'
        os.environ['MAX_ROBOT_WARNINGS'] = '0'
        with patch('sys.stdout', new=StringIO()) as fake_out:
            retval = warnings_wrapper([
                '--config',
                'tests/test_in/config_example_robot.json',
                'tests/test_in/robot_double_fail.xml',
            ])
        stdout_log = fake_out.getvalue()
        self.assertEqual(
            '\n'.join([
                "Suite 'Suite One': 1 warnings found",
                "2 warnings found",
                "Suite 'Suite Two': 1 warnings found",
                "Suite 'b4d su1te name': 0 warnings found",
                "Counted failures for test suite 'Suite One'.",
                "Number of warnings (1) is between limits 0 and 1. Well done.",
                "Counted failures for all test suites.",
                "Number of warnings (2) is higher than the maximum limit (1). Returning error code 2.",
                "Counted failures for test suite 'Suite Two'.",
                "Number of warnings (1) is between limits 1 and 2. Well done.",
                "Counted failures for test suite 'b4d su1te name'.",
                "Number of warnings (0) is exactly as expected. Well done.",
            ]) + '\n',
            stdout_log
        )
        self.assertEqual(2, retval)
        for var in ('MIN_ROBOT_WARNINGS', 'MAX_ROBOT_WARNINGS'):
            if var in os.environ:
                del os.environ[var]

    def test_robot_config_check_names(self):
        self.maxDiff = None
        with self.assertLogs(level="INFO") as fake_out:
            with self.assertRaises(SystemExit) as cm_err:
                warnings_wrapper(['--config', 'tests/test_in/config_example_robot_invalid_suite.json',
                                  'tests/test_in/robot_double_fail.xml'])
        stdout_log = fake_out.output
        self.assertIn("ERROR:root:No suite with name 'b4d su1te name' found. Returning error code -1.",
                      stdout_log)
        self.assertEqual(cm_err.exception.code, -1)

    def test_robot_cli_check_name(self):
        self.maxDiff = None
        with self.assertLogs(level="INFO") as fake_out:
            with self.assertRaises(SystemExit) as cm_err:
                warnings_wrapper(['--verbose', '--robot', '--name', 'Inv4lid Name',
                                  'tests/test_in/robot_double_fail.xml'])
        stdout_log = fake_out.output

        self.assertIn("ERROR:root:No suite with name 'Inv4lid Name' found. Returning error code -1.", stdout_log)
        self.assertEqual(cm_err.exception.code, -1)

    def test_output_file_sphinx(self):
        filename = 'sphinx_double_deprecation_warning_summary.txt'
        out_file = str(TEST_OUT_DIR / filename)
        ref_file = str(TEST_IN_DIR / filename)
        retval = warnings_wrapper(['--sphinx', '--include-sphinx-deprecation', '-o', out_file,
                                   'tests/test_in/sphinx_double_deprecation_warning.txt'])
        self.assertEqual(2, retval)
        self.assertTrue(filecmp.cmp(out_file, ref_file))

    def test_output_file_robot_basic(self):
        filename = 'robot_double_fail_summary.txt'
        out_file = str(TEST_OUT_DIR / filename)
        ref_file = str(TEST_IN_DIR / filename)
        retval = warnings_wrapper([
            '--output', out_file,
            '-r',
            'tests/test_in/robot_double_fail.xml',
        ])
        self.assertEqual(2, retval)
        self.assertTrue(filecmp.cmp(out_file, ref_file), '{} differs from {}'.format(out_file, ref_file))

    def test_output_file_robot_config(self):
        os.environ['MIN_ROBOT_WARNINGS'] = '0'
        os.environ['MAX_ROBOT_WARNINGS'] = '0'
        filename = 'robot_double_fail_config_summary.txt'
        out_file = str(TEST_OUT_DIR / filename)
        ref_file = str(TEST_IN_DIR / filename)
        retval = warnings_wrapper([
            '--output', out_file,
            '--config', 'tests/test_in/config_example_robot.json',
            'tests/test_in/robot_double_fail.xml',
        ])
        self.assertEqual(2, retval)
        self.assertTrue(filecmp.cmp(out_file, ref_file), '{} differs from {}'.format(out_file, ref_file))
        for var in ('MIN_ROBOT_WARNINGS', 'MAX_ROBOT_WARNINGS'):
            if var in os.environ:
                del os.environ[var]

    def test_output_file_junit(self):
        filename = 'junit_double_fail_summary.txt'
        out_file = str(TEST_OUT_DIR / filename)
        ref_file = str(TEST_IN_DIR / filename)
        retval = warnings_wrapper([
            '--output', out_file,
            '--junit',
            'tests/test_in/junit_double_fail.xml',
        ])
        self.assertEqual(2, retval)
        self.assertTrue(filecmp.cmp(out_file, ref_file), '{} differs from {}'.format(out_file, ref_file))

    @patch('pathlib.Path.cwd')
    def test_code_quality(self, path_cwd_mock):
        os.environ['MIN_SPHINX_WARNINGS'] = '0'
        os.environ['MAX_SPHINX_WARNINGS'] = '0'
        path_cwd_mock.return_value = '/home/user/myproject'
        filename = 'code_quality.json'
        out_file = str(TEST_OUT_DIR / filename)
        ref_file = str(TEST_IN_DIR / filename)
        retval = warnings_wrapper([
            '--code-quality', out_file,
            '--config', 'tests/test_in/config_example.json',
            'tests/test_in/mixed_warnings.txt',
        ])
        self.assertEqual(2, retval)
        self.assertTrue(filecmp.cmp(out_file, ref_file), '{} differs from {}'.format(out_file, ref_file))

    def test_code_quality_abspath_failure(self):
        os.environ['MIN_SPHINX_WARNINGS'] = '0'
        os.environ['MAX_SPHINX_WARNINGS'] = '0'
        filename = 'code_quality.json'
        out_file = str(TEST_OUT_DIR / filename)
        with self.assertRaises(ValueError) as c_m:
            warnings_wrapper([
                '--code-quality', out_file,
                '--config', 'tests/test_in/config_example.json',
                'tests/test_in/mixed_warnings.txt',
            ])
        self.assertTrue(str(c_m.exception).startswith(
            "Failed to convert abolute path to relative path for Code Quality report: "
            "'/home/user/myproject/helper/SimpleTimer.h'")
        )

    def test_cq_description_format_missing_envvar(self):
        os.environ['FIRST_ENVVAR'] = 'envvar_value'
        filename = 'code_quality_format.json'
        out_file = str(TEST_OUT_DIR / filename)
        with self.assertRaises(WarningsConfigError) as c_m:
            warnings_wrapper([
                '--code-quality', out_file,
                '--config', 'tests/test_in/config_cq_description_format.json',
                'tests/test_in/mixed_warnings.txt',
            ])
        self.assertEqual(
            str(c_m.exception),
            "Failed to find environment variable from configuration value 'cq_description_template': 'SECOND_ENVVAR'")

    @patch('pathlib.Path.cwd')
    def test_cq_description_format(self, path_cwd_mock):
        os.environ['FIRST_ENVVAR'] = 'envvar_value'
        os.environ['SECOND_ENVVAR'] = '12345'
        path_cwd_mock.return_value = '/home/user/myproject'
        filename = 'code_quality_format.json'
        out_file = str(TEST_OUT_DIR / filename)
        ref_file = str(TEST_IN_DIR / filename)
        with self.assertLogs(level="INFO") as fake_out:
            retval = warnings_wrapper([
                '--code-quality', out_file,
                '--config', 'tests/test_in/config_cq_description_format.json',
                'tests/test_in/mixed_warnings.txt',
            ])
        output = fake_out.output
        self.assertIn("WARNING:root:Unrecognized classification 'max'", output)
        self.assertIn("WARNING:root:Unrecognized classification 'min'", output)
        self.assertEqual(2, retval)
        self.assertTrue(filecmp.cmp(out_file, ref_file), '{} differs from {}'.format(out_file, ref_file))

    @patch('pathlib.Path.cwd')
    def test_polyspace_error(self, path_cwd_mock):
        config_file = str(TEST_IN_DIR / 'config_example_polyspace_error.yml')
        with self.assertRaises(exceptions.WarningsConfigError) as context:
            warnings_wrapper([
                '--config', config_file,
                'tests/test_in/mixed_warnings.txt',
            ])
        self.assertEqual(str(context.exception), 'Polyspace checker cannot be combined with other warnings checkers')


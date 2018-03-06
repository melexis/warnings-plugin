from unittest import TestCase

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

    junit_warning_cnt = 3

    def test_single_argument(self):
        retval = warnings_wrapper(['--junit', 'tests/junit_single_fail.xml'])
        self.assertEqual(1, retval)

    def test_two_arguments(self):
        retval = warnings_wrapper(['--junit', 'tests/junit_single_fail.xml', 'tests/junit_double_fail.xml'])
        self.assertEqual(1 + 2, retval)

    def test_single_command_argument(self):
        retval = warnings_wrapper(['--junit', '--command', 'cat', 'tests/junit_single_fail.xml'])
        self.assertEqual(1, retval)

    def test_two_command_arguments(self):
        retval = warnings_wrapper(['--sphinx', '--command', 'cat', 'tests/sphinx_single_warning.txt', 'tests/sphinx_double_warning.txt'])
        self.assertEqual(1 + 2, retval)

    def test_command_with_its_own_arguments(self):
        retval = warnings_wrapper(['--sphinx', '--command', 'cat', '-A', 'tests/sphinx_single_warning.txt', 'tests/sphinx_double_warning.txt'])
        self.assertEqual(1 + 2, retval)

    def test_command_to_stderr(self):
        retval = warnings_wrapper(['--sphinx', '--command', 'cat', 'tests/sphinx_single_warning.txt', '>&2'])
        self.assertEqual(1, retval)

    def test_faulty_command(self):
        with self.assertRaises(OSError):
            warnings_wrapper(['--sphinx', '--command', 'blahahahaha', 'tests/sphinx_single_warning.txt'])

    def test_command_revtal_err(self):
        retval = warnings_wrapper(['--sphinx', '--command', 'false'])
        self.assertEqual(1, retval)

    def test_command_revtal_err_supress(self):
        retval = warnings_wrapper(['--sphinx', '--ignore-retval', '--command', 'false'])
        self.assertEqual(0, retval)

    def test_wildcarded_arguments(self):
        # note: no shell expansion simulation (e.g. as in windows)
        retval = warnings_wrapper(['--junit', 'tests/junit*.xml'])
        self.assertEqual(self.junit_warning_cnt, retval)

    def test_max(self):
        retval = warnings_wrapper(['--junit', '--maxwarnings', '2', 'tests/junit*.xml'])
        self.assertEqual(self.junit_warning_cnt, retval)

    def test_max_but_still_ok(self):
        retval = warnings_wrapper(['--junit', '--maxwarnings', '100', 'tests/junit*.xml'])
        self.assertEqual(0, retval)

    def test_min(self):
        retval = warnings_wrapper(['--junit', '--maxwarnings', '100', '--minwarnings', '100', 'tests/junit*.xml'])
        self.assertEqual(self.junit_warning_cnt, retval)

    def test_min_but_still_ok(self):
        retval = warnings_wrapper(['--junit', '--maxwarnings', '100', '--minwarnings', '2', 'tests/junit*.xml'])
        self.assertEqual(0, retval)

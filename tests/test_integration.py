from unittest import TestCase

from mlx.warnings import warnings_wrapper


class TestIntegration(TestCase):

    junit_warning_cnt = 3

    def test_single_argument(self):
        retval = warnings_wrapper(['--junit', 'tests/junit_single_fail.xml'])
        self.assertEqual(1, retval)

    def test_two_arguments(self):
        retval = warnings_wrapper(['--junit', 'tests/junit_single_fail.xml', 'tests/junit_double_fail.xml'])
        self.assertEqual(1 + 2, retval)

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

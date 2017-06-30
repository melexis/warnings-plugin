from unittest import TestCase

from mlx.warnings import WarningsPlugin


class TestJUnitFailures(TestCase):
    def setUp(self):
        self.warnings = WarningsPlugin(False, False, True)

    def test_no_warning(self):
        self.warnings.check_file('tests/junit_no_fail.xml')
        self.assertEqual(self.warnings.return_count(), 0)

    def test_single_warning(self):
        self.warnings.check_file('tests/junit_single_fail.xml')
        self.assertEqual(self.warnings.return_count(), 1)

    def test_dual_warning(self):
        self.warnings.check_file('tests/junit_double_fail.xml')
        self.assertEqual(self.warnings.return_count(), 2)


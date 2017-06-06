from unittest import TestCase

from mlx.warnings import WarningsPlugin


class TestDoxygenWarnings(TestCase):
    def setUp(self):
        self.warnings = WarningsPlugin()

    def test_no_warning(self):
        self.warnings.check_doxygen_warnings('This should not be treated as warning')
        self.assertEqual(self.warnings.return_doxygen_warnings(), 0)

    def test_single_warning(self):
        self.warnings.check_doxygen_warnings('testfile.c:6: warning: group test: ignoring title "Some test functions" that does not match old title "Some freaky test functions"')
        self.assertEqual(self.warnings.return_doxygen_warnings(), 1)

    def test_single_warning_mixed(self):
        self.warnings.check_doxygen_warnings('This1 should not be treated as warning')
        self.warnings.check_doxygen_warnings('testfile.c:6: warning: group test: ignoring title "Some test functions" that does not match old title "Some freaky test functions"')
        self.warnings.check_doxygen_warnings('This should not be treated as warning2')

        self.assertEqual(self.warnings.return_doxygen_warnings(), 1)


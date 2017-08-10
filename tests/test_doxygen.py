try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
from mock import patch
from unittest import TestCase

from mlx.warnings import WarningsPlugin


class TestDoxygenWarnings(TestCase):
    def setUp(self):
        self.warnings = WarningsPlugin(doxygen=True, verbose=True)

    def test_no_warning(self):
        dut = 'This should not be treated as warning'
        self.warnings.check(dut)
        self.assertEqual(self.warnings.return_count(), 0)

    def test_single_warning(self):
        dut = 'testfile.c:6: warning: group test: ignoring title "Some test functions" that does not match old title "Some freaky test functions"'
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.warnings.check(dut)
        self.assertEqual(self.warnings.return_count(), 1)
        self.assertRegexpMatches(fake_out.getvalue(), dut)

    def test_single_warning_mixed(self):
        dut1 = 'This1 should not be treated as warning'
        dut2 = 'testfile.c:6: warning: group test: ignoring title "Some test functions" that does not match old title "Some freaky test functions"'
        dut3 = 'This should not be treated as warning2'
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.warnings.check(dut1)
            self.warnings.check(dut2)
            self.warnings.check(dut3)
        self.assertEqual(self.warnings.return_count(), 1)
        self.assertRegexpMatches(fake_out.getvalue(), dut2)

    def test_multiline(self):
        duterr1 = "testfile.c:6: warning: group test: ignoring title \"Some test functions\" that does not match old title \"Some freaky test functions\"\n"
        duterr2 = "testfile.c:8: warning: group test: ignoring title \"Some test functions\" that does not match old title \"Some freaky test functions\"\n"
        dut = "This1 should not be treated as warning\n"
        dut += duterr1
        dut += "This should not be treated as warning2\n"
        dut += duterr2
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.warnings.check(dut)
        self.assertEqual(self.warnings.return_count(), 2)
        self.assertRegexpMatches(fake_out.getvalue(), duterr1)
        self.assertRegexpMatches(fake_out.getvalue(), duterr2)


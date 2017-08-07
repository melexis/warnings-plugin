import sys
from io import StringIO
from mock import patch
from unittest import TestCase

from mlx.warnings import WarningsPlugin


class TestDoxygenWarnings(TestCase):
    def setUp(self):
        self.warnings = WarningsPlugin(False, True, False, verbose=True)

    def test_no_warning(self):
        dut = 'This should not be treated as warning'
        self.warnings.check(dut)
        self.assertEqual(self.warnings.return_count(), 0)

    def test_single_warning(self):
        dut = 'testfile.c:6: warning: group test: ignoring title "Some test functions" that does not match old title "Some freaky test functions"'
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.warnings.check(dut)
        self.assertEqual(self.warnings.return_count(), 1)
        self.assertEqual(dut, fake_out.getvalue())

    def test_single_warning_mixed(self):
        self.warnings.check('This1 should not be treated as warning')
        self.warnings.check('testfile.c:6: warning: group test: ignoring title "Some test functions" that does not match old title "Some freaky test functions"')
        self.warnings.check('This should not be treated as warning2')
        self.assertEqual(self.warnings.return_count(), 1)


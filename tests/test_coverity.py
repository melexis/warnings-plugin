from io import StringIO
from unittest import TestCase

from unittest.mock import patch

from mlx.warnings import WarningsPlugin


class TestCoverityWarnings(TestCase):
    def setUp(self):
        self.warnings = WarningsPlugin(verbose=True)
        self.warnings.activate_checker_name('coverity')

    def test_no_warning_normal_text(self):
        dut = 'This should not be treated as warning'
        self.warnings.check(dut)
        self.assertEqual(self.warnings.return_count(), 0)

    def test_no_warning_but_still_command_output(self):
        dut = 'src/something/src/somefile.c:82: 1. misra_violation: Essential type of the left hand operand "0U" (unsigned) is not the same as that of the right operand "1U"(signed).'
        self.warnings.check(dut)
        self.assertEqual(self.warnings.return_count(), 0)

    def test_single_warning(self):
        dut = '/src/somefile.c:82: CID 113396 (#2 of 2): Coding standard violation (MISRA C-2012 Rule 10.1): Unclassified, Unspecified, Undecided, owner is nobody, first detected on 2017-07-27.'
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.warnings.check(dut)
        self.assertEqual(self.warnings.return_count(), 1)
        self.assertIn(dut, fake_out.getvalue())

    def test_single_warning_count_one(self):
        dut1 = '/src/somefile.c:80: CID 113396 (#1 of 2): Coding standard violation (MISRA C-2012 Rule 10.1): Unclassified, Unspecified, Undecided, owner is nobody, first detected on 2017-07-27.'
        dut2 = '/src/somefile.c:82: CID 113396 (#2 of 2): Coding standard violation (MISRA C-2012 Rule 10.1): Unclassified, Unspecified, Undecided, owner is nobody, first detected on 2017-07-27.'
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.warnings.check(dut1)
            self.warnings.check(dut2)
        self.assertEqual(self.warnings.return_count(), 1)
        self.assertIn(dut2, fake_out.getvalue())

    def test_single_warning_real_output(self):
        dut1 = '/src/somefile.c:80: CID 113396 (#1 of 2): Coding standard violation (MISRA C-2012 Rule 10.1): Unclassified, Unspecified, Undecided, owner is nobody, first detected on 2017-07-27.'
        dut2 = '/src/somefile.c:82: CID 113396 (#2 of 2): Coding standard violation (MISRA C-2012 Rule 10.1): Unclassified, Unspecified, Undecided, owner is nobody, first detected on 2017-07-27.'
        dut3 = 'src/something/src/somefile.c:82: 1. misra_violation: Essential type of the left hand operand "0U" (unsigned) is not the same as that of the right operand "1U"(signed).'
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.warnings.check(dut1)
            self.warnings.check(dut2)
            self.warnings.check(dut3)
        self.assertEqual(self.warnings.return_count(), 1)
        self.assertIn(dut2, fake_out.getvalue())

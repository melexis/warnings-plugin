from io import StringIO
from unittest import TestCase

from unittest.mock import patch

from mlx.warnings import WarningsPlugin


class TestGccWarnings(TestCase):
    def setUp(self):
        self.warnings = WarningsPlugin(verbose=True)
        self.warnings.activate_checker_name('gcc')

    def test_no_warning(self):
        dut = 'This should not be treated as warning'
        self.warnings.check(dut)
        self.assertEqual(self.warnings.return_count(), 0)

    def test_single_warning(self):
        dut = "testfile.c:6:1: warning: missing initializer for field 'reserved' of 'ARM_SPI_CAPABILITIES' {aka 'const struct _ARM_SPI_CAPABILITIES'} [-Wmissing-field-initializers]"
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.warnings.check(dut)
        self.assertEqual(self.warnings.return_count(), 1)
        #self.assertRegex(fake_out.getvalue(), dut)

    def test_single_warning_mixed(self):
        dut1 = 'This1 should not be treated as warning'
        dut2 = "testfile.c:6:1: warning: missing initializer for field 'reserved' of 'ARM_SPI_CAPABILITIES' {aka 'const struct _ARM_SPI_CAPABILITIES'} [-Wmissing-field-initializers]"
        dut3 = 'This should not be treated as warning2'
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.warnings.check(dut1)
            self.warnings.check(dut2)
            self.warnings.check(dut3)
        self.assertEqual(self.warnings.return_count(), 1)
        #self.assertRegex(fake_out.getvalue(), dut2)

    def test_multiline(self):
        duterr1 = "../Driver/bla/Source/example_spi.c: In function 'SPI_InterruptReceive':\n../Driver/bla/Source/example_spi.c:957:43: warning: unused parameter 'data' [-Wunused-parameter]\n  957 | static int32_t SPI_InterruptReceive(void *data, uint32_t num, DEV_SPI_INFO *spi_info_ptr)\n      |                                     ~~~~~~^~~~"
        duterr2 = "../Driver/bla/Source/example_spi.c: In function 'SPI_MasterCommonControl':\n../Driver/bla/Source/example_spi.c:200:18: warning: statement will never be executed [-Wswitch-unreachable]\n  200 |         uint32_t val32 = SPI_CPOL_0_CPHA_0;\n      |                  ^~~~~"
        dut = "This1 should not be treated as warning\n"
        dut += duterr1
        dut += "This should not be treated as warning2\n"
        dut += duterr2
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.warnings.check(dut)
        self.assertEqual(self.warnings.return_count(), 2)
        #self.assertRegex(fake_out.getvalue(), duterr1)
        #self.assertRegex(fake_out.getvalue(), duterr2)

    def test_gcc_warnings_txt(self):
        dut_file = 'tests/test_in/gcc_warnings.txt'
        with open(dut_file, 'r') as open_file:
            self.warnings.check(open_file.read())
        self.assertEqual(self.warnings.return_count(), 15)

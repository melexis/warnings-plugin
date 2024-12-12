from unittest import TestCase

from mlx.warnings import WarningsPlugin


class TestXMLRunnerWarnings(TestCase):
    def setUp(self):
        self.warnings = WarningsPlugin()
        self.warnings.activate_checker_name('xmlrunner', True)

    def test_no_warning(self):
        dut = 'This should not be treated as warning'
        self.warnings.check(dut)
        self.assertEqual(self.warnings.return_count(), 0)

    def test_single_warning(self):
        dut = 'ERROR [0.000s]: test_some_error_test (something.anything.somewhere)'
        with self.assertLogs(logger="xmlrunner", level="INFO") as fake_out:
            self.warnings.check(dut)
        self.assertEqual(self.warnings.return_count(), 1)
        self.assertIn(f"INFO:xmlrunner:{dut}", fake_out.output)

    def test_single_warning_mixed(self):
        dut1 = 'This1 should not be treated as warning'
        dut2 = 'ERROR [0.000s]: test_some_error_test (something.anything.somewhere)'
        dut3 = 'This should not be treated as warning2'
        with self.assertLogs(logger="xmlrunner", level="INFO") as fake_out:
            self.warnings.check(dut1)
            self.warnings.check(dut2)
            self.warnings.check(dut3)
        self.assertEqual(self.warnings.return_count(), 1)
        self.assertIn(f"INFO:xmlrunner:{dut2}", fake_out.output)

    def test_multiline(self):
        duterr1 = "ERROR [0.000s]: test_some_error_test (something.anything.somewhere) \"Some test functions\" that does not match old title \"Some freaky test functions\"\n"
        duterr2 = "ERROR [0.000s]: ignoring title \"Some test functions\" that does not match old title \"Some freaky test functions\"\n"
        dut = "This1 should not be treated as warning\n"
        dut += duterr1
        dut += "This should not be treated as warning2\n"
        dut += duterr2
        with self.assertLogs(logger="xmlrunner", level="INFO") as fake_out:
            self.warnings.check(dut)
        self.assertEqual(self.warnings.return_count(), 2)
        self.assertIn(f"INFO:xmlrunner:{duterr1.strip()}", fake_out.output)
        self.assertIn(f"INFO:xmlrunner:{duterr2.strip()}", fake_out.output)

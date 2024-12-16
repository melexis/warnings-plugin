from unittest import TestCase

import pytest

from mlx.warnings import WarningsPlugin


class TestXMLRunnerWarnings(TestCase):
    @pytest.fixture(autouse=True)
    def caplog(self, caplog):
        self.caplog = caplog

    def setUp(self):
        self.warnings = WarningsPlugin()
        self.warnings.activate_checker_name("xmlrunner", True, None)

    def test_no_warning(self):
        dut = "This should not be treated as warning"
        self.warnings.check(dut)
        self.assertEqual(self.warnings.return_count(), 0)

    def test_single_warning(self):
        dut = "ERROR [0.000s]: test_some_error_test (something.anything.somewhere)"
        self.warnings.check(dut)
        self.assertEqual(self.warnings.return_count(), 1)
        self.assertEqual([f"{dut}"], self.caplog.messages)

    def test_single_warning_mixed(self):
        dut1 = "This1 should not be treated as warning"
        dut2 = "ERROR [0.000s]: test_some_error_test (something.anything.somewhere)"
        dut3 = "This should not be treated as warning2"
        self.warnings.check(dut1)
        self.warnings.check(dut2)
        self.warnings.check(dut3)
        self.assertEqual(self.warnings.return_count(), 1)
        self.assertEqual([f"{dut2}"], self.caplog.messages)

    def test_multiline(self):
        duterr1 = "ERROR [0.000s]: test_some_error_test (something.anything.somewhere) \"Some test functions\" "\
                  "that does not match old title \"Some freaky test functions\"\n"
        duterr2 = "ERROR [0.000s]: ignoring title \"Some test functions\" that does not match old title "\
                  "\"Some freaky test functions\"\n"
        dut = "This1 should not be treated as warning\n"
        dut += duterr1
        dut += "This should not be treated as warning2\n"
        dut += duterr2
        self.warnings.check(dut)
        self.assertEqual(self.warnings.return_count(), 2)
        self.assertEqual([f"{duterr1.strip()}", f"{duterr2.strip()}"], self.caplog.messages)

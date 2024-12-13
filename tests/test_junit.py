from unittest import TestCase

import pytest

from mlx.warnings import WarningsPlugin


class TestJUnitFailures(TestCase):
    @pytest.fixture(autouse=True)
    def caplog(self, caplog):
        self.caplog = caplog

    def setUp(self):
        self.warnings = WarningsPlugin()
        self.warnings.activate_checker_name('junit', True)

    def test_no_warning(self):
        with open('tests/test_in/junit_no_fail.xml') as xmlfile:
            self.warnings.check(xmlfile.read())
        self.assertEqual(self.warnings.return_count(), 0)

    def test_single_warning(self):
        with open('tests/test_in/junit_single_fail.xml') as xmlfile:
            self.warnings.check(xmlfile.read())
        self.assertEqual(self.warnings.return_count(), 1)
        self.assertEqual(["test_warn_plugin_single_fail.myfirstfai1ure"], self.caplog.messages)

    def test_dual_warning(self):
        with open('tests/test_in/junit_double_fail.xml') as xmlfile:
            self.warnings.check(xmlfile.read())
        self.assertEqual(self.warnings.return_count(), 2)
        self.assertEqual(["test_warn_plugin_double_fail.myfirstfai1ure",
                          "test_warn_plugin_no_double_fail.mysecondfai1ure"],
                         self.caplog.messages)

    def test_invalid_xml(self):
        self.warnings.check('this is not xml')
        self.assertEqual(self.warnings.return_count(), 0)

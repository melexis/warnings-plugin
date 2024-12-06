from unittest import TestCase

from mlx.warnings import WarningsPlugin


class TestJUnitFailures(TestCase):
    def setUp(self):
        self.warnings = WarningsPlugin(verbose=True)
        self.warnings.activate_checker_name('junit')

    def test_no_warning(self):
        with open('tests/test_in/junit_no_fail.xml') as xmlfile:
            self.warnings.check(xmlfile.read())
        self.assertEqual(self.warnings.return_count(), 0)

    def test_single_warning(self):
        with open('tests/test_in/junit_single_fail.xml') as xmlfile:
            with self.assertLogs(level="INFO") as fake_out:
                self.warnings.check(xmlfile.read())
        self.assertEqual(self.warnings.return_count(), 1)
        self.assertIn("INFO:root:test_warn_plugin_single_fail.myfirstfai1ure", fake_out.output)

    def test_dual_warning(self):
        with open('tests/test_in/junit_double_fail.xml') as xmlfile:
            with self.assertLogs(level="INFO") as fake_out:
                self.warnings.check(xmlfile.read())
        self.assertEqual(self.warnings.return_count(), 2)
        self.assertIn("INFO:root:test_warn_plugin_double_fail.myfirstfai1ure", fake_out.output)
        self.assertIn("INFO:root:test_warn_plugin_no_double_fail.mysecondfai1ure", fake_out.output)

    def test_invalid_xml(self):
        self.warnings.check('this is not xml')
        self.assertEqual(self.warnings.return_count(), 0)

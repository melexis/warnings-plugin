try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
from mock import patch
from unittest import TestCase

from mlx.warnings import WarningsPlugin


class TestSphinxWarnings(TestCase):
    def setUp(self):
        self.warnings = WarningsPlugin(sphinx=True, verbose=True)

    def test_no_warning(self):
        self.warnings.check('This should not be treated as warning')
        self.assertEqual(self.warnings.return_count(), 0)

    def test_single_warning(self):
        dut = "/home/bljah/test/index.rst:5: WARNING: toctree contains reference to nonexisting document u'installation'"
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.warnings.check(dut)
        self.assertEqual(self.warnings.return_count(), 1)
        self.assertRegexpMatches(fake_out.getvalue(), dut)

    def test_warning_no_line_number(self):
        dut1 = "/home/bljah/test/index.rst:5: WARNING: toctree contains reference to nonexisting document u'installation'"
        dut2 = "/home/bljah/test/index.rst:None: WARNING: toctree contains reference to nonexisting document u'installation'"
        dut3 = "/home/bljah/test/index.rst:: WARNING: toctree contains reference to nonexisting document u'installation'"
        dut4 = "/home/bljah/test/SRS.rst: WARNING: item non_existing_requirement is not defined"
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.warnings.check(dut1)
            self.warnings.check(dut2)
            self.warnings.check(dut3)
            self.warnings.check(dut4)
        self.assertEqual(self.warnings.return_count(), 4)
        self.assertRegexpMatches(fake_out.getvalue(), dut1)
        self.assertRegexpMatches(fake_out.getvalue(), dut2)
        self.assertRegexpMatches(fake_out.getvalue(), dut3)
        self.assertRegexpMatches(fake_out.getvalue(), dut4)

    def test_single_warning_mixed(self):
        dut1 = 'This1 should not be treated as warning'
        dut2 = "/home/bljah/test/index.rst:5: WARNING: toctree contains reference to nonexisting document u'installation'"
        dut3 = 'This should not be treated as warning2'
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.warnings.check(dut1)
            self.warnings.check(dut2)
            self.warnings.check(dut3)
        self.assertEqual(self.warnings.return_count(), 1)
        self.assertRegexpMatches(fake_out.getvalue(), dut2)

    def test_multiline(self):
        duterr1 = "/home/bljah/test/index.rst:5: WARNING: toctree contains reference to nonexisting document u'installation'\n"
        duterr2 = "/home/bljah/test/index.rst:None: WARNING: toctree contains reference to nonexisting document u'installation'\n"
        dut = "This1 should not be treated as warning\n"
        dut += duterr1
        dut += "This should not be treated as warning2\n"
        dut += duterr2
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.warnings.check(dut)
        self.assertEqual(self.warnings.return_count(), 2)
        self.assertRegexpMatches(fake_out.getvalue(), duterr1)
        self.assertRegexpMatches(fake_out.getvalue(), duterr2)


from unittest import TestCase

from mlx.warnings import WarningsPlugin


class TestSphinxWarnings(TestCase):
    def setUp(self):
        self.warnings = WarningsPlugin(True, False, False)

    def test_no_warning(self):
        self.warnings.check('This should not be treated as warning')
        self.assertEqual(self.warnings.return_count(), 0)

    def test_single_warning(self):
        self.warnings.check("/home/bljah/test/index.rst:5: WARNING: toctree contains reference to nonexisting document u'installation'")
        self.assertEqual(self.warnings.return_count(), 1)

    def test_single_warning_no_line_number(self):
        self.warnings.check("/home/bljah/test/index.rst:5: WARNING: toctree contains reference to nonexisting document u'installation'")
        self.warnings.check("/home/bljah/test/index.rst:None: WARNING: toctree contains reference to nonexisting document u'installation'")
        self.assertEqual(self.warnings.return_count(), 2)

    def test_single_warning_mixed(self):
        self.warnings.check('This1 should not be treated as warning')
        self.warnings.check("/home/bljah/test/index.rst:5: WARNING: toctree contains reference to nonexisting document u'installation'")
        self.warnings.check('This should not be treated as warning2')

        self.assertEqual(self.warnings.return_count(), 1)


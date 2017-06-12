from unittest import TestCase

from mlx.warnings import WarningsPlugin


class TestSphinxWarnings(TestCase):
    def setUp(self):
        self.warnings = WarningsPlugin()

    def test_no_warning(self):
        self.warnings.check_sphinx_warnings('This should not be treated as warning')
        self.assertEqual(self.warnings.return_sphinx_warnings(), 0)

    def test_single_warning(self):
        self.warnings.check_sphinx_warnings("/home/bljah/test/index.rst:5: WARNING: toctree contains reference to nonexisting document u'installation'")
        self.assertEqual(self.warnings.return_sphinx_warnings(), 1)

    def test_single_warning_no_line_number(self):
        self.warnings.check_sphinx_warnings("/home/bljah/test/index.rst:5: WARNING: toctree contains reference to nonexisting document u'installation'")
        self.warnings.check_sphinx_warnings("/home/bljah/test/index.rst:None: WARNING: toctree contains reference to nonexisting document u'installation'")
        self.assertEqual(self.warnings.return_sphinx_warnings(), 2)

    def test_single_warning_mixed(self):
        self.warnings.check_sphinx_warnings('This1 should not be treated as warning')
        self.warnings.check_sphinx_warnings("/home/bljah/test/index.rst:5: WARNING: toctree contains reference to nonexisting document u'installation'")
        self.warnings.check_sphinx_warnings('This should not be treated as warning2')

        self.assertEqual(self.warnings.return_sphinx_warnings(), 1)


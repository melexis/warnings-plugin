from unittest import TestCase

from mlx.warnings import WarningsPlugin


class TestWarningsPlugin(TestCase):
    def test_doxygen_warning(self):
        warnings = WarningsPlugin(False, True, False)
        warnings.check('testfile.c:6: warning: group test: ignoring title "Some test functions" that does not match old title "Some freaky test functions"')
        self.assertEqual(warnings.return_count(), 1)

    def test_sphinx_warning(self):
        warnings = WarningsPlugin(True, False, False)
        warnings.check("/home/bljah/test/index.rst:5: WARNING: toctree contains reference to nonexisting document u'installation'")
        self.assertEqual(warnings.return_count(), 1)

    def test_junit_warning(self):
        warnings = WarningsPlugin(False, False, True)
        warnings.check('<testcase classname="dummy_class" name="dummy_name"><failure message="some random message from test case" /></testcase>')
        self.assertEqual(warnings.return_count(), 1)

    def test_doxygen_warning_only(self):
        warnings = WarningsPlugin(False, True, False)
        warnings.check('testfile.c:6: warning: group test: ignoring title "Some test functions" that does not match old title "Some freaky test functions"')
        self.assertEqual(warnings.return_count(), 1)
        warnings.check("/home/bljah/test/index.rst:5: WARNING: toctree contains reference to nonexisting document u'installation'")
        self.assertEqual(warnings.return_count(), 1)
        warnings.check('<testcase classname="dummy_class" name="dummy_name"><failure message="some random message from test case" /></testcase>')
        self.assertEqual(warnings.return_count(), 1)
        warnings.check('This should not be treated as warning2')
        self.assertEqual(warnings.return_count(), 1)

    def test_sphinx_warning_only(self):
        warnings = WarningsPlugin(True, False, False)
        warnings.check("/home/bljah/test/index.rst:5: WARNING: toctree contains reference to nonexisting document u'installation'")
        self.assertEqual(warnings.return_count(), 1)
        warnings.check('testfile.c:6: warning: group test: ignoring title "Some test functions" that does not match old title "Some freaky test functions"')
        self.assertEqual(warnings.return_count(), 1)
        warnings.check('<testcase classname="dummy_class" name="dummy_name"><failure message="some random message from test case" /></testcase>')
        self.assertEqual(warnings.return_count(), 1)
        warnings.check('This should not be treated as warning2')
        self.assertEqual(warnings.return_count(), 1)

    def test_junit_warning_only(self):
        warnings = WarningsPlugin(False, False, True)
        warnings.check('<testcase classname="dummy_class" name="dummy_name"><failure message="some random message from test case" /></testcase>')
        self.assertEqual(warnings.return_count(), 1)
        warnings.check("/home/bljah/test/index.rst:5: WARNING: toctree contains reference to nonexisting document u'installation'")
        self.assertEqual(warnings.return_count(), 1)
        warnings.check('testfile.c:6: warning: group test: ignoring title "Some test functions" that does not match old title "Some freaky test functions"')
        self.assertEqual(warnings.return_count(), 1)
        warnings.check('This should not be treated as warning2')
        self.assertEqual(warnings.return_count(), 1)



from io import StringIO
from unittest import TestCase

from unittest.mock import patch

from mlx.warnings import WarningsPlugin


class TestWarningsPlugin(TestCase):
    def test_doxygen_warning(self):
        warnings = WarningsPlugin()
        warnings.activate_checker_name('doxygen')
        warnings.check('testfile.c:6: warning: group test: ignoring title "Some test functions" that does not match old title "Some freaky test functions"')
        self.assertEqual(warnings.return_count(), 1)

    def test_sphinx_warning(self):
        warnings = WarningsPlugin()
        warnings.activate_checker_name('sphinx')
        warnings.check("/home/bljah/test/index.rst:5: WARNING: toctree contains reference to nonexisting document u'installation'")
        self.assertEqual(warnings.return_count(), 1)

    def test_junit_warning(self):
        warnings = WarningsPlugin()
        warnings.activate_checker_name('junit')
        with open('tests/test_in/junit_single_fail.xml') as xmlfile:
            warnings.check(xmlfile.read())
        self.assertEqual(warnings.return_count(), 1)

    def test_doxygen_warning_only(self):
        warnings = WarningsPlugin()
        warnings.activate_checker_name('doxygen')
        warnings.check('testfile.c:6: warning: group test: ignoring title "Some test functions" that does not match old title "Some freaky test functions"')
        self.assertEqual(warnings.return_count(), 1)
        warnings.check("/home/bljah/test/index.rst:5: WARNING: toctree contains reference to nonexisting document u'installation'")
        self.assertEqual(warnings.return_count(), 1)
        with open('tests/test_in/junit_single_fail.xml') as xmlfile:
            warnings.check(xmlfile.read())
        self.assertEqual(warnings.return_count(), 1)
        warnings.check('This should not be treated as warning2')
        self.assertEqual(warnings.return_count(), 1)

    def test_sphinx_warning_only(self):
        warnings = WarningsPlugin()
        warnings.activate_checker_name('sphinx')
        warnings.check("/home/bljah/test/index.rst:5: WARNING: toctree contains reference to nonexisting document u'installation'")
        self.assertEqual(warnings.return_count(), 1)
        warnings.check('testfile.c:6: warning: group test: ignoring title "Some test functions" that does not match old title "Some freaky test functions"')
        self.assertEqual(warnings.return_count(), 1)
        with open('tests/test_in/junit_single_fail.xml') as xmlfile:
            warnings.check(xmlfile.read())
        self.assertEqual(warnings.return_count(), 1)
        warnings.check('This should not be treated as warning2')
        self.assertEqual(warnings.return_count(), 1)

    def test_junit_warning_only(self):
        warnings = WarningsPlugin()
        warnings.activate_checker_name('junit')
        with open('tests/test_in/junit_single_fail.xml') as xmlfile:
            warnings.check(xmlfile.read())
        self.assertEqual(warnings.return_count(), 1)
        warnings.check("/home/bljah/test/index.rst:5: WARNING: toctree contains reference to nonexisting document u'installation'")
        self.assertEqual(warnings.return_count(), 1)
        warnings.check('testfile.c:6: warning: group test: ignoring title "Some test functions" that does not match old title "Some freaky test functions"')
        self.assertEqual(warnings.return_count(), 1)
        warnings.check('This should not be treated as warning2')
        self.assertEqual(warnings.return_count(), 1)

    def test_doxy_sphinx_warning(self):
        warnings = WarningsPlugin()
        warnings.activate_checker_name('sphinx')
        warnings.activate_checker_name('doxygen')
        warnings.check('testfile.c:6: warning: group test: ignoring title "Some test functions" that does not match old title "Some freaky test functions"')
        self.assertEqual(warnings.return_count(), 1)
        warnings.check("/home/bljah/test/index.rst:5: WARNING: toctree contains reference to nonexisting document u'installation'")
        self.assertEqual(warnings.return_count(), 2)
        with open('tests/test_in/junit_single_fail.xml') as xmlfile:
            warnings.check(xmlfile.read())
        self.assertEqual(warnings.return_count(), 2)
        warnings.check('This should not be treated as warning2')
        self.assertEqual(warnings.return_count(), 2)

    def test_doxy_junit_warning(self):
        warnings = WarningsPlugin()
        warnings.activate_checker_name('doxygen')
        warnings.activate_checker_name('junit')
        warnings.check('testfile.c:6: warning: group test: ignoring title "Some test functions" that does not match old title "Some freaky test functions"')
        self.assertEqual(warnings.return_count(), 1)
        warnings.check("/home/bljah/test/index.rst:5: WARNING: toctree contains reference to nonexisting document u'installation'")
        self.assertEqual(warnings.return_count(), 1)
        with open('tests/test_in/junit_single_fail.xml') as xmlfile:
            warnings.check(xmlfile.read())
        self.assertEqual(warnings.return_count(), 2)
        warnings.check('This should not be treated as warning2')
        self.assertEqual(warnings.return_count(), 2)

    def test_sphinx_junit_warning(self):
        warnings = WarningsPlugin()
        warnings.activate_checker_name('sphinx')
        warnings.activate_checker_name('junit')
        warnings.check('testfile.c:6: warning: group test: ignoring title "Some test functions" that does not match old title "Some freaky test functions"')
        self.assertEqual(warnings.return_count(), 0)
        warnings.check("/home/bljah/test/index.rst:5: WARNING: toctree contains reference to nonexisting document u'installation'")
        self.assertEqual(warnings.return_count(), 1)
        with open('tests/test_in/junit_single_fail.xml') as xmlfile:
            warnings.check(xmlfile.read())
        self.assertEqual(warnings.return_count(), 2)
        warnings.check('This should not be treated as warning2')
        self.assertEqual(warnings.return_count(), 2)

    def test_all_warning(self):
        warnings = WarningsPlugin()
        warnings.activate_checker_name('sphinx')
        warnings.activate_checker_name('doxygen')
        warnings.activate_checker_name('junit')
        warnings.check('testfile.c:6: warning: group test: ignoring title "Some test functions" that does not match old title "Some freaky test functions"')
        self.assertEqual(warnings.return_count(), 1)
        warnings.check("/home/bljah/test/index.rst:5: WARNING: toctree contains reference to nonexisting document u'installation'")
        self.assertEqual(warnings.return_count(), 2)
        with open('tests/test_in/junit_single_fail.xml') as xmlfile:
            warnings.check(xmlfile.read())
        self.assertEqual(warnings.return_count(), 3)
        warnings.check('This should not be treated as warning2')
        self.assertEqual(warnings.return_count(), 3)

    def test_non_existent_checker_name(self):
        warnings = WarningsPlugin()
        invalid_checker_name = 'non-existent'
        with patch('sys.stdout', new=StringIO()) as fake_out:
            warnings.activate_checker_name(invalid_checker_name)
        self.assertIn("Checker {} does not exist".format(invalid_checker_name), fake_out.getvalue())

from unittest import TestCase

import pytest

from mlx.warnings import WarningsPlugin


class TestWarningsPlugin(TestCase):
    logging_args = (False, None)

    @pytest.fixture(autouse=True)
    def caplog(self, caplog):
        self.caplog = caplog

    def test_doxygen_warning(self):
        warnings = WarningsPlugin()
        warnings.activate_checker_name('doxygen', *self.logging_args)
        warnings.check('testfile.c:6: warning: group test: ignoring title "Some test functions" that does not match old title "Some freaky test functions"')
        self.assertEqual(warnings.return_count(), 1)

    def test_sphinx_warning(self):
        warnings = WarningsPlugin()
        warnings.activate_checker_name('sphinx', *self.logging_args)
        warnings.check("/home/bljah/test/index.rst:5: WARNING: toctree contains reference to nonexisting document u'installation'")
        self.assertEqual(warnings.return_count(), 1)

    def test_junit_warning(self):
        warnings = WarningsPlugin()
        warnings.activate_checker_name('junit', *self.logging_args)
        with open('tests/test_in/junit_single_fail.xml') as xmlfile:
            warnings.check(xmlfile.read())
        self.assertEqual(warnings.return_count(), 1)

    def test_doxygen_warning_only(self):
        warnings = WarningsPlugin()
        warnings.activate_checker_name('doxygen', *self.logging_args)
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
        warnings.activate_checker_name('sphinx', *self.logging_args)
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
        warnings.activate_checker_name('junit', *self.logging_args)
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
        warnings.activate_checker_name('sphinx', *self.logging_args)
        warnings.activate_checker_name('doxygen', *self.logging_args)
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
        warnings.activate_checker_name('doxygen', *self.logging_args)
        warnings.activate_checker_name('junit', *self.logging_args)
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
        warnings.activate_checker_name('sphinx', *self.logging_args)
        warnings.activate_checker_name('junit', *self.logging_args)
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
        warnings.activate_checker_name('sphinx', *self.logging_args)
        warnings.activate_checker_name('doxygen', *self.logging_args)
        warnings.activate_checker_name('junit', *self.logging_args)
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
        warnings.activate_checker_name(invalid_checker_name, *self.logging_args)
        self.assertEqual([f"Checker {invalid_checker_name} does not exist"], self.caplog.messages)

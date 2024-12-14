from unittest import TestCase

import pytest

from mlx.warnings import WarningsPlugin


class TestSphinxWarnings(TestCase):
    @pytest.fixture(autouse=True)
    def caplog(self, caplog):
        self.caplog = caplog

    def setUp(self):
        self.warnings = WarningsPlugin()
        self.warnings.activate_checker_name('sphinx', True, None)

    def test_no_warning(self):
        self.warnings.check('This should not be treated as warning')
        self.assertEqual(self.warnings.return_count(), 0)

    def test_single_warning(self):
        dut = "/home/bljah/test/index.rst:5: WARNING: toctree contains reference to nonexisting document u'installation'"
        self.warnings.check(dut)
        self.assertEqual(self.warnings.return_count(), 1)
        self.assertEqual([f"{dut}"], self.caplog.messages)

    def test_warning_no_line_number(self):
        dut1 = "/home/bljah/test/index.rst:5: WARNING: toctree contains reference to nonexisting document u'installation'"
        dut2 = "/home/bljah/test/index.rst:None: WARNING: toctree contains reference to nonexisting document u'installation'"
        dut3 = "/home/bljah/test/index.rst:: WARNING: toctree contains reference to nonexisting document u'installation'"
        dut4 = "/home/bljah/test/SRS.rst: WARNING: item non_existing_requirement is not defined"
        dut5 = "CRITICAL: Problems with \"include\" directive path:"
        self.warnings.check(dut1)
        self.warnings.check(dut2)
        self.warnings.check(dut3)
        self.warnings.check(dut4)
        self.warnings.check(dut5)
        self.assertEqual(self.warnings.return_count(), 5)
        self.assertEqual([f"{dut1}", f"{dut2}", f"{dut3}", f"{dut4}", f"{dut5}"], self.caplog.messages)

    def test_single_warning_mixed(self):
        dut1 = 'This1 should not be treated as warning'
        dut2 = "/home/bljah/test/index.rst:5: WARNING: toctree contains reference to nonexisting document u'installation'"
        dut3 = 'This should not be treated as warning2'
        self.warnings.check(dut1)
        self.warnings.check(dut2)
        self.warnings.check(dut3)
        self.assertEqual(self.warnings.return_count(), 1)
        self.assertEqual([f"{dut2}"], self.caplog.messages)

    def test_multiline(self):
        duterr1 = "/home/bljah/test/index.rst:5: WARNING: toctree contains reference to nonexisting document u'installation'\n"
        duterr2 = "/home/bljah/test/index.rst:None: WARNING: toctree contains reference to nonexisting document u'installation'\n"
        dut = "This1 should not be treated as warning\n"
        dut += duterr1
        dut += "This should not be treated as warning2\n"
        dut += duterr2
        self.warnings.check(dut)
        self.assertEqual(self.warnings.return_count(), 2)
        self.assertEqual([f"{duterr1.strip()}", f"{duterr2.strip()}"], self.caplog.messages)

    def test_deprecation_warning(self):
        duterr1 = "/usr/local/lib/python3.5/dist-packages/sphinx/application.py:402: RemovedInSphinx20Warning: "\
            "app.info() is now deprecated. Use sphinx.util.logging instead. RemovedInSphinx20Warning\n"
        dut = "This should not be treated as warning2\n"
        dut += duterr1
        self.warnings.check(dut)
        self.assertEqual(self.warnings.return_count(), 0)
        self.assertEqual([], self.caplog.messages)

    def test_deprecation_warning_included(self):
        self.warnings.get_checker('sphinx').include_sphinx_deprecation()
        duterr1 = "/usr/local/lib/python3.5/dist-packages/sphinx/application.py:402: RemovedInSphinx20Warning: "\
            "app.info() is now deprecated. Use sphinx.util.logging instead. RemovedInSphinx20Warning\n"
        dut = "This1 should not be treated as warning\n"
        dut += duterr1
        self.warnings.check(dut)
        self.assertEqual(self.warnings.return_count(), 1)
        self.assertEqual([f"{duterr1.strip()}"], self.caplog.messages)

    def test_warning_no_docname(self):
        duterr1 = "WARNING: List item 'CL-UNDEFINED_CL_ITEM' in merge/pull request 138 is not defined as a checklist-item.\n"
        self.warnings.check(duterr1)
        self.assertEqual(self.warnings.return_count(), 1)
        self.assertEqual([f"{duterr1.strip()}"], self.caplog.messages)

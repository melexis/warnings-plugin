from unittest import TestCase

from mlx.warnings import WarningsPlugin


class TestSphinxWarnings(TestCase):
    def setUp(self):
        self.warnings = WarningsPlugin()
        self.warnings.activate_checker_name('sphinx', True)

    def test_no_warning(self):
        self.warnings.check('This should not be treated as warning')
        self.assertEqual(self.warnings.return_count(), 0)

    def test_single_warning(self):
        dut = "/home/bljah/test/index.rst:5: WARNING: toctree contains reference to nonexisting document u'installation'"
        with self.assertLogs(logger="sphinx", level="INFO") as fake_out:
            self.warnings.check(dut)
        self.assertEqual(self.warnings.return_count(), 1)
        self.assertIn(f"INFO:sphinx:{dut}", fake_out.output)

    def test_warning_no_line_number(self):
        dut1 = "/home/bljah/test/index.rst:5: WARNING: toctree contains reference to nonexisting document u'installation'"
        dut2 = "/home/bljah/test/index.rst:None: WARNING: toctree contains reference to nonexisting document u'installation'"
        dut3 = "/home/bljah/test/index.rst:: WARNING: toctree contains reference to nonexisting document u'installation'"
        dut4 = "/home/bljah/test/SRS.rst: WARNING: item non_existing_requirement is not defined"
        dut5 = "CRITICAL: Problems with \"include\" directive path:"
        with self.assertLogs(logger="sphinx", level="INFO") as fake_out:
            self.warnings.check(dut1)
            self.warnings.check(dut2)
            self.warnings.check(dut3)
            self.warnings.check(dut4)
            self.warnings.check(dut5)
        self.assertEqual(self.warnings.return_count(), 5)
        self.assertIn(f"INFO:sphinx:{dut1}", fake_out.output)
        self.assertIn(f"INFO:sphinx:{dut2}", fake_out.output)
        self.assertIn(f"INFO:sphinx:{dut3}", fake_out.output)
        self.assertIn(f"INFO:sphinx:{dut4}", fake_out.output)
        self.assertIn(f"INFO:sphinx:{dut5}", fake_out.output)

    def test_single_warning_mixed(self):
        dut1 = 'This1 should not be treated as warning'
        dut2 = "/home/bljah/test/index.rst:5: WARNING: toctree contains reference to nonexisting document u'installation'"
        dut3 = 'This should not be treated as warning2'
        with self.assertLogs(logger="sphinx", level="INFO") as fake_out:
            self.warnings.check(dut1)
            self.warnings.check(dut2)
            self.warnings.check(dut3)
        self.assertEqual(self.warnings.return_count(), 1)
        self.assertIn(f"INFO:sphinx:{dut2}", fake_out.output)

    def test_multiline(self):
        duterr1 = "/home/bljah/test/index.rst:5: WARNING: toctree contains reference to nonexisting document u'installation'\n"
        duterr2 = "/home/bljah/test/index.rst:None: WARNING: toctree contains reference to nonexisting document u'installation'\n"
        dut = "This1 should not be treated as warning\n"
        dut += duterr1
        dut += "This should not be treated as warning2\n"
        dut += duterr2
        with self.assertLogs(logger="sphinx", level="INFO") as fake_out:
            self.warnings.check(dut)
        self.assertEqual(self.warnings.return_count(), 2)
        self.assertIn(f"INFO:sphinx:{duterr1.strip()}", fake_out.output)
        self.assertIn(f"INFO:sphinx:{duterr2.strip()}", fake_out.output)

    def test_deprecation_warning(self):
        duterr1 = "/usr/local/lib/python3.5/dist-packages/sphinx/application.py:402: RemovedInSphinx20Warning: "\
            "app.info() is now deprecated. Use sphinx.util.logging instead. RemovedInSphinx20Warning\n"
        dut = "This should not be treated as warning2\n"
        dut += duterr1
        with self.assertRaises(AssertionError) as err:
            with self.assertLogs(logger="sphinx", level="INFO"):
                self.warnings.check(dut)
        self.assertEqual(str(err.exception), "no logs of level INFO or higher triggered on sphinx")
        self.assertEqual(self.warnings.return_count(), 0)

    def test_deprecation_warning_included(self):
        self.warnings.get_checker('sphinx').include_sphinx_deprecation()
        duterr1 = "/usr/local/lib/python3.5/dist-packages/sphinx/application.py:402: RemovedInSphinx20Warning: "\
            "app.info() is now deprecated. Use sphinx.util.logging instead. RemovedInSphinx20Warning\n"
        dut = "This1 should not be treated as warning\n"
        dut += duterr1
        with self.assertLogs(logger="sphinx", level="INFO") as fake_out:
            self.warnings.check(dut)
        self.assertEqual(self.warnings.return_count(), 1)
        self.assertEqual([f"INFO:sphinx:{duterr1.strip()}"], fake_out.output)

    def test_warning_no_docname(self):
        duterr1 = "WARNING: List item 'CL-UNDEFINED_CL_ITEM' in merge/pull request 138 is not defined as a checklist-item.\n"
        with self.assertLogs(logger="sphinx", level="INFO") as fake_out:
            self.warnings.check(duterr1)
        self.assertEqual(self.warnings.return_count(), 1)
        self.assertEqual([f"INFO:sphinx:{duterr1.strip()}"], fake_out.output)

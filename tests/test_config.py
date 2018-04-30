from unittest import TestCase

from mlx.warnings import WarningsPlugin, SphinxChecker, DoxyChecker, JUnitChecker, XMLRunnerChecker


class TestConfig(TestCase):
    def test_configfile_parsing(self):
        warnings = WarningsPlugin(configfile="tests/config_example.json")
        warnings.check('testfile.c:6: warning: group test: ignoring title "Some test functions" that does not match old title "Some freaky test functions"')
        self.assertEqual(warnings.return_count(), 0)
        warnings.check('<testcase classname="dummy_class" name="dummy_name"><failure message="some random message from test case" /></testcase>')
        self.assertEqual(warnings.return_count(), 0)
        warnings.check("/home/bljah/test/index.rst:5: WARNING: toctree contains reference to nonexisting document u'installation'")
        self.assertEqual(warnings.return_count(), 1)
        warnings.check('This should not be treated as warning2')
        self.assertEqual(warnings.return_count(), 1)
        warnings.check('ERROR [0.000s]: test_some_error_test (something.anything.somewhere)')
        self.assertEqual(warnings.return_count(), 1)

    def test_partial_sphinx_config_parsing(self):
        warnings = WarningsPlugin()
        tmpjson = {
            'sphinx': {
                'enabled': True,
                'min': 0,
                'max': 0
            }
        }

        warnings.config_parser_json(tmpjson)
        warnings.check('testfile.c:6: warning: group test: ignoring title "Some test functions" that does not match old title "Some freaky test functions"')
        self.assertEqual(warnings.return_count(), 0)
        with open('tests/junit_single_fail.xml', 'r') as xmlfile:
            warnings.check(xmlfile.read())
        self.assertEqual(warnings.return_count(), 0)
        warnings.check('ERROR [0.000s]: test_some_error_test (something.anything.somewhere)')
        self.assertEqual(warnings.return_count(), 0)
        warnings.check("/home/bljah/test/index.rst:5: WARNING: toctree contains reference to nonexisting document u'installation'")
        self.assertEqual(warnings.return_count(), 1)

    def test_partial_doxygen_config_parsing(self):
        warnings = WarningsPlugin()
        tmpjson = {
            'doxygen': {
                'enabled': True,
                'min': 0,
                'max': 0
            }
        }

        warnings.config_parser_json(tmpjson)
        with open('tests/junit_single_fail.xml', 'r') as xmlfile:
            warnings.check(xmlfile.read())
        self.assertEqual(warnings.return_count(), 0)
        warnings.check("/home/bljah/test/index.rst:5: WARNING: toctree contains reference to nonexisting document u'installation'")
        self.assertEqual(warnings.return_count(), 0)
        warnings.check('ERROR [0.000s]: test_some_error_test (something.anything.somewhere)')
        self.assertEqual(warnings.return_count(), 0)
        warnings.check('testfile.c:6: warning: group test: ignoring title "Some test functions" that does not match old title "Some freaky test functions"')
        self.assertEqual(warnings.return_count(), 1)

    def test_partial_junit_config_parsing(self):
        warnings = WarningsPlugin()
        tmpjson = {
            'junit': {
                'enabled': True,
                'min': 0,
                'max': 0
            }
        }

        warnings.config_parser_json(tmpjson)
        warnings.check("/home/bljah/test/index.rst:5: WARNING: toctree contains reference to nonexisting document u'installation'")
        self.assertEqual(warnings.return_count(), 0)
        warnings.check('testfile.c:6: warning: group test: ignoring title "Some test functions" that does not match old title "Some freaky test functions"')
        self.assertEqual(warnings.return_count(), 0)
        warnings.check('ERROR [0.000s]: test_some_error_test (something.anything.somewhere)')
        self.assertEqual(warnings.return_count(), 0)
        with open('tests/junit_single_fail.xml', 'r') as xmlfile:
            warnings.check(xmlfile.read())
        self.assertEqual(warnings.return_count(), 1)

    def test_partial_xmlrunner_config_parsing(self):
        warnings = WarningsPlugin()
        tmpjson = {
            'xmlrunner': {
                'enabled': True,
                'min': 0,
                'max': 0
            }
        }

        warnings.config_parser_json(tmpjson)
        with open('tests/junit_single_fail.xml', 'r') as xmlfile:
            warnings.check(xmlfile.read())
        self.assertEqual(warnings.return_count(), 0)
        warnings.check("/home/bljah/test/index.rst:5: WARNING: toctree contains reference to nonexisting document u'installation'")
        self.assertEqual(warnings.return_count(), 0)
        warnings.check('testfile.c:6: warning: group test: ignoring title "Some test functions" that does not match old title "Some freaky test functions"')
        self.assertEqual(warnings.return_count(), 0)
        warnings.check('ERROR [0.000s]: test_some_error_test (something.anything.somewhere)')
        self.assertEqual(warnings.return_count(), 1)

    def test_doxy_junit_options_config_parsing(self):
        warnings = WarningsPlugin()
        tmpjson = {
            'doxygen': {
                'enabled': True,
                'min': 0,
                'max': 0
            },
            'junit': {
                'enabled': True,
                'min': 0,
                'max': 0
            }

        }
        warnings.config_parser_json(tmpjson)
        warnings.check("/home/bljah/test/index.rst:5: WARNING: toctree contains reference to nonexisting document u'installation'")
        self.assertEqual(warnings.return_count(), 0)
        warnings.check('testfile.c:6: warning: group test: ignoring title "Some test functions" that does not match old title "Some freaky test functions"')
        self.assertEqual(warnings.return_count(), 1)
        with open('tests/junit_single_fail.xml', 'r') as xmlfile:
            warnings.check(xmlfile.read())
        self.assertEqual(warnings.return_count(), 2)

    def test_sphinx_doxy_config_parsing(self):
        warnings = WarningsPlugin()
        tmpjson = {
            'sphinx': {
                'enabled': True,
                'min': 0,
                'max': 0
            },
            'doxygen': {
                'enabled': True,
                'min': 0,
                'max': 0
            }
        }

        warnings.config_parser_json(tmpjson)
        with open('tests/junit_single_fail.xml', 'r') as xmlfile:
            warnings.check(xmlfile.read())
        self.assertEqual(warnings.return_count(), 0)
        warnings.check('testfile.c:6: warning: group test: ignoring title "Some test functions" that does not match old title "Some freaky test functions"')
        self.assertEqual(warnings.return_count(), 1)
        warnings.check("/home/bljah/test/index.rst:5: WARNING: toctree contains reference to nonexisting document u'installation'")
        self.assertEqual(warnings.return_count(), 2)
        with open('tests/junit_single_fail.xml', 'r') as xmlfile:
            warnings.check(xmlfile.read())
        self.assertEqual(warnings.return_count(), 2)
        warnings.check("/home/bljah/test/index.rst:5: WARNING: toctree contains reference to nonexisting document u'installation'")
        self.assertEqual(warnings.return_count(), 3)
        warnings.check('testfile.c:6: warning: group test: ignoring title "Some test functions" that does not match old title "Some freaky test functions"')
        self.assertEqual(warnings.return_count(), 4)

    def test_sphinx_config_max(self):
        warnings = WarningsPlugin()
        tmpjson = {
            'sphinx': {
                'enabled': True,
                'min': 0,
                'max': 5
            }
        }

        warnings.config_parser_json(tmpjson)
        self.assertEqual(warnings.get_checker(SphinxChecker().name).get_maximum(), 5)

    def test_doxygen_config_max(self):
        warnings = WarningsPlugin()
        tmpjson = {
            'doxygen': {
                'enabled': True,
                'min': 0,
                'max': 5
            }
        }

        warnings.config_parser_json(tmpjson)
        self.assertEqual(warnings.get_checker(DoxyChecker().name).get_maximum(), 5)

    def test_junit_config_max(self):
        warnings = WarningsPlugin()
        tmpjson = {
            'junit': {
                'enabled': True,
                'min': 0,
                'max': 5
            }
        }

        warnings.config_parser_json(tmpjson)
        self.assertEqual(warnings.get_checker(JUnitChecker().name).get_maximum(), 5)

    def test_xmlrunner_config_max(self):
        warnings = WarningsPlugin()
        tmpjson = {
            'xmlrunner': {
                'enabled': True,
                'min': 0,
                'max': 5
            }
        }

        warnings.config_parser_json(tmpjson)
        self.assertEqual(warnings.get_checker(XMLRunnerChecker().name).get_maximum(), 5)

    def test_all_config_max(self):
        warnings = WarningsPlugin()
        tmpjson = {
            'sphinx': {
                'enabled': True,
                'min': 0,
                'max': 4
            },
            'doxygen': {
                'enabled': True,
                'min': 0,
                'max': 5
            },
            'junit': {
                'enabled': True,
                'min': 0,
                'max': 6
            },
            'xmlrunner': {
                'enabled': True,
                'min': 0,
                'max': 6
            }
        }

        warnings.config_parser_json(tmpjson)
        self.assertEqual(warnings.get_checker(SphinxChecker().name).get_maximum(), 4)
        self.assertEqual(warnings.get_checker(DoxyChecker().name).get_maximum(), 5)
        self.assertEqual(warnings.get_checker(JUnitChecker().name).get_maximum(), 6)
        self.assertEqual(warnings.get_checker(XMLRunnerChecker().name).get_maximum(), 6)

    def test_sphinx_config_min(self):
        warnings = WarningsPlugin()
        tmpjson = {
            'sphinx': {
                'enabled': True,
                'min': 5,
                'max': 7
            }
        }

        warnings.config_parser_json(tmpjson)
        self.assertEqual(warnings.get_checker(SphinxChecker().name).get_minimum(), 5)

    def test_doxygen_config_min(self):
        warnings = WarningsPlugin()
        tmpjson = {
            'doxygen': {
                'enabled': True,
                'min': 5,
                'max': 7
            }
        }

        warnings.config_parser_json(tmpjson)
        self.assertEqual(warnings.get_checker(DoxyChecker().name).get_minimum(), 5)

    def test_junit_config_min(self):
        warnings = WarningsPlugin()
        tmpjson = {
            'junit': {
                'enabled': True,
                'min': 5,
                'max': 7
            }
        }

        warnings.config_parser_json(tmpjson)
        self.assertEqual(warnings.get_checker(JUnitChecker().name).get_minimum(), 5)

    def test_xmlrunner_config_min(self):
        warnings = WarningsPlugin()
        tmpjson = {
            'xmlrunner': {
                'enabled': True,
                'min': 5,
                'max': 7
            }
        }

        warnings.config_parser_json(tmpjson)
        self.assertEqual(warnings.get_checker(XMLRunnerChecker().name).get_minimum(), 5)

    def test_all_config_min(self):
        warnings = WarningsPlugin()
        tmpjson = {
            'sphinx': {
                'enabled': True,
                'min': 4,
                'max': 7
            },
            'doxygen': {
                'enabled': True,
                'min': 3,
                'max': 7
            },
            'junit': {
                'enabled': True,
                'min': 5,
                'max': 7
            },
            'xmlrunner': {
                'enabled': True,
                'min': 5,
                'max': 7
            }
        }

        warnings.config_parser_json(tmpjson)
        self.assertEqual(warnings.get_checker(SphinxChecker().name).get_minimum(), 4)
        self.assertEqual(warnings.get_checker(DoxyChecker().name).get_minimum(), 3)
        self.assertEqual(warnings.get_checker(JUnitChecker().name).get_minimum(), 5)
        self.assertEqual(warnings.get_checker(XMLRunnerChecker().name).get_minimum(), 5)


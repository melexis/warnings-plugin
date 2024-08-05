import os
from io import StringIO
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from mlx.warnings import (JUnitChecker, DoxyChecker, SphinxChecker, XMLRunnerChecker, RobotChecker, WarningsPlugin,
                          WarningsConfigError)

TEST_IN_DIR = Path(__file__).parent / 'test_in'


class TestConfig(TestCase):
    def setUp(self):
        os.environ['MIN_SPHINX_WARNINGS'] = '0'
        os.environ['MAX_SPHINX_WARNINGS'] = '0'

    def tearDown(self):
        for var in ('MIN_SPHINX_WARNINGS', 'MAX_SPHINX_WARNINGS'):
            if var in os.environ:
                del os.environ[var]

    def test_configfile_parsing(self):
        warnings = WarningsPlugin(config_file=(TEST_IN_DIR / "config_example.json"))
        warnings.check('testfile.c:6: warning: group test: ignoring title "Some test functions" that does not match old title "Some freaky test functions"')
        self.assertEqual(warnings.return_count(), 1)
        warnings.check('<testcase classname="dummy_class" name="dummy_name"><failure message="some random message from test case" /></testcase>')
        self.assertEqual(warnings.return_count(), 1)
        warnings.check("/home/bljah/test/index.rst:5: WARNING: toctree contains reference to nonexisting document u'installation'")
        self.assertEqual(warnings.return_count(), 2)
        warnings.check('This should not be treated as warning2')
        self.assertEqual(warnings.return_count(), 2)
        warnings.check('ERROR [0.000s]: test_some_error_test (something.anything.somewhere)')
        self.assertEqual(warnings.return_count(), 3)

    def test_configfile_parsing_missing_envvar(self):
        del os.environ['MAX_SPHINX_WARNINGS']
        with self.assertRaises(WarningsConfigError) as c_m:
            WarningsPlugin(config_file=(TEST_IN_DIR / "config_example.json"))
        self.assertEqual(
            str(c_m.exception),
            "Failed to find environment variable 'MAX_SPHINX_WARNINGS' for configuration value 'max'")

    def _helper_exclude(self, warnings):
        with patch('sys.stdout', new=StringIO()) as verbose_output:
            warnings.check('testfile.c:6: warning: group test: ignoring title "Some test functions" that does not match old title "Some freaky test functions"')
            self.assertEqual(warnings.return_count(), 0)
            warnings.check('<testcase classname="dummy_class" name="dummy_name"><failure message="some random message from test case" /></testcase>')
            self.assertEqual(warnings.return_count(), 0)
            deprecation_warning = 'sphinx/application.py:402: RemovedInSphinx20Warning: app.info() is now deprecated. Use sphinx.util.logging instead.'
            warnings.check(deprecation_warning)
            self.assertEqual(warnings.return_count(), 0)
            toctree_warning = "/home/bljah/test/index.rst:5: WARNING: toctree contains reference to nonexisting document u'installation'"
            warnings.check(toctree_warning)
            self.assertEqual(warnings.return_count(), 0)  # ignored because of configured "exclude" regex
            warnings.check("home/bljah/test/index.rst:5: WARNING: this warning should not get excluded")
            self.assertEqual(warnings.return_count(), 1)
            warnings.check('This should not be treated as warning2')
            self.assertEqual(warnings.return_count(), 1)
            warnings.check('ERROR [0.000s]: test_some_error_test (something.anything.somewhere)')
            self.assertEqual(warnings.return_count(), 1)
        excluded_toctree_warning = "Excluded {!r} because of configured regex {!r}".format(toctree_warning, "WARNING: toctree")
        self.assertIn(excluded_toctree_warning, verbose_output.getvalue())
        warning_echo = "home/bljah/test/index.rst:5: WARNING: this warning should not get excluded"
        self.assertIn(warning_echo, verbose_output.getvalue())

    def test_configfile_parsing_exclude_json(self):
        warnings = WarningsPlugin(verbose=True, config_file=(TEST_IN_DIR / "config_example_exclude.json"))
        self._helper_exclude(warnings)

    def test_configfile_parsing_exclude_yml(self):
        warnings = WarningsPlugin(verbose=True, config_file=(TEST_IN_DIR / "config_example_exclude.yml"))
        self._helper_exclude(warnings)

    def test_configfile_parsing_include_priority(self):
        warnings = WarningsPlugin(verbose=True, config_file=(TEST_IN_DIR / "config_example_exclude.json"))
        warnings.get_checker('sphinx').include_sphinx_deprecation()
        deprecation_warning = 'sphinx/application.py:402: RemovedInSphinx20Warning: app.info() is now deprecated. Use sphinx.util.logging instead.'
        warnings.check(deprecation_warning)
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

        warnings.config_parser(tmpjson)
        warnings.check('testfile.c:6: warning: group test: ignoring title "Some test functions" that does not match old title "Some freaky test functions"')
        self.assertEqual(warnings.return_count(), 0)
        with open('tests/test_in/junit_single_fail.xml', 'r') as xmlfile:
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

        warnings.config_parser(tmpjson)
        with open('tests/test_in/junit_single_fail.xml', 'r') as xmlfile:
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

        warnings.config_parser(tmpjson)
        warnings.check("/home/bljah/test/index.rst:5: WARNING: toctree contains reference to nonexisting document u'installation'")
        self.assertEqual(warnings.return_count(), 0)
        warnings.check('testfile.c:6: warning: group test: ignoring title "Some test functions" that does not match old title "Some freaky test functions"')
        self.assertEqual(warnings.return_count(), 0)
        warnings.check('ERROR [0.000s]: test_some_error_test (something.anything.somewhere)')
        self.assertEqual(warnings.return_count(), 0)
        with open('tests/test_in/junit_single_fail.xml', 'r') as xmlfile:
            warnings.check(xmlfile.read())
        self.assertEqual(warnings.return_count(), 1)

    def test_exclude_feature_type_error(self):
        warnings = WarningsPlugin()
        tmpjson = {
            'junit': {
                'enabled': True,
                'min': 0,
                'max': 0,
                "exclude": "able to trace this random failure msg"
            }
        }
        with self.assertRaises(TypeError) as c_m:
            warnings.config_parser(tmpjson)
        self.assertEqual(str(c_m.exception), "Expected a list value for exclude key in configuration file; got str")

    def test_partial_junit_config_parsing_exclude_regex(self):
        warnings = WarningsPlugin()
        tmpjson = {
            'junit': {
                'enabled': True,
                'min': 0,
                'max': 0,
                "exclude": ["able to trace this random failure msg"]
            }
        }
        warnings.config_parser(tmpjson)
        with open('tests/test_in/junit_single_fail.xml', 'r') as xmlfile:
            warnings.check(xmlfile.read())
        self.assertEqual(warnings.return_count(), 0)

    def test_partial_robot_config_parsing_exclude_regex(self):
        warnings = WarningsPlugin(verbose=True)
        tmpjson = {
            'robot': {
                'enabled': True,
                'suites': [
                    {
                        'name': 'Suite One',
                        'min': 0,
                        'max': 0,
                        "exclude": ["does not exist"]  # excludes failure in suite
                    },
                    {
                        'name': 'Suite Two',
                        'min': 1,
                        'max': 1,
                        "exclude": ["does not exist"]  # no match for failure in suite
                    }
                ]
            }
        }
        warnings.config_parser(tmpjson)
        with open('tests/test_in/robot_double_fail.xml', 'r') as xmlfile:
            with patch('sys.stdout', new=StringIO()) as verbose_output:
                warnings.check(xmlfile.read())
                count = warnings.return_count()
        self.assertEqual(count, 1)
        self.assertEqual(warnings.return_check_limits(), 0)
        self.assertEqual(
            '\n'.join([
                r"Excluded 'Directory &#x27;C:\\nonexistent&#x27; does not exist.' because of configured regex 'does not exist'",
                "Suite One &amp; Suite Two.Suite Two.Another test",
                "Suite 'Suite One': 0 warnings found",
                "Suite 'Suite Two': 1 warnings found",
            ]) + '\n',
            verbose_output.getvalue()
        )

    def test_partial_robot_config_empty_name(self):
        warnings = WarningsPlugin(verbose=True)
        tmpjson = {
            'robot': {
                'enabled': True,
                'suites': [
                    {
                        'name': '',
                        'min': 1,
                        'max': 1,
                        "exclude": ["does not exist"]  # excludes 1 out of 2 failures in suites
                    }
                ]
            }
        }
        warnings.config_parser(tmpjson)
        with open('tests/test_in/robot_double_fail.xml', 'r') as xmlfile:
            with patch('sys.stdout', new=StringIO()) as verbose_output:
                warnings.check(xmlfile.read())
                count = warnings.return_count()
        self.assertEqual(count, 1)
        self.assertEqual(warnings.return_check_limits(), 0)
        self.assertEqual(
            '\n'.join([
                r"Excluded 'Directory &#x27;C:\\nonexistent&#x27; does not exist.' because of configured regex 'does not exist'",
                "Suite One &amp; Suite Two.Suite Two.Another test",
                "1 warnings found",
            ]) + '\n',
            verbose_output.getvalue()
        )

    def test_partial_xmlrunner_config_parsing(self):
        warnings = WarningsPlugin()
        tmpjson = {
            'xmlrunner': {
                'enabled': True,
                'min': 0,
                'max': 0
            }
        }

        warnings.config_parser(tmpjson)
        with open('tests/test_in/junit_single_fail.xml', 'r') as xmlfile:
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
        warnings.config_parser(tmpjson)
        warnings.check("/home/bljah/test/index.rst:5: WARNING: toctree contains reference to nonexisting document u'installation'")
        self.assertEqual(warnings.return_count(), 0)
        warnings.check('testfile.c:6: warning: group test: ignoring title "Some test functions" that does not match old title "Some freaky test functions"')
        self.assertEqual(warnings.return_count(), 1)
        with open('tests/test_in/junit_single_fail.xml', 'r') as xmlfile:
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

        warnings.config_parser(tmpjson)
        with open('tests/test_in/junit_single_fail.xml', 'r') as xmlfile:
            warnings.check(xmlfile.read())
        self.assertEqual(warnings.return_count(), 0)
        warnings.check('testfile.c:6: warning: group test: ignoring title "Some test functions" that does not match old title "Some freaky test functions"')
        self.assertEqual(warnings.return_count(), 1)
        warnings.check("/home/bljah/test/index.rst:5: WARNING: toctree contains reference to nonexisting document u'installation'")
        self.assertEqual(warnings.return_count(), 2)
        with open('tests/test_in/junit_single_fail.xml', 'r') as xmlfile:
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

        warnings.config_parser(tmpjson)
        self.assertEqual(warnings.get_checker(SphinxChecker().name).maximum, 5)

    def test_doxygen_config_max(self):
        warnings = WarningsPlugin()
        tmpjson = {
            'doxygen': {
                'enabled': True,
                'min': 0,
                'max': 5
            }
        }

        warnings.config_parser(tmpjson)
        self.assertEqual(warnings.get_checker(DoxyChecker().name).maximum, 5)

    def test_junit_config_max(self):
        warnings = WarningsPlugin()
        tmpjson = {
            'junit': {
                'enabled': True,
                'min': 0,
                'max': 5
            }
        }

        warnings.config_parser(tmpjson)
        self.assertEqual(warnings.get_checker(JUnitChecker().name).maximum, 5)

    def test_xmlrunner_config_max(self):
        warnings = WarningsPlugin()
        tmpjson = {
            'xmlrunner': {
                'enabled': True,
                'min': 0,
                'max': 5
            }
        }

        warnings.config_parser(tmpjson)
        self.assertEqual(warnings.get_checker(XMLRunnerChecker().name).maximum, 5)

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
            },
            'robot': {
                'enabled': True,
                'suites': [
                    {
                        'name': 'dummy1',
                        'min': 5,
                        'max': 7,
                    },
                    {
                        'name': 'dummy2',
                        'min': 1,
                        'max': 9,
                    },
                    {
                        'name': 'dummy3',
                        'min': 2,
                        'max': 2,
                    }
                ]
            }
        }

        warnings.config_parser(tmpjson)
        self.assertEqual(warnings.get_checker(SphinxChecker().name).maximum, 4)
        self.assertEqual(warnings.get_checker(DoxyChecker().name).maximum, 5)
        self.assertEqual(warnings.get_checker(JUnitChecker().name).maximum, 6)
        self.assertEqual(warnings.get_checker(XMLRunnerChecker().name).maximum, 6)
        self.assertEqual(warnings.get_checker(RobotChecker().name).maximum, 9)

    def test_sphinx_config_min(self):
        warnings = WarningsPlugin()
        tmpjson = {
            'sphinx': {
                'enabled': True,
                'min': 5,
                'max': 7
            }
        }

        warnings.config_parser(tmpjson)
        self.assertEqual(warnings.get_checker(SphinxChecker().name).minimum, 5)

    def test_doxygen_config_min(self):
        warnings = WarningsPlugin()
        tmpjson = {
            'doxygen': {
                'enabled': True,
                'min': 5,
                'max': 7
            }
        }

        warnings.config_parser(tmpjson)
        self.assertEqual(warnings.get_checker(DoxyChecker().name).minimum, 5)

    def test_junit_config_min(self):
        warnings = WarningsPlugin()
        tmpjson = {
            'junit': {
                'enabled': True,
                'min': 5,
                'max': 7
            }
        }

        warnings.config_parser(tmpjson)
        self.assertEqual(warnings.get_checker(JUnitChecker().name).minimum, 5)

    def test_xmlrunner_config_min(self):
        warnings = WarningsPlugin()
        tmpjson = {
            'xmlrunner': {
                'enabled': True,
                'min': 5,
                'max': 7
            }
        }

        warnings.config_parser(tmpjson)
        self.assertEqual(warnings.get_checker(XMLRunnerChecker().name).minimum, 5)

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
            },
            'robot': {
                'enabled': True,
                'suites': [
                    {
                        'name': 'dummy1',
                        'min': 5,
                        'max': 7,
                    },
                    {
                        'name': 'dummy2',
                        'min': 1,
                        'max': 9,
                    },
                    {
                        'name': 'dummy3',
                        'min': 2,
                        'max': 2,
                    }
                ]
            }
        }

        warnings.config_parser(tmpjson)
        self.assertEqual(warnings.get_checker(SphinxChecker().name).minimum, 4)
        self.assertEqual(warnings.get_checker(DoxyChecker().name).minimum, 3)
        self.assertEqual(warnings.get_checker(JUnitChecker().name).minimum, 5)
        self.assertEqual(warnings.get_checker(XMLRunnerChecker().name).minimum, 5)
        self.assertEqual(warnings.get_checker(RobotChecker().name).minimum, 1)

    def test_invalid_config(self):
        warnings = WarningsPlugin()
        tmpjson = {
            'robot': {
                'enabled': True,
                'suites': [
                    {
                        'name': '',
                        'min': 5,
                        'max': 7,
                    },
                    {
                        'name': 'dummy2',
                        'min': 10,
                        'max': 9,
                    },
                    {
                        'name': 'dummy3',
                        'min': 2,
                        'max': 2,
                    }
                ]
            }
        }
        with self.assertRaises(ValueError) as c_m:
            warnings.config_parser(tmpjson)
        self.assertEqual(str(c_m.exception),
                         'Invalid argument: minimum limit must be lower than maximum limit (9); cannot set 10.')

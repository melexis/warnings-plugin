
.. _software_design:

===============
Software Design
===============

.. _class_diagram:

Class Diagram
=============

.. uml generated by `pyreverse mlx.warnings --filter ALL -o plantuml`
.. uml::

    @startuml classes
    set namespaceSeparator none
    class "CoverityChecker" as mlx.warnings.regex_checker.CoverityChecker {
      CLASSIFICATION : str
      count
      name : str
      pattern
      check(content)
    }
    class "DoxyChecker" as mlx.warnings.regex_checker.DoxyChecker {
      name : str
      pattern
    }
    class "JUnitChecker" as mlx.warnings.junit_checker.JUnitChecker {
      count
      name : str
      _check_testcase(testcase)
      check(content)
      prepare_tree(root_input)
    }
    class "PolyspaceChecker" as mlx.warnings.polyspace_checker.PolyspaceChecker {
      _cq_description_template : Template
      checkers : list
      count : int
      counted_warnings
      cq_default_path
      cq_description_template
      maximum
      minimum
      name : str
      __init__(verbose)
      check(content)
      parse_config(config)
      return_check_limits()
      return_count()
    }
    class "PolyspaceFamilyChecker" as mlx.warnings.polyspace_checker.PolyspaceFamilyChecker {
      _cq_description_template
      check_value
      code_quality_severity : dict
      column_name
      count
      cq_description_template
      cq_findings : list
      family_value
      __init__(family_value, column_name, check_value)
      add_code_quality_finding(row)
      check(content)
      return_count()
    }
    class "RegexChecker" as mlx.warnings.regex_checker.RegexChecker {
      SEVERITY_MAP : dict
      count
      name : str
      pattern : NoneType
      add_code_quality_finding(match)
      check(content)
    }
    class "RobotChecker" as mlx.warnings.robot_checker.RobotChecker {
      checkers : list
      count : int
      counted_warnings
      maximum
      minimum
      name : str
      check(content)
      parse_config(config)
      return_check_limits()
      return_count()
    }
    class "RobotSuiteChecker" as mlx.warnings.robot_checker.RobotSuiteChecker {
      check_suite_name : bool
      is_valid_suite_name : bool
      name
      __init__(name, check_suite_name)
      _check_testcase(testcase)
      check(content)
      return_count()
    }
    class "SphinxChecker" as mlx.warnings.regex_checker.SphinxChecker {
      name : str
      pattern
      sphinx_deprecation_regex : str
      sphinx_deprecation_regex_in_match : str
      include_sphinx_deprecation()
    }
    class "WarningsChecker" as mlx.warnings.warnings_checker.WarningsChecker {
      _counted_warnings : list
      _cq_description_template : Template
      _maximum : int
      _minimum : int
      count : int
      counted_warnings
      cq_default_path : str
      cq_description_template
      cq_enabled : bool
      cq_findings : list
      exclude_patterns : list
      include_patterns : list
      maximum
      minimum
      name : str
      verbose : bool
      __init__(verbose)
      _is_excluded(content)
      _return_error_code()
      _search_patterns(content, patterns)
      add_patterns(regexes, pattern_container)
      {abstract}check(content)
      parse_config(config)
      print_when_verbose(message)
      return_check_limits()
      return_count()
    }
    class "<color:red>WarningsConfigError</color>" as mlx.warnings.exceptions.WarningsConfigError {
    }
    class "WarningsPlugin" as mlx.warnings.warnings.WarningsPlugin {
      _maximum : int
      _minimum : int
      activated_checkers : dict
      count : int
      cq_enabled : bool
      printout : bool
      public_checkers : list
      verbose : bool
      __init__(verbose, config_file, cq_enabled)
      activate_checker(checker)
      activate_checker_name(name)
      check(content)
      check_logfile(file)
      config_parser(config)
      configure_maximum(maximum)
      configure_minimum(minimum)
      get_checker(name)
      return_check_limits(name)
      return_count(name)
      toggle_printout(printout)
      write_code_quality_report(out_file)
      write_counted_warnings(out_file)
    }
    class "XMLRunnerChecker" as mlx.warnings.regex_checker.XMLRunnerChecker {
      name : str
      pattern
    }
    mlx.warnings.junit_checker.JUnitChecker --|> mlx.warnings.warnings_checker.WarningsChecker
    mlx.warnings.polyspace_checker.PolyspaceChecker --|> mlx.warnings.warnings_checker.WarningsChecker
    mlx.warnings.polyspace_checker.PolyspaceFamilyChecker --|> mlx.warnings.warnings_checker.WarningsChecker
    mlx.warnings.regex_checker.CoverityChecker --|> mlx.warnings.regex_checker.RegexChecker
    mlx.warnings.regex_checker.DoxyChecker --|> mlx.warnings.regex_checker.RegexChecker
    mlx.warnings.regex_checker.RegexChecker --|> mlx.warnings.warnings_checker.WarningsChecker
    mlx.warnings.regex_checker.SphinxChecker --|> mlx.warnings.regex_checker.RegexChecker
    mlx.warnings.regex_checker.XMLRunnerChecker --|> mlx.warnings.regex_checker.RegexChecker
    mlx.warnings.robot_checker.RobotChecker --|> mlx.warnings.warnings_checker.WarningsChecker
    mlx.warnings.robot_checker.RobotSuiteChecker --|> mlx.warnings.junit_checker.JUnitChecker
    @enduml


String Handling
===============

Convention is to use plain python strings everywhere. Where needed the strings can be converted to anything else.

Example: junitparser expects byte array objects, so we encode our string right before passing it to junitparser.

Instrument Module
=================

.. automodule:: mlx.warnings
    :members:
    :undoc-members:
    :show-inheritance:

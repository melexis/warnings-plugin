.. image:: https://img.shields.io/hexpm/l/plug.svg
    :target: https://www.apache.org/licenses/LICENSE-2.0
    :alt: Apache2 License

.. image:: https://github.com/melexis/warnings-plugin/actions/workflows/python-package.yml/badge.svg?branch=master
    :target: https://github.com/melexis/warnings-plugin/actions/workflows/python-package.yml
    :alt: Build status

.. image:: https://badge.fury.io/py/mlx.warnings.svg
    :target: https://pypi.org/project/mlx.warnings
    :alt: PyPI packaged release

.. image:: https://img.shields.io/badge/Documentation-published-brightgreen.svg
    :target: https://melexis.github.io/warnings-plugin/
    :alt: Documentation

.. image:: https://scan.coverity.com/projects/15266/badge.svg
    :target: https://scan.coverity.com/projects/melexis-warnings-plugin
    :alt: Coverity Scan Build Status

.. image:: https://codecov.io/gh/melexis/warnings-plugin/branch/master/graph/badge.svg
    :target: https://app.codecov.io/gh/melexis/warnings-plugin
    :alt: Code Coverage

.. image:: https://codeclimate.com/github/melexis/warnings-plugin/badges/gpa.svg
    :target: https://codeclimate.com/github/melexis/warnings-plugin
    :alt: Code Climate Status

.. image:: https://codeclimate.com/github/melexis/warnings-plugin/badges/issue_count.svg
    :target: https://codeclimate.com/github/melexis/warnings-plugin/issues
    :alt: Issue Count

.. image:: https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat
    :target: https://github.com/melexis/warnings-plugin/issues
    :alt: Contributions welcome

.. image:: https://www.bestpractices.dev/projects/4368/badge
    :target: https://www.bestpractices.dev/projects/4368
    :alt: CII Best Practices


============================
Command Line Warnings Plugin
============================

Command-line alternative for https://github.com/jenkinsci/warnings-plugin.
Useable with plugin-less CI systems. It can be used with GitLab-CI to enable
warning threshold setting for failing the job and for parsing warnings from
various tools and report them as errors.


============
Installation
============

Every release is uploaded to pip so it can be installed simply by using pip.

.. code-block:: bash

    # Python3
    pip3 install mlx.warnings

You can find more details in the `Installation guide`_.

.. _`Installation guide`: https://melexis.github.io/warnings-plugin/installation.html

=====
Usage
=====

Warnings plugin parses log messages as well as direct command stream. In case you
want to create log file, you will need to redirect your stderr to some text file.
You can do that with shell pipes or with
command line arguments to command (if it supports outputting errors to file
instead of stderr). Be aware that some commands print warnings on stdout.

Also warnings plugin log files need to be the last argument as otherwise the
arguments after that are discarded, because they are considered as command
arguments (with or without command flag).

------------
Pipe Example
------------

Below is one of the ways to redirect your stderr to stdout and save it inside a
file.

.. code-block:: bash

    yourcommand 2>&1 | tee doc_log.txt

---------------
Command Example
---------------

Below is the command example for the plugin (keep in mind that parse commands are
required).

.. code-block:: bash

    mlx-warnings --command <yourcommand>

---------------
Running Command
---------------

There are few ways to run warnings plugin. If you are playing with Python on
your computer you want to use ``virtualenv``. This will separate your packages
per project and there is less chance of some dependency hell. You can
initialize virtual environment in current directory by ``virtualenv .`` .

Melexis Warnings plugin can be called directly from shell/console using:

.. code-block:: bash

    mlx-warnings -h

It has also possibility to be called as module from ``python3``. In
that case command will look like:

.. code-block:: bash

    python3 -m mlx.warnings -h

Help prints all currently supported commands and their usages.

The command returns (shell $? variable):

- value 0 when the number of counted warnings is within the supplied minimum and maximum limits: ok,
- number of counted warnings (positive) when the counter number is not within those limit (1 in case of 0 counted warnings).

---------------------------
Simple Command Line Options
---------------------------

Plugin has two forms of passing the arguments to checkers. The command line
option which enables checkers and sets minimum and maximum to each checker
individually, or the configuration file option which provides more flexibility
and also traceability as it resides inside repository and provides option to
adjust minimum and maximum per individual checker.

Parse for Sphinx Warnings
-------------------------

After you saved your Sphinx warnings to the file, you can parse it with
command:

.. code-block:: bash

    # command line log file
    mlx-warnings doc_log.txt --sphinx
    # command line command execution
    mlx-warnings --sphinx --command <command-for-sphinx>

    # explicitly as python module for log file
    python3 -m mlx.warnings --sphinx doc_log.txt
    python -m mlx.warnings --sphinx doc_log.txt
    # explicitly as python module
    python3 -m mlx.warnings --sphinx --command <command-for-sphinx>
    python -m mlx.warnings --sphinx --command <command-for-sphinx>


Parse for Doxygen Warnings
--------------------------

After you saved your Doxygen warnings to the file, you can parse it with
command:

.. code-block:: bash

    # command line log file
    mlx-warnings doc_log.txt --doxygen
    # command line command execution
    mlx-warnings --doxygen --command <command-for-doxygen>

    # explicitly as python module for log file
    python3 -m mlx.warnings --doxygen doc_log.txt
    python -m mlx.warnings --doxygen doc_log.txt
    # explicitly as python module
    python3 -m mlx.warnings --doxygen --command <command-for-doxygen>
    python -m mlx.warnings --doxygen --command <command-for-doxygen>


Parse for Coverity Defects
--------------------------

Coverity is a static analysis tool that includes a CLI tool to run desktop analysis
on your local changes and report the results back directly in the console.
You only need to list affected files and below example lists changed files
between your source and target branch, e.g. 'main', which it then forwards to ``cov-run-desktop``:

.. code-block:: bash

    cov-run-desktop --text-output-style=oneline `git diff --name-only --ignore-submodules main`

You can either pipe the results to a log file and pass it to the warnings-plugin, or you can use
the ``--command`` argument to let the plugin invoke ``cov-run-desktop``.

.. code-block:: bash

    # command line log file
    mlx-warnings --coverity cov-run-desktop-output.txt
    # command line command execution
    mlx-warnings --coverity --command <command-for-coverity>

    # explicitly as python module for log file
    python3 -m mlx.warnings --coverity cov-run-desktop-output.txt
    python -m mlx.warnings --coverity cov-run-desktop-output.txt
    # explicitly as python module
    python3 -m mlx.warnings --coverity --command <command-for-coverity>
    python -m mlx.warnings --coverity --command <command-for-coverity>


The command below demonstrates how we utilize `cov-run-desktop`:

.. code-block:: bash

    cov-run-desktop --text-output-style=oneline --exit1-if-defects false --triage-attribute-regex "classification" ".*" <coverity_files> | tee raw_defects.log

Then, the mlx-warnings plugin processes the output log file, `raw_defects.log`, based on the optional configuration file
`config.yml` to produce three outputs:

- A text file that contains all counted Coverity defects.
- `A Code Quality report`_ `report.json` that contains all counted Coverity defects.
- A return code equal to the amount of counted Coverity defects. The value is 0 if the amount of Coverity defects is
  within limits. We use this return code to determine whether our CI job passes or fails.

.. code-block:: bash

    mlx-warnings --config config.yml --output counted_defects.txt --code-quality report.json raw_defects.log

Below is an example configuration for the Coverity checker:

.. code-block:: yaml

    coverity:
        enabled: true
        unclassified:
          max: 0
        pending:
          max: 0
        bug:
          min: 2
          max: 2
        false_positive:
          max: -1
        intentional:
          max: -1

As you can see, we have configured limits for 5 out of 5 Coverity Classifications. You can configure a minimum and a
maximum limit for the number of allowed Coverity defects that belong to the Classification.
The default value for both limits is 0.
A value of `-1` for `max` corresponds to effectively no limit (an infinite amount).
If one or more Classifications are missing from your configuration, the Coverity defects are counted and 0 are
allowed. To ignore certain classifications, modify the value for
`cov-run-desktop --triage-attribute-regex "classification"`.

.. note::
    The warnings-plugin counts only one warning if there are multiple warnings for the same CID.

Parse for JUnit Failures
------------------------

After you saved your JUnit XML output to the file, you can parse it with
command:

.. code-block:: bash

    # command line log file
    mlx-warnings junit_output.xml --junit
    # command line command execution
    mlx-warnings --junit --command <command-for-junit>

    # explicitly as python module for log file
    python3 -m mlx.warnings --junit junit_output.xml
    python -m mlx.warnings --junit junit_output.xml
    # explicitly as python module
    python3 -m mlx.warnings --junit --command <command-for-junit>
    python -m mlx.warnings --junit --command <command-for-junit>


Parse for XMLRunner Errors
--------------------------

When you run XMLRunner_,
the errors are reported on the output, but they are not marked as failures in
the test reports xml files. Since command exits as 1, we could not detect tests
that just did not run (not failed). warnings-plugin now parses for the output
with command:

.. code-block:: bash

    # command line log file
    mlx-warnings xmlrunner_log.txt --xmlrunner
    # command line command execution
    mlx-warnings --xmlrunner --command <command-for-xmlrunner>

    # explicitly as python module for log file
    python3 -m mlx.warnings --xmlrunner xmlrunner_log.txt
    python -m mlx.warnings --xmlrunner xmlrunner_log.txt
    # explicitly as python module
    python3 -m mlx.warnings --xmlrunner --command <command-for-xmlrunner>
    python -m mlx.warnings --xmlrunner --command <command-for-xmlrunner>

.. _XMLRunner: https://github.com/xmlrunner/unittest-xml-reporting

Parse for Robot Framework Test Failures
---------------------------------------

When running `Robot Framework`_ tests with |--xunit report.xml|_ as an input
argument, an xUnit compatible result file is generated. The warnings-plugin can
parse this file and check the amount of failures. By default, the test results
of all test suites in the file are taken into account. If you only care about
one specific test suite, you can use ``--name <<suite name>>``. If this suite
name doesn't exist in the input file, an error is raised. The warning
limits can be configured for multiple test suites individually by means of a
`configuration file to pass options`_, which supports additional configuration parameters:

- ``"check_suite_names"``, which is ``true`` by default, raises an error when a configured suite name
  does not exist in the input XML file. This helps you verify that all of the test suites in your configuration file
  were passed to the `robot` CLI.
- ``"allow_unconfigured"``, which is ``true`` by default, raises an error when a suite name in the input
  XML file is missing from your configuration file. Note: a configuration value ``""`` matches all suite names.

.. code-block:: bash

    # command line xunit file
    mlx-warnings --robot report.xml
    # ignore all but the specified suite
    mlx-warnings --robot --name "Suite Name" report.xml

    # explicitly as python module
    python3 -m mlx.warnings --robot --name "Suite Name" report.xml

.. _`Robot Framework`: https://robotframework.org/
.. |--xunit report.xml| replace:: ``--xunit report.xml``
.. _`--xunit report.xml`: https://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#xunit-compatible-result-file

Parse for Polyspace Failures
----------------------------

The Polyspace checker requires as input a TSV file exported by Polyspace.
You can find instructions on exporting TSV files in the Polyspace documentation.

Exporting Polyspace Results
^^^^^^^^^^^^^^^^^^^^^^^^^^^

The following commands instruct Polyspace to export the results as a TSV file:

.. code-block:: bash

    polyspace-results-export -format csv -results-dir <resultsFolder> <export_options>
    # or
    polyspace-results-export -format csv -host <hostName> -run-id <runID> <export_options> <polyspace_access_options>

The csv format outputs tab-separated values (TSV).
Each result in the TSV format consists of tab-separated information in columns.
Starting from Polyspace version R2024a these columns are available:
ID, Family, Group, Color, New, Check, Information, Function, File, Status, Severity, Comment, Key, Line and Col.
In previous versions of Polyspace the Line and Col column are not available yet.

This file is required when you enable Polyspace in the configuration file.

Configuration
^^^^^^^^^^^^^

Polyspace checking can only be enabled with a configuration file,
and it cannot be used together with other checkers enabled.
In this case, only the Polyspace checker will run.

When you enable Polyspace checking in the configuration file,
the checks consist of a key that represents the "family" column of the TSV file.
For example, "run-time check" is the family of Code Prover and "defect" is the family of Bug Finder.
The value of that key is a list, which contains the name of the column to check as a key and
the value of that column to check together with ``min`` and ``max`` values.

All results with one of the following statuses are discarded altogether:

- Justified
- Not a Defect

These statuses indicate that you have given due consideration and justified that result, as described
in `Polyspace's documentation about results`_.
The status "No Action Planned" is not treated differently because this is the default status for annotations.

.. _`Polyspace's documentation about results`: https://www.mathworks.com/help/polyspace_access/ug/fix-or-comment-polyspace-results-web-browser.html

Example Checks
^^^^^^^^^^^^^^

In case of Code Prover, you might want to check the ``color`` column on ``red`` or ``orange`` issues.
In case of Bug Finder, you might want to check the ``information`` column on ``impact: high``, ``impact: medium``, or even ``impact: low``.
Other issues, such as "Global variable", can also be handled.
You can specify any column and value you want to check in the configuration file.

Running the mlx-warnings plugin
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The following commands demonstrate how to run the mlx-warnings plugin with the TSV file:

.. code-block:: bash

    # basic Polyspace checker
    mlx-warnings --config <configuration_file> <tsv_file>
    # Polyspace checker with code quality export
    mlx-warnings --code-quality path/to/code_quality.json --config <configuration_file> <tsv_file>

----------------------------------
Configuration File to Pass Options
----------------------------------

Beside command line, you can pass options through the configuration file.
Configuration file is in JSON or YAML_ format with a simple structure.
The values for 'min' and 'max' can be set with environment variables via a
|string.Template|_, e.g. ``"${MAX_SPHINX_WARNINGS}"``.

.. code-block:: json

    {
        "sphinx": {
            "enabled": true,
            "cq_default_path": "doc/source/conf.py",
            "cq_description_template": "$PRODUCT | $description",
            "min": 0,
            "max": "${MAX_SPHINX_WARNINGS}"
        },
        "doxygen": {
            "enabled": true,
            "cq_default_path": "doc/doxygen/Doxyfile",
            "min": "$MIN_DOXY_WARNINGS",
            "max": "$MAX_DOXY_WARNINGS"
        },
        "junit": {
            "enabled": false,
            "min": 0,
            "max": 0
        },
        "xmlrunner": {
            "enabled": false,
            "min": 0,
            "max": 0
        },
        "coverity": {
            "enabled": false,
            "bug": {
                "min": 0,
                "max": 0
            },
            "pending": {
                "min": 0,
                "max": 0
            }
        },
        "robot": {
            "enabled": false,
            "check_suite_names": true,
            "suites": [
                {
                    "name": "My First Suite",
                    "min": 8,
                    "max": 10
                },
                {
                    "name": "My Second Suite",
                    "min": 0,
                    "max": 0
                }
            ]
        },
        "polyspace": {
            "enabled": false,
            "cq_description_template": "$PRODUCT $family: $check",
            "exclude": [
                ".+\\tdummy_function\\(\\)\\tdummy_file_name\\.c\\t"
            ],
            "run-time check": [
                {
                    "color": "red",
                    "min": 0,
                    "max": 0
                }
            ]
        }
    }


First key is ``checkername``, then it contains a boolean value for key ``enabled``,
value for minimum number of warnings with key ``min`` and value for maximum
number of warnings with key ``max``. This structure allows simple expansion.

To run the plugin with configuration file you simply pass ``--config`` flag with
path to configuration file

.. code-block:: bash

    # command line log file
    mlx-warnings --config path/to/config.json junit_output.xml
    # command line command execution
    mlx-warnings --config path/to/config.json --command <command-for-junit>


-------------
Other Options
-------------

Since the plugin is under active development there are new Features added fast.
Important options currently include setting a minimum and a maximum number of warnings
that are still acceptable to return 0 (success). Requiring an exact amount of warnings
using a single option is also possible. Look at scripts help for more details about the options.

Exclude Matches With Regexes
----------------------------

In case you want a checker to exclude certain matches, you can configure
one or more regular expressions in the configuration file on a per-checker basis.
If a pattern of a regex to exclude is found in a match of the checker's regex, the checker
won't count that match. Add the regex(es) as a list of string values for the ``exclude`` key.
An example configuration for the sphinx checker is given below:

.. code-block:: json

    {
        "sphinx":{
            "enabled": true,
            "min": 0,
            "max": 0,
            "exclude": [
                "RemovedInSphinx\\d+Warning",
                "WARNING: toctree"
            ]
        }
    }

You can define regular expressions to exclude certain Polyspace results, i.e. specific rows of the TSV file,
when they match against the string that represents the row. This string is a concatenation of the values
of all cells in the row, separated by a tab character (`\t`).
Note: backslashes need to be escaped in JSON syntax.

.. code-block:: json

    {
        "polyspace": {
            "enabled": true,
            "cq_description_template": "$PRODUCT $family: $check",
            "exclude": [
                ".+\\tdummy_function\\(\\)\\tdummy_file_name\\.c\\t"
            ],
            "run-time check": [
                {
                    "color": "red",
                    "min": 0,
                    "max": 0
                }
            ]
        }
    }

Exclude Sphinx Deprecation Warnings
-----------------------------------

There is a special flag ``--exclude-sphinx-deprecation`` that lets the sphinx checker exclude
Sphinx deprecation warnings. These warnings match the following regular expression:
``RemovedInSphinx\\d+Warning``. Using this flag results in the same behavior as adding this
regex to the configuration file as value for the ``exclude`` key for the sphinx checker.

Store All Counted Warnings
--------------------------

Use `-o, --output <file_path>` to let the plugin write all counted warnings/failures as strings to a text file.
This can help you separate the warnings/failures that matter from those that are excluded or from irrelevant text that
may exist in the input file (or produced by the given command).

Code Quality Report
-------------------

Use ``-C, --code-quality`` to let the plugin generate `a Code Quality report`_ for GitLab CI. All counted
Sphinx, Doxygen, XMLRunner, Coverity and Polyspace warnings/errors/failures will be included. Other checker types are not yet supported by this feature. The report is
a JSON file that follows `the Code Climate spec`_. Define this file `as a codequality report artifact`_
of the CI job.

If a warning doesn't contain a path, ``"cq_default_path"`` from the `configuration file to pass options`_ will be used.
If not configured, ``.gitlab-ci.yml`` will be used as a fallback path.

You can customize the description with ``"cq_description_template"``, see `configuration file to pass options`_.
Its value should be a template for Python's |string.Template|_. The template has access to all environment variables,
e.g. ``$HOME``, and other variables that depend on the checker type:

Polyspace
  Any field of a Polyspace defect can be included by using the corresponding
  `column title <Exporting Polyspace Results_>`_ in lowercase as the variable name.
  The default template is ``Polyspace: $check``.

Coverity
  Named groups of the regular expression can be used as variables.
  Useful names are: `checker` and `classification`.
  The default template is ``Coverity: CID $cid: $checker``.

Other
  The template should contain ``$description``, which is the default.

The Polyspace checker generates the fingerprint (a unique identifier) for each row in the TSV file that is exported as finding.
Specific columns (``new``, ``status``, ``severity``, ``comment``, and ``key``) are excluded as they might contain transient information.
The remaining values in the row are hashed using a MD5 function to create the fingerprint.

=======================
Issues and New Features
=======================

In case you have any problems with usage of the plugin, please open an issue
on GitHub. Provide as many valid information as possible, as this will help us
to resolve Issues faster. We would also like to hear your suggestions about new
features which would help your Continuous Integration run better.

==========
Contribute
==========

There is a Contribution guide available if you would like to get involved in
development of the plugin. We encourage anyone to contribute to our repository.

.. |string.Template| replace:: ``string.Template``
.. _YAML: https://yaml.org/spec/1.2.2/
.. _a Code Quality report: https://docs.gitlab.com/ee/ci/testing/code_quality.html
.. _the Code Climate spec: https://docs.gitlab.com/ci/testing/code_quality/#code-quality-report-format
.. _as a codequality report artifact: https://docs.gitlab.com/ee/ci/yaml/artifacts_reports.html#artifactsreportscodequality
.. _string.Template: https://docs.python.org/3/library/string.html#string.Template.template

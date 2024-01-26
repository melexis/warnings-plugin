.. image:: https://img.shields.io/hexpm/l/plug.svg
    :target: http://www.apache.org/licenses/LICENSE-2.0
    :alt: Apache2 License

.. image:: https://github.com/melexis/warnings-plugin/actions/workflows/python-package.yml/badge.svg?branch=master
    :target: https://github.com/melexis/warnings-plugin/actions/workflows/python-package.yml
    :alt: Build status

.. image:: https://badge.fury.io/py/mlx.warnings.svg
    :target: https://badge.fury.io/py/mlx.warnings
    :alt: Pypi packaged release

.. image:: https://img.shields.io/badge/Documentation-published-brightgreen.svg
    :target: https://melexis.github.io/warnings-plugin/
    :alt: Documentation

.. image:: https://scan.coverity.com/projects/15266/badge.svg
    :target: https://scan.coverity.com/projects/melexis-warnings-plugin
    :alt: Coverity Scan Build Status

.. image:: https://codecov.io/gh/melexis/warnings-plugin/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/melexis/warnings-plugin
    :alt: Code Coverage

.. image:: https://codeclimate.com/github/melexis/warnings-plugin/badges/gpa.svg
    :target: https://codeclimate.com/github/melexis/warnings-plugin
    :alt: Code Climate Status

.. image:: https://codeclimate.com/github/melexis/warnings-plugin/badges/issue_count.svg
    :target: https://codeclimate.com/github/melexis/warnings-plugin
    :alt: Issue Count

.. image:: https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat
    :target: https://github.com/melexis/warnings-plugin/issues
    :alt: Contributions welcome

.. image:: https://bestpractices.coreinfrastructure.org/projects/4368/badge
    :target: https://bestpractices.coreinfrastructure.org/projects/4368
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
    mlx-warnings --sphinx --command <commandforsphinx>

    # explicitly as python module for log file
    python3 -m mlx.warnings --sphinx doc_log.txt
    python -m mlx.warnings --sphinx doc_log.txt
    # explicitly as python module
    python3 -m mlx.warnings --sphinx --command <commandforsphinx>
    python -m mlx.warnings --sphinx --command <commandforsphinx>


Parse for Doxygen Warnings
--------------------------

After you saved your Doxygen warnings to the file, you can parse it with
command:

.. code-block:: bash

    # command line log file
    mlx-warnings doc_log.txt --doxygen
    # command line command execution
    mlx-warnings --doxygen --command <commandfordoxygen>

    # explicitly as python module for log file
    python3 -m mlx.warnings --doxygen doc_log.txt
    python -m mlx.warnings --doxygen doc_log.txt
    # explicitly as python module
    python3 -m mlx.warnings --doxygen --command <commandfordoxygen>
    python -m mlx.warnings --doxygen --command <commandfordoxygen>


Parse for Coverity Defects
--------------------------

Coverity is a static analysis tool which has option to run desktop analysis
on your local changes and report the results back directly in the console.
You only need to list affected files and below example lists changed files
between your branch and master, which it then forwards to ``cov-run-desktop``:

.. code-block:: bash

    cov-run-desktop --text-output-style=oneline `git diff --name-only --ignore-submodules master`


You can pipe the results to logfile, which you pass to warnings-plugin, or you use
the ``--command`` argument and execute the ``cov-run-desktop`` through

.. code-block:: bash

    # command line log file
    mlx-warnings cov-run-desktop-output.txt --coverity
    # command line command execution
    mlx-warnings --coverity --command <commandforcoverity>

    # explicitly as python module for log file
    python3 -m mlx.warnings --coverity cov-run-desktop-output.txt
    python -m mlx.warnings --coverity cov-run-desktop-output.txt
    # explicitly as python module
    python3 -m mlx.warnings --coverity --command <commandforcoverity>
    python -m mlx.warnings --coverity --command <commandforcoverity>


Parse for JUnit Failures
------------------------

After you saved your JUnit XML output to the file, you can parse it with
command:

.. code-block:: bash

    # command line log file
    mlx-warnings junit_output.xml --junit
    # command line command execution
    mlx-warnings --junit --command <commandforjunit>

    # explicitly as python module for log file
    python3 -m mlx.warnings --junit junit_output.xml
    python -m mlx.warnings --junit junit_output.xml
    # explicitly as python module
    python3 -m mlx.warnings --junit --command <commandforjunit>
    python -m mlx.warnings --junit --command <commandforjunit>


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
    mlx-warnings --xmlrunner --command <commandforxmlrunner>

    # explicitly as python module for log file
    python3 -m mlx.warnings --xmlrunner xmlrunner_log.txt
    python -m mlx.warnings --xmlrunner xmlrunner_log.txt
    # explicitly as python module
    python3 -m mlx.warnings --xmlrunner --command <commandforxmlrunner>
    python -m mlx.warnings --xmlrunner --command <commandforxmlrunner>

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
`configuration file to pass options`_. If the setting ``"check_suite_names"``
is false, no error is raised when a suite name doesn't exist in the
input file. When this setting is missing, the default value ``true`` is used.

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
            "min": 0,
            "max": 0
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
    mlx-warnings --config path/to/config.json --command <commandforjunit>


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
Sphinx, Doxygen and XMLRunner will be included. Other checker types are not supported by this feature. The report is
a JSON file that implements `a subset of the Code Climate spec`_. Define this file `as a codequality report artifact`_
of the CI job.

If a warning doesn't contain a path, ``"cq_default_path"`` from the `configuration file to pass options`_ will be used.
If not configured, ``.gitlab-ci.yml`` will be used as a fallback path.

You can customize the description with ``"cq_description_template"``, see `configuration file to pass options`_.
Its value should be a template for Python's |string.Template|_. The template should contain ``$description`` and has
access to all environment variables, e.g. ``$HOME``.

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
.. _a subset of the Code Climate spec: https://docs.gitlab.com/ee/ci/testing/code_quality.html#implement-a-custom-tool
.. _as a codequality report artifact: https://docs.gitlab.com/ee/ci/yaml/artifacts_reports.html#artifactsreportscodequality
.. _string.Template: https://docs.python.org/3/library/string.html#string.Template.template

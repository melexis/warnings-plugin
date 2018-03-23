.. image:: https://img.shields.io/hexpm/l/plug.svg
    :target: http://www.apache.org/licenses/LICENSE-2.0
    :alt: Apache2 License

.. image:: https://travis-ci.org/melexis/warnings-plugin.svg?branch=master
    :target: https://travis-ci.org/melexis/warnings-plugin
    :alt: Build status

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

.. image:: https://requires.io/github/melexis/warnings-plugin/requirements.svg?branch=master
    :target: https://requires.io/github/melexis/warnings-plugin/requirements/?branch=master
    :alt: Requirements Status

.. image:: https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat
    :target: https://github.com/melexis/warnings-plugin/issues
    :alt: Contributions welcome


============================
Command line warnings-plugin
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

    # Python2
    pip2 install mlx.warnings

    # Python3
    pip3 install mlx.warnings

You can find more details in `Installation guide <docs/installation.rst>`_

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
Pipe example
------------

Below is one of the ways to redirect your stderr to stdout and save it inside
file.

.. code-block:: bash

    yourcommand 2>&1 | tee doc_log.txt

---------------
Command example
---------------

Below is the command example for the plugin (keep in mind that parse commands are
required).

.. code-block:: bash

    mlx-warnings --command <yourcommand>

---------------
Running command
---------------

There are few ways to run warnings plugin. If you are playing with Python on
your computer you want to use `virtualenv`. This will separate your packages
per project and there is less chance of some dependency hell. You can
initialize virtual environment in current directory by `virtualenv .` .

Melexis Warnings plugin can be called directly from shell/console using:

.. code-block:: bash

    mlx-warnings -h

It has also possibility to be called as module from `Python2` or `Python3`. In
that case command will look like:

.. code-block:: bash

    python -m mlx.warnings -h
    python3 -m mlx.warnings -h

Help prints all currently supported commands and their usages.

The command returns (shell $? variable):

- value 0 when the number of counted warnings is within the supplied minimum and maximum limits: ok,
- number of counted warnings (positive) when the counter number is not within those limit.

---------------------------
Simple Command line options
---------------------------

Plugin has two forms of passing the arguments to checkers. The command line
option which enables checkers and sets minimum and maximum to each checker
individually, or the configuration file option which provides more flexibility
and also traceability as it resides inside repository and provides option to
adjust minimum and maximum per individual checker.

Parse for Sphinx warnings
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


Parse for Doxygen warnings
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


Parse for JUnit failures
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


----------------------------------
Configuration file to pass options
----------------------------------

Beside command line, you can pass options through the configuration file.
Configuration file is in JSON format with a simple structure.

.. code-block:: json

    {
        "sphinx":{
    	    "enabled": true,
    	    "min": 0,
    	    "max": 0
        },
        "doxygen":{
    	    "enabled": false,
    	    "min": 0,
    	    "max": 0
        },
        "junit":{
    	    "enabled": false,
    	    "min": 0,
    	    "max": 0
        }
    }

First key is `checkername`, then it contains a boolean value for key `enabled`,
value for minimum number of warnings with key `min` and value for maximum
number of warnings with key `max`. This structure allows simple expansion.

To run the plugin with configuration file you simply pass `--config` flag with
path to configuration file

.. code-block:: bash

    # command line log file
    mlx-warnings --config pathtoconfig.json junit_output.xml
    # command line command execution
    mlx-warnings --config patchtoconfig.json --command <commandforjunit>


-------------
Other options
-------------

Since plugin is under active development there are new Features added fast.
Important options currently include setting maximum number of warnings or
minimum number of warnings, that are still acceptable to return 0 (success)
return code. Look at scripts help, for more details about the options.

=======================
Issues and new Features
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


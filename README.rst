.. image:: https://img.shields.io/hexpm/l/plug.svg
    :target: http://www.apache.org/licenses/LICENSE-2.0
    :alt: Apache2 License

.. image:: https://travis-ci.org/melexis/warnings-plugin.svg?branch=master
    :target: https://travis-ci.org/melexis/warnings-plugin
    :alt: Build status

.. image:: https://codecov.io/gh/melexis/warnings-plugin/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/melexis/warnings-plugin
    :alt: Code Coverage

.. image:: https://requires.io/github/melexis/warnings-plugin/requirements.svg?branch=master
    :target: https://requires.io/github/melexis/warnings-plugin/requirements/?branch=master
    :alt: Requirements Status


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

Since warnings plugin parses log messages (so far), you will need to redirect
your stderr to some text file. You can do that with shell pipes or with
command line arguments to command (if it supports outputting errors to file
instead of stderr). Be aware that some commands print warnings on stdout.

------------
Pipe example
------------

Below is one of the ways to redirect your stderr to stdout and save it inside
file.

.. code-block:: bash

    yourcommand 2>&1 | tee doc_log.txt


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

----------------------------
Parse for Sphinx warnings
----------------------------

After you saved your Sphinx warnings to the file, you can parse it with
command:

.. code-block:: bash

    # command line
    mlx-warnings doc_log.txt --sphinx
    # explicitly as python module
    python3 -m mlx.warnings doc_log.txt --sphinx
    python -m mlx.warnings doc_log.txt --sphinx


--------------------------
Parse for Doxygen warnings
--------------------------

After you saved your Doxygen warnings to the file, you can parse it with
command:

.. code-block:: bash

    # command line
    mlx-warnings doc_log.txt --doxygen
    # explicitly as python module
    python3 -m mlx.warnings doc_log.txt --doxygen
    python -m mlx.warnings doc_log.txt --doxygen


------------------------
Parse for JUnit failures
------------------------

After you saved your JUnit XML output to the file, you can parse it with
command:

.. code-block:: bash

    # command line
    mlx-warnings junit_output.xml --junit
    # explicitly as python module
    python3 -m mlx.warnings junit_output.xml --junit
    python -m mlx.warnings junit_output.xml --junit

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


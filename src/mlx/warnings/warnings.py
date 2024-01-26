#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import errno
import glob
import json
import os
import subprocess
import sys
from importlib.metadata import distribution
from pathlib import Path
from string import Template

from ruamel.yaml import YAML

from .exceptions import WarningsConfigError
from .junit_checker import JUnitChecker
from .regex_checker import CoverityChecker, DoxyChecker, SphinxChecker, XMLRunnerChecker
from .robot_checker import RobotChecker

__version__ = distribution('mlx.warnings').version


def substitute_envvar(checker_config, keys):
    """Modifies configuration for checker in-place, resolving any environment variables for ``keys``

    Args:
        checker_config (dict): Configuration for a specific WarningsChecker
        keys (set): Set of keys to process the value of

    Raises:
        WarningsConfigError: Failed to find an environment variable
    """
    for key in keys:
        if key in checker_config and isinstance(checker_config[key], str):
            template_obj = Template(checker_config[key])
            try:
                checker_config[key] = template_obj.substitute(os.environ)
            except KeyError as err:
                raise WarningsConfigError(f"Failed to find environment variable {err} for configuration value {key!r}")\
                    from None


class WarningsPlugin:

    def __init__(self, verbose=False, config_file=None, cq_enabled=False):
        '''
        Function for initializing the parsers

        Args:
            verbose (bool): optional - enable verbose logging
            config_file (Path): optional - configuration file with setup
            cq_enabled (bool): optional - enable generation of Code Quality report
        '''
        self.activated_checkers = {}
        self.verbose = verbose
        self.cq_enabled = cq_enabled
        self.public_checkers = [SphinxChecker(self.verbose), DoxyChecker(self.verbose), JUnitChecker(self.verbose),
                                XMLRunnerChecker(self.verbose), CoverityChecker(self.verbose),
                                RobotChecker(self.verbose)]

        if config_file:
            with open(config_file, 'r', encoding='utf-8') as open_file:
                if config_file.suffix.lower().startswith('.y'):
                    config = YAML().load(open_file)
                else:
                    config = json.load(open_file)
            self.config_parser(config)

        self.warn_min = 0
        self.warn_max = 0
        self.count = 0
        self.printout = False

    def activate_checker(self, checker):
        '''
        Activate additional checkers after initialization

        Args:
            checker (WarningsChecker): checker object
        '''
        checker.cq_enabled = self.cq_enabled and checker.name in ('doxygen', 'sphinx', 'xmlrunner')
        self.activated_checkers[checker.name] = checker

    def activate_checker_name(self, name):
        '''
        Activates checker by name

        Args:
            name (str): checker name

        Returns:
            WarningsChecker: activated checker object, or None when no checker with the given name exists
        '''
        for checker in self.public_checkers:
            if checker.name == name:
                self.activate_checker(checker)
                return checker
        else:
            print("Checker %s does not exist" % name)

    def get_checker(self, name):
        ''' Get checker by name

        Args:
            name (str): checker name
        Return:
            checker object (WarningsChecker)
        '''
        return self.activated_checkers[name]

    def check(self, content):
        '''
        Function for counting the number of warnings in a specific text

        Args:
            content (str): The text to parse
        '''
        if self.printout:
            print(content)

        if not self.activated_checkers:
            print("No checkers activated. Please use activate_checker function")
        else:
            for checker in self.activated_checkers.values():
                checker.check(content)

    def set_maximum(self, maximum):
        ''' Setter function for the maximum amount of warnings

        Args:
            maximum (int): maximum amount of warnings allowed
        '''
        for checker in self.activated_checkers.values():
            checker.set_maximum(maximum)

    def set_minimum(self, minimum):
        ''' Setter function for the minimum amount of warnings

        Args:
            minimum (int): minimum amount of warnings allowed
        '''
        for checker in self.activated_checkers.values():
            checker.set_minimum(minimum)

    def return_count(self, name=None):
        ''' Getter function for the amount of found warnings

        If the name parameter is set, this function will return the amount of
        warnings found by that checker. If not, the function will return the sum
        of the warnings found by all registered checkers.

        Args:
            name (WarningsChecker): The checker for which to return the amount of warnings (if set)

        Returns:
            int: Amount of found warnings
        '''
        self.count = 0
        if name is None:
            for checker in self.activated_checkers.values():
                self.count += checker.return_count()
        else:
            self.count = self.activated_checkers[name].return_count()
        return self.count

    def return_check_limits(self, name=None):
        ''' Function for determining the return value of the script

        If the name parameter is set, this function will check (and return) the
        return value of that checker. If not, this function checks whether the
        warnings for each registered checker are within the configured limits.

        Args:
            name (WarningsChecker): The checker for which to check the return value

        Return:
            int: 0 if the amount of warnings is within limits, the count of warnings otherwise
                (or 1 in case of a count of 0 warnings)
        '''
        if name is None:
            for checker in self.activated_checkers.values():
                retval = checker.return_check_limits()
                if retval:
                    return retval
        else:
            return self.activated_checkers[name].return_check_limits()

        return 0

    def toggle_printout(self, printout):
        ''' Toggle printout of all the parsed content

        Useful for command input where we want to print content as well

        Args:
            printout (bool): True enables the printout, False provides more silent mode
        '''
        self.printout = printout

    def config_parser(self, config):
        ''' Parsing configuration dict extracted by previously opened JSON file

        Args:
            config (dict): Content of configuration file
        '''
        # activate checker
        for checker in self.public_checkers:
            try:
                checker_config = config[checker.name]
                if bool(checker_config['enabled']):
                    substitute_envvar(checker_config, {'min', 'max'})
                    self.activate_checker(checker)
                    checker.parse_config(checker_config)
                    print("Config parsing for {name} completed".format(name=checker.name))
            except KeyError as err:
                print("Incomplete config. Missing: {key}".format(key=err))

    def write_counted_warnings(self, out_file):
        ''' Writes counted warnings to the given file

        Args:
            out_file (str): Location for the output file
        '''
        with open(out_file, 'w', encoding='utf-8', newline='\n') as open_file:
            for checker in self.activated_checkers.values():
                open_file.write("\n".join(checker.counted_warnings) + "\n")

    def write_code_quality_report(self, out_file):
        ''' Generates the Code Quality report artifact as a JSON file that implements a subset of the Code Climate spec

        Args:
            out_file (str): Location for the output file
        '''
        results = []
        for checker in self.activated_checkers.values():
            results.extend(checker.cq_findings)
        content = json.dumps(results, indent=4, sort_keys=False)
        with open(out_file, 'w', encoding='utf-8', newline='\n') as open_file:
            open_file.write(f"{content}\n")


def warnings_wrapper(args):
    parser = argparse.ArgumentParser(prog='mlx-warnings')
    group1 = parser.add_argument_group('Configuration command line options')
    group1.add_argument('--coverity', dest='coverity', action='store_true')
    group1.add_argument('-d', '--doxygen', dest='doxygen', action='store_true')
    group1.add_argument('-j', '--junit', dest='junit', action='store_true')
    group1.add_argument('-r', '--robot', dest='robot', action='store_true')
    group1.add_argument('-s', '--sphinx', dest='sphinx', action='store_true')
    group1.add_argument('-x', '--xmlrunner', dest='xmlrunner', action='store_true')
    group1.add_argument('--name', default='',
                        help='Name of the Robot Framework test suite to check results of')
    group1.add_argument('-m', '--maxwarnings', '--max-warnings', type=int, default=0,
                        help='Maximum amount of warnings accepted')
    group1.add_argument('--minwarnings', '--min-warnings', type=int, default=0,
                        help='Minimum amount of warnings accepted')
    group1.add_argument('--exact-warnings', type=int, default=0,
                        help='Exact amount of warnings expected')
    group2 = parser.add_argument_group('Configuration file with options')
    group2.add_argument('--config', dest='configfile', action='store', required=False, type=Path,
                        help='Config file in JSON format provides toggle of checkers and their limits')
    group2.add_argument('--include-sphinx-deprecation', dest='include_sphinx_deprecation', action='store_true',
                        help="Sphinx checker will include warnings matching (RemovedInSphinx\\d+Warning) regex")
    parser.add_argument('-o', '--output',
                        help='Output file that contains all counted warnings')
    parser.add_argument('-C', '--code-quality',
                        help='Output Code Quality report artifact for GitLab CI')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true')
    parser.add_argument('--command', dest='command', action='store_true',
                        help='Treat program arguments as command to execute to obtain data')
    parser.add_argument('--ignore-retval', dest='ignore', action='store_true',
                        help='Ignore return value of the executed command')
    parser.add_argument('--version', action='version', version='%(prog)s {version}'.format(version=__version__))
    parser.add_argument('logfile', nargs='+', help='Logfile (or command) that might contain warnings')
    parser.add_argument('flags', nargs=argparse.REMAINDER,
                        help='Possible not-used flags from above are considered as command flags')

    args = parser.parse_args(args)
    code_quality_enabled = bool(args.code_quality)

    # Read config file
    if args.configfile is not None:
        checker_flags = args.sphinx or args.doxygen or args.junit or args.coverity or args.xmlrunner or args.robot
        warning_args = args.maxwarnings or args.minwarnings or args.exact_warnings
        if checker_flags or warning_args:
            print("Configfile cannot be provided with other arguments")
            sys.exit(2)
        warnings = WarningsPlugin(verbose=args.verbose, config_file=args.configfile, cq_enabled=code_quality_enabled)
    else:
        warnings = WarningsPlugin(verbose=args.verbose, cq_enabled=code_quality_enabled)
        if args.sphinx:
            warnings.activate_checker_name('sphinx')
        if args.doxygen:
            warnings.activate_checker_name('doxygen')
        if args.junit:
            warnings.activate_checker_name('junit')
        if args.xmlrunner:
            warnings.activate_checker_name('xmlrunner')
        if args.coverity:
            warnings.activate_checker_name('coverity')
        if args.robot:
            robot_checker = warnings.activate_checker_name('robot')
            robot_checker.parse_config({
                'suites': [{'name': args.name, 'min': 0, 'max': 0}],
                'check_suite_names': True,
            })
        if args.exact_warnings:
            if args.maxwarnings | args.minwarnings:
                print("expected-warnings cannot be provided with maxwarnings or minwarnings")
                sys.exit(2)
            warnings.set_maximum(args.exact_warnings)
            warnings.set_minimum(args.exact_warnings)
        else:
            warnings.set_maximum(args.maxwarnings)
            warnings.set_minimum(args.minwarnings)

    if args.include_sphinx_deprecation and 'sphinx' in warnings.activated_checkers.keys():
        warnings.get_checker('sphinx').include_sphinx_deprecation()

    if args.command:
        cmd = args.logfile
        if args.flags:
            cmd.extend(args.flags)
        warnings.toggle_printout(True)
        retval = warnings_command(warnings, cmd)

        if (not args.ignore) and (retval != 0):
            return retval
    else:
        if args.flags:
            print(f"WARNING: Some keyword arguments have been ignored because they followed positional arguments: "
                  f"{' '.join(args.flags)!r}")
        retval = warnings_logfile(warnings, args.logfile)
        if retval != 0:
            return retval

    warnings.return_count()
    if args.output:
        warnings.write_counted_warnings(args.output)
    if args.code_quality:
        warnings.write_code_quality_report(args.code_quality)
    return warnings.return_check_limits()


def warnings_command(warnings, cmd):
    ''' Execute command to obtain input for parsing for warnings

    Usually log files are output of the commands. To avoid this additional step
    this function runs a command instead and parses the stderr and stdout of the
    command for warnings.

    Args:
        warnings (WarningsPlugin): Object for warnings where errors should be logged
        cmd (list): List of commands (str), which should be executed to obtain input for parsing

    Return:
        int: Return value of executed command(s)

    Raises:
        OSError: When program is not installed.
    '''
    try:
        print("Executing: ", end='')
        print(cmd)
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                stdin=subprocess.PIPE, bufsize=1, universal_newlines=True)
        out, err = proc.communicate()
        # Check stdout
        if out:
            try:
                warnings.check(out.decode(encoding="utf-8"))
            except AttributeError:
                warnings.check(out)
        # Check stderr
        if err:
            try:
                warnings.check(err.decode(encoding="utf-8"))
            except AttributeError:
                warnings.check(err)
        return proc.returncode
    except OSError as err:
        if err.errno == errno.ENOENT:
            print("It seems like program " + str(cmd) + " is not installed.")
        raise


def warnings_logfile(warnings, log):
    ''' Parse logfile for warnings

    Args:
        warnings (WarningsPlugin): Object for warnings where errors should be logged
        log: Logfile for parsing

    Return:
        0: Log files existed and are parsed successfully
        1: Log files did not exist
    '''
    # args.logfile doesn't necessarily contain wildcards, but just to be safe, we
    # assume it does, and try to expand them.
    # This mechanism is put in place to allow wildcards to be passed on even when
    # executing the script on windows (in that case there is no shell expansion of wildcards)
    # so that the script can be used in the exact same way even when moving from one
    # OS to another.
    for file_wildcard in log:
        if glob.glob(file_wildcard):
            for logfile in glob.glob(file_wildcard):
                with open(logfile, 'r') as loghandle:
                    warnings.check(loghandle.read())
        else:
            print("FILE: %s does not exist" % file_wildcard)
            return 1

    return 0


def main():
    sys.exit(warnings_wrapper(sys.argv[1:]))


if __name__ == '__main__':
    main()

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import argparse
import json
import os
import pkg_resources
import subprocess
import sys
import glob
from mlx.warnings_checker import SphinxChecker, DoxyChecker, JUnitChecker, XMLRunnerChecker
from setuptools_scm import get_version

__version__ = get_version()


class WarningsPlugin:

    def __init__(self, verbose = False, configfile= None):
        '''
        Function for initializing the parsers

        Args:
            verbose (bool, optional):           enable verbose logging
            configfile (filename, optional):    configuration file with setup
        '''
        self.checkerList = {}
        self.verbose = verbose
        self.publicCheckers = [SphinxChecker(self.verbose), DoxyChecker(self.verbose), JUnitChecker(self.verbose),
                               XMLRunnerChecker(self.verbose)]

        if configfile is not None:
            with open(configfile, 'r') as f:
                config = json.load(f)
            self.config_parser_json(config)

        self.warn_min = 0
        self.warn_max = 0
        self.count = 0
        self.printout = False

    def activate_checker(self, checker):
        '''
        Activate additional checkers after initialization

        Args:
            checker (WarningsChecker):         checker object
        '''
        checker.reset()
        self.checkerList[checker.name] = checker

    def activate_checker_name(self, name):
        '''
        Activate checker by name

        Args:
            name (str): checker name
        '''
        for checker in self.publicCheckers:
            if checker.name == name:
                self.activate_checker(checker)
                break
        else:
            print("Checker %s does not exist" % name)

    def get_checker(self, name):
        ''' Get checker by name

        Args:
            name (str): checker name
        Return:
            checker object (WarningsChecker)
        '''
        return self.checkerList[name]

    def check(self, content):
        '''
        Function for counting the number of warnings in a specific text

        Args:
            content (str): The text to parse
        '''
        if self.printout:
            print(content)

        if len(self.checkerList) == 0:
            print("No checkers activated. Please use activate_checker function")
        else:
            for name, checker in self.checkerList.items():
                checker.check(content)

    def set_maximum(self, maximum):
        ''' Setter function for the maximum amount of warnings

        Args:
            maximum (int): maximum amount of warnings allowed
        '''
        for name, checker in self.checkerList.items():
            checker.set_maximum(maximum)

    def set_minimum(self, minimum):
        ''' Setter function for the minimum amount of warnings

        Args:
            minimum (int): minimum amount of warnings allowed
        '''
        for name, checker in self.checkerList.items():
            checker.set_minimum(minimum)

    def return_count(self, name = None):
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
            for name, checker in self.checkerList.items():
                self.count += checker.return_count()
        else:
            self.count = self.checkerList[name].return_count()
        return self.count

    def return_check_limits(self, name = None):
        ''' Function for determining the return value of the script

        If the name parameter is set, this function will check (and return) the
        return value of that checker. If not, this function checks whether the
        warnings for each registred checker are within the configured limits.

        Args:
            name (WarningsChecker): The checker for which to check the return value

        Return:
            int: 0 if the amount warnings are within limits otherwise 1
        '''
        if name is None:
            for name, checker in self.checkerList.items():
                retval = checker.return_check_limits()
                if retval != 0:
                    return retval
        else:
            return self.checkerList[name].return_check_limits()

        return 0

    def toggle_printout(self, printout):
        ''' Toggle printout of all the parsed content

        Useful for command input where we want to print content as well

        Args:
            printout: True enables the printout, False provides more silent mode
        '''
        self.printout = printout

    def config_parser_json(self, config):
        ''' Parsing configuration dict extracted by previously opened json file

        Args:
            config (dict): json dump of the configuration
        '''
        # activate checker
        for checker in self.publicCheckers:
            try:
                if bool(config[checker.name]['enabled']):
                    self.activate_checker(checker)
                    self.get_checker(checker.name).set_maximum(int(config[checker.name]['max']))
                    self.get_checker(checker.name).set_minimum(int(config[checker.name]['min']))
                    print("Config parsing for {name} completed".format(name=checker.name))
            except KeyError as e:
                print("Incomplete config. Missing: {key}".format(key=e))


def warnings_wrapper(args):
    parser = argparse.ArgumentParser(prog='mlx-warnings')
    group1 = parser.add_argument_group('Configuration command line options')
    group1.add_argument('-d', '--doxygen', dest='doxygen', action='store_true')
    group1.add_argument('-s', '--sphinx', dest='sphinx', action='store_true')
    group1.add_argument('-j', '--junit', dest='junit', action='store_true')
    group1.add_argument('-x', '--xmlrunner', dest='xmlrunner', action='store_true')
    group1.add_argument('-m', '--maxwarnings', type=int, required=False, default=0,
                        help='Maximum amount of warnings accepted')
    group1.add_argument('--minwarnings', type=int, required=False, default=0,
                        help='Minimum amount of warnings accepted')
    group2 = parser.add_argument_group('Configuration file with options')
    group2.add_argument('--config', dest='configfile', action='store', required=False, help='Config file in JSON format provides toggle of checkers and their limits')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true')
    parser.add_argument('--command', dest='command', action='store_true',
                        help='Treat program arguments as command to execute to obtain data')
    parser.add_argument('--ignore-retval', dest='ignore', action='store_true',
                        help='Ignore return value of the executed command')
    parser.add_argument('--version', action='version', version='%(prog)s {version}'.format(version=pkg_resources.require('mlx.warnings')[0].version))
    parser.add_argument('logfile', nargs='+', help='Logfile (or command) that might contain warnings')
    parser.add_argument('flags', nargs=argparse.REMAINDER, help='Possible not-used flags from above are considered as command flags')

    args = parser.parse_args(args)

    # Read config file
    if args.configfile is not None:
        if args.sphinx or args.doxygen or args.junit or (args.maxwarnings != 0) or (args.minwarnings != 0):
            print("Configfile cannot be provided with other arguments")
            sys.exit(2)
        warnings = WarningsPlugin(verbose=args.verbose, configfile=args.configfile)
    else:
        warnings = WarningsPlugin(verbose=args.verbose)
        if args.sphinx:
            warnings.activate_checker_name('sphinx')
        if args.doxygen:
            warnings.activate_checker_name('doxygen')
        if args.junit:
            warnings.activate_checker_name('junit')
        if args.xmlrunner:
            warnings.activate_checker_name('xmlrunner')
        warnings.set_maximum(args.maxwarnings)
        warnings.set_minimum(args.minwarnings)

    if args.command:
        cmd = args.logfile
        if args.flags:
            cmd.extend(args.flags)
        warnings.toggle_printout(True)
        retval = warnings_command(warnings, cmd)

        if (not args.ignore) and (retval != 0):
            return retval
    else:
        retval = warnings_logfile(warnings, args.logfile)
        if retval != 0:
            return retval

    warnings.return_count()
    return warnings.return_check_limits()


def warnings_command(warnings, cmd):
    ''' Execute command to obtain input for parsing for warnings

    Usually log files are output of the commands. To avoid this additional step
    this function runs a command instead and parses the stderr and stdout of the
    command for warnings.

    Args:
        warnings (WarningsPlugin): Object for warnings where errors should be logged
        cmd: Command list, which should be executed to obtain input for parsing
        ignore: Flag to ignore return value of the command

    Return:
        retval: Return value of executed command

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
            except AttributeError as e:
                warnings.check(out)
        # Check stderr
        if err:
            try:
                warnings.check(err.decode(encoding="utf-8"))
            except AttributeError as e:
                warnings.check(err)
        return proc.returncode
    except OSError as e:
        if e.errno == os.errno.ENOENT:
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


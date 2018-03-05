#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import argparse
import os
import pkg_resources
import re
import subprocess
import sys
import abc
from junitparser import JUnitXml, Failure, Error
import glob
from setuptools_scm import get_version

DOXYGEN_WARNING_REGEX = r"(?:((?:[/.]|[A-Za-z]).+?):(-?\d+):\s*([Ww]arning|[Ee]rror)|<.+>:-?\d+(?::\s*([Ww]arning|[Ee]rror))?): (.+(?:(?!\s*(?:[Nn]otice|[Ww]arning|[Ee]rror): )[^/<\n][^:\n][^/\n].+)*)|\s*([Nn]otice|[Ww]arning|[Ee]rror): (.+)\n?"
doxy_pattern = re.compile(DOXYGEN_WARNING_REGEX)

SPHINX_WARNING_REGEX = r"(.+?:(?:\d+|None)?):?\s*(DEBUG|INFO|WARNING|ERROR|SEVERE):\s*(.+)\n?"
sphinx_pattern = re.compile(SPHINX_WARNING_REGEX)

__version__ = get_version()


class WarningsChecker(object):
    name = 'checker'

    def __init__(self, verbose=False):
        ''' Constructor

        Args:
            name (str): Name of the checker
            verbose (bool): Enable/disable verbose logging
        '''
        self.verbose = verbose
        self.reset()

    def reset(self):
        ''' Reset function (resets min, max and counter values) '''
        self.count = 0
        self.warn_min = 0
        self.warn_max = 0

    @abc.abstractmethod
    def check(self, content):
        '''
        Function for counting the number of warnings in a specific text

        Args:
            content (str): The content to parse
        '''
        return

    def set_maximum(self, maximum):
        ''' Setter function for the maximum amount of warnings

        Args:
            maximum (int): maximum amount of warnings allowed

        Raises:
            ValueError: Invalid argument (min limit higher than max limit)
        '''
        if self.warn_min == 0:
            self.warn_max = maximum
        elif self.warn_min > maximum:
            raise ValueError("Invalid argument: mininum limit ({min}) is higher than maximum limit ({max}). Cannot enter {value}". format(min=self.warn_min, max=self.warn_max, value=maximum))
        else:
            self.warn_max = maximum

    def get_maximum(self):
        ''' Getter function for the maximum amount of warnings

        Returns:
            int: Maximum amount of warnings
        '''
        return self.warn_max

    def set_minimum(self, minimum):
        ''' Setter function for the minimum amount of warnings

        Args:
            minimum (int): minimum amount of warnings allowed

        Raises:
            ValueError: Invalid argument (min limit higher than max limit)
        '''
        if minimum > self.warn_max:
            raise ValueError("Invalid argument: mininum limit ({min}) is higher than maximum limit ({max}). Cannot enter {value}". format(min=self.warn_min, max=self.warn_max, value=minimum))
        else:
            self.warn_min = minimum

    def get_minimum(self):
        ''' Getter function for the minimum amount of warnings

        Returns:
            int: Minimum amount of warnings
        '''
        return self.warn_min

    def return_count(self):
        ''' Getter function for the amount of warnings found

        Returns:
            int: Number of warnings found
        '''
        print("{count} {name} warnings found".format(count=self.count, name=self.name))
        return self.count

    def return_check_limits(self):
        ''' Function for checking whether the warning count is within the configured limits

        Returns:
            int: 0 if the amount of warnings is within limits. the count of warnings otherwise
        '''
        if self.count > self.warn_max:
            print("Number of warnings ({count}) is higher than the maximum limit ({max}). Returning error code 1.".format(count=self.count, max=self.warn_max))
            return self.count
        elif self.count < self.warn_min:
            print("Number of warnings ({count}) is lower than the minimum limit ({min}). Returning error code 1.".format(count=self.count, min=self.warn_min))
            return self.count
        else:
            print("Number of warnings ({count}) is between limits {min} and {max}. Well done.".format(count=self.count, min=self.warn_min, max=self.warn_max))
            return 0


class RegexChecker(WarningsChecker):
    name = 'regex'
    pattern = None

    def __init__(self, verbose=False):
        ''' Constructor

        Args:
            name (str): Name of the checker
            pattern (str): Regular expression used by the checker in order to find warnings
        '''
        super(RegexChecker, self).__init__(verbose=verbose)

    def check(self, content):
        '''
        Function for counting the number of warnings in a specific text

        Args:
            content (str): The content to parse
        '''
        matches = re.finditer(self.pattern, content)
        for match in matches:
            self.count += 1
            if self.verbose:
                print(match.group(0).strip())


class SphinxChecker(RegexChecker):
    name = 'sphinx'
    pattern = sphinx_pattern


class DoxyChecker(RegexChecker):
    name = 'doxygen'
    pattern = doxy_pattern


class JUnitChecker(WarningsChecker):
    name = 'junit'

    def __init__(self, verbose=False):
        ''' Constructor

        Args:
            verbose (bool): Enable/disable verbose logging
        '''
        super(JUnitChecker, self).__init__(verbose=verbose)

    def check(self, content):
        '''
        Function for counting the number of JUnit failures in a specific text

        Args:
            content (str): The content to parse
        '''
        result = JUnitXml.fromstring(content.encode('utf-8'))
        if self.verbose:
            for suite in result:
                for testcase in filter(lambda testcase: isinstance(testcase.result, (Failure, Error)), suite):
                    print('{classname}.{testname}'.format(classname=testcase.classname,
                                                          testname=testcase.name))
        result.update_statistics()
        self.count += result.errors + result.failures


class WarningsPlugin:

    def __init__(self, sphinx = False, doxygen = False, junit = False, verbose = False):
        '''
        Function for initializing the parsers

        Args:
            sphinx (bool, optional):    enable sphinx parser
            doxygen (bool, optional):   enable doxygen parser
            junit (bool, optional):     enable junit parser
            verbose (bool, optional):   enable verbose logging
        '''
        self.checkerList = {}
        self.verbose = verbose
        if sphinx:
            self.activate_checker(SphinxChecker(self.verbose))
        if doxygen:
            self.activate_checker(DoxyChecker(self.verbose))
        if junit:
            self.activate_checker(JUnitChecker(self.verbose))

        self.warn_min = 0
        self.warn_max = 0
        self.count = 0

    def activate_checker(self, checker):
        '''
        Activate additional checkers after initialization

        Args:
            checker (WarningsChecker):         checker object
        '''
        checker.reset()
        self.checkerList[checker.name] = checker

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


def warnings_wrapper(args):
    parser = argparse.ArgumentParser(prog='mlx-warnings')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-d', '--doxygen', dest='doxygen', action='store_true')
    group.add_argument('-s', '--sphinx', dest='sphinx', action='store_true')
    group.add_argument('-j', '--junit', dest='junit', action='store_true')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true')
    parser.add_argument('--command', dest='command', action='store_true',
                        help='Treat program arguments as command to execute to obtain data')
    parser.add_argument('-m', '--maxwarnings', type=int, required=False, default=0,
                        help='Maximum amount of warnings accepted')
    parser.add_argument('--minwarnings', type=int, required=False, default=0,
                        help='Minimum amount of warnings accepted')
    parser.add_argument('--version', action='version', version='%(prog)s {version}'.format(version=pkg_resources.require('mlx.warnings')[0].version))

    parser.add_argument('logfile', nargs='+', help='Logfile (or command) that might contain warnings')
    parser.add_argument('flags', nargs=argparse.REMAINDER, help='Possible not-used flags from above are considered as command flags')

    args = parser.parse_args(args)

    warnings = WarningsPlugin(sphinx=args.sphinx, doxygen=args.doxygen, junit=args.junit, verbose=args.verbose)
    warnings.set_maximum(args.maxwarnings)
    warnings.set_minimum(args.minwarnings)

    if args.command:
        cmd = args.logfile
        if args.flags:
            cmd.extend(args.flags)
        warnings_command(warnings, cmd)
    else:
        warnings_logfile(warnings, args.logfile)

    warnings.return_count()
    return warnings.return_check_limits()


def warnings_command(warnings, cmd):
    try:
        print("Executing: ", end='')
        print(cmd)
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                stdin=subprocess.PIPE, bufsize=1, universal_newlines=True)
        out, err = proc.communicate()
        # Check stdout
        if out:
            try:
                print(out.decode(encoding="utf-8"))
                warnings.check(out.decode(encoding="utf-8"))
            except AttributeError as e:
                warnings.check(out)
                print(out)
        # Check stderr
        if err:
            try:
                warnings.check(err.decode(encoding="utf-8"))
                print(err.decode(encoding="utf-8"), file=sys.stderr)
            except AttributeError as e:
                warnings.check(err)
                print(err, file=sys.stderr)
    except OSError as e:
        if e.errno == os.errno.ENOENT:
            print("It seems like program " + str(cmd) + " is not installed.")
        raise


def warnings_logfile(warnings, log):
    # args.logfile doesn't necessarily contain wildcards, but just to be safe, we
    # assume it does, and try to expand them.
    # This mechanism is put in place to allow wildcards to be passed on even when
    # executing the script on windows (in that case there is no shell expansion of wildcards)
    # so that the script can be used in the exact same way even when moving from one
    # OS to another.
    for file_wildcard in log:
        for logfile in glob.glob(file_wildcard):
            with open(logfile, 'r') as loghandle:
                warnings.check(loghandle.read())


def main():
    sys.exit(warnings_wrapper(sys.argv[1:]))


if __name__ == '__main__':
    main()


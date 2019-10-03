#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import abc
import re
from xml.etree.ElementTree import ParseError

from junitparser import Error, Failure, JUnitXml

DOXYGEN_WARNING_REGEX = r"(?:((?:[/.]|[A-Za-z]).+?):(-?\d+):\s*([Ww]arning|[Ee]rror)|<.+>:-?\d+(?::\s*([Ww]arning|[Ee]rror))?): ((?!notes).+(?:(?!\s*(?:[Nn]otice|[Ww]arning|[Ee]rror): )[^/<\n][^:\n][^/\n].+)*)|\s*(\b[Nn]otice|\b[Ww]arning|\b[Ee]rror): (?!notes)(.+)\n?"
doxy_pattern = re.compile(DOXYGEN_WARNING_REGEX)

SPHINX_WARNING_REGEX = r"(?m)^(?:(.+?:(?:\d+|None)?):?\s*)?(DEBUG|INFO|WARNING|ERROR|SEVERE|(?:\w+Sphinx\d+Warning)):\s*(.+)$"
sphinx_pattern = re.compile(SPHINX_WARNING_REGEX)

PYTHON_XMLRUNNER_REGEX = r"(\s*(ERROR|FAILED) (\[\d+.\d\d\ds\]: \s*(.+)))\n?"
xmlrunner_pattern = re.compile(PYTHON_XMLRUNNER_REGEX)

COVERITY_WARNING_REGEX = r"(?:((?:[/.]|[A-Za-z]).+?):(-?\d+):) (CID) \d+ \(#(?P<curr>\d+) of (?P<max>\d+)\): (?P<checker>.+)\): (?P<classification>\w+), *(.+)\n?"
coverity_pattern = re.compile(COVERITY_WARNING_REGEX)


class WarningsChecker:
    name = 'checker'

    def __init__(self, verbose=False):
        ''' Constructor

        Args:
            name (str): Name of the checker
            verbose (bool): Enable/disable verbose logging
        '''
        self.verbose = verbose
        self.reset()
        self.exclude_patterns = []

    def reset(self):
        ''' Reset function (resets min, max and counter values) '''
        self.count = 0
        self.warn_min = 0
        self.warn_max = 0

    @abc.abstractmethod
    def check(self, content):
        ''' Function for counting the number of warnings in a specific text

        Args:
            content (str): The content to parse
        '''
        return

    def add_exclude_patterns(self, exclude_regexes):
        ''' Abstract setter function for the exclude patterns list[re.Pattern]

        Args:
            exclude_regexes (list|None): List of regexes to ignore certain matched warning messages

        Raises:
            Exception: Feature of regexes to exclude warnings is only configurable for RegexChecker classes
        '''
        if exclude_regexes:
            raise Exception("Feature of regexes to exclude warnings is not configurable for the {}."
                            .format(self.__class__.__name__))

    def set_maximum(self, maximum):
        ''' Setter function for the maximum amount of warnings

        Args:
            maximum (int): maximum amount of warnings allowed

        Raises:
            ValueError: Invalid argument (min limit higher than max limit)
        '''
        if self.warn_min > maximum:
            raise ValueError("Invalid argument: mininum limit ({0.warn_min}) is higher than maximum limit "
                             "({0.warn_max}). Cannot enter {value}". format(self, value=maximum))
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
            raise ValueError("Invalid argument: mininum limit ({0.warn_min}) is higher than maximum limit "
                             "({0.warn_max}). Cannot enter {value}".format(self, value=minimum))
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
        print("{0.count} {0.name} warnings found".format(self))
        return self.count

    def return_check_limits(self):
        ''' Function for checking whether the warning count is within the configured limits

        Returns:
            int: 0 if the amount of warnings is within limits. the count of warnings otherwise
        '''
        if self.count > self.warn_max:
            print("Number of warnings ({0.count}) is higher than the maximum limit ({0.warn_max}). "
                  "Returning error code 1.".format(self))
            return self.count
        if self.count < self.warn_min:
            print("Number of warnings ({0.count}) is lower than the minimum limit ({0.warn_min}). "
                  "Returning error code 1.".format(self))
            return self.count
        print("Number of warnings ({0.count}) is between limits {0.warn_min} and {0.warn_max}. Well done.".format(self))
        return 0

    def print_when_verbose(self, message):
        ''' Prints message only when verbose mode is enabled.

        Args:
            message (str): Message to conditionally print
        '''
        if self.verbose:
            print(message)


class RegexChecker(WarningsChecker):
    name = 'regex'
    pattern = None

    def add_exclude_patterns(self, exclude_regexes):
        ''' Setter function for the exclude patterns list[re.Pattern]

        Args:
            exclude_regexes (list|None): List of regexes to ignore certain matched warning messages
        '''
        if exclude_regexes:
            if not isinstance(exclude_regexes, list):
                raise TypeError("Excpected a list value for exclude key in configuration file; got {}"
                                .format(exclude_regexes.__class__.__name__))
            for regex in exclude_regexes:
                self.exclude_patterns.append(re.compile(regex))

    def check(self, content):
        ''' Function for counting the number of warnings in a specific text

        Args:
            content (str): The content to parse
        '''
        matches = re.finditer(self.pattern, content)
        for match in matches:
            match_string = match.group(0).strip()
            if self._is_excluded(match_string):
                continue
            self.count += 1
            self.print_when_verbose(match_string)

    def _is_excluded(self, content):
        ''' Checks if the specific text must be excluded based on the configured regexes for exclusion.

        Args:
            content (str): The content to parse

        Returns:
            bool: True for exclusion, False for inclusion
        '''
        for pattern in self.exclude_patterns:
            if pattern.search(content):
                self.print_when_verbose("Excluded {!r} because of configured regex {!r}"
                                        .format(content, pattern.pattern))
                return True
        return False


class SphinxChecker(RegexChecker):
    name = 'sphinx'
    pattern = sphinx_pattern
    sphinx_deprecation_regex = "RemovedInSphinx\\d+Warning"

    def exclude_sphinx_deprecation(self):
        ''' Adds the pattern for sphinx_deprecation_regex to the list patterns to exclude '''
        self.add_exclude_patterns([self.sphinx_deprecation_regex])


class DoxyChecker(RegexChecker):
    name = 'doxygen'
    pattern = doxy_pattern


class XMLRunnerChecker(RegexChecker):
    name = 'xmlrunner'
    pattern = xmlrunner_pattern


class JUnitChecker(WarningsChecker):
    name = 'junit'

    def check(self, content):
        '''
        Function for counting the number of JUnit failures in a specific text

        Args:
            content (str): The content to parse
        '''
        try:
            result = JUnitXml.fromstring(content.encode('utf-8'))
            if self.verbose:
                for suite in result:
                    for testcase in filter(lambda testcase: isinstance(testcase.result, (Failure, Error)), suite):
                        print('{classname}.{testname}'.format(classname=testcase.classname,
                                                              testname=testcase.name))
            result.update_statistics()
            self.count += result.errors + result.failures
        except ParseError:
            return


class CoverityChecker(RegexChecker):
    name = 'coverity'
    pattern = coverity_pattern
    CLASSIFICATION = "Unclassified"

    def check(self, content):
        '''
        Function for counting the number of warnings, but adopted for Coverity
        output

        Args:
            content (str): The content to parse
        '''
        matches = re.finditer(self.pattern, content)
        for match in matches:
            if (match.group('curr') == match.group('max')) and \
                    (match.group('classification') in self.CLASSIFICATION):
                self.count += 1
                self.print_when_verbose(match.group(0).strip())

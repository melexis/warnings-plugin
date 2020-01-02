#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import abc
import re
from xml.etree.ElementTree import ParseError

from junitparser import Error, Failure, JUnitXml

DOXYGEN_WARNING_REGEX = r"(?:((?:[/.]|[A-Za-z]).+?):(-?\d+):\s*([Ww]arning|[Ee]rror)|<.+>:-?\d+(?::\s*([Ww]arning|[Ee]rror))?): ((?!notes).+(?:(?!\s*(?:[Nn]otice|[Ww]arning|[Ee]rror): )[^/<\n][^:\n][^/\n].+)*)|\s*(\b[Nn]otice|\b[Ww]arning|\b[Ee]rror): (?!notes)(.+)\n?"
doxy_pattern = re.compile(DOXYGEN_WARNING_REGEX)

SPHINX_WARNING_REGEX = r"(?m)^(?:(.+?:(?:\d+|None)?):?\s*)?(DEBUG|INFO|WARNING|ERROR|SEVERE):\s*(.+)$"
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
        self.include_patterns = []

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

    def add_patterns(self, regexes, pattern_container):
        ''' Raises an Exception to explain that this feature is not available for the targeted checker

        Args:
            regexes (list[str]|None): List of regexes to add
            pattern_container (list[re.Pattern]): Target storage container for patterns

        Raises:
            Exception: Feature of regexes to include/exclude warnings is only configurable for the RegexChecker classes
        '''
        if regexes:
            raise Exception("Feature of regexes to include/exclude warnings is not configurable for the {}."
                            .format(self.__class__.__name__))

    def set_maximum(self, maximum):
        ''' Setter function for the maximum amount of warnings

        Args:
            maximum (int): maximum amount of warnings allowed

        Raises:
            ValueError: Invalid argument (min limit higher than max limit)
        '''
        if self.warn_min > maximum:
            raise ValueError("Invalid argument: minimum limit ({0.warn_min}) is higher than maximum limit "
                             "({0.warn_max}). Cannot enter {value}.". format(self, value=maximum))
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
            raise ValueError("Invalid argument: minimum limit ({0.warn_min}) is higher than maximum limit "
                             "({0.warn_max}). Cannot enter {value}.".format(self, value=minimum))
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
            int: 0 if the amount of warnings is within limits, the count of warnings otherwise
                (or 1 in case of a count of 0 warnings)
        '''
        if self.count > self.warn_max or self.count < self.warn_min:
            return self._return_error_code()
        elif self.warn_min == self.warn_max and self.count == self.warn_max:
            print("Number of warnings ({0.count}) is exactly as expected. Well done."
                  .format(self))
        else:
            print("Number of warnings ({0.count}) is between limits {0.warn_min} and {0.warn_max}. Well done."
                  .format(self))
        return 0

    def _return_error_code(self):
        ''' Function for determining the return code and message on failure

        Returns:
            int: The count of warnings (or 1 in case of a count of 0 warnings)
        '''
        if self.count > self.warn_max:
            error_reason = "higher than the maximum limit"
        else:
            error_reason = "lower than the minimum limit"

        error_code = self.count
        if error_code == 0:
            error_code = 1
        print("Number of warnings ({0.count}) is {1} ({0.warn_min}). Returning error code {2}."
              .format(self, error_reason, error_code))
        return error_code

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

    def add_patterns(self, regexes, pattern_container):
        ''' Adds regexes as patterns to the specified container

        Args:
            regexes (list[str]|None): List of regexes to add
            pattern_container (list[re.Pattern]): Target storage container for patterns
        '''
        if regexes:
            if not isinstance(regexes, list):
                raise TypeError("Expected a list value for exclude key in configuration file; got {}"
                                .format(regexes.__class__.__name__))
            for regex in regexes:
                pattern_container.append(re.compile(regex))

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
        ''' Checks if the specific text must be excluded based on the configured regexes for exclusion and inclusion.

        Inclusion has priority over exclusion.

        Args:
            content (str): The content to parse

        Returns:
            bool: True for exclusion, False for inclusion
        '''
        matching_exclude_pattern = self._search_patterns(content, self.exclude_patterns)
        if not self._search_patterns(content, self.include_patterns) and matching_exclude_pattern:
            self.print_when_verbose("Excluded {!r} because of configured regex {!r}"
                                    .format(content, matching_exclude_pattern))
            return True
        return False

    @staticmethod
    def _search_patterns(content, patterns):
        ''' Returns the regex of the first pattern that matches specified content, None if nothing matches '''
        for pattern in patterns:
            if pattern.search(content):
                return pattern.pattern
        return None


class SphinxChecker(RegexChecker):
    name = 'sphinx'
    pattern = sphinx_pattern
    sphinx_deprecation_regex = r"(?m)^(?:(.+?:(?:\d+|None)?):?\s*)?(DEBUG|INFO|WARNING|ERROR|SEVERE|(?:\w+Sphinx\d+Warning)):\s*(.+)$"
    sphinx_deprecation_regex_in_match = "RemovedInSphinx\\d+Warning"

    def include_sphinx_deprecation(self):
        '''
        Adds the pattern for sphinx_deprecation_regex to the list patterns to include and alters the main pattern
        '''
        self.pattern = re.compile(self.sphinx_deprecation_regex)
        self.add_patterns([self.sphinx_deprecation_regex_in_match], self.include_patterns)


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

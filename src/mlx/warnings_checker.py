#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc
import re
from decouple import config
from junitparser import JUnitXml, Failure, Error
from mlx.coverity_services import CoverityConfigurationService, CoverityDefectService
try:
    # For Python 3.0 and later
    from urllib.error import URLError
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import URLError
from xml.etree.ElementTree import ParseError


DOXYGEN_WARNING_REGEX = r"(?:((?:[/.]|[A-Za-z]).+?):(-?\d+):\s*([Ww]arning|[Ee]rror)|<.+>:-?\d+(?::\s*([Ww]arning|[Ee]rror))?): (.+(?:(?!\s*(?:[Nn]otice|[Ww]arning|[Ee]rror): )[^/<\n][^:\n][^/\n].+)*)|\s*([Nn]otice|[Ww]arning|[Ee]rror): (.+)\n?"
doxy_pattern = re.compile(DOXYGEN_WARNING_REGEX)

SPHINX_WARNING_REGEX = r"(.+?:(?:\d+|None)?):?\s*(DEBUG|INFO|WARNING|ERROR|SEVERE):\s*(.+)\n?"
sphinx_pattern = re.compile(SPHINX_WARNING_REGEX)

PYTHON_XMLRUNNER_REGEX = r"(\s*(ERROR|FAILED) (\[\d+.\d\d\ds\]: \s*(.+)))\n?"
xmlrunner_pattern = re.compile(PYTHON_XMLRUNNER_REGEX)


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
        if self.warn_min > maximum:
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


class XMLRunnerChecker(RegexChecker):
    name = 'xmlrunner'
    pattern = xmlrunner_pattern


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


class CoverityChecker(WarningsChecker):
    name = 'coverity'

    def __init__(self, verbose=False):
        ''' Constructor

        Args:
            verbose (bool): Enable/disable verbose logging
        '''
        self.transport = config('COVERITY_TRANSPORT', default='http')
        self.port = config('COVERITY_PORT', default='8080')
        self.hostname = config('COVERITY_HOSTNAME')
        self.username = config('COVERITY_USERNAME')
        self.password = config('COVERITY_PASSWORD')
        self.stream = config('COVERITY_STREAM')
        self.classification = "Pending,Bug,Unclassified"

        super(CoverityChecker, self).__init__(verbose=verbose)

    def __extract_args__(self, content):
        return

    def __connect_to_coverity__(self):
        print("Login to Coverity Server: %s%s:%s" % (self.transport, self.hostname, self.port))
        coverity_conf_service = CoverityConfigurationService(self.transport, self.hostname, self.port)
        coverity_conf_service.login(self.username, self.password)
        if self.verbose:
            print("Retrieve stream from Coverity Server" % (self.transport, self.hostname, self.port))
        check_stream = coverity_conf_service.get_stream(self.stream)
        if check_stream is None:
            raise ValueError('Coverity checker failed. No such Coverity stream [%s] found on [%s]',
                             self.stream, coverity_conf_service.get_service_url())
        self.project_name = coverity_conf_service.get_project_name(check_stream)
        self.coverity_service = CoverityDefectService(coverity_conf_service)
        self.coverity_service.login(self.username, self.password)

    def check(self, content):
        '''
        Function for retrieving number of defects from Coverity server

        Args:
            content (str): some sort of configuration string
        '''
        self.__extract_args__(content)
        self.__connect_to_coverity__()
        print("Querying Coverity Server for defects")
        try:
            defects = self.coverity_service.get_defects(self.project_name, self.stream, classification=self.classification)
        except (URLError, AttributeError) as error:
            print('Coverity checker failed with %s' % error)
            return
        self.count = defects.totalNumberOfRecords





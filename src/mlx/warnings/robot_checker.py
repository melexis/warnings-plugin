# SPDX-License-Identifier: Apache-2.0

import logging
import sys

from junitparser import Error, Failure

from .junit_checker import JUnitChecker
from .warnings_checker import WarningsChecker


class RobotChecker(WarningsChecker):
    name = 'robot'
    checkers = []
    logging_fmt = "{checker_name}: {suite_name:<20} {message:>60}"

    @property
    def minimum(self):
        ''' Gets the lowest minimum amount of warnings

        Returns:
            int: the lowest minimum for warnings
        '''
        if self.checkers:
            return min(x.minimum for x in self.checkers)
        return 0

    @minimum.setter
    def minimum(self, minimum):
        for checker in self.checkers:
            checker.minimum = minimum

    @property
    def maximum(self):
        ''' Gets the highest minimum amount of warnings

        Returns:
            int: the highest maximum for warnings
        '''
        if self.checkers:
            return max(x.maximum for x in self.checkers)
        return 0

    @maximum.setter
    def maximum(self, maximum):
        for checker in self.checkers:
            checker.maximum = maximum

    def check(self, content):
        '''
        Function for counting the number of failures in a specific Robot
        Framework test suite

        Args:
            content (str): The content to parse
        '''
        for checker in self.checkers:
            checker.check(content)

    def return_count(self):
        ''' Getter function for the amount of warnings found

        Returns:
            int: Number of warnings found
        '''
        self.count = 0
        for checker in self.checkers:
            self.count += checker.return_count()
        return self.count

    def return_check_limits(self):
        ''' Function for checking whether the warning count is within the configured limits

        Returns:
            int: 0 if the amount of warnings is within limits, the count of warnings otherwise
                (or 1 in case of a count of 0 warnings)
        '''
        count = 0
        for checker in self.checkers:
            if checker.suite_name:
                extra = {
                    "suite_name": f"test suite {checker.suite_name!r}",
                }
                count += checker.return_check_limits(extra)
            else:
                extra = {
                    "suite_name": "all test suites",
                }
                count += checker.return_check_limits(extra)
        if count:
            print(f"Robot: Returning error code {count}.")
        return count

    def parse_config(self, config):
        self.checkers = []
        check_suite_name = config.get('check_suite_names', True)
        for suite_config in config['suites']:
            checker = RobotSuiteChecker(suite_config['name'], check_suite_name=check_suite_name)
            checker.parse_config(suite_config)
            self.checkers.append(checker)


class RobotSuiteChecker(JUnitChecker):
    name = 'robot'

    def __init__(self, suite_name, check_suite_name=False):
        ''' Constructor

        Args:
            name (str): Name of the test suite to check the results of
            check_suite_name (bool): Whether to raise an error when no test in suite with given name is found
        '''
        super().__init__()
        self.suite_name = suite_name
        self.check_suite_name = check_suite_name
        self.is_valid_suite_name = False
        self.logger = logging.getLogger(self.name)
        self.output_logger = logging.getLogger(f"{self.name}.output")

    def _check_testcase(self, testcase):
        """ Handles the check of a test case element by checking if the result is a failure/error.

        If it is to be excluded by a configured regex, or the test case does not belong to the suite, 1 is returned.
        Otherwise, when in verbose mode, the suite name and test case name are printed.

        Args:
            testcase (junitparser.TestCase): Test case element to check for failure or error

        Returns:
            int: 1 if a failure/error is to be subtracted from the final count, 0 otherwise
        """
        if testcase.classname.endswith(self.suite_name):
            self.is_valid_suite_name = True
            return super()._check_testcase(testcase)
        return int(self.suite_name and isinstance(testcase.result, (Failure, Error)))

    def check(self, content):
        """ Function for counting the number of JUnit failures in a specific text

        The test cases with a ``classname`` that does not end with the ``name`` class attribute are ignored.

        Args:
            content (str): The content to parse

        Raises:
            SystemExit: No suite with name ``self.suite_name`` found. Returning error code -1.
        """
        super().check(content)
        if not self.is_valid_suite_name and self.check_suite_name:
            logging.error(f'No suite with name {self.suite_name!r} found. Returning error code -1.')
            sys.exit(-1)

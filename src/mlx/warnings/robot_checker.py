# SPDX-License-Identifier: Apache-2.0

import sys

from junitparser import Error, Failure

from .exceptions import WarningsConfigError
from .junit_checker import JUnitChecker
from .warnings_checker import WarningsChecker


class RobotChecker(WarningsChecker):
    name = "robot"
    logging_fmt = "{checker.name_repr}: {message}"

    def __init__(self, *logging_args):
        ''' Constructor '''
        super().__init__(*logging_args)
        self.checkers = []
        self.allow_unconfigured = True

    @property
    def minimum(self):
        """Gets the lowest minimum amount of warnings

        Returns:
            int: the lowest minimum for warnings
        """
        if self.checkers:
            return min(x.minimum for x in self.checkers)
        return 0

    @minimum.setter
    def minimum(self, minimum):
        for checker in self.checkers:
            checker.minimum = minimum

    @property
    def maximum(self):
        """Gets the highest minimum amount of warnings

        Returns:
            int: the highest maximum for warnings
        """
        if self.checkers:
            return max(x.maximum for x in self.checkers)
        return 0

    @maximum.setter
    def maximum(self, maximum):
        for checker in self.checkers:
            checker.maximum = maximum

    @property
    def ignored_testsuites(self):
        ignored_testcases = set.intersection(*(c.ignored_testsuites for c in self.checkers))
        return sorted({t.classname.split(".")[-1] for t in ignored_testcases})

    def check(self, content):
        """
        Function for counting the number of failures in a specific Robot
        Framework test suite

        Args:
            content (str): The content to parse
        """
        for checker in self.checkers:
            checker.check(content)

    def return_count(self):
        """Getter function for the amount of warnings found

        Returns:
            int: Number of warnings found
        """
        self.count = 0
        for checker in self.checkers:
            self.count += checker.return_count()
        if not self.allow_unconfigured and self.ignored_testsuites:
            raise WarningsConfigError(f"{len(self.ignored_testsuites)} test suites have been ignored due to "
                                      f"incomplete configuration: {self.ignored_testsuites}")
        return self.count

    def return_check_limits(self):
        """Function for checking whether the warning count is within the configured limits

        Returns:
            int: 0 if the amount of warnings is within limits, the count of warnings otherwise
                (or 1 in case of a count of 0 warnings)
        """
        count = 0
        for checker in self.checkers:
            count += checker.return_check_limits()
        if count:
            self.logger.warning(f"Returning error code {count}.")
        return count

    def parse_config(self, config):
        self.allow_unconfigured = config.get("allow_unconfigured", True)
        check_suite_name = config.get("check_suite_names", True)
        for suite_config in config["suites"]:
            checker = RobotSuiteChecker(suite_config["name"], *self.logging_args, check_suite_name=check_suite_name)
            checker.parse_config(suite_config)
            self.checkers.append(checker)


class RobotSuiteChecker(JUnitChecker):
    name = "robot_sub"
    logging_fmt = "{checker.name_repr}: {checker.suite_name_repr:<20} {message}"

    def __init__(self, suite_name, *logging_args, check_suite_name=False):
        """Constructor

        Args:
            name (str): Name of the test suite to check the results of
            check_suite_name (bool): Whether to raise an error when no test in suite with given name is found
        """
        super().__init__(*logging_args)
        self.suite_name = suite_name
        self.check_suite_name = check_suite_name
        self.is_valid_suite_name = False
        self.ignored_testsuites = set()

    @property
    def suite_name_repr(self):
        return f"suite {self.suite_name!r}" if self.suite_name else "all test suites"

    def _check_testcase(self, testcase):
        """Handles the check of a test case element by checking if the result is a failure/error.

        If it is to be excluded by a configured regex, or the test case does not belong to the suite, 1 is returned.
        Otherwise, when in verbose/output mode, the suite name and test case name are printed/written along with the
        failure/error message.

        Args:
            testcase (junitparser.TestCase): Test case element to check for failure or error

        Returns:
            int: 1 if a failure/error is to be subtracted from the final count, 0 otherwise
        """
        if testcase.classname.endswith(self.suite_name):
            self.is_valid_suite_name = True
            return super()._check_testcase(testcase)
        self.ignored_testsuites.add(testcase)
        return int(isinstance(testcase.result, (Failure, Error)))

    def check(self, content):
        """Function for counting the number of JUnit failures in a specific text

        The test cases with a ``classname`` that does not end with the ``name`` class attribute are ignored.

        Args:
            content (str): The content to parse

        Raises:
            SystemExit: No suite with name ``self.suite_name`` found. Returning error code -1.
        """
        super().check(content)
        if not self.is_valid_suite_name and self.check_suite_name:
            self.logger.error(f"No suite with name {self.suite_name!r} found. Returning error code -1.")
            sys.exit(-1)

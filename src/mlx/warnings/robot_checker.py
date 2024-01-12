import sys

from junitparser import Error, Failure

from .junit_checker import JUnitChecker
from .warnings_checker import WarningsChecker


class RobotChecker(WarningsChecker):
    name = 'robot'
    checkers = []

    @property
    def counted_warnings(self):
        ''' List: list of counted warnings (str) '''
        all_counted_warnings = []
        for checker in self.checkers:
            all_counted_warnings.extend(checker.counted_warnings)
        return all_counted_warnings

    def get_minimum(self):
        ''' Gets the lowest minimum amount of warnings

        Returns:
            int: the lowest minimum for warnings
        '''
        if self.checkers:
            return min(x.get_minimum() for x in self.checkers)
        return 0

    def set_minimum(self, minimum):
        ''' Setter function for the minimum amount of warnings

        Args:
            minimum (int): minimum amount of warnings allowed
        '''
        for checker in self.checkers:
            checker.set_minimum(minimum)

    def get_maximum(self):
        ''' Gets the highest minimum amount of warnings

        Returns:
            int: the highest maximum for warnings
        '''
        if self.checkers:
            return max(x.get_maximum() for x in self.checkers)
        return 0

    def set_maximum(self, maximum):
        ''' Setter function for the maximum amount of warnings

        Args:
            maximum (int): maximum amount of warnings allowed
        '''
        for checker in self.checkers:
            checker.set_maximum(maximum)

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
            if checker.name:
                print('Counted failures for test suite {!r}.'.format(checker.name))
            else:
                print('Counted failures for all test suites.')
            count += checker.return_check_limits()
        return count

    def parse_config(self, config):
        self.checkers = []
        check_suite_name = config.get('check_suite_names', True)
        for suite_config in config['suites']:
            checker = RobotSuiteChecker(suite_config['name'], check_suite_name=check_suite_name,
                                        verbose=self.verbose)
            checker.parse_config(suite_config)
            self.checkers.append(checker)


class RobotSuiteChecker(JUnitChecker):
    def __init__(self, name, check_suite_name=False, **kwargs):
        ''' Constructor

        Args:
            name (str): Name of the test suite to check the results of
            check_suite_name (bool): Whether to raise an error when no test in suite with given name is found
        '''
        super().__init__(**kwargs)
        self.name = name
        self.check_suite_name = check_suite_name
        self.is_valid_suite_name = False

    def return_count(self):
        ''' Getter function for the amount of warnings found

        Returns:
            int: Number of warnings found
        '''
        msg = "{} warnings found".format(self.count)
        if self.name:
            msg = "Suite {!r}: {}".format(self.name, msg)
        print(msg)
        return self.count

    def _check_testcase(self, testcase):
        """ Handles the check of a test case element by checking if the result is a failure/error.

        If it is to be excluded by a configured regex, or the test case does not belong to the suite, 1 is returned.
        Otherwise, when in verbose mode, the suite name and test case name are printed.

        Args:
            testcase (junitparser.TestCase): Test case element to check for failure or error

        Returns:
            int: 1 if a failure/error is to be subtracted from the final count, 0 otherwise
        """
        if testcase.classname.endswith(self.name):
            self.is_valid_suite_name = True
            return super()._check_testcase(testcase)
        return int(self.name and isinstance(testcase.result, (Failure, Error)))

    def check(self, content):
        """ Function for counting the number of JUnit failures in a specific text

        The test cases with a ``classname`` that does not end with the ``name`` class attribute are ignored.

        Args:
            content (str): The content to parse

        Raises:
            SystemExit: No suite with name ``self.name`` found. Returning error code -1.
        """
        super().check(content)
        if not self.is_valid_suite_name and self.check_suite_name:
            print('ERROR: No suite with name {!r} found. Returning error code -1.'.format(self.name))
            sys.exit(-1)

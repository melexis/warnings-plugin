from mlx.junit_checker import JUnitChecker
from mlx.warnings_checker import WarningsChecker


class RobotChecker(WarningsChecker):
    name = 'robot'
    checkers = []

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
        for suite_config in config['suites']:
            checker = RobotSuiteChecker(suite_config['name'], verbose=self.verbose)
            checker.parse_config(suite_config)
            self.checkers.append(checker)


class RobotSuiteChecker(JUnitChecker):
    def __init__(self, name, **kwargs):
        ''' Constructor

        Args:
            name: Name of the test suite to check the results of
        '''
        super().__init__(**kwargs)
        self.name = name

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

import pathlib

from .warnings_checker import WarningsChecker


class PolyspaceChecker(WarningsChecker):
    name = 'polyspace'
    checkers = []

    @property
    def counted_warnings(self, name):
        ''' List: list of counted warnings (str) '''
        all_counted_warnings = []
        for checker in self.checkers[name]:
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
        Function for counting the number of failures in a TSV file exported by Polyspace

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
                print('Counted failures for severity {!r}.'.format(checker.name))
            count += checker.return_check_limits()
        return count

    def parse_config(self, config):
        self.checkers = []
        for family, data in config.items():
            if family == "enabled":
                continue
            for check in data:
                for key, value in check.items():
                    if key == "min":
                        minimum = value
                    elif key == "max":
                        maximum = value
                    else:
                        colomn = key
                        check_value = value
                if not (minimum and maximum and colomn and check_value):
                    raise ValueError("Expected a dict with these key value pairs:"
                                     "{\n   <colomn-name>: <value_to_check>,\n   min: <number>,\n   max: <number>\n}")
                self.checkers.append(PolyspaceCheck(self.log_file, family, colomn, check_value, minimum, maximum))

class PolyspaceCheck:

    def __init__(self, log_file, family, colomn, check_value, minimum, maximum):
        self.log_file = log_file
        self.family = family
        self.colomn = colomn
        self.check_value = check_value
        self.minimum = minimum
        self.maximum = maximum

    def check(self, content):
        """ Function for counting the number the specified value to be checked in a specified colomn of the TSV file.

        Args:
            content (str): The content to parse

        Raises:
            SystemExit: No suite with name ``self.name`` found. Returning error code -1.
        """
        pass  #TODO: add the check

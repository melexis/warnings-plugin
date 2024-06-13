import pathlib

from .warnings_checker import WarningsChecker


class PolyspaceChecker(WarningsChecker):
    checkers = {}

    @property
    def counted_warnings(self, name):
        ''' List: list of counted warnings (str) '''
        all_counted_warnings = []
        for checker in self.checkers[name]:
            all_counted_warnings.extend(checker.counted_warnings)
        return all_counted_warnings

    def get_minimum(self, name):
        ''' Gets the lowest minimum amount of warnings

        Returns:
            int: the lowest minimum for warnings
        '''
        if self.checkers[name]:
            return min(x.get_minimum() for x in self.checkers[name])
        return 0

    def set_minimum(self, minimum, name):
        ''' Setter function for the minimum amount of warnings

        Args:
            minimum (int): minimum amount of warnings allowed
        '''
        for checker in self.checkers[name]:
            checker.set_minimum(minimum)

    def get_maximum(self, name):
        ''' Gets the highest minimum amount of warnings

        Returns:
            int: the highest maximum for warnings
        '''
        if self.checkers[name]:
            return max(x.get_maximum() for x in self.checkers[name])
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


class CodeProverChecker(PolyspaceChecker):
    name = 'code_prover'
    _tsv_file = None

    def __init__(self, name, **kwargs):
        ''' Constructor

        Args:
            name (str): Name of the test suite to check the results of
            check_suite_name (bool): Whether to raise an error when no test in suite with given name is found
        '''
        super().__init__(**kwargs)
        self.name = name

    @property
    def tsv_file(self):
        """The path of the TSV file"""
        return self._tsv_file

    @tsv_file.setter
    def tsv_file(self, file_path):
        if file_path.is_file():
            self._tsv_file = file_path
        else:
            raise ValueError(f"{file_path} is not a file")

    def parse_config(self, config):
        self.checkers = []
        for suite_config in config['severity']:
            checker = PolyspaceChecker(verbose=self.verbose)
            checker.parse_config(suite_config)
            self.checkers.append(checker)

    def return_count(self):
        ''' Getter function for the amount of warnings found

        Returns:
            int: Number of warnings found
        '''
        self.count = 0
        for checker in self.checkers:
            self.count += checker.return_count()
        return self.count

class BugFinderChecker(PolyspaceChecker):
    name = 'bug_finder'
    checkers = []

    def __init__(self, name, **kwargs):
        ''' Constructor

        Args:
            name (str): Name of the test suite to check the results of
            check_suite_name (bool): Whether to raise an error when no test in suite with given name is found
        '''
        super().__init__(**kwargs)
        self.name = name

    @property
    def tsv_file(self):
        """The path of the TSV file"""
        return self._tsv_file

    @tsv_file.setter
    def tsv_file(self, file_path):
        if file_path.is_file():
            self._tsv_file = file_path
        else:
            raise ValueError(f"{file_path} is not a file")

    def parse_config(self, config):
        self.checkers = []
        for suite_config in config['severity']:
            checker = PolyspaceChecker(verbose=self.verbose)
            checker.parse_config(suite_config)
            self.checkers.append(checker)

    def return_count(self):
        ''' Getter function for the amount of warnings found

        Returns:
            int: Number of warnings found
        '''
        self.count = 0
        for checker in self.checkers:
            self.count += checker.return_count()
        return self.count

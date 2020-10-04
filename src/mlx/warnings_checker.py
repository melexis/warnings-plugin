import abc


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
            raise ValueError("Invalid argument: maximum limit must be higher than minimum limit ({min}); cannot "
                             "set {max}.".format(max=maximum, min=self.warn_min))
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
            raise ValueError("Invalid argument: minimum limit must be lower than maximum limit ({max}); cannot "
                             "set {min}.".format(min=minimum, max=self.warn_max))
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
            error_reason = "higher than the maximum limit ({0.warn_max})".format(self)
        else:
            error_reason = "lower than the minimum limit ({0.warn_min})".format(self)

        error_code = self.count
        if error_code == 0:
            error_code = 1
        print("Number of warnings ({0.count}) is {1}. Returning error code {2}."
              .format(self, error_reason, error_code))
        return error_code

    def print_when_verbose(self, message):
        ''' Prints message only when verbose mode is enabled.

        Args:
            message (str): Message to conditionally print
        '''
        if self.verbose:
            print(message)

    def parse_config(self, config):
        self.set_maximum(int(config['max']))
        self.set_minimum(int(config['min']))
        self.add_patterns(config.get("exclude"), self.exclude_patterns)

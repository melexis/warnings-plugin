import argparse
import re
import sys

DOXYGEN_WARNING_REGEX = r"(?:(?:((?:[/.]|[A-Za-z]:).+?):(-?\d+):\s*([Ww]arning|[Ee]rror)|<.+>:-?\d+(?::\s*([Ww]arning|[Ee]rror))?): (.+(?:\n(?!\s*(?:[Nn]otice|[Ww]arning|[Ee]rror): )[^/<\n][^:\n][^/\n].+)*)|\s*([Nn]otice|[Ww]arning|[Ee]rror): (.+))$"
doxy_pattern = re.compile(DOXYGEN_WARNING_REGEX)

SPHINX_WARNING_REGEX = r"^(.+?:(?:\d+|None)): (DEBUG|INFO|WARNING|ERROR|SEVERE): (.+)\n?$"
sphinx_pattern = re.compile(SPHINX_WARNING_REGEX)

JUNIT_WARNING_REGEX = r"\<\s*failure\s+message"
junit_pattern = re.compile(JUNIT_WARNING_REGEX)


class WarningsChecker(object):

    def __init__(self, name, pattern = None):
        ''' Constructor

        Args:
            name (str): Name of the checker
            pattern (str): Regular expression used by the checker in order to find warnings
        '''
        self.pattern = pattern
        self.name = name
        self.reset()

    def reset(self):
        ''' Reset function (resets min, max and counter values) '''
        self.count = 0
        self.warn_min = 0
        self.warn_max = 0

    def check(self, line):
        ''' Function for counting the number of sphinx warnings in a specific line '''
        self.count += len(re.findall(self.pattern, line))

    def set_maximum(self, maximum):
        ''' Setter function for the maximum amount of warnings

        Args:
            maximum (int): maximum amount of warnings allowed

        Raises:
            ValueError: Invalid argument (min limit higher than max limit)
        '''
        if self.warn_min == 0:
            self.warn_max = maximum
        elif self.warn_min > maximum:
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
            int: 0 if the amount of warnings is within limits. 1 otherwise
        '''
        if self.count > self.warn_max:
            print("Number of warnings ({count}) is higher than the maximum limit ({max}). Returning error code 1.".format(count=self.count, max=self.warn_max))
            return 1
        elif self.count < self.warn_min:
            print("Number of warnings ({count}) is lower than the minimum limit ({min}). Returning error code 1.".format(count=self.count, min=self.warn_min))
            return 1
        else:
            print("Number of warnings ({count}) is between limits {min} and {max}. Well done.".format(count=self.count, min=self.warn_min, max=self.warn_max))
            return 0


class SphinxChecker(WarningsChecker):
    name = 'sphinx'

    def __init__(self):
        super(SphinxChecker, self).__init__(name=SphinxChecker.name, pattern=sphinx_pattern)


class DoxyChecker(WarningsChecker):
    name = 'doxygen'

    def __init__(self):
        super(DoxyChecker, self).__init__(name=DoxyChecker.name, pattern=doxy_pattern)


class JUnitChecker(WarningsChecker):
    name = 'junit'

    def __init__(self):
        super(JUnitChecker, self).__init__(name=JUnitChecker.name, pattern=junit_pattern)


class WarningsPlugin:

    def __init__(self, sphinx = False, doxygen = False, junit = False):
        '''
        Function for initializing the parsers

        Args:
            sphinx (bool, optional):    enable sphinx parser
            doxygen (bool, optional):   enable doxygen parser
            junit (bool, optional):     enable junit parser
        '''
        self.checkerList = {}
        if sphinx:
            self.activate_checker(SphinxChecker())
        if doxygen:
            self.activate_checker(DoxyChecker())
        if junit:
            self.activate_checker(JUnitChecker())

        self.warn_min = 0
        self.warn_max = 0
        self.count = 0

    def activate_checker(self, checker):
        '''
        Activate additional checkers after initialization

        Args:
            checker (WarningsChecker):         checker object
        '''
        checker.reset()
        self.checkerList[checker.name] = checker

    def get_checker(self, name):
        ''' Get checker by name

        Args:
            name (str): checker name
        Return:
            checker object (WarningsChecker)
        '''
        return self.checkerList[name]

    def check(self, line):
        '''
        Function for running checks with each initalized parser

        Args:
            line (str): The line of the file/console output to parse
        '''
        if len(self.checkerList) == 0:
            print("No checkers activated. Please use activate_checker function")
        else:
            for name, checker in self.checkerList.items():
                checker.check(line)

    def set_maximum(self, maximum):
        ''' Setter function for the maximum amount of warnings

        Args:
            maximum (int): maximum amount of warnings allowed
        '''
        for name, checker in self.checkerList.items():
            checker.set_maximum(maximum)

    def set_minimum(self, minimum):
        ''' Setter function for the minimum amount of warnings

        Args:
            minimum (int): minimum amount of warnings allowed
        '''
        for name, checker in self.checkerList.items():
            checker.set_minimum(minimum)

    def return_count(self, name = None):
        ''' Getter function for the amount of found warnings

        If the name parameter is set, this function will return the amount of
        warnings found by that checker. If not, the function will return the sum
        of the warnings found by all registered checkers.

        Args:
            name (WarningsChecker): The checker for which to return the amount of warnings (if set)

        Returns:
            int: Amount of found warnings
        '''
        self.count = 0
        if name is None:
            for name, checker in self.checkerList.items():
                self.count += checker.return_count()
        else:
            self.count = self.checkerList[name].return_count()
        return self.count

    def return_check_limits(self, name = None):
        ''' Function for determining the return value of the script

        If the name parameter is set, this function will check (and return) the
        return value of that checker. If not, this function checks whether the
        warnings for each registred checker are within the configured limits.

        Args:
            name (WarningsChecker): The checker for which to check the return value

        Return:
            int: 0 if the amount warnings are within limits otherwise 1
        '''
        if name is None:
            for name, checker in self.checkerList.items():
                retval = checker.return_check_limits()
                if retval != 0:
                    return retval
        else:
            return self.checkerList[name].return_check_limits()

        return 0


def main():
    parser = argparse.ArgumentParser(prog='mlx-warnings')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-d', '--doxygen', dest='doxygen', action='store_true')
    group.add_argument('-s', '--sphinx', dest='sphinx', action='store_true')
    group.add_argument('-j', '--junit', dest='junit', action='store_true')
    parser.add_argument('-m', '--maxwarnings', type=int, required=False, default=0,
                        help='Maximum amount of warnings accepted')
    parser.add_argument('--minwarnings', type=int, required=False, default=0,
                        help='Minimum amount of warnings accepted')

    parser.add_argument('logfile', help='Logfile that might contain warnings')
    args = parser.parse_args()

    warnings = WarningsPlugin(sphinx=args.sphinx, doxygen=args.doxygen, junit=args.junit)
    warnings.set_maximum(args.maxwarnings)
    warnings.set_minimum(args.minwarnings)

    for line in open(args.logfile, 'r'):
        warnings.check(line)

    warnings.return_count()
    sys.exit(warnings.return_check_limits())


if __name__ == '__main__':
    main()


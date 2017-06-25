import argparse
import re
import sys
import errno

DOXYGEN_WARNING_REGEX = r"(?:(?:((?:[/.]|[A-Za-z]:).+?):(-?\d+):\s*([Ww]arning|[Ee]rror)|<.+>:-?\d+(?::\s*([Ww]arning|[Ee]rror))?): (.+(?:\n(?!\s*(?:[Nn]otice|[Ww]arning|[Ee]rror): )[^/<\n][^:\n][^/\n].+)*)|\s*([Nn]otice|[Ww]arning|[Ee]rror): (.+))$"
doxy_pattern = re.compile(DOXYGEN_WARNING_REGEX)

SPHINX_WARNING_REGEX = r"^(.+?:(?:\d+|None)): (DEBUG|INFO|WARNING|ERROR|SEVERE): (.+)\n?$"
sphinx_pattern = re.compile(SPHINX_WARNING_REGEX)

JUNIT_WARNING_REGEX = r"\<\s*failure\s+message"
junit_pattern = re.compile(JUNIT_WARNING_REGEX)


class WarningsPlugin:

    def __init__(self, sphinx = False, doxygen = False, junit = False):
        # type: (boolean, boolean, boolean) -> None
        '''
        Function for initializing the parsers

        Args:
            sphinx          enable sphinx parser
            doxygen         enable doxygen parser
            junit           enable junit parser
        '''
        self.checkerList = []
        if sphinx:
            self.checkerList.append(WarningsChecker('sphinx', sphinx_pattern))
        if doxygen:
            self.checkerList.append(WarningsChecker('doxygen', doxy_pattern))
        if junit:
            self.checkerList.append(WarningsChecker('junit', junit_pattern))

        self.warn_min = 0
        self.warn_max = 0
        self.count = 0

    def check(self, line):
        # type: (string) -> None
        '''
        Function for running checks with each initalized parser
        '''
        for checker in self.checkerList:
            checker.check(line)

    def set_maximum(self, maximum):
        if self.warn_min == 0:
            self.warn_max = maximum
            return 0
        elif self.warn_min > maximum:
            print("Invalid argument: mininum limit ({min}) is higher than maximum limit ({max}). Cannot enter {value}". format(min=self.warn_min, max=self.warn_max, value=maximum))
            return errno.EINVAL
        else:
            self.warn_max = maximum
            return 0

    def get_maximum(self):
        return self.warn_max

    def set_minimum(self, minimum):
        if minimum > self.warn_max:
            print("Invalid argument: mininum limit ({min}) is higher than maximum limit ({max}). Cannot enter {value}". format(min=self.warn_min, max=self.warn_max, value=minimum))
            return errno.EINVAL
        else:
            self.warn_min = minimum
            return 0

    def get_minimum(self):
        return self.warn_min

    def return_count(self):
        self.count = 0
        for checker in self.checkerList:
            self.count += checker.return_count()

        return self.count

    def return_check_limits(self):
        if self.count > self.warn_max:
            print("Number of warnings ({count}) is higher than the maximum limit ({max}). Returning error code 1.".format(count=self.count, max=self.warn_max))
            return 1
        elif self.count < self.warn_min:
            print("Number of warnings ({count}) is lower than the minimum limit ({min}). Returning error code 1.".format(count=self.count, min=self.warn_min))
            return 1
        else:
            print("Number of warnings ({count}) is between limits {min} and {max}. Well done.".format(count=self.count, min=self.warn_min, max=self.warn_max))
            return 0


class WarningsChecker:

    def __init__(self, name, pattern):
        # type: (string, unicode) -> None
        self.counter = 0
        self.name = name
        self.pattern = pattern

    def check(self, line):
        '''
        Function for counting the number of sphinx warnings in a logfile.
        The function returns the number of warnings found
        '''
        self.counter += len(re.findall(self.pattern, line))

    def return_count(self):
        print("{count} {name} warnings found".format(count=self.counter, name=self.name))
        return self.counter


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

    warnings = WarningsPlugin(args.sphinx, args.doxygen, args.junit)
    warnings.limit_maximum(args.maxwarnings)
    warnings.limit_minimum(args.minwarnings)

    for line in open(args.logfile, 'r'):
        warnings.check(line)

    warnings.return_count()
    sys.exit(warnings.return_check_limits())


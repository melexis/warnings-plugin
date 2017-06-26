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


class WarningsChecker(object):

    def __init__(self, name = None, pattern = None):
        # type: (string, unicode) -> None
        self.pattern = pattern
        if name is None:
            self.name = 'uninitialized'
        else:
            self.name = name
        self.reset()

    def reset(self):
        self.count = 0
        self.warn_min = 0
        self.warn_max = 0

    def check(self, line):
        '''
        Function for counting the number of sphinx warnings in a logfile.
        The function returns the number of warnings found
        '''
        self.count += len(re.findall(self.pattern, line))

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
        print("{count} {name} warnings found".format(count=self.count, name=self.name))
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


class SphinxChecker(WarningsChecker):

    def __init__(self):
        super(SphinxChecker, self).__init__(name='sphinx', pattern=sphinx_pattern)


class DoxyChecker(WarningsChecker):

    def __init__(self):
        super(DoxyChecker, self).__init__(name='doxygen', pattern=doxy_pattern)


class JUnitChecker(WarningsChecker):

    def __init__(self):
        super(JUnitChecker, self).__init__(name='junit', pattern=junit_pattern)


class WarningsPlugin:
    Sphinx = SphinxChecker()
    Doxygen = DoxyChecker()
    JUnit = JUnitChecker()

    def __init__(self, sphinx = False, doxygen = False, junit = False):
        # type: (boolean, boolean, boolean) -> None
        '''
        Function for initializing the parsers

        Args:
            sphinx (bool, optional):    enable sphinx parser
            doxygen (bool, optional):   enable doxygen parser
            junit (bool, optional):     enable junit parser
        '''
        self.checkerList = []
        if sphinx:
            self.activate_checker(WarningsPlugin.Sphinx)
        if doxygen:
            self.activate_checker(WarningsPlugin.Doxygen)
        if junit:
            self.activate_checker(WarningsPlugin.JUnit)

        self.warn_min = 0
        self.warn_max = 0
        self.count = 0

    def activate_checker(self, checker):
        # type: (WarningsChecker) -> None
        '''
        Activate additional checkers after initialization

        Args:
            checker (WarningsChecker):         checker object
        '''
        checker.reset()
        self.checkerList.append(checker)

    def check(self, line):
        # type: (string) -> None
        '''
        Function for running checks with each initalized parser
        '''
        if len(self.checkerList) == 0:
            print("No checkers activated. Please use activate_checker function")
        else:
            for checker in self.checkerList:
                checker.check(line)

    def set_maximum(self, maximum):
        for checker in self.checkerList:
            retval = checker.set_maximum(maximum)
            if retval != 0:
                return retval
        return 0

    def set_minimum(self, minimum):
        for checker in self.checkerList:
            retval = checker.set_minimum(minimum)
            if retval != 0:
                return retval
        return 0

    def return_count(self, name = None):
        self.count = 0
        if name is None:
            for checker in self.checkerList:
                self.count += checker.return_count()
        else:
            self.count = name.return_count()
        return self.count

    def return_check_limits(self, name = None):
        if name is None:
            for checker in self.checkerList:
                retval = checker.return_check_limits()
                if retval != 0:
                    return retval
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


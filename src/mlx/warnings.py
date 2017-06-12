import argparse
import re
import sys
import math

DOXYGEN_WARNING_REGEX = r"(?:(?:((?:[/.]|[A-Za-z]:).+?):(-?\d+):\s*([Ww]arning|[Ee]rror)|<.+>:-?\d+(?::\s*([Ww]arning|[Ee]rror))?): (.+(?:\n(?!\s*(?:[Nn]otice|[Ww]arning|[Ee]rror): )[^/<\n][^:\n][^/\n].+)*)|\s*([Nn]otice|[Ww]arning|[Ee]rror): (.+))$"
doxy_pattern = re.compile(DOXYGEN_WARNING_REGEX)

SPHINX_WARNING_REGEX = r"^(.+?:(?:\d+|None)): (DEBUG|INFO|WARNING|ERROR|SEVERE): (.+)\n?$"
sphinx_pattern = re.compile(SPHINX_WARNING_REGEX)


class WarningsPlugin:
    def __init__(self):
        self.sphinx_counter = 0
        self.doxygen_counter = 0

    def check_sphinx_warnings(self, line):
        '''
        Function for counting the number of sphinx warnings in a logfile.
        The function returns the number of warnings found
        '''
        if re.search(sphinx_pattern, line):
            self.sphinx_counter += 1

    def return_sphinx_warnings(self):
        print("{count} sphinx warnings found".format(count=self.sphinx_counter))
        return self.sphinx_counter

    def check_doxygen_warnings(self, line):
        '''
        Function for counting the number of doxygen warnings in a logfile.
        The function returns the number of warnings found
        '''
        if re.search(doxy_pattern, line):
            self.doxygen_counter += 1

    def return_doxygen_warnings(self):
        print("{count} doxygen warnings found".format(count=self.doxygen_counter))
        return self.doxygen_counter


def main():
    parser = argparse.ArgumentParser(prog='warnings-plugin')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-d', '--doxygen', dest='doxygen', action='store_true')
    group.add_argument('-s', '--sphinx', dest='sphinx', action='store_true')
    parser.add_argument('-m', '--maxwarnings', type=int, required=False, default=0,
                        help='Maximum amount of warnings accepted')
    parser.add_argument('--minwarnings', type=int, required=False, default=math.inf,
                        help='Minimum amount of warnings accepted')
    parser.add_argument('logfile', help='Logfile that might contain warnings')
    args = parser.parse_args()

    warn_count = 0
    warn_max = args.maxwarnings
    warn_min = args.minwarnings

    warnings = WarningsPlugin()

    for line in open(args.logfile, 'r'):
        if args.doxygen:
            warnings.check_doxygen_warnings(line)
        elif args.sphinx:
            warnings.check_sphinx_warnings(line)

    warn_count = warnings.return_sphinx_warnings() + warnings.return_doxygen_warnings()
    if warn_count > warn_max:
        print("Number of warnings ({count}) is higher than the maximum limit ({max}). Returning error code 1.".format(count=warn_count, max=warn_max))
        sys.exit(1)
    elif warn_count < warn_min:
        print("Number of warnings ({count}) is lower than the minimum limit ({min}). Returning error code 1.".format(count=warn_count, min=warn_min))
        sys.exit(1)
    else:
        print("Number of warnings ({count}) is between limits {min} and {max}. Well done.".format(count=warn_count, min=warn_min, max=warn_max))
        sys.exit(0)


import re
import argparse
import sys

DOXYGEN_WARNING_REGEX =  r"(?:(?:((?:[/.]|[A-Za-z]:).+?):(-?\d+):\s*([Ww]arning|[Ee]rror)|<.+>:-?\d+(?::\s*([Ww]arning|[Ee]rror))?): (.+(?:\n(?!\s*(?:[Nn]otice|[Ww]arning|[Ee]rror): )[^/<\n][^:\n][^/\n].+)*)|\s*([Nn]otice|[Ww]arning|[Ee]rror): (.+))$"
doxy_pattern = re.compile(DOXYGEN_WARNING_REGEX)

SPHINX_WARNING_REGEX = r"^(.+?:\d+): (DEBUG|INFO|WARNING|ERROR|SEVERE): (.+)\n?$"
sphinx_pattern = re.compile(SPHINX_WARNING_REGEX)

def check_sphinx_warnings(logfile):
    '''
    Function for counting the number of sphinx warnings in a logfile.
    The function returns the number of warnings found
    '''
    counter = 0
    for line in open(logfile, 'r'):
        if re.search(sphinx_pattern, line):
            counter += 1

    print("{count} sphinx warnings found".format(count=counter))
    return counter

def check_doxygen_warnings(logfile):
    '''
    Function for counting the number of doxygen warnings in a logfile.
    The function returns the number of warnings found
    '''
    counter = 0
    for line in open(logfile, 'r'):
        if re.search(doxy_pattern, line):
            counter += 1

    print("{count} doxygen warnings found".format(count=counter))
    return counter

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='warnings-plugin')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-d', '--doxygen', action='store_true')
    group.add_argument('-s', '--sphinx', action='store_false')
    parser.add_argument('-m', '--maxwarnings', type=int, required=False, default=0,
                        help='Maximum amount of warnings accepted')
    parser.add_argument('logfile', help='Logfile that might contain warnings')
    args=parser.parse_args()

    warn_count = 0
    warn_max = args.maxwarnings

    if args.doxygen:
        warn_count = check_doxygen_warnings()
    elif args.sphinx:
        warn_count = check_sphinx_warnings()

    if warn_count > warn_max:
        print("Number of warnings ({count}) is higher than the limit ({max}). Returning error code 1.".format(count=warn_count, max=warn_max))
        sys.exit(1)
    else:
        print("Number of warnings ({count}) is lower than (or equal to) the limit ({max}). Well done.".format(count=warn_count, max=warn_max))
        sys.exit(0)

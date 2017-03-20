import re

DOXYGEN_WARNING_REGEX =  r"(?:(?:((?:[/.]|[A-Za-z]:).+?):(-?\d+):\s*([Ww]arning|[Ee]rror)|<.+>:-?\d+(?::\s*([Ww]arning|[Ee]rror))?): (.+(?:\n(?!\s*(?:[Nn]otice|[Ww]arning|[Ee]rror): )[^/<\n][^:\n][^/\n].+)*)|\s*([Nn]otice|[Ww]arning|[Ee]rror): (.+))$"
SPHINX_WARNING_REGEX = r"^(.+?:\d+): (DEBUG|INFO|WARNING|ERROR|SEVERE): (.+)\n?$"

doxy_pattern = re.compile(DOXYGEN_WARNING_REGEX)
sphinx_pattern = re.compile(SPHINX_WARNING_REGEX)

counter = 0

for line in open('test.txt', 'r'):
    if re.search(sphinx_pattern, line):
        counter += 1

print(counter)

counter = 0

for line in open('test.txt', 'r'):
    if re.search(doxy_pattern, line):
        counter += 1

print(counter)

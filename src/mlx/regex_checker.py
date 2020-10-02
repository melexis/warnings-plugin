import re

from mlx.warnings_checker import WarningsChecker

DOXYGEN_WARNING_REGEX = r"(?:((?:[/.]|[A-Za-z]).+?):(-?\d+):\s*([Ww]arning|[Ee]rror)|<.+>:-?\d+(?::\s*([Ww]arning|[Ee]rror))?): ((?!notes).+(?:(?!\s*(?:[Nn]otice|[Ww]arning|[Ee]rror): )[^/<\n][^:\n][^/\n].+)*)|\s*(\b[Nn]otice|\b[Ww]arning|\b[Ee]rror): (?!notes)(.+)\n?"
doxy_pattern = re.compile(DOXYGEN_WARNING_REGEX)

SPHINX_WARNING_REGEX = r"(?m)^(?:(.+?:(?:\d+|None)?):?\s*)?(DEBUG|INFO|WARNING|ERROR|SEVERE):\s*(.+)$"
sphinx_pattern = re.compile(SPHINX_WARNING_REGEX)

PYTHON_XMLRUNNER_REGEX = r"(\s*(ERROR|FAILED) (\[\d+.\d\d\ds\]: \s*(.+)))\n?"
xmlrunner_pattern = re.compile(PYTHON_XMLRUNNER_REGEX)

COVERITY_WARNING_REGEX = r"(?:((?:[/.]|[A-Za-z]).+?):(-?\d+):) (CID) \d+ \(#(?P<curr>\d+) of (?P<max>\d+)\): (?P<checker>.+)\): (?P<classification>\w+), *(.+)\n?"
coverity_pattern = re.compile(COVERITY_WARNING_REGEX)


class RegexChecker(WarningsChecker):
    name = 'regex'
    pattern = None

    def add_patterns(self, regexes, pattern_container):
        ''' Adds regexes as patterns to the specified container

        Args:
            regexes (list[str]|None): List of regexes to add
            pattern_container (list[re.Pattern]): Target storage container for patterns
        '''
        if regexes:
            if not isinstance(regexes, list):
                raise TypeError("Expected a list value for exclude key in configuration file; got {}"
                                .format(regexes.__class__.__name__))
            for regex in regexes:
                pattern_container.append(re.compile(regex))

    def check(self, content):
        ''' Function for counting the number of warnings in a specific text

        Args:
            content (str): The content to parse
        '''
        matches = re.finditer(self.pattern, content)
        for match in matches:
            match_string = match.group(0).strip()
            if self._is_excluded(match_string):
                continue
            self.count += 1
            self.print_when_verbose(match_string)

    def _is_excluded(self, content):
        ''' Checks if the specific text must be excluded based on the configured regexes for exclusion and inclusion.

        Inclusion has priority over exclusion.

        Args:
            content (str): The content to parse

        Returns:
            bool: True for exclusion, False for inclusion
        '''
        matching_exclude_pattern = self._search_patterns(content, self.exclude_patterns)
        if not self._search_patterns(content, self.include_patterns) and matching_exclude_pattern:
            self.print_when_verbose("Excluded {!r} because of configured regex {!r}"
                                    .format(content, matching_exclude_pattern))
            return True
        return False

    @staticmethod
    def _search_patterns(content, patterns):
        ''' Returns the regex of the first pattern that matches specified content, None if nothing matches '''
        for pattern in patterns:
            if pattern.search(content):
                return pattern.pattern
        return None


class CoverityChecker(RegexChecker):
    name = 'coverity'
    pattern = coverity_pattern
    CLASSIFICATION = "Unclassified"

    def check(self, content):
        '''
        Function for counting the number of warnings, but adopted for Coverity
        output

        Args:
            content (str): The content to parse
        '''
        matches = re.finditer(self.pattern, content)
        for match in matches:
            if (match.group('curr') == match.group('max')) and \
                    (match.group('classification') in self.CLASSIFICATION):
                self.count += 1
                self.print_when_verbose(match.group(0).strip())


class DoxyChecker(RegexChecker):
    name = 'doxygen'
    pattern = doxy_pattern


class SphinxChecker(RegexChecker):
    name = 'sphinx'
    pattern = sphinx_pattern
    sphinx_deprecation_regex = r"(?m)^(?:(.+?:(?:\d+|None)?):?\s*)?(DEBUG|INFO|WARNING|ERROR|SEVERE|(?:\w+Sphinx\d+Warning)):\s*(.+)$"
    sphinx_deprecation_regex_in_match = "RemovedInSphinx\\d+Warning"

    def include_sphinx_deprecation(self):
        '''
        Adds the pattern for sphinx_deprecation_regex to the list patterns to include and alters the main pattern
        '''
        self.pattern = re.compile(self.sphinx_deprecation_regex)
        self.add_patterns([self.sphinx_deprecation_regex_in_match], self.include_patterns)


class XMLRunnerChecker(RegexChecker):
    name = 'xmlrunner'
    pattern = xmlrunner_pattern

import hashlib
import re
from pathlib import Path

from .warnings_checker import WarningsChecker

DOXYGEN_WARNING_REGEX = r"(?:(?P<path1>(?:[/.]|[A-Za-z]).+?):(?P<line1>-?\d+):\s*(?P<severity1>[Ww]arning|[Ee]rror)|<.+>:(?P<line2>-?\d+)(?::\s*(?P<severity2>[Ww]arning|[Ee]rror))?): (?P<description1>.+(?:(?!\s*([Nn]otice|[Ww]arning|[Ee]rror): )[^/<\n][^:\n][^/\n].+)*)|\s*\b(?P<severity3>[Nn]otice|[Ww]arning|[Ee]rror): (?!notes)(?P<description2>.+)\n?"
doxy_pattern = re.compile(DOXYGEN_WARNING_REGEX)

SPHINX_WARNING_REGEX = r"(?m)^(?:((?P<path1>.+?):(?P<line1>\d+|None)?):?\s*)?(?P<severity1>DEBUG|INFO|WARNING|ERROR|SEVERE|CRITICAL):\s*(?P<description1>.+)$"
sphinx_pattern = re.compile(SPHINX_WARNING_REGEX)

PYTHON_XMLRUNNER_REGEX = r"(\s*(?P<severity1>ERROR|FAILED) (\[\d+\.\d{3}s\]: \s*(?P<description1>.+)))\n?"
xmlrunner_pattern = re.compile(PYTHON_XMLRUNNER_REGEX)

COVERITY_WARNING_REGEX = r"(?:((?:[/.]|[A-Za-z]).+?):(-?\d+):) (CID) \d+ \(#(?P<curr>\d+) of (?P<max>\d+)\): (?P<checker>.+\)): (?P<classification>\w+), *(.+)\n?"
coverity_pattern = re.compile(COVERITY_WARNING_REGEX)


class RegexChecker(WarningsChecker):
    name = 'regex'
    pattern = None
    SEVERITY_MAP = {
        'debug': 'info',
        'info': 'info',
        'notice': 'info',
        'warning': 'major',
        'error': 'critical',
        'severe': 'critical',
        'critical': 'critical',
        'failed': 'critical',
    }

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
            self.counted_warnings.append(match_string)
            self.print_when_verbose(match_string)
            if self.cq_enabled:
                self.add_code_quality_finding(match)

    def add_code_quality_finding(self, match):
        finding = {
            "severity": "major",
            "location": {
                "path": self.cq_default_path,
                "lines": {
                    "begin": 1,
                }
            }
        }
        groups = {name: result for name, result in match.groupdict().items() if result}
        for name, result in groups.items():
            if name.startswith("description"):
                finding["description"] = self.cq_description_template.substitute(description=result)
                break
        else:
            return  # no description was found, which is the bare minimum
        for name, result in groups.items():
            if name.startswith("severity"):
                finding["severity"] = self.SEVERITY_MAP[result.lower()]
                break
        for name, result in groups.items():
            if name.startswith("path"):
                path = Path(result)
                if path.is_absolute():
                    try:
                        path = path.relative_to(Path.cwd())
                    except ValueError as err:
                        raise ValueError("Failed to convert abolute path to relative path for Code Quality report: "
                                         f"{err}") from err
                finding["location"]["path"] = str(path)
                break
        for name, result in groups.items():
            if name.startswith("line"):
                try:
                    lineno = int(result, 0)
                except (TypeError, ValueError):
                    lineno = 1
                finding["location"]["lines"]["begin"] = lineno
                break
        finding["fingerprint"] = hashlib.md5(str(finding).encode('utf8')).hexdigest()
        self.cq_findings.append(finding)


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
                match_string = match.group(0).strip()
                self.counted_warnings.append(match_string)
                self.print_when_verbose(match_string)


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

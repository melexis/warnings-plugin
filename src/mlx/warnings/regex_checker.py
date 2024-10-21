import hashlib
import os
import re
from pathlib import Path
from string import Template

from .exceptions import WarningsConfigError
from .warnings_checker import WarningsChecker

DOXYGEN_WARNING_REGEX = r"(?:(?P<path1>(?:[/.]|[A-Za-z]).+?):(?P<line1>-?\d+):\s*(?P<severity1>[Ww]arning|[Ee]rror)|<.+>:(?P<line2>-?\d+)(?::\s*(?P<severity2>[Ww]arning|[Ee]rror))?): (?P<description1>.+(?:(?!\s*([Nn]otice|[Ww]arning|[Ee]rror): )[^/<\n][^:\n][^/\n].+)*)|\s*\b(?P<severity3>[Nn]otice|[Ww]arning|[Ee]rror): (?!notes)(?P<description2>.+)\n?"
doxy_pattern = re.compile(DOXYGEN_WARNING_REGEX)

SPHINX_WARNING_REGEX = r"(?m)^(?:((?P<path1>.+?):(?P<line1>\d+|None)?):?\s*)?(?P<severity1>DEBUG|INFO|WARNING|ERROR|SEVERE|CRITICAL):\s*(?P<description1>.+)$"
sphinx_pattern = re.compile(SPHINX_WARNING_REGEX)

PYTHON_XMLRUNNER_REGEX = r"(\s*(?P<severity1>ERROR|FAILED) (\[\d+\.\d{3}s\]: \s*(?P<description1>.+)))\n?"
xmlrunner_pattern = re.compile(PYTHON_XMLRUNNER_REGEX)

COVERITY_WARNING_REGEX = r"(?P<path>[\d\w/\\/-_]+\.\w+)(:(?P<line>\d+)(:(?P<column>\d+))?)?: ?CID \d+ \(#(?P<curr>\d+) of (?P<max>\d+)\): (?P<checker>.+): (?P<classification>[\w ]+),.+"
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
        '''Add code quality finding

        Args:
            match (re.Match): The regex match
        '''
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
        finding["fingerprint"] = hashlib.md5(str(finding).encode('utf-8')).hexdigest()
        self.cq_findings.append(finding)


class CoverityChecker(RegexChecker):
    name = 'coverity'
    pattern = coverity_pattern

    def __init__(self, verbose=False):
        super().__init__(verbose)
        self._cq_description_template = Template('Coverity: $checker')
        self.checkers = {}

    @property
    def counted_warnings(self):
        ''' List[str]: list of counted warnings'''
        all_counted_warnings = []
        for checker in self.checkers.values():
            all_counted_warnings.extend(checker.counted_warnings)
        return all_counted_warnings

    @property
    def cq_findings(self):
        ''' List[dict]: list of code quality findings'''
        for checker in self.checkers.values():
            self._cq_findings.extend(checker.cq_findings)
        return self._cq_findings

    @property
    def cq_description_template(self):
        ''' Template: string.Template instance based on the configured template string '''
        return self._cq_description_template

    @cq_description_template.setter
    def cq_description_template(self, template_obj):
        self._cq_description_template = template_obj

    def return_count(self):
        ''' Getter function for the amount of warnings found

        Returns:
            int: Number of warnings found
        '''
        self.count = 0
        for checker in self.checkers.values():
            self.count += checker.return_count()
        return self.count

    def return_check_limits(self):
        ''' Function for checking whether the warning count is within the configured limits

        Returns:
            int: 0 if the amount of warnings is within limits, the count of warnings otherwise
                (or 1 in case of a count of 0 warnings)
        '''
        count = 0
        for checker in self.checkers.values():
            print(f"Counted failures for classification {checker.classification!r}")
            count += checker.return_check_limits()
        print(f"total warnings = {count}")
        return count

    def check(self, content):
        '''
        Function for counting the number of warnings, but adopted for Coverity
        output

        Args:
            content (str): The content to parse
        '''
        matches = re.finditer(self.pattern, content)
        for match in matches:
            if (classification := match.group("classification").lower()) in self.checkers:
                self.checkers[classification].check(match)
            else:
                checker = CoverityClassificationChecker(classification=classification, verbose=self.verbose)
                self.checkers[classification] = checker
                checker.cq_enabled = self.cq_enabled
                checker.exclude_patterns = self.exclude_patterns
                checker.cq_description_template = self.cq_description_template
                checker.cq_default_path = self.cq_default_path
                checker.check(match)

    def parse_config(self, config):
        """Process configuration

        Args:
            config (dict): Content of configuration file
        """
        config.pop("enabled")
        if value := config.pop("cq_description_template", None):
            self.cq_description_template = Template(value)
        if value := config.pop("cq_default_path", None):
            self.cq_default_path = value
        if value := config.pop("exclude", None):
            self.add_patterns(value, self.exclude_patterns)
        for classification, checker_config in config.items():
            classification_key = classification.lower().replace("_", " ")
            if classification_key in CoverityClassificationChecker.SEVERITY_MAP:
                checker = CoverityClassificationChecker(classification=classification_key, verbose=self.verbose)
                if maximum := checker_config.get("max", 0):
                    checker.maximum = int(maximum)
                if minimum := checker_config.get("min", 0):
                    checker.minimum = int(minimum)
                self.checkers[classification_key] = checker
            else:
                print(f"WARNING: Unrecognized classification {classification!r}")

        for checker in self.checkers.values():
            checker.cq_enabled = self.cq_enabled
            checker.exclude_patterns = self.exclude_patterns
            checker.cq_description_template = self.cq_description_template
            checker.cq_default_path = self.cq_default_path


class CoverityClassificationChecker(WarningsChecker):
    SEVERITY_MAP = {
        'false positive': 'info',
        'intentional': 'info',
        'bug': 'major',
        'unclassified': 'major',
        'pending': 'critical',
    }

    def __init__(self, classification, **kwargs):
        """Initialize the CoverityClassificationChecker:

        Args:
            classification (str): The coverity classification
        """
        super().__init__(**kwargs)
        self.classification = classification

    @property
    def cq_description_template(self):
        ''' Template: string.Template instance based on the configured template string '''
        return self._cq_description_template

    @cq_description_template.setter
    def cq_description_template(self, template_obj):
        self._cq_description_template = template_obj

    def return_count(self):
        ''' Getter function for the amount of warnings found

        Returns:
            int: Number of warnings found
        '''
        return self.count

    def add_code_quality_finding(self, match):
        '''Add code quality finding

        Args:
            match (re.Match): The regex match
        '''
        finding = {
            "severity": "major",
            "location": {
                "path": self.cq_default_path,
                "positions": {
                    "begin": {
                        "line": 1,
                        "column": 1
                    }
                }
            }
        }
        groups = {name: result for name, result in match.groupdict().items() if result}
        try:
            description = self.cq_description_template.substitute(os.environ, **groups)
        except KeyError as err:
            raise WarningsConfigError(f"Failed to find environment variable from configuration value "
                                      f"'cq_description_template': {err}") from err
        if classification_raw := groups.get("classification"):
            finding["severity"] = self.SEVERITY_MAP[classification_raw.lower()]
        if "path" in groups:
            path = Path(groups["path"])
            if path.is_absolute():
                try:
                    path = path.relative_to(Path.cwd())
                except ValueError as err:
                    raise ValueError("Failed to convert abolute path to relative path for Code Quality report: "
                                     f"{err}") from err
            finding["location"]["path"] = str(path)
        for group_name in ("line", "column"):
            if group_name in groups:
                try:
                    finding["location"]["positions"]["begin"][group_name] = int(groups[group_name], 0)
                except (TypeError, ValueError):
                    pass

        finding["description"] = description
        finding["fingerprint"] = hashlib.md5(str(match.group(0).strip()).encode('utf-8')).hexdigest()
        self.cq_findings.append(finding)

    def check(self, content):
        '''
        Function for counting the number of warnings, but adopted for Coverity output.
        Multiple warnings for the same CID are counted as one.

        Args:
            content (re.Match): The regex match
        '''
        match_string = content.group(0).strip()
        if not self._is_excluded(match_string) and (content.group('curr') == content.group('max')):
            self.count += 1
            self.counted_warnings.append(match_string)
            self.print_when_verbose(match_string)
            if self.cq_enabled:
                self.add_code_quality_finding(content)


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

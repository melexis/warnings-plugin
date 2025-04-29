import os
import re
from string import Template

from .code_quality import Finding
from .exceptions import WarningsConfigError
from .warnings_checker import WarningsChecker

DOXYGEN_WARNING_REGEX = r"(?:(?P<path1>(?:[/.]|[A-Za-z]).+?):(?P<line1>-?\d+):\s*(?P<severity1>[Ww]arning|[Ee]rror)|<.+>:(?P<line2>-?\d+)(?::\s*(?P<severity2>[Ww]arning|[Ee]rror))?): (?P<description1>.+(?:(?!\s*([Nn]otice|[Ww]arning|[Ee]rror): )[^/<\n][^:\n][^/\n].+)*)|\s*\b(?P<severity3>[Nn]otice|[Ww]arning|[Ee]rror): (?!notes)(?P<description2>.+)\n?"
doxy_pattern = re.compile(DOXYGEN_WARNING_REGEX)

SPHINX_WARNING_REGEX = r"(?m)^(?:((?P<path1>.+?):(?P<line1>\d+|None)?):?\s*)?(?P<severity1>DEBUG|INFO|WARNING|ERROR|SEVERE|CRITICAL):\s*(?P<description1>.+)$"
sphinx_pattern = re.compile(SPHINX_WARNING_REGEX)

PYTHON_XMLRUNNER_REGEX = r"(\s*(?P<severity1>ERROR|FAILED) (\[\d+\.\d{3}s\]: \s*(?P<description1>.+)))\n?"
xmlrunner_pattern = re.compile(PYTHON_XMLRUNNER_REGEX)

COVERITY_WARNING_REGEX = r"(?P<path>[\w\.\\/\- ]+)(:(?P<line>\d+)(:(?P<column>\d+))?)?: ?CID (?P<cid>\d+) \(#(?P<curr>\d+) of (?P<max>\d+)\): (?P<checker>.+): (?P<classification>[\w ]+),.+"
coverity_pattern = re.compile(COVERITY_WARNING_REGEX)


class RegexChecker(WarningsChecker):
    name = "regex"
    pattern = None
    SEVERITY_MAP = {
        "debug": "info",
        "info": "info",
        "notice": "info",
        "warning": "major",
        "error": "critical",
        "severe": "critical",
        "critical": "critical",
        "failed": "critical",
    }

    def check(self, content):
        """Function for counting the number of warnings in a specific text

        Args:
            content (str): The content to parse
        """
        matches = re.finditer(self.pattern, content)
        for match in matches:
            match_string = match.group(0).strip()
            if self._is_excluded(match_string):
                continue
            self.count += 1
            self.logger.info(match_string)
            self.logger.debug(match_string)
            if self.cq_enabled:
                self.add_code_quality_finding(match)

    def add_code_quality_finding(self, match):
        """Add code quality finding

        Args:
            match (re.Match): The regex match
        """
        groups = {name: result for name, result in match.groupdict().items() if result}

        description = next((result for name, result in groups.items() if name.startswith("description")), None)
        if not description:
            return  # No description was found, which is the bare minimum

        finding = Finding(self.cq_description_template.substitute(description=description))
        finding.check_name = self.name_repr
        finding.severity = next((self.SEVERITY_MAP[result.lower()] for name, result in groups.items()
                                 if name.startswith("severity")), "info")
        finding.path = next((result for name, result in groups.items()
                             if name.startswith("path")), self.cq_default_path)
        finding.line = next((result for name, result in groups.items() if name.startswith("line")), 1)
        self.cq_findings.append(finding.to_dict())


class CoverityChecker(RegexChecker):
    name = "coverity"
    pattern = coverity_pattern

    def __init__(self, *logging_args):
        super().__init__(*logging_args)
        self._cq_description_template = Template("Coverity: CID $cid: $checker")
        self.checkers = {
            "unclassified": CoverityClassificationChecker("unclassified", *logging_args),
            "pending": CoverityClassificationChecker("pending", *logging_args),
            "bug": CoverityClassificationChecker("bug", *logging_args),
            "intentional": CoverityClassificationChecker("intentional", *logging_args),
            "false positive": CoverityClassificationChecker("false positive", *logging_args),
        }

    @property
    def cq_findings(self):
        """List[dict]: list of code quality findings"""
        for checker in self.checkers.values():
            self._cq_findings.extend(checker.cq_findings)
        return self._cq_findings

    @property
    def cq_description_template(self):
        """Template: string.Template instance based on the configured template string"""
        return self._cq_description_template

    @cq_description_template.setter
    def cq_description_template(self, template_obj):
        self._cq_description_template = template_obj

    def return_count(self):
        """Getter function for the amount of warnings found

        Returns:
            int: Number of warnings found
        """
        self.count = 0
        for checker in self.checkers.values():
            self.count += checker.return_count()
        return self.count

    def return_check_limits(self):
        """Function for checking whether the warning count is within the configured limits

        Returns:
            int: 0 if the amount of warnings is within limits, the count of warnings otherwise
                (or 1 in case of a count of 0 warnings)
        """
        count = 0
        for checker in self.checkers.values():
            count += checker.return_check_limits()
        if count:
            self.logger.warning(f"Returning error code {count}.")
        return count

    def check(self, content):
        """
        Function for counting the number of warnings, but adopted for Coverity
        output

        Args:
            content (str): The content to parse
        """
        matches = re.finditer(self.pattern, content)
        for match in matches:
            if (classification := match.group("classification").lower()) in self.checkers:
                checker = self.checkers[classification]
                checker.cq_enabled = self.cq_enabled
                checker.exclude_patterns = self.exclude_patterns
                checker.cq_description_template = self.cq_description_template
                checker.cq_default_path = self.cq_default_path
                checker.check(match)
            else:
                self.logger.warning(f"Unrecognized classification {match.group('classification')!r}")

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
            if classification_key in self.checkers:
                self.checkers[classification_key].parse_config(checker_config)
            else:
                self.logger.warning(f"Unrecognized classification {classification!r}")


class CoverityClassificationChecker(WarningsChecker):
    name = "coverity_sub"
    logging_fmt = "{checker.name_repr}: {checker.classification:<14} | {message}"
    SEVERITY_MAP = {
        "false positive": "info",
        "intentional": "info",
        "bug": "major",
        "unclassified": "major",
        "pending": "critical",
    }

    def __init__(self, classification, *args):
        """Initialize the CoverityClassificationChecker:

        Args:
            classification (str): The coverity classification
        """
        super().__init__(*args)
        self.classification = classification

    @property
    def cq_description_template(self):
        """Template: string.Template instance based on the configured template string"""
        return self._cq_description_template

    @cq_description_template.setter
    def cq_description_template(self, template_obj):
        self._cq_description_template = template_obj

    def add_code_quality_finding(self, match):
        """Add code quality finding

        Args:
            match (re.Match): The regex match
        """
        groups = {name: result for name, result in match.groupdict().items() if result}
        try:
            description = self.cq_description_template.substitute(os.environ, **groups)
        except KeyError as err:
            raise WarningsConfigError(f"Failed to find environment variable from configuration value "
                                      f"'cq_description_template': {err}") from err
        finding = Finding(description)
        finding.check_name = "Coverity"  # for all classifications

        if classification_raw := groups.get("classification"):
            finding.severity = self.SEVERITY_MAP[classification_raw.lower()]
        if path := groups.get("path", self.cq_default_path):
            finding.path = path
        if line := groups.get("line", 1):
            finding.line = line
        if column := groups.get("column", 1):
            finding.column = column

        self.cq_findings.append(finding.to_dict())

    def check(self, content):
        """
        Function for counting the number of warnings, but adopted for Coverity output.
        Multiple warnings for the same CID are counted as one.

        Args:
            content (re.Match): The regex match
        """
        match_string = content.group(0).strip()
        if not self._is_excluded(match_string) and (content.group("curr") == content.group("max")):
            self.count += 1
            self.logger.info(match_string)
            self.logger.debug(match_string)
            if self.cq_enabled:
                self.add_code_quality_finding(content)


class DoxyChecker(RegexChecker):
    name = "doxygen"
    pattern = doxy_pattern


class SphinxChecker(RegexChecker):
    name = "sphinx"
    pattern = sphinx_pattern
    sphinx_deprecation_regex = r"(?m)^(?:(.+?:(?:\d+|None)?):?\s*)?(DEBUG|INFO|WARNING|ERROR|SEVERE|(?:\w+Sphinx\d+Warning)):\s*(.+)$"
    sphinx_deprecation_regex_in_match = "RemovedInSphinx\\d+Warning"

    def include_sphinx_deprecation(self):
        """
        Adds the pattern for sphinx_deprecation_regex to the list patterns to include and alters the main pattern
        """
        self.pattern = re.compile(self.sphinx_deprecation_regex)
        self.add_patterns([self.sphinx_deprecation_regex_in_match], self.include_patterns)


class XMLRunnerChecker(RegexChecker):
    name = "xmlrunner"
    pattern = xmlrunner_pattern

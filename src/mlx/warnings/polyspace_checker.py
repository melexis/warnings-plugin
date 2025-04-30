# SPDX-License-Identifier: Apache-2.0

import csv
import os
from io import TextIOWrapper
from string import Template

from .code_quality import Finding
from .exceptions import WarningsConfigError
from .warnings_checker import WarningsChecker


class PolyspaceChecker(WarningsChecker):
    name = "polyspace"
    checkers = []

    def __init__(self, *logging_args):
        '''Constructor to set the default code quality description template to "Polyspace: $check"'''
        super().__init__(*logging_args)
        self._cq_description_template = Template("Polyspace: $check")

    @property
    def cq_findings(self):
        """List[dict]: list of code quality findings"""
        for checker in self.checkers:
            self._cq_findings.extend(checker.cq_findings)
        return self._cq_findings

    @property
    def cq_description_template(self):
        """Template: string.Template instance based on the configured template string"""
        return self._cq_description_template

    @cq_description_template.setter
    def cq_description_template(self, template_obj):
        self._cq_description_template = template_obj

    @property
    def minimum(self):
        """Gets the lowest minimum amount of warnings

        Returns:
            int: the lowest minimum for warnings
        """
        if self.checkers:
            return min(x.minimum for x in self.checkers)
        return 0

    @minimum.setter
    def minimum(self, minimum):
        for checker in self.checkers:
            checker.minimum = minimum

    @property
    def maximum(self):
        """Gets the highest minimum amount of warnings

        Returns:
            int: the highest maximum for warnings
        """
        if self.checkers:
            return max(x.maximum for x in self.checkers)
        return 0

    @maximum.setter
    def maximum(self, maximum):
        for checker in self.checkers:
            checker.maximum = maximum

    def check(self, content):
        """
        Function for counting the number of failures in a TSV file exported by Polyspace

        Args:
            content (_io.TextIOWrapper): The open file to parse
        """
        if not isinstance(content, TextIOWrapper):
            raise TypeError(
                f"{self.__class__.__name__} can't handle this type; expected {type(TextIOWrapper)}; got {type(content)}"
            )
        reader = csv.DictReader(content, dialect="excel-tab")
        # set column names to lowercase
        reader.fieldnames = [name.lower() for name in reader.fieldnames]

        for row in reader:
            for checker in self.checkers:
                if row["family"].lower() == checker.family_value:
                    checker.check(row)

    def return_count(self):
        """Getter function for the amount of warnings found

        Returns:
            int: Number of warnings found
        """
        self.count = 0
        for checker in self.checkers:
            self.count += checker.return_count()
        return self.count

    def return_check_limits(self):
        """Function for checking whether the warning count is within the configured limits

        Returns:
            int: 0 if the amount of warnings is within limits, the count of warnings otherwise
                (or 1 in case of a count of 0 warnings)
        """
        count = 0
        for checker in self.checkers:
            count += checker.return_check_limits()
        if count:
            self.logger.warning(f"Returning error code {count}.")
        return count

    def parse_config(self, config):
        """Parsing configuration dict extracted by previously opened JSON or yaml/yml file

        Args:
            config (dict): Content of configuration file

        Raises:
            ValueError: Expected a list of dicts as value of the key which represents the value of the 'Family' column.
            These dicts need to consist 3 key-value pairs (Note: if 'min' or 'max' is not defined, it will get the
            default value of 0):
            {\n    <column-name>: <value_to_check>,\n    min: <number>,\n    max: <number>\n}
        """
        self.checkers = []
        for family_value, data in config.items():
            if family_value == "enabled":
                continue
            if family_value == "cq_description_template":
                self.cq_description_template = Template(config["cq_description_template"])
                continue
            if family_value == "cq_default_path":
                self.cq_default_path = config["cq_default_path"]
                continue
            if family_value == "exclude":
                self.add_patterns(config.get("exclude"), self.exclude_patterns)
                continue
            for check in data:
                for key, value in check.items():
                    if key in ["min", "max"]:
                        continue
                    column_name = key.lower()
                    check_value = value.lower()
                    checker = PolyspaceFamilyChecker(family_value, column_name, check_value, *self.logging_args)
                    checker.parse_config(check)
                    self.checkers.append(checker)
                if not (column_name and check_value):
                    raise ValueError(
                        "Expected a list of dicts as value of the key which represents the value of the "
                        "'Family' column. These dicts need to consist 3 key-value pairs (Note: if 'min' or "
                        "'max' is not defined, it will get the default value of 0):\n"
                        "{\n    <column_name>: <value_to_check>,\n    min: <number>,\n    max: <number>\n};"
                        f"got {column_name!r} as column_name and {check_value!r} as value_to_check"
                    )
        for checker in self.checkers:
            checker.cq_enabled = self.cq_enabled
            checker.exclude_patterns = self.exclude_patterns
            checker.cq_description_template = self.cq_description_template
            checker.cq_default_path = self.cq_default_path


class PolyspaceFamilyChecker(WarningsChecker):
    name = "polyspace_sub"
    code_quality_severity = {
        "impact: high": "critical",
        "impact: medium": "major",
        "impact: low": "minor",
        "red": "critical",
        "orange": "major",
    }
    logging_fmt = "{checker.name_repr}: {checker.family_value:15s} : {checker.column_name:11s} : {checker.check_value:14s} | {message}"

    def __init__(self, family_value, column_name, check_value, *logging_args):
        """Initialize the PolyspaceFamilyChecker

        Args:
            family_value (str): The value to search for in the 'Family' column
            column_name (str): The name of the column
            check_value (str): The value to check in the column
        """
        super().__init__(*logging_args)
        self.family_value = family_value
        self.column_name = column_name
        self.check_value = check_value

    @property
    def cq_description_template(self):
        """Template: string.Template instance based on the configured template string"""
        return self._cq_description_template

    @cq_description_template.setter
    def cq_description_template(self, template_obj):
        self._cq_description_template = template_obj

    def add_code_quality_finding(self, row):
        """Add code quality finding

        Args:
            row (dict): The row of the warning with the corresponding colomn names
        """
        try:
            description = self.cq_description_template.substitute(os.environ, **row)
        except KeyError as err:
            raise WarningsConfigError(f"Failed to find environment variable from configuration value "
                                      f"'cq_description_template': {err}") from err

        finding = Finding(description)
        finding.check_name = self.family_value

        # Attention to bug finder: items have color red for impact: high, medium and low.
        if (severity := self.code_quality_severity.get(row["information"].lower())) is not None:
            finding.severity = severity
        elif (severity := self.code_quality_severity.get(row["color"].lower())) is not None:
            finding.severity = severity
        finding.path = row.get("file", self.cq_default_path)
        finding.line = row.get("line", 1)
        finding.column = row.get("col", 1)

        self.cq_findings.append(finding.to_dict())

    def check(self, content):
        """
        Function for counting the number of failures in a TSV/CSV file exported by Polyspace

        Args:
            content (dict): The row of the TSV file
        """
        if content[self.column_name].lower() == self.check_value:
            if content["status"].lower() in ["not a defect", "justified"]:
                self.logger.info(f"Excluded defect with ID {content.get('id', None)!r} because the status is "
                                 "'Not a defect' or 'Justified'")
            else:
                valid_content_values = [item or "" for item in content.values()]
                tab_sep_string = "\t".join(valid_content_values)
                if not self._is_excluded(tab_sep_string):
                    self.count = self.count + 1
                    verbose_log_msg = f"ID {content.get('id', None)!r}"
                    self.logger.info(verbose_log_msg)
                    self.logger.debug(verbose_log_msg)
                    if self.cq_enabled and content["color"].lower() != "green":
                        self.add_code_quality_finding(content)

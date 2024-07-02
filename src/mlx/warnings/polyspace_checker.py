import csv
import hashlib
from string import Template

from .warnings_checker import WarningsChecker


class PolyspaceFamilyChecker(WarningsChecker):
    name = 'polyspace'
    checkers = []
    code_quality_severity = {
        "impact: high": "critical",
        "impact: medium": "major",
        "impact: low": "minor",
        "red": "critical",
        "orange": "major",
        "green": "info",
    }

    @property
    def counted_warnings(self):
        ''' List: list of counted warnings (str) '''
        all_counted_warnings = []
        for checker in self.checkers:
            all_counted_warnings.extend(checker.counted_warnings)
        return all_counted_warnings

    @property
    def cq_description_template(self):
        ''' Template: string.Template instance based on the configured template string '''
        return self._cq_description_template

    @cq_description_template.setter
    def cq_description_template(self, template_obj):
        self._cq_description_template = template_obj

    @property
    def minimum(self):
        ''' Gets the lowest minimum amount of warnings

        Returns:
            int: the lowest minimum for warnings
        '''
        if self.checkers:
            return min(x.minimum for x in self.checkers)
        return 0

    @minimum.setter
    def minimum(self, minimum):
        for checker in self.checkers:
            checker.minimum = minimum

    @property
    def maximum(self):
        ''' Gets the highest minimum amount of warnings

        Returns:
            int: the highest maximum for warnings
        '''
        if self.checkers:
            return max(x.maximum for x in self.checkers)
        return 0

    @maximum.setter
    def maximum(self, maximum):
        for checker in self.checkers:
            checker.maximum = maximum

    def add_code_quality_finding(self, row):
        '''Add code quality finding

        Args:
            row (dict): The row of the warning with the corresponding colomn names
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
        # Attention to bug finder: items have color red for impact: high, medium and low.
        if row["information"].lower() in self.code_quality_severity.keys():
            finding["severity"] = self.code_quality_severity[row["information"].lower()]
        elif row["color"].lower() in self.code_quality_severity.keys():
            finding["severity"] = self.code_quality_severity[row["color"].lower()]
        else:
            finding["severity"] = "info"

        if row["file"]:
            finding["location"]["path"] = row["file"]
        if self.cq_description_template:
            finding["description"] = self.cq_description_template.safe_substitute(row)

        finding["fingerprint"] = hashlib.md5(str(finding).encode('utf8')).hexdigest()
        self.cq_findings.append(finding)

    def check(self, content, **kwargs):
        '''
        Function for counting the number of failures in a TSV/CSV file exported by Polyspace

        Args:
            content (_io.TextIOWrapper): The open file to parse
        '''
        if kwargs["file_extension"] == ".tsv":
            reader = csv.DictReader(content, delimiter="\t")
        elif kwargs["file_extension"] == ".csv":
            reader = csv.DictReader(content)
        # set column names to lowercase
        reader.fieldnames = [name.lower() for name in reader.fieldnames]

        for row in reader:
            for checker in self.checkers:
                if row['family'].lower() == checker.family_value:
                    if row[checker.column_name].lower() == checker.check_value:
                        checker.count = checker.count + 1
                        checker.counted_warnings.append('family: {} -> {}: {}'.format(
                            checker.family_value,
                            checker.column_name,
                            checker.check_value
                        ))
                        if self.cq_enabled:
                            self.add_code_quality_finding(row)

    def return_count(self):
        ''' Getter function for the amount of warnings found

        Returns:
            int: Number of warnings found
        '''
        self.count = 0
        for checker in self.checkers:
            self.count += checker.return_count()
        return self.count

    def return_check_limits(self):
        ''' Function for checking whether the warning count is within the configured limits

        Returns:
            int: 0 if the amount of warnings is within limits, the count of warnings otherwise
                (or 1 in case of a count of 0 warnings)
        '''
        count = 0
        for checker in self.checkers:
            print(
                'Counted failures for family {!r} \'{}\': \'{}\''
                .format(checker.family_value, checker.column_name, checker.check_value)
            )
            count += checker.return_check_limits()
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
                self.cq_description_template = Template(config['cq_description_template'])
                continue
            if family_value == "cq_default_path":
                self.cq_default_path = config['cq_default_path']
                continue
            for check in data:
                for key, value in check.items():
                    if key in ["min", "max"]:
                        continue
                    column_name = key.lower()
                    check_value = value.lower()
                    checker = PolyspaceFamilyChecker(family_value, column_name, check_value, verbose=self.verbose)
                    checker.parse_config(check)
                    self.checkers.append(checker)
                if not (column_name and check_value):
                    raise ValueError(
                        "Expected a list of dicts as value of the key which represents the value of the "
                        "'Family' column. These dicts need to consist 3 key-value pairs (Note: if 'min' or "
                        "'max' is not defined, it will get the default value of 0):\n"
                        "{\n    <column_name>: <value_to_check>,\n    min: <number>,\n    max: <number>\n};"
                        f"got {column_name} as column_name and {check_value} as value_to_check"
                    )


class PolyspaceSubChecker(WarningsChecker):

    def __init__(self, family_value, column_name, check_value, **kwargs):
        """Initialize the PolyspaceSubChecker

        Args:
            family_value (str): The value to search for in the 'Family' column
            column_name (str): The name of the column
            check_value (str): The value to check in the column
            minimum (int): The minimum amount the check_value can occur
            maximum (int): The maximum amount the check_value can occur
        """
        super().__init__(**kwargs)
        self.family_value = family_value
        self.column_name = column_name
        self.check_value = check_value

    def return_count(self):
        ''' Getter function for the amount of warnings found

        Returns:
            int: Number of warnings found
        '''
        print("{} warnings found for {!r}: {!r}".format(self.count, self.column_name, self.check_value))
        return self.count

import csv

from .warnings_checker import WarningsChecker


class PolyspaceChecker(WarningsChecker):
    name = 'polyspace'
    checkers = []

    @property
    def counted_warnings(self, name):
        ''' List: list of counted warnings (str) '''
        all_counted_warnings = []
        for checker in self.checkers[name]:
            all_counted_warnings.extend(checker.counted_warnings)
        return all_counted_warnings

    def check(self, content, **kwargs):
        '''
        Function for counting the number of failures in a TSV/CSV file exported by Polyspace

        Args:
            content (_io.TextIOWrapper): The open file to parse
            file_extension (str): The file extenstion
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

    def return_count(self):
        ''' Getter function for the amount of warnings found

        Returns:
            int: Number of warnings found
        '''
        self.count = 0
        for checker in self.checkers:
            print("{0.count} warnings found for '{0.column_name}: {0.check_value}'".format(checker))
            self.count += checker.count
        return self.count

    def return_check_limits(self):
        ''' Function for checking whether the warning count is within the configured limits

        Returns:
            int: 0 if the amount of warnings is within limits, the count of warnings otherwise
                (or 1 in case of a count of 0 warnings)
        '''
        check_failures = 0
        if len(self.checkers) == 0:
            print("Warning: There are no polyspace checks recognised. Please specify them in a configuration file.")
        for checker in self.checkers:
            print('Counted failures for {!r}: {!r}.'.format(checker.column_name, checker.check_value))
            self.count = checker.count
            self.warn_min = checker.minimum
            self.warn_max = checker.maximum
            if checker.count > checker.maximum or checker.count < checker.minimum:
                check_failures += 1
                self._return_error_code()
            elif self.warn_min == self.warn_max and self.count == self.warn_max:
                print("Number of warnings ({0.count}) is exactly as expected. Well done.".format(self))
            else:
                print(
                    "Number of warnings ({0.count}) is between limits {0.warn_min} and {0.warn_max}. Well done."
                    .format(self)
                )
        self.warn_min = 0
        self.warn_max = 0
        self.count = check_failures
        return check_failures

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
            for check in data:
                for key, value in check.items():
                    if key == "min":
                        minimum = value
                    elif key == "max":
                        maximum = value
                    else:
                        column_name = key.lower()
                        check_value = value.lower()
                if not minimum:
                    minimum = 0
                if not maximum:
                    maximum = 0
                if not (column_name and check_value):
                    raise ValueError(
                        "Expected a list of dicts as value of the key which represents the value of the "
                        "'Family' column. These dicts need to consist 3 key-value pairs (Note: if 'min' or "
                        "'max' is not defined, it will get the default value of 0):\n"
                        "{\n    <column-name>: <value_to_check>,\n    min: <number>,\n    max: <number>\n};"
                        f"got\n{{\n    {column_name}: {check_value},\n    min: {minimum},\n    max: {maximum}\n}}\n"
                    )
                self.checkers.append(PolyspaceCheck(family_value, column_name, check_value, minimum, maximum))


class PolyspaceCheck:

    def __init__(self, family_value, column_name, check_value, minimum, maximum):
        """Initialize the PolyspaceCheck

        Args:
            family_value (str): The value to search for in the 'Family' column
            column_name (str): The name of the column
            check_value (str): The value to check in the column
            minimum (int): The minimum amount the check_value can occur
            maximum (int): The maximum amount the check_value can occur
        """
        self.family_value = family_value
        self.column_name = column_name
        self.check_value = check_value
        self.minimum = minimum
        self.maximum = maximum
        self.count = 0

    def get_minimum(self):
        ''' Gets the lowest minimum amount of warnings

        Returns:
            int: the lowest minimum for warnings
        '''
        return self.minimum

    def get_maximum(self):
        ''' Gets the highest minimum amount of warnings

        Returns:
            int: the highest maximum for warnings
        '''
        return self.maximum

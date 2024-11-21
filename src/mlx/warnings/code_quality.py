
import hashlib
from pathlib import Path


class Finding:
    """Code quality violation"""

    """A dictionary mapping fingerprints (unique hashes) to instances of Finding"""
    fingerprints = {}

    _severity = "info"
    _path = ""
    _line = 1
    _column = 1

    def __init__(self, description):
        if not description:
            raise ValueError(f"Expected a non empty description; Got {description!r}")
        self.description = description

    @property
    def fingerprint(self):
        """str: The unique fingerprint to identify this specific code quality violation.

        The fingerprint is generated as follows:

        1. A base string is created by concatenating the severity, path, and description of the finding.
        2. The base string is hashed to produce an initial hash.
        3. If the hash already exists (hash collision), a new hash is generated by concatenating the base string
           with the current hash and hashing the result.
        4. Step 3 is repeated until a unique hash is obtained.
        """
        hashable_string = f"{self.severity}{self.path}{self.description}"
        new_hash = hashlib.md5(str(hashable_string).encode('utf-8')).hexdigest()
        while new_hash in self.fingerprints and self.fingerprints[new_hash] != self:
            new_hash = hashlib.md5(f"{hashable_string}{new_hash}".encode('utf-8')).hexdigest()
        type(self).fingerprints[new_hash] = self
        return new_hash

    @property
    def severity(self):
        """str: The severity of the violation."""
        return self._severity

    @severity.setter
    def severity(self, value):
        expected_values = ["info", "minor", "major", "critical", "blocker"]
        if value not in expected_values:
            raise ValueError(f"Expected severity to be one of {expected_values}; Got {value!r}")
        self._severity = value

    @property
    def path(self):
        """str: The file containing the code quality violation, expressed as a relative path in the repository."""
        return self._path

    @path.setter
    def path(self, value):
        path = Path(value)
        if path.is_absolute():
            try:
                path = path.relative_to(Path.cwd())
            except ValueError as err:
                raise ValueError("Failed to convert abolute path to relative path for Code Quality report: "
                                 f"{err}") from err
        self._path = str(path)

    @property
    def line(self):
        """int: The line on which the code quality violation occurred. Defaults to 1."""
        return self._line

    @line.setter
    def line(self, value):
        try:
            line_number = int(value)
        except (TypeError, ValueError):
            line_number = 1

        if line_number <= 0:
            raise ValueError(f"Expected line number greater than 0; Got {line_number}")
        self._line = line_number

    @property
    def column(self):
        """int: The column on which the code quality violation occurred. Defaults to 1."""
        return self._column

    @column.setter
    def column(self, value):
        column_number = int(value)
        if column_number <= 0:
            raise ValueError(f"Expected column number greater than 0; Got {column_number}")
        self._column = column_number

    def to_dict(self):
        """Returns the code quality finding as dictionary with a unique fingerprint.

        Returns:
            dict: The code quality finding
        """
        return {
            "severity": self.severity,
            "description": self.description,
            "location": {
                "path": self.path,
                "positions": {
                    "begin": {
                        "line": self.line,
                        "column": self.column
                    }
                }
            },
            "fingerprint": self.fingerprint
        }




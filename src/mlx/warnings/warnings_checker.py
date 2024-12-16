# SPDX-License-Identifier: Apache-2.0

import abc
import logging
import os
import re
from math import inf
from string import Template

from .exceptions import WarningsConfigError


def substitute_envvar(checker_config, keys):
    """Modifies configuration for checker inplace, resolving any environment variables for ``keys``

    Args:
        checker_config (dict): Configuration for a specific WarningsChecker
        keys (set): Set of keys to process the value of

    Raises:
        WarningsConfigError: Failed to find an environment variable
    """
    for key in keys:
        if key in checker_config and isinstance(checker_config[key], str):
            template_obj = Template(checker_config[key])
            try:
                checker_config[key] = template_obj.substitute(os.environ)
            except KeyError as err:
                raise WarningsConfigError(f"Failed to find environment variable {err} for configuration value {key!r}")\
                    from None


class DebugOnlyFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if record.levelno <= logging.DEBUG:
            return True
        return False


class WarningsChecker:
    name = "checker"
    logging_fmt = "{checker.name_repr}: {message}"

    def __init__(self, verbose, output):
        """Constructor

        The logging is configured. A handler is added only if a parent checker hasn't done this already.
        A parent-checker uses the same logger as its sub-checkers, but each with their own LoggerAdapter.

        Args:
            verbose (bool): Enable/disable verbose logging
            output (Path/None): The path to the output file
        """
        self.count = 0
        self._minimum = 0
        self._maximum = 0
        self._cq_findings = []
        self.cq_enabled = False
        self.cq_default_path = ".gitlab-ci.yml"
        self._cq_description_template = Template("$description")
        self.exclude_patterns = []
        self.include_patterns = []
        self.logging_args = (verbose, output)

        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.WARNING)
        if output:
            self.logger.setLevel(logging.DEBUG)
        elif verbose:
            self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter(fmt=self.logging_fmt, style="{")
        if not self.logger.handlers:
            self.logger.propagate = True  # Propagate to parent loggers
            handler = logging.StreamHandler()
            handler.setFormatter(formatter)
            if verbose:
                handler.setLevel(logging.INFO)
            else:
                handler.setLevel(logging.WARNING)
            self.logger.addHandler(handler)
            if output is not None:
                handler = logging.FileHandler(output, "a")
                handler.setFormatter(formatter)
                handler.setLevel(logging.DEBUG)
                handler.addFilter(DebugOnlyFilter())
                self.logger.addHandler(handler)
        logging_vars = {"checker": self}
        self.logger = logging.LoggerAdapter(self.logger, extra=logging_vars)

    @property
    def name_repr(self):
        return self.name.replace("_sub", "").capitalize()

    @property
    def is_sub_checker(self):
        return self.name.endswith("_sub")

    @property
    def cq_findings(self):
        """List[dict]: list of code quality findings"""
        return self._cq_findings

    @property
    def cq_description_template(self):
        """Template: string.Template instance based on the configured template string"""
        return self._cq_description_template

    @cq_description_template.setter
    def cq_description_template(self, template_obj):
        try:
            template_obj.template = template_obj.substitute(os.environ, description="$description")
        except KeyError as err:
            raise WarningsConfigError(f"Failed to find environment variable from configuration value "
                                      f"'cq_description_template': {err}") from err
        self._cq_description_template = template_obj

    @property
    def maximum(self):
        """Getter function for the maximum amount of warnings

        Returns:
            int: Maximum amount of warnings
        """
        return self._maximum

    @maximum.setter
    def maximum(self, maximum):
        if maximum == -1:
            maximum = inf
        if self._minimum > maximum:
            raise ValueError("Invalid argument: maximum limit must be higher than minimum limit ({min}); cannot "
                             "set {max}.".format(max=maximum, min=self._minimum))
        self._maximum = maximum

    @property
    def minimum(self):
        """Getter function for the minimum amount of warnings

        Returns:
            int: Minimum amount of warnings
        """
        return self._minimum

    @minimum.setter
    def minimum(self, minimum):
        if minimum > self._maximum:
            raise ValueError("Invalid argument: minimum limit must be lower than maximum limit ({max}); cannot "
                             "set {min}.".format(min=minimum, max=self._maximum))
        self._minimum = minimum

    @abc.abstractmethod
    def check(self, content):
        """Function for counting the number of warnings in a specific text

        Args:
            content (str): The content to parse
        """
        return

    def add_patterns(self, regexes, pattern_container):
        """Adds regexes as patterns to the specified container

        Args:
            regexes (list[str]|None): List of regexes to add
            pattern_container (list[re.Pattern]): Target storage container for patterns
        """
        if regexes:
            if not isinstance(regexes, list):
                raise TypeError("Expected a list value for exclude key in configuration file; got {}"
                                .format(regexes.__class__.__name__))
            for regex in regexes:
                pattern_container.append(re.compile(regex))

    def return_count(self):
        """Getter function for the amount of warnings found

        Returns:
            int: Number of warnings found
        """
        return self.count

    def return_check_limits(self):
        """Function for checking whether the warning count is within the configured limits
        A checker instance with sub-checkers is responsible for printing 'Returning error code X.'
        when the exit code is not 0.

        Returns:
            int: 0 if the amount of warnings is within limits, the count of (the sum of sub-checker) warnings otherwise
                (or 1 in case of a count of 0 warnings)
        """
        if self.count > self._maximum or self.count < self._minimum:
            return self._return_error_code()
        elif self._minimum == self._maximum and self.count == self._maximum:
            msg = f"number of warnings ({self.count}) is exactly as expected. Well done."
        else:
            msg = f"number of warnings ({self.count}) is between limits {self._minimum} and {self._maximum}. Well done."
        self.logger.warning(msg)
        return 0

    def _return_error_code(self):
        """Function for determining the return code and message on failure

        Returns:
            int: The count of warnings (or 1 in case of a count of 0 warnings)
        """
        if self.count > self._maximum:
            error_reason = f"higher than the maximum limit ({self._maximum})"
        else:
            error_reason = f"lower than the minimum limit ({self._minimum})"

        error_code = self.count
        if error_code == 0:
            error_code = 1
        string_to_print = f"number of warnings ({self.count}) is {error_reason}."
        if not self.is_sub_checker:
            string_to_print += f" Returning error code {error_code}."
        self.logger.warning(string_to_print)
        return error_code

    def parse_config(self, config):
        substitute_envvar(config, {"min", "max"})
        self.maximum = int(config["max"])
        self.minimum = int(config["min"])
        self.add_patterns(config.get("exclude"), self.exclude_patterns)
        if "cq_default_path" in config:
            self.cq_default_path = config["cq_default_path"]
        if "cq_description_template" in config:
            self.cq_description_template = Template(config["cq_description_template"])

    def _is_excluded(self, content):
        """Checks if the specific text must be excluded based on the configured regexes for exclusion and inclusion.

        Inclusion has priority over exclusion.

        Args:
            content (str): The content to parse

        Returns:
            bool: True for exclusion, False for inclusion
        """
        matching_exclude_pattern = self._search_patterns(content, self.exclude_patterns)
        if not self._search_patterns(content, self.include_patterns) and matching_exclude_pattern:
            self.logger.info(f"Excluded {content!r} because of configured regex {matching_exclude_pattern!r}")
            return True
        return False

    @staticmethod
    def _search_patterns(content, patterns):
        """Returns the regex of the first pattern that matches specified content, None if nothing matches"""
        for pattern in patterns:
            if pattern.search(content):
                return pattern.pattern
        return None

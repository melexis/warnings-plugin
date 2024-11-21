# SPDX-License-Identifier: Apache-2.0

import abc
from math import inf
import os
import re
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


class WarningsChecker:
    name = 'checker'

    def __init__(self, verbose=False):
        ''' Constructor

        Args:
            name (str): Name of the checker
            verbose (bool): Enable/disable verbose logging
        '''
        self.verbose = verbose
        self.count = 0
        self._minimum = 0
        self._maximum = 0
        self._counted_warnings = []
        self._cq_findings = []
        self.cq_enabled = False
        self.cq_default_path = '.gitlab-ci.yml'
        self._cq_description_template = Template('$description')
        self.exclude_patterns = []
        self.include_patterns = []

    @property
    def cq_findings(self):
        ''' List[dict]: list of code quality findings'''
        return self._cq_findings

    @property
    def counted_warnings(self):
        ''' List[str]: list of counted warnings'''
        return self._counted_warnings

    @property
    def cq_description_template(self):
        ''' Template: string.Template instance based on the configured template string '''
        return self._cq_description_template

    @cq_description_template.setter
    def cq_description_template(self, template_obj):
        try:
            template_obj.template = template_obj.substitute(os.environ, description='$description')
        except KeyError as err:
            raise WarningsConfigError(f"Failed to find environment variable from configuration value "
                                      f"'cq_description_template': {err}") from err
        self._cq_description_template = template_obj

    @property
    def maximum(self):
        ''' Getter function for the maximum amount of warnings

        Returns:
            int: Maximum amount of warnings
        '''
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
        ''' Getter function for the minimum amount of warnings

        Returns:
            int: Minimum amount of warnings
        '''
        return self._minimum

    @minimum.setter
    def minimum(self, minimum):
        if minimum > self._maximum:
            raise ValueError("Invalid argument: minimum limit must be lower than maximum limit ({max}); cannot "
                             "set {min}.".format(min=minimum, max=self._maximum))
        self._minimum = minimum

    @abc.abstractmethod
    def check(self, content):
        ''' Function for counting the number of warnings in a specific text

        Args:
            content (str): The content to parse
        '''
        return

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

    def return_count(self):
        ''' Getter function for the amount of warnings found

        Returns:
            int: Number of warnings found
        '''
        print("{0.count} {0.name} warnings found".format(self))
        return self.count

    def return_check_limits(self):
        ''' Function for checking whether the warning count is within the configured limits

        Returns:
            int: 0 if the amount of warnings is within limits, the count of warnings otherwise
                (or 1 in case of a count of 0 warnings)
        '''
        if self.count > self._maximum or self.count < self._minimum:
            return self._return_error_code()
        elif self._minimum == self._maximum and self.count == self._maximum:
            print("Number of warnings ({0.count}) is exactly as expected. Well done."
                  .format(self))
        else:
            print("Number of warnings ({0.count}) is between limits {0._minimum} and {0._maximum}. Well done."
                  .format(self))
        return 0

    def _return_error_code(self):
        ''' Function for determining the return code and message on failure

        Returns:
            int: The count of warnings (or 1 in case of a count of 0 warnings)
        '''
        if self.count > self._maximum:
            error_reason = "higher than the maximum limit ({0._maximum})".format(self)
        else:
            error_reason = "lower than the minimum limit ({0._minimum})".format(self)

        error_code = self.count
        if error_code == 0:
            error_code = 1
        print("Number of warnings ({0.count}) is {1}. Returning error code {2}."
              .format(self, error_reason, error_code))
        return error_code

    def print_when_verbose(self, message):
        ''' Prints message only when verbose mode is enabled.

        Args:
            message (str): Message to conditionally print
        '''
        if self.verbose:
            print(message)

    def parse_config(self, config):
        substitute_envvar(config, {'min', 'max'})
        self.maximum = int(config['max'])
        self.minimum = int(config['min'])
        self.add_patterns(config.get("exclude"), self.exclude_patterns)
        if 'cq_default_path' in config:
            self.cq_default_path = config['cq_default_path']
        if 'cq_description_template' in config:
            self.cq_description_template = Template(config['cq_description_template'])

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

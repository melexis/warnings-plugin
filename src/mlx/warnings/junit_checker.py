# SPDX-License-Identifier: Apache-2.0

try:
    from lxml import etree
except ImportError:
    from xml.etree import ElementTree as etree

from junitparser import Error, Failure, JUnitXml

from .warnings_checker import WarningsChecker


class JUnitChecker(WarningsChecker):
    name = "junit"

    def check(self, content):
        """Function for counting the number of JUnit failures in a specific text

        Args:
            content (str): The content to parse
        """
        try:
            root_input = etree.fromstring(content.encode("utf-8"))
            testsuites_root = self.prepare_tree(root_input)
            suites = JUnitXml.fromelem(testsuites_root)
            amount_to_exclude = self._traverse_suites(suites)
            self.count += suites.failures + suites.errors - amount_to_exclude
        except etree.ParseError as err:
            self.logger.error(err.msg)

    @property
    def name_repr(self):
        return "JUnit" if self.name == "junit" else super().name_repr

    @staticmethod
    def prepare_tree(root_input):
        """Prepares the tree element by adding a testsuites element as root when missing (to please JUnitXml)

        Args:
            root_input (lxml.etree._Element/xml.etree.ElementTree.Element): Top-level XML element from input file

        Returns:
            lxml.etree._Element/xml.etree.ElementTree.Element: Top-level XML element with testsuites tag
        """
        if root_input.tag.startswith("testsuite") and root_input.find("testcase") is None:
            testsuites_root = root_input
        else:
            testsuites_root = etree.Element("testsuites")
            testsuites_root.append(root_input)
        return testsuites_root

    def _check_testcase(self, testcase):
        """Handles the check of a test case element by checking if the result is a failure/error.

        If it is to be excluded by a configured regex, 1 is returned.
        Otherwise, when in verbose/output mode, the suite name and test case name are printed/written
        In output mode, the failure/error message is written additionally.

        Args:
            testcase (junitparser.TestCase): Test case element to check for failure or error

        Returns:
            int: 1 if a failure/error is to be subtracted from the final count, 0 otherwise
        """
        if isinstance(testcase.result, (Failure, Error)):
            if self._is_excluded(testcase.result.message):
                return 1
            self.logger.info(f"{testcase.classname}.{testcase.name}")
            self.logger.debug(f"{testcase.classname}.{testcase.name} | {testcase.result.message}")
        return 0

    def _traverse_suites(self, suites):
        """Traverses through all test suites, including nested suites, to check for test case failures.

        This method performs a depth-first traversal of the test suites.

        Args:
            suites (junitparser.JUnitXml): A collection of test suites.

        Returns:
            int: The total number of failures to exclude based on the configured regex.
        """
        amount_to_exclude = 0
        for suite in suites:
            for testcase in suite:
                amount_to_exclude += self._check_testcase(testcase)
            if hasattr(suite, "testsuites"):
                sub_suites = suite.testsuites()
                if sub_suites:
                    amount_to_exclude += self._traverse_suites(sub_suites)
        return amount_to_exclude

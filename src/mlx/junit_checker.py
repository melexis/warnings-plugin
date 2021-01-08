import sys
import xml.etree.ElementTree as ET

from junitparser import Error, Failure, JUnitXml

from mlx.warnings_checker import WarningsChecker


class JUnitChecker(WarningsChecker):
    name = 'junit'

    def check(self, content):
        ''' Function for counting the number of JUnit failures in a specific text

        If this class is subclassed, the test cases with a ``classname`` that does
        not end with the ``name`` class attribute are ignored.

        Args:
            content (str): The content to parse
        '''
        try:
            root_input = ET.fromstring(content.encode('utf-8'))
            testsuites_root = self.prepare_tree(root_input)
            suites = JUnitXml.fromelem(testsuites_root)
            amount_to_exclude = 0
            for suite in suites:
                for testcase in suite:
                    amount_to_exclude += self._check_testcase(testcase)
            suites.update_statistics()
            self.count += suites.failures + suites.errors - amount_to_exclude
            if not getattr(self, 'is_valid_suite_name', True) and getattr(self, 'check_suite_name', False):
                print('ERROR: No suite with name {!r} found. Returning error code -1.'.format(self.name))
                sys.exit(-1)
        except ET.ParseError as err:
            print(err)

    @staticmethod
    def prepare_tree(root_input):
        ''' Prepares the tree element by adding a testsuites element as root when missing (to please JUnitXml)

        Args:
            root_input (lxml.etree._Element): Top-level XML element from input file

        Returns:
            lxml.etree._Element: Top-level XML element with testsuites tag
        '''
        if root_input.tag == 'testsuites':
            testsuites_root = root_input
        else:
            testsuites_root = ET.Element("testsuites")
            testsuites_root.append(root_input)
        return testsuites_root

    def _check_testcase(self, testcase):
        """ Handles the check of a test case element by checking if the result is a failure/error.

        If it is to be excluded by a configured regex, 1 is returned.
        Otherwise, when in verbose mode, the suite name and test case name are printed.

        Args:
            testcase (junitparser.TestCase): Test case element to check for failure or error

        Returns:
            int: 1 if a failure/error is to be subtracted from the final count, 0 otherwise
        """
        if isinstance(testcase.result, (Failure, Error)):
            if self._is_excluded(testcase.result.message):
                return 1
            self.print_when_verbose('{classname}.{testname}'.format(classname=testcase.classname,
                                                                    testname=testcase.name))
        return 0

try:
    from lxml import etree
except ImportError:
    from xml.etree import ElementTree as etree

from junitparser import Error, Failure, JUnitXml

from .warnings_checker import WarningsChecker


class JUnitChecker(WarningsChecker):
    name = 'junit'

    def check(self, content):
        ''' Function for counting the number of JUnit failures in a specific text

        Args:
            content (str): The content to parse
        '''
        try:
            root_input = etree.fromstring(content.encode('utf-8'))
            testsuites_root = self.prepare_tree(root_input)
            suites = JUnitXml.fromelem(testsuites_root)
            amount_to_exclude = 0
            for suite in suites:
                for testcase in suite:
                    amount_to_exclude += self._check_testcase(testcase)
            suites.update_statistics()
            self.count += suites.failures + suites.errors - amount_to_exclude
        except etree.ParseError as err:
            print(err)

    @staticmethod
    def prepare_tree(root_input):
        ''' Prepares the tree element by adding a testsuites element as root when missing (to please JUnitXml)

        Args:
            root_input (lxml.etree._Element/xml.etree.ElementTree.Element): Top-level XML element from input file

        Returns:
            lxml.etree._Element/xml.etree.ElementTree.Element: Top-level XML element with testsuites tag
        '''
        if root_input.tag.startswith('testsuite') and root_input.find('testcase') is None:
            testsuites_root = root_input
        else:
            testsuites_root = etree.Element("testsuites")
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
            string = '{classname}.{testname}'.format(classname=testcase.classname, testname=testcase.name)
            self.counted_warnings.append('{}: {}'.format(string, testcase.result.message))
            self.print_when_verbose(string)
        return 0

from junitparser import Error, Failure, JUnitXml
from lxml import etree as ET

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
            for suite in suites:
                for testcase in tuple(suite):
                    if type(self) != JUnitChecker and self.name and not testcase.classname.endswith(self.name):
                        suite.remove_testcase(testcase)
                    elif isinstance(testcase.result, (Failure, Error)):
                        self.print_when_verbose('{classname}.{testname}'.format(classname=testcase.classname,
                                                                                testname=testcase.name))
            suites.update_statistics()
            self.count += suites.failures + suites.errors
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

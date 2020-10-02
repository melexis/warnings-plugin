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
            if root_input.tag == 'testsuites':
                test_suites = root_input
            else:
                test_suites = ET.Element("testsuites")
                test_suites.append(root_input)

            suites = JUnitXml.fromelem(test_suites)
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

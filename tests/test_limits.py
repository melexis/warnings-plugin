from unittest import TestCase

from mlx.warnings import WarningsPlugin, DoxyChecker


class TestLimits(TestCase):

    def setUp(self):
        self.warnings = WarningsPlugin(verbose=True)
        self.warnings.activate_checker_name('doxygen')

    def test_set_maximum(self):
        for x in range(0, 10):
            self.warnings.set_maximum(x)
            self.assertEqual(self.warnings.get_checker(DoxyChecker.name).get_maximum(), x)

    def test_set_minimum(self):
        # Setting minimum is tricky - we need to max out maximum
        self.warnings.set_maximum(11)
        for x in range(0, 10):
            self.warnings.set_minimum(x)
            self.assertEqual(self.warnings.get_checker(DoxyChecker.name).get_minimum(), x)

    def test_set_minimum_fail(self):
        self.warnings.set_maximum(5)
        for x in range(1, 5):
            self.warnings.set_minimum(x)
            self.assertEqual(self.warnings.get_checker(DoxyChecker.name).get_minimum(), x)

        for x in range(6, 10):
            self.assertRaises(ValueError, self.warnings.set_minimum, x)

    def test_return_values_maximum_decrease(self):
        self.warnings.check('testfile.c:6: warning: group test: ignoring title "Some test functions" that does not match old title "Some freaky test functions"')
        self.assertEqual(self.warnings.return_count(), 1)
        self.warnings.set_maximum(1)
        self.assertEqual(self.warnings.return_check_limits(), 0)
        self.warnings.set_maximum(0)
        self.assertEqual(self.warnings.return_check_limits(), 1)

    def test_return_values_maximum_increase(self):
        self.warnings.check('testfile.c:6: warning: group test: ignoring title "Some test functions" that does not match old title "Some freaky test functions"')
        self.assertEqual(self.warnings.return_count(), 1)
        self.warnings.check('testfile.c:12: warning: group test: ignoring title "Some test functions" that does not match old title "Some freaky test functions"')
        self.assertEqual(self.warnings.return_count(), 2)
        self.warnings.set_maximum(1)
        self.assertEqual(self.warnings.return_check_limits(), 2)
        self.warnings.set_maximum(2)
        self.assertEqual(self.warnings.return_check_limits(), 0)

    def test_return_values_minimum_increase(self):
        self.warnings.check('testfile.c:6: warning: group test: ignoring title "Some test functions" that does not match old title "Some freaky test functions"')
        self.assertEqual(self.warnings.return_count(), 1)
        self.warnings.check('testfile.c:6: warning: group test: ignoring title "Some test functions" that does not match old title "Some freaky test functions"')
        self.assertEqual(self.warnings.return_count(), 2)
        # default behavior
        self.assertEqual(self.warnings.return_check_limits(), 2)

        # to set minimum we need to make maximum higher
        self.warnings.set_maximum(10)
        for x in range(1, 10):
            if x <= 3:
                self.assertEqual(self.warnings.return_check_limits(), 0)
            else:
                self.assertEqual(self.warnings.return_check_limits(), 2)
            self.warnings.set_minimum(x)



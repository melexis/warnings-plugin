from unittest import TestCase

from mlx.warnings import WarningsPlugin, DoxyChecker


class TestLimits(TestCase):

    def test_set_maximum(self):
        warnings = WarningsPlugin(False, True, False)
        for x in range(0, 10):
            warnings.set_maximum(x)
            self.assertEqual(warnings.get_checker(DoxyChecker.name).get_maximum(), x)

    def test_set_minimum(self):
        warnings = WarningsPlugin(False, True, False)
        # Setting minimum is tricky - we need to max out maximum
        warnings.set_maximum(11)
        for x in range(0, 10):
            warnings.set_minimum(x)
            self.assertEqual(warnings.get_checker(DoxyChecker.name).get_minimum(), x)

    def test_set_minimum_fail(self):
        warnings = WarningsPlugin(False, True, False)
        warnings.set_maximum(5)
        for x in range(1, 5):
            warnings.set_minimum(x)
            self.assertEqual(warnings.get_checker(DoxyChecker.name).get_minimum(), x)

        for x in range(6, 10):
            self.assertRaises(ValueError, warnings.set_minimum, x)

    def test_return_values_maximum_decrease(self):
        warnings = WarningsPlugin(False, True, False)
        warnings.check('testfile.c:6: warning: group test: ignoring title "Some test functions" that does not match old title "Some freaky test functions"')
        self.assertEqual(warnings.return_count(), 1)
        warnings.set_maximum(1)
        self.assertEqual(warnings.return_check_limits(), 0)
        warnings.set_maximum(0)
        self.assertEqual(warnings.return_check_limits(), 1)

    def test_return_values_maximum_increase(self):
        warnings = WarningsPlugin(False, True, False)
        warnings.check('testfile.c:6: warning: group test: ignoring title "Some test functions" that does not match old title "Some freaky test functions"')
        self.assertEqual(warnings.return_count(), 1)
        warnings.check('testfile.c:12: warning: group test: ignoring title "Some test functions" that does not match old title "Some freaky test functions"')
        self.assertEqual(warnings.return_count(), 2)
        warnings.set_maximum(1)
        self.assertEqual(warnings.return_check_limits(), 2)
        warnings.set_maximum(2)
        self.assertEqual(warnings.return_check_limits(), 0)

    def test_return_values_minimum_increase(self):
        warnings = WarningsPlugin(False, True, False)
        warnings.check('testfile.c:6: warning: group test: ignoring title "Some test functions" that does not match old title "Some freaky test functions"')
        self.assertEqual(warnings.return_count(), 1)
        warnings.check('testfile.c:6: warning: group test: ignoring title "Some test functions" that does not match old title "Some freaky test functions"')
        self.assertEqual(warnings.return_count(), 2)
        # default behavior
        self.assertEqual(warnings.return_check_limits(), 2)

        # to set minimum we need to make maximum higher
        warnings.set_maximum(10)
        for x in range(1, 10):
            if x <= 3:
                self.assertEqual(warnings.return_check_limits(), 0)
            else:
                self.assertEqual(warnings.return_check_limits(), 2)
            warnings.set_minimum(x)



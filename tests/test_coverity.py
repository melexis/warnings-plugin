from unittest import TestCase

from mlx.warnings import WarningsPlugin


class TestCoverityWarnings(TestCase):
    def setUp(self):
        self.warnings = WarningsPlugin(verbose=True)
        self.warnings.activate_checker_name('coverity')

    def test_config_vars_not_set(self):
        with self.assertRaises(ValueError):
            self.warnings.check('fakefile')


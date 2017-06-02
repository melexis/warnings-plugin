from unittest import TestCase

from mlx.warnings import WarningsPlugin


class TestSphinxWarnings(TestCase):
    def test(self):
        warnings = WarningsPlugin()
        warnings.check_sphinx_warnings('This should not be treated as warning')
        retval = warnings.return_sphinx_warnings()

        assert retval == 0

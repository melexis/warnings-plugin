import filecmp
import os
import unittest
from pathlib import Path

import pytest

from mlx.warnings import (
    Finding,
    PolyspaceFamilyChecker,
    WarningsPlugin,
    warnings_wrapper,
)

TEST_IN_DIR = Path(__file__).parent / 'test_in'
TEST_OUT_DIR = Path(__file__).parent / 'test_out'


class TestCodeProverWarnings(unittest.TestCase):
    @pytest.fixture(autouse=True)
    def caplog(self, caplog):
        self.caplog = caplog

    def setUp(self):
        Finding.fingerprints = {}
        self.warnings = WarningsPlugin()
        self.dut = self.warnings.activate_checker_name('polyspace', False, None)
        self.dut.checkers = [
            PolyspaceFamilyChecker("run-time check", "color", "red", *self.dut.logging_args),
            PolyspaceFamilyChecker("run-time check", "color", "orange", *self.dut.logging_args),
        ]

    def test_code_prover_tsv_file(self):
        with open(TEST_IN_DIR / 'polyspace.tsv', newline="") as file:
            self.warnings.check_logfile(file)
            count = self.warnings.return_check_limits()
        self.assertEqual(
            ["number of warnings (0) is exactly as expected. Well done.",
             "number of warnings (19) is higher than the maximum limit (0).",
             "Returning error code 19."],
            self.caplog.messages
        )
        self.assertEqual(count, 19)


class TestBugFinderWarnings(unittest.TestCase):
    @pytest.fixture(autouse=True)
    def caplog(self, caplog):
        self.caplog = caplog

    def setUp(self):
        self.warnings = WarningsPlugin()
        self.dut = self.warnings.activate_checker_name('polyspace', False, None)
        self.dut.checkers = [
            PolyspaceFamilyChecker("defect", "information", "impact: high", *self.dut.logging_args),
            PolyspaceFamilyChecker("defect", "information", "impact: medium", *self.dut.logging_args),
            PolyspaceFamilyChecker("defect", "information", "impact: low", *self.dut.logging_args),
        ]

    def test_bug_finder_tsv_file(self):
        with open(TEST_IN_DIR / 'polyspace.tsv', newline="") as file:
            self.warnings.check_logfile(file)
            count = self.warnings.return_check_limits()
        self.assertEqual(
            ["number of warnings (42) is higher than the maximum limit (0).",
             "number of warnings (9) is higher than the maximum limit (0).",
             "number of warnings (4) is higher than the maximum limit (0).",
             "Returning error code 55."],
            self.caplog.messages
        )
        self.assertEqual(count, 55)


class TestPolyspaceWarnings(unittest.TestCase):
    def setUp(self):
        Finding.fingerprints = {}
        os.environ['MIN_POLY_WARNINGS'] = '0'
        os.environ['MAX_POLY_WARNINGS'] = '0'

    def tearDown(self):
        for var in ('MIN_POLY_WARNINGS', 'MAX_POLY_WARNINGS'):
            if var in os.environ:
                del os.environ[var]

    def test_config_file(self):
        retval = warnings_wrapper([
            '--config', str(TEST_IN_DIR / 'config_example_polyspace.yml'),
            str(TEST_IN_DIR / 'polyspace.tsv')
        ])
        self.assertEqual(61, retval)

    def test_code_quality(self):
        filename = 'polyspace_code_quality.json'
        out_file = str(TEST_OUT_DIR / filename)
        ref_file = str(TEST_IN_DIR / filename)
        retval = warnings_wrapper([
            '--code-quality', out_file,
            '--config', str(TEST_IN_DIR / 'config_example_polyspace.yml'),
            str(TEST_IN_DIR / 'polyspace.tsv'),
        ])
        self.assertEqual(61, retval)
        self.assertTrue(filecmp.cmp(out_file, ref_file))

    def test_code_quality_no_green(self):
        out_file = str(TEST_OUT_DIR / 'polyspace_code_quality_green.json')
        ref_file = str(TEST_IN_DIR / 'polyspace_code_quality.json')
        retval = warnings_wrapper([
            '--code-quality', out_file,
            '--config', str(TEST_IN_DIR / 'config_example_polyspace_green.yml'),
            str(TEST_IN_DIR / 'polyspace.tsv'),
        ])
        self.assertEqual(61, retval)
        self.assertTrue(filecmp.cmp(out_file, ref_file))

    def test_exclude_yaml_config(self):
        os.environ['PRODUCT'] = '12345'
        filename = "polyspace_code_quality_exclude.json"
        out_file = str(TEST_OUT_DIR / filename)
        ref_file = str(TEST_IN_DIR / filename)
        retval = warnings_wrapper([
            '--code-quality', out_file,
            '--config', str(TEST_IN_DIR / 'config_example_polyspace_exclude.yml'),
            str(TEST_IN_DIR / 'polyspace.tsv'),
        ])
        self.assertEqual(42, retval)
        self.assertTrue(filecmp.cmp(out_file, ref_file))
        del os.environ["PRODUCT"]

    def test_exclude_json_config(self):
        os.environ['PRODUCT'] = '12345'
        filename = "polyspace_code_quality_exclude.json"
        out_file = str(TEST_OUT_DIR / filename)
        ref_file = str(TEST_IN_DIR / filename)
        retval = warnings_wrapper([
            '--code-quality', out_file,
            '--config', str(TEST_IN_DIR / 'config_example_polyspace_exclude.json'),
            str(TEST_IN_DIR / 'polyspace.tsv'),
        ])
        self.assertEqual(42, retval)
        self.assertTrue(filecmp.cmp(out_file, ref_file))
        del os.environ["PRODUCT"]


if __name__ == '__main__':
    unittest.main()

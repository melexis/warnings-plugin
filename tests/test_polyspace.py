import filecmp
import os
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from mlx.warnings import (
    Finding,
    PolyspaceFamilyChecker,
    WarningsPlugin,
    warnings_wrapper,
)

TEST_IN_DIR = Path(__file__).parent / 'test_in'
TEST_OUT_DIR = Path(__file__).parent / 'test_out'


class TestCodeProverWarnings(unittest.TestCase):
    def setUp(self):
        Finding.fingerprints = {}
        self.warnings = WarningsPlugin(verbose=True)
        self.dut = self.warnings.activate_checker_name('polyspace')
        self.dut.checkers = [
            PolyspaceFamilyChecker("run-time check", "color", "red"),
            PolyspaceFamilyChecker("run-time check", "color", "orange"),
        ]

    def test_code_prover_tsv_file(self):
        with open(TEST_IN_DIR / 'polyspace.tsv', newline="") as file:
            with patch('sys.stdout', new=StringIO()) as fake_out:
                self.warnings.check_logfile(file)
                count = self.warnings.return_count()
        stdout_log = fake_out.getvalue()

        count_sum = 0
        for checker in self.dut.checkers:
            count_sum += checker.count
            self.assertIn(
                f"{checker.count} warnings found for '{checker.column_name}': '{checker.check_value}'",
                stdout_log
            )
        self.assertEqual(count, count_sum)
        self.assertEqual(count, 19)


class TestBugFinderWarnings(unittest.TestCase):
    def setUp(self):
        self.warnings = WarningsPlugin(verbose=True)
        self.dut = self.warnings.activate_checker_name('polyspace')
        self.dut.checkers = [
            PolyspaceFamilyChecker("defect", "information", "impact: high"),
            PolyspaceFamilyChecker("defect", "information", "impact: medium"),
            PolyspaceFamilyChecker("defect", "information", "impact: low"),
        ]

    def test_bug_finder_tsv_file(self):
        with open(TEST_IN_DIR / 'polyspace.tsv', newline="") as file:
            with patch('sys.stdout', new=StringIO()) as fake_out:
                self.warnings.check_logfile(file)
                count = self.warnings.return_count()
        stdout_log = fake_out.getvalue()

        for checker in self.dut.checkers:
            self.assertIn(
                f"{checker.count} warnings found for '{checker.column_name}': '{checker.check_value}'",
                stdout_log
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

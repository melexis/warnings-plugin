import os
from io import StringIO
import unittest
from pathlib import Path

from unittest.mock import patch

from mlx.warnings import PolyspaceCheck, WarningsPlugin, warnings_wrapper

TEST_IN_DIR = Path(__file__).parent / 'test_in'


class TestCodeProverWarnings(unittest.TestCase):
    def setUp(self):
        self.warnings = WarningsPlugin(verbose=True)
        self.dut = self.warnings.activate_checker_name('polyspace')
        self.dut.checkers = [
            PolyspaceCheck("run-time check", "color", "red"),
            PolyspaceCheck("run-time check", "color", "orange"),
        ]

    def test_code_prover_tsv_file(self):
        with open(TEST_IN_DIR / 'polyspace.tsv', newline="") as file:
            with patch('sys.stdout', new=StringIO()) as fake_out:
                self.warnings.check(file, file_extension='.tsv')
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
        self.assertEqual(count, 24)

    def test_code_prover_csv_file(self):
        with open(TEST_IN_DIR / 'polyspace.csv', newline="") as file:
            with patch('sys.stdout', new=StringIO()) as fake_out:
                self.warnings.check(file, file_extension='.csv')
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
        self.assertEqual(count, 24)


class TestBugFinderWarnings(unittest.TestCase):
    def setUp(self):
        self.warnings = WarningsPlugin(verbose=True)
        self.dut = self.warnings.activate_checker_name('polyspace')
        self.dut.checkers = [
            PolyspaceCheck("defect", "information", "impact: high"),
            PolyspaceCheck("defect", "information", "impact: medium"),
            PolyspaceCheck("defect", "information", "impact: low"),
        ]

    def test_bug_finder_tsv_file(self):
        with open(TEST_IN_DIR / 'polyspace.tsv', newline="") as file:
            with patch('sys.stdout', new=StringIO()) as fake_out:
                self.warnings.check(file, file_extension='.tsv')
                count = self.warnings.return_count()
        stdout_log = fake_out.getvalue()

        for checker in self.dut.checkers:
            self.assertIn(
                f"{checker.count} warnings found for '{checker.column_name}': '{checker.check_value}'",
                stdout_log
            )
        self.assertEqual(count, 55)

    def test_bug_finder_csv_file(self):
        with open(TEST_IN_DIR / 'polyspace.csv', newline="") as file:
            with patch('sys.stdout', new=StringIO()) as fake_out:
                self.warnings.check(file, file_extension='.csv')
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
        self.assertEqual(count, 55)


class TestPolyspaceWarnings(unittest.TestCase):
    def setUp(self):
        os.environ['MIN_SPHINX_WARNINGS'] = '0'
        os.environ['MAX_SPHINX_WARNINGS'] = '0'

    def tearDown(self):
        for var in ('MIN_SPHINX_WARNINGS', 'MAX_SPHINX_WARNINGS'):
            if var in os.environ:
                del os.environ[var]

    def test_config_file(self):
        retval = warnings_wrapper(['--config', str(TEST_IN_DIR / 'config_example_polyspace.yml'),
                                   str(TEST_IN_DIR / 'polyspace.tsv')])
        self.assertEqual(66, retval)


if __name__ == '__main__':
    unittest.main()
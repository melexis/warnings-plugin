from io import StringIO
import unittest
from pathlib import Path

from unittest.mock import patch

from mlx.warnings import PolyspaceCheck, WarningsPlugin

TEST_IN_DIR = Path(__file__).parent / 'test_in'


class TestCodeProverWarnings(unittest.TestCase):
    def setUp(self):
        self.warnings = WarningsPlugin(verbose=True)
        self.dut = self.warnings.activate_checker_name('polyspace')
        self.dut.checkers = [
            PolyspaceCheck("run-time check", "color", "red", 0, 0),
            PolyspaceCheck("run-time check", "color", "orange", 0, 50),
        ]

    def test_code_prover_tsv_file(self):
        with open(TEST_IN_DIR / 'polyspace_code_prover.tsv', newline="") as file:
            with patch('sys.stdout', new=StringIO()) as fake_out:
                self.warnings.check(file, file_extension='.tsv')
                count = self.warnings.return_count()
        stdout_log = fake_out.getvalue()

        count_sum = 0
        for checker in self.dut.checkers:
            count_sum += checker.count
            self.assertIn(
                f"{checker.count} warnings found for '{checker.column_name}: {checker.check_value}'",
                stdout_log
            )
        self.assertEqual(count, count_sum)
        self.assertEqual(count, 169)

    def test_code_prover_csv_file(self):
        with open(TEST_IN_DIR / 'polyspace_code_prover.csv', newline="") as file:
            with patch('sys.stdout', new=StringIO()) as fake_out:
                self.warnings.check(file, file_extension='.csv')
                count = self.warnings.return_count()
        stdout_log = fake_out.getvalue()

        count_sum = 0
        for checker in self.dut.checkers:
            count_sum += checker.count
            self.assertIn(
                f"{checker.count} warnings found for '{checker.column_name}: {checker.check_value}'",
                stdout_log
            )
        self.assertEqual(count, count_sum)
        self.assertEqual(count, 169)


class TestBugFinderWarnings(unittest.TestCase):
    def setUp(self):
        self.warnings = WarningsPlugin(verbose=True)
        self.dut = self.warnings.activate_checker_name('polyspace')
        self.dut.checkers = [
            PolyspaceCheck("defect", "information", "impact: high", 0, 55),
            PolyspaceCheck("defect", "information", "impact: medium", 0, 70),
            PolyspaceCheck("defect", "information", "impact: low", 0, 100),
        ]

    def test_bug_finder_tsv_file(self):
        with open(TEST_IN_DIR / 'polyspace_bug_finder.tsv', newline="") as file:
            with patch('sys.stdout', new=StringIO()) as fake_out:
                self.warnings.check(file, file_extension='.tsv')
                count = self.warnings.return_count()
        stdout_log = fake_out.getvalue()

        count_sum = 0
        for checker in self.dut.checkers:
            count_sum += checker.count
            self.assertIn(
                f"{checker.count} warnings found for '{checker.column_name}: {checker.check_value}'",
                stdout_log
            )
        self.assertEqual(count, count_sum)
        self.assertEqual(count, 75)

    def test_bug_finder_csv_file(self):
        with open(TEST_IN_DIR / 'polyspace_bug_finder.csv', newline="") as file:
            with patch('sys.stdout', new=StringIO()) as fake_out:
                self.warnings.check(file, file_extension='.csv')
                count = self.warnings.return_count()
        stdout_log = fake_out.getvalue()

        count_sum = 0
        for checker in self.dut.checkers:
            count_sum += checker.count
            self.assertIn(
                f"{checker.count} warnings found for '{checker.column_name}: {checker.check_value}'",
                stdout_log
            )
        self.assertEqual(count, count_sum)
        self.assertEqual(count, 75)

if __name__ == '__main__':
    unittest.main()

from io import StringIO
import unittest
from pathlib import Path

from unittest.mock import patch

from mlx.warnings import PolyspaceCheck, WarningsPlugin

TEST_IN_DIR = Path(__file__).parent / 'test_in'


class TestPolyspaceWarnings(unittest.TestCase):
    def setUp(self):
        self.warnings = WarningsPlugin(verbose=True)
        self.dut = self.warnings.activate_checker_name('polyspace')
        self.dut.checkers = [
            PolyspaceCheck("run-time check", "color", "red", 0, 0),
            PolyspaceCheck("run-time check", "color", "orange", 0, 50),
        ]

    def test_code_prover_tsv_file(self):
        with open('tests/test_in/polyspace_code_prover.tsv', newline="") as file:
            with patch('sys.stdout', new=StringIO()) as fake_out:
                self.warnings.check(file, file_extension='.tsv')
                count = self.warnings.return_count()
        stdout_log = fake_out.getvalue()

        self.assertEqual(count, 169)
        self.assertIn(f"{self.dut.checkers[0].count} warnings found for '{self.dut.checkers[0].column_name}: {self.dut.checkers[0].check_value}'", stdout_log)
        self.assertIn(f"{self.dut.checkers[1].count} warnings found for '{self.dut.checkers[1].column_name}: {self.dut.checkers[1].check_value}'", stdout_log)

    def test_code_prover_csv_file(self):
        with open('tests/test_in/polyspace_code_prover.csv', newline="") as file:
            with patch('sys.stdout', new=StringIO()) as fake_out:
                self.warnings.check(file, file_extension='.csv')
                count = self.warnings.return_count()
        stdout_log = fake_out.getvalue()

        self.assertEqual(count, 169)
        self.assertIn(f"{self.dut.checkers[0].count} warnings found for '{self.dut.checkers[0].column_name}: {self.dut.checkers[0].check_value}'", stdout_log)
        self.assertIn(f"{self.dut.checkers[1].count} warnings found for '{self.dut.checkers[1].column_name}: {self.dut.checkers[1].check_value}'", stdout_log)

if __name__ == '__main__':
    unittest.main()

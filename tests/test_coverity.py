import json
import os
from io import StringIO
from pathlib import Path
from unittest import TestCase, mock
from unittest.mock import patch

from mlx.warnings import WarningsPlugin, warnings_wrapper

TEST_IN_DIR = Path(__file__).parent / 'test_in'
TEST_OUT_DIR = Path(__file__).parent / 'test_out'


def ordered(obj):
    if isinstance(obj, dict):
        return sorted((k, ordered(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(ordered(x) for x in obj)
    else:
        return obj

@mock.patch.dict(os.environ, {"MIN_COV_WARNINGS": "1", "MAX_COV_WARNINGS": "2"})
class TestCoverityWarnings(TestCase):
    def setUp(self):
        self.warnings = WarningsPlugin(verbose=True)
        self.warnings.activate_checker_name('coverity')

    def test_no_warning_normal_text(self):
        dut = 'This should not be treated as warning'
        self.warnings.check(dut)
        self.assertEqual(self.warnings.return_count(), 0)

    def test_no_warning_but_still_command_output(self):
        dut = 'src/something/src/somefile.c:82: 1. misra_violation: Essential type of the left hand operand "0U" (unsigned) is not the same as that of the right operand "1U"(signed).'
        self.warnings.check(dut)
        self.assertEqual(self.warnings.return_count(), 0)

    def test_single_warning(self):
        dut = '/src/somefile.c:82: CID 113396 (#2 of 2): Coding standard violation (MISRA C-2012 Rule 10.1): Unclassified, Unspecified, Undecided, owner is nobody, first detected on 2017-07-27.'
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.warnings.check(dut)
        self.assertEqual(self.warnings.return_count(), 1)
        self.assertIn(dut, fake_out.getvalue())

    def test_single_warning_count_one(self):
        dut1 = '/src/somefile.c:80: CID 113396 (#1 of 2): Coding standard violation (MISRA C-2012 Rule 10.1): Unclassified, Unspecified, Undecided, owner is nobody, first detected on 2017-07-27.'
        dut2 = '/src/somefile.c:82: CID 113396 (#2 of 2): Coding standard violation (MISRA C-2012 Rule 10.1): Unclassified, Unspecified, Undecided, owner is nobody, first detected on 2017-07-27.'
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.warnings.check(dut1)
            self.warnings.check(dut2)
        self.assertEqual(self.warnings.return_count(), 1)
        self.assertIn(dut2, fake_out.getvalue())

    def test_single_warning_real_output(self):
        dut1 = '/src/somefile.c:80: CID 113396 (#1 of 2): Coding standard violation (MISRA C-2012 Rule 10.1): Unclassified, Unspecified, Undecided, owner is nobody, first detected on 2017-07-27.'
        dut2 = '/src/somefile.c:82: CID 113396 (#2 of 2): Coding standard violation (MISRA C-2012 Rule 10.1): Unclassified, Unspecified, Undecided, owner is nobody, first detected on 2017-07-27.'
        dut3 = 'src/something/src/somefile.c:82: 1. misra_violation: Essential type of the left hand operand "0U" (unsigned) is not the same as that of the right operand "1U"(signed).'
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.warnings.check(dut1)
            self.warnings.check(dut2)
            self.warnings.check(dut3)
        self.assertEqual(self.warnings.return_count(), 1)
        self.assertIn(dut2, fake_out.getvalue())

    def test_code_quality_without_config(self):
        filename = 'coverity_cq.json'
        out_file = str(TEST_OUT_DIR / filename)
        ref_file = str(TEST_IN_DIR / filename)
        retval = warnings_wrapper([
            '--coverity',
            '--code-quality', out_file,
            str(TEST_IN_DIR / 'defects.txt'),
        ])
        self.assertEqual(8, retval)
        with open(out_file) as file:
            cq_out = json.load(file)
        with open(ref_file) as file:
            cq_ref = json.load(file)
        self.assertEqual(ordered(cq_out), ordered(cq_ref))

    def test_code_quality_with_config(self):
        filename = 'coverity_cq.json'
        out_file = str(TEST_OUT_DIR / filename)
        ref_file = str(TEST_IN_DIR / filename)
        retval = warnings_wrapper([
            '--code-quality', out_file,
            '--config', str(TEST_IN_DIR / 'config_example_coverity.yml'),
            str(TEST_IN_DIR / 'defects.txt'),
        ])
        self.assertEqual(3, retval)
        with open(out_file) as file:
            cq_out = json.load(file)
        with open(ref_file) as file:
            cq_ref = json.load(file)
        self.assertEqual(ordered(cq_out), ordered(cq_ref))

import filecmp
from io import StringIO
from pathlib import Path
from unittest import TestCase

from unittest.mock import patch

from mlx.warnings import warnings_wrapper

TEST_IN_DIR = Path(__file__).parent / 'test_in'
TEST_OUT_DIR = Path(__file__).parent / 'test_out'


class TestIntegration(TestCase):
    def setUp(self):
        if not TEST_OUT_DIR.exists():
            TEST_OUT_DIR.mkdir()



    def test_output_file_robot_basic(self):
        filename = 'robot_double_fail_summary.txt'
        out_file = str(TEST_OUT_DIR / filename)
        ref_file = str(TEST_IN_DIR / filename)
        retval = warnings_wrapper([
            '--output', out_file,
            '-r',
            'tests/test_in/robot_double_fail.xml',
        ])
        self.assertEqual(2, retval)
        self.assertTrue(filecmp.cmp(out_file, ref_file), '{} differs from {}'.format(out_file, ref_file))

    def test_output_file_robot_config(self):
        filename = 'robot_double_fail_config_summary.txt'
        out_file = str(TEST_OUT_DIR / filename)
        ref_file = str(TEST_IN_DIR / filename)
        retval = warnings_wrapper([
            '--output', out_file,
            '--config', 'tests/test_in/config_example_robot.json',
            'tests/test_in/robot_double_fail.xml',
        ])
        self.assertEqual(2, retval)
        self.assertTrue(filecmp.cmp(out_file, ref_file), '{} differs from {}'.format(out_file, ref_file))

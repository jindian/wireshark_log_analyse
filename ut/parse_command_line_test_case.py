########################################################################################################################
# Module to test parse command line
# Author Jin Feng
#
########################################################################################################################

import sys
from src import parse_command_line
import unittest


class parse_command_line_test_case(unittest.TestCase):
    def test_parse_input_parameter_without_options(self):
        argv = ["frame_loss_and_delay_analyse.py"]
        with self.assertRaises(SystemExit) as SE:
            parse_command_line.parse_input_parameter(argv)
        self.assertEqual(SE.exception.code, 1)
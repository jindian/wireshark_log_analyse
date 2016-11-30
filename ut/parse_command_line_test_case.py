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

    def test_parse_input_parameter_with_option_null(self):
        argv = ["frame_loss_and_delay_analyse.py", "-d"]
        with self.assertRaises(SystemExit) as SE:
            parse_command_line.parse_input_parameter(argv)
        self.assertEqual(SE.exception.code, 2)

    def test_parse_input_parameter_with_h(self):
        argv = ["frame_loss_and_delay_analyse.py", "-h"]
        with self.assertRaises(SystemExit) as SE:
            parse_command_line.parse_input_parameter(argv)
        self.assertEqual(SE.exception.code, 0)

    def test_parse_input_parameter_with_help(self):
        argv = ["frame_loss_and_delay_analyse.py", "--help"]
        with self.assertRaises(SystemExit) as SE:
            parse_command_line.parse_input_parameter(argv)
        self.assertEqual(SE.exception.code, 0)

    def test_parse_input_parameter_with_d(self):
        argv = ["frame_loss_and_delay_analyse.py", "-d", "test"]
        dir, fsn, delay = parse_command_line.parse_input_parameter(argv)
        self.assertEqual(dir, "test")
        self.assertIs(fsn, True)
        self.assertIs(delay, True)

    def test_parse_input_parameter_with_directory(self):
        argv = ["frame_loss_and_delay_analyse.py", "--directory", "test"]
        dir, fsn, delay = parse_command_line.parse_input_parameter(argv)
        self.assertEqual(dir, "test")
        self.assertIs(fsn, True)
        self.assertIs(delay, True)

    def test_parse_input_parameter_with_d_t_not_fns_delay(self):
        argv = ["frame_loss_and_delay_analyse.py", "-d", "test", "-t", "abc"]
        dir, fsn, delay = parse_command_line.parse_input_parameter(argv)
        self.assertEqual(dir, "test")
        self.assertIs(fsn, True)
        self.assertIs(delay, True)

    def test_parse_input_parameter_with_d_t_fsn(self):
        argv = ["frame_loss_and_delay_analyse.py", "-d", "test", "-t", "fsn"]
        dir, fsn, delay = parse_command_line.parse_input_parameter(argv)
        self.assertEqual(dir, "test")
        self.assertIs(fsn, True)
        self.assertIs(delay, False)

    def test_parse_input_parameter_with_d_t_delay(self):
        argv = ["frame_loss_and_delay_analyse.py", "-d", "test", "-t", "delay"]
        dir, fsn, delay = parse_command_line.parse_input_parameter(argv)
        self.assertEqual(dir, "test")
        self.assertIs(fsn, False)
        self.assertIs(delay, True)

    def test_parse_input_parameter_with_no_d_have_t(self):
        argv = ["frame_loss_and_delay_analyse.py", "-t", "delay"]
        with self.assertRaises(SystemExit) as SE:
            parse_command_line.parse_input_parameter(argv)
        self.assertEqual(SE.exception.code, 3)
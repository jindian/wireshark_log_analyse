"""
Unit Test of wireshark log analyse
"""


import unittest
from parse_command_line_test_case import *


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(parse_command_line_test_case)
    unittest.main()

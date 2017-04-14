########################################################################################################################
# Module used to parse command line
# Author: Feng Jin
# Data: 2016.11.30
#
########################################################################################################################

import getopt
import sys

"""
bit of option
"""
option_bit = {
    "fsn": 0,
    "delay": 1,
    "fach": 2
}

print_help = "python frame_loss_and_delay_analyse.py -d <analyze_folder> -t <analyze_type>\r\n" \
             "Options:\r\n" \
             "-h, --help\r\n" \
             "       usage of this script\r\n" \
             "-d, --directory\r\n" \
             "       directory to analyze\r\n" \
             "-t, --type\r\n" \
             "       fsn or delay or both if not specified\r\n" \
             "-f, --fach_indicator\r\n" \
             "       find hsfach connections"


class command_line:
    def __init__(self, argv):
        self.dir = ""
        self.option_bitmap = 0
        self.parse_input_parameter(argv)


    def parse_input_parameter(self, argv):
        options = "hd:t:fi:"
        long_options = ["help", "directory=", "type=", "fach_indicator"]

        # Arguments not specified
        if len(argv) < 2:
            self.help()
            sys.exit(1)

        try:
            opts, args = getopt.getopt(argv[1:], options, long_options)
        except getopt.GetoptError:
            self.help()
            sys.exit(2)

        for opt, arg in opts:
            if opt in ("-h", "--help"):
                self.help()
                sys.exit(0)
            elif opt in ("-d", "--directory"):
                self.dir = arg
            elif opt in ("-t", "--type"):
                if arg is "fsn":
                    self.set_option(option_bit["fsn"])
                elif arg is "delay":
                    self.set_option(option_bit["delay"])
            elif opt in ("-f", "--fach_indicator"):
                self.set_option(option_bit["fach"])

        # Directory not specified
        if self.dir == '':
            print "Directory not specified, select a directory and try again!!\n\r"
            self.help()
            sys.exit(3)

        # If option doesn't specify, check fsn and delay both by default
        if self.has_option(option_bit["fsn"]) is 0 and self.has_option(option_bit["delay"]) is 0:
            self.set_option(option_bit["fsn"])
            self.set_option(option_bit["delay"])

        return

    def set_option(self, bit):
        self.option_bitmap |= 1<bit

    def has_option(self, bit):
        return (self.option_bitmap & 1<bit)

    def help(self):
        print print_help
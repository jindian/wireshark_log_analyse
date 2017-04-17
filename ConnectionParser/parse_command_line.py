import getopt
import sys

print_help = "frame_loss_and_delay_analyse.py -d <analyze_folder> [Options]\r\n" \
             "Options:\r\n" \
             "-h, --help\r\n" \
             "       usage of this script\r\n" \
             "-d, --directory\r\n" \
             "       directory to analyze\r\n" \
             "-t, --type\r\n" \
             "       fsn or delay or both if not specified\r\n" \
             "-f, --fach_indicator\r\n" \
             "       find hsfach connections\r\n" \
             "-m, --merge_hsdpa\r\n" \
             "       merge all hsdpa data"


"""
Class:
            command_line
Usage:
            Manage command line information
Interfaces:
            parse_input_parameter       : parse input parameters
            has_option                  : check if specified option exist
            get_dir                     : get directory to analyze
            help                        : print usage of Connection Parser
Variables:
            dir                         : directory all csv file stored
            option_bitmap               : bit map of option information
"""


class command_line:
    def __init__(self):
        self.dir = ""
        self.option_bitmap = 0
        self.option_obj_list = []

    def parse_input_parameter(self, argv):
        # options = "hd:t:fm"
        # long_options = ["help", "directory=", "type=", "fach_indicator", "merge_hsdpa"]

        # Arguments not specified
        if len(argv) < 2:
            self.help()
            sys.exit(1)

        try:
            opts, args = getopt.getopt(argv[1:], self.options, self.options_long)
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
                if arg == "fsn":
                    self.set_option("fsn")
                elif arg == "delay":
                    self.set_option("delay")
            elif opt in ("-f", "--fach_indicator"):
                self.set_option("fach")
            elif opt in ("-m", "--merge_hsdpa"):
                self.set_option("merge")

        # Directory not specified
        if self.dir == '':
            print "Directory not specified, select a directory and try again!!\n\r"
            self.help()
            sys.exit(3)

        # If option doesn't specify, check fsn and delay both by default
        if self.has_option("fsn") is False and self.has_option("delay") is False:
            self.set_option("fsn")
            self.set_option("delay")
            # print "{0:b}".format(self.option_bitmap)

        return

    def register_option(self, option_obj):
        self.option_obj_list.append(option_obj)

    def set_option(self, bit):
        bit_index = 0
        try:
            bit_index = option_bit[bit]
            self.option_bitmap |= 1 << bit_index
        except KeyError:
            print "No key value: " + bit

    def has_option(self, bit):
        bit_index = 0
        has_opt = False
        try:
            bit_index = option_bit[bit]
            if self.option_bitmap & 1 << bit_index is not 0:
                has_opt = True
        except KeyError:
            print "No Key Value: " + bit

        return has_opt

    def get_dir(self):
        return self.dir

    def help(self):
        print print_help


class single_option:
    def __init__(self):
        self.option_name = ""
        self.option_short = ""
        self.option_long = ""
        self.option_desc = ""
        self.option_args = ()

    def get_option_name(self):
        return self.option_name

    def get_option(self):
        return self.option_short, self.option_long

    def get_option_args(self):
        return self.option_args

    def option_action(self):
        return


class help(single_option):
    def __init__(self):
        single_option.__init__(self)
        self.option_name = "help"
        self.option_short = "h"
        self.option_long = "help"
        self.option_desc = "usage of wireshark log analyse"

    def option_action(self):
        print print_help
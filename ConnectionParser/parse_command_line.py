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
                if arg == "fsn":
                    self.set_option("fsn")
                elif arg == "delay":
                    self.set_option("delay")
            elif opt in ("-f", "--fach_indicator"):
                self.set_option("fach")

        # Directory not specified
        if self.dir == '':
            print "Directory not specified, select a directory and try again!!\n\r"
            self.help()
            sys.exit(3)

        # print "{0:b}".format(self.option_bitmap)
        # If option doesn't specify, check fsn and delay both by default
        if self.has_option("fsn") is False and self.has_option("delay") is False:
            self.set_option("fsn")
            self.set_option("delay")
            # print "{0:b}".format(self.option_bitmap)

        return

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
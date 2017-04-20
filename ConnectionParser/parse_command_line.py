import getopt
import sys

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
        # It's possible option_list_dict and option_obj_list are not equal
        # because of argument of option exist
        self.option_list_dict = {}
        # Be sure help object should be added to list ahead of others
        self.option_obj_list = []
        self.option_bitmap = 0
        self.usage = "frame_loss_and_delay_analyse.py -d <analyze_folder> [Options]\r\n" \
                     "Options:\r\n"

    def parse_input_parameter(self, argv):
        # generate options list to parse
        options, long_options = self.generate_options()

        # Arguments not specified
        if len(argv) < 2:
            self.option_obj_list[0].option_action(self, self.usage)
            sys.exit(1)

        try:
            opts, args = getopt.getopt(argv[1:], options, long_options)
        except getopt.GetoptError:
            self.option_obj_list[0].option_action(self, self.usage)
            sys.exit(2)

        for opt, arg in opts:
            for obj in self.option_obj_list:
                opt_short, opt_long = obj.get_option()
                cmd_opt_short = "-" + opt_short
                cmd_opt_long = "--" + opt_long
                if opt in (cmd_opt_short, cmd_opt_long):
                    if obj.get_option_name() != "help":
                        obj.option_action(self, arg)
                    else:
                        obj.option_action(self, self.usage)
                    break

        # Directory not specified
        if self.dir == '':
            print "Directory not specified, select a directory and try again!!\n\r"
            self.option_obj_list[0].option_action(self, self.usage)
            sys.exit(3)

        # If option doesn't specify, check fsn and delay both by default
        if self.has_option("fsn") is False and self.has_option("delay") is False:
            self.set_option("fsn")
            self.set_option("delay")

        print "{0:b}".format(self.option_bitmap)
        return

    def register_option(self, option_obj):
        self.option_obj_list.append(option_obj)

    def generate_options(self):
        options = ""
        long_options = []
        dict_index = 0
        for obj in self.option_obj_list:
            option_short, option_long = obj.get_option()
            self.usage += "-" + option_short + ", --" + option_long + "\r\n"
            self.usage += "       " + obj.get_option_desc() + "\r\n"
            args_list = obj.get_option_args()
            if len(args_list) is 0:
                options += option_short
                long_options.append(option_long)
                if obj.do_add_option_bitmap() is True:
                    self.option_list_dict[obj.get_option_name()] = dict_index
                    dict_index += 1
            else:
                options += (option_short + ":")
                long_options.append(option_long + "=")
                for arg in args_list:
                    if obj.do_add_option_bitmap() is True:
                        self.option_list_dict[arg] = dict_index
                        dict_index +=1

        return options, long_options

    def query_option_bit_index(self, bit):
        bit_index = -1
        try:
            bit_index = self.option_list_dict[bit]
        except KeyError:
            print "No option with key <" + bit + "> exist"

        return bit_index

    def set_option(self, bit):
        bit_index = self.query_option_bit_index(bit)
        if bit_index is not -1:
            self.option_bitmap |= 1 << bit_index

    def has_option(self, bit):
        bit_index = self.query_option_bit_index(bit)
        has_opt = False
        if self.option_bitmap & 1 << bit_index is not 0:
            has_opt = True

        return has_opt

    def set_dir(self, dir):
        self.dir = dir

    def get_dir(self):
        return self.dir


class single_option:
    def __init__(self):
        self.option_name = ""
        self.option_short = ""
        self.option_long = ""
        self.option_desc = ""
        self.option_args = []
        self.option_bitmap_add = False

    def get_option_name(self):
        return self.option_name

    def get_option(self):
        return self.option_short, self.option_long

    def get_option_desc(self):
        return self.option_desc

    def get_option_args(self):
        return self.option_args

    def do_add_option_bitmap(self):
        return self.option_bitmap_add

    def option_action(self, cmd_obj, arg):
        return


class option_help(single_option):
    def __init__(self):
        single_option.__init__(self)
        self.option_name = "help"
        self.option_short = "h"
        self.option_long = "help"
        self.option_desc = "usage of our script"

    def option_action(self, cmd_obj, arg):
        print arg
        sys.exit(0)


class option_directory(single_option):
    def __init__(self):
        single_option.__init__(self)
        self.option_name = "directory"
        self.option_short = "d"
        self.option_long = "directory"
        self.option_desc = "directory to analyze"
        self.option_args = [""]

    def option_action(self, cmd_obj, arg):
        cmd_obj.set_dir(arg)


class option_fach_indicator(single_option):
    def __init__(self):
        single_option.__init__(self)
        self.option_name = "fach_indicator"
        self.option_short = "f"
        self.option_long = "fach_indicator"
        self.option_desc = "find hsfach connections"
        self.option_bitmap_add = True

    def option_action(self, cmd_obj, arg):
        cmd_obj.set_option("fach_indicator")


class option_merge_hsdpa(single_option):
    def __init__(self):
        single_option.__init__(self)
        self.option_name = "merge_hsdpa"
        self.option_short = "m"
        self.option_long = "merge_hsdpa"
        self.option_desc = "merge all hsdpa data"
        self.option_bitmap_add = True

    def option_action(self, cmd_obj, arg):
        cmd_obj.set_option("merge_hsdpa")


class option_type(single_option):
    def __init__(self):
        single_option.__init__(self)
        self.option_name = "type"
        self.option_short = "t"
        self.option_long = "type"
        self.option_desc = "fsn or delay or both if not specified"
        self.option_args = ["fsn", "delay"]
        self.option_bitmap_add = True

    def option_action(self, cmd_obj, arg):
        if arg == "":
            print "Type doesn't specify, please try again"
            sys.exit(1)
        else:
            cmd_obj.set_option(arg)



########################################################################################################################
# Module used to parse command line
# Author: Feng Jin
# Data: 2016.11.30
#
########################################################################################################################

import getopt
import sys


def parse_input_parameter(argv):
    options = "hd:t:fi:"
    long_options = ["help", "directory=", "type=", "fach_indicator"]
    analyze_dir = ""
    analyze_fsn = False
    analyze_delay = False
    find_hsfach_connections = False
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

    # Arguments not specified
    if len(argv) < 2:
        print print_help
        sys.exit(1)

    try:
        opts, args = getopt.getopt(argv[1:], options, long_options)
    except getopt.GetoptError:
        print print_help
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print print_help
            sys.exit(0)
        elif opt in ("-d", "--directory"):
            analyze_dir = arg
        elif opt in ("-t", "--type"):
            if arg is "fsn":
                analyze_fsn = True
            elif arg is "delay":
                analyze_delay = True
        elif opt in ("-f", "--fach_indicator"):
            find_hsfach_connections = True

    # Directory not specified
    if analyze_dir == '':
        print "Directory not specified, select a directory and try again!!\n\r"
        print print_help
        sys.exit(3)

    # If option doesn't specify, check fsn and delay both by default
    if analyze_fsn is False and analyze_delay is False:
        analyze_fsn = True
        analyze_delay = True

    return analyze_dir, analyze_fsn, analyze_delay, find_hsfach_connections
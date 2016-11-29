########################################################################################################################
# Tool to analyse down link data frame loss and delay
# Author: Feng Jin
# Data: 2016.11.15
#
########################################################################################################################


import os
import sys
import csv
import getopt

from group_emulator import group_emulator
from analysis_statistic import analysis_statistic
from fp_analyzer import delay_analyzer


def analyze_fsn_without_improvement(fsn_list, frame_no_list):
    fsn_list_len = len(fsn_list)
    if fsn_list_len == 0:
        return 0
    step = 0
    pre_fsn = 0
    cur_fsn = 0
    dist_fsn = 0
    lost_frames = 0
    while step < fsn_list_len:
        if step == 0:
            pre_fsn = int(fsn_list[step])
            step += 1
            continue

        if int(fsn_list[step]) == 0:
            pre_fsn = int(fsn_list[step])
            step += 1
            continue
        else:
            cur_fsn = int(fsn_list[step])

        dist_fsn = cur_fsn - pre_fsn
        if dist_fsn <= 0:
            dist_fsn += 15

        pre_fsn = int(fsn_list[step])

        final_fsn = dist_fsn - 1
        if final_fsn > 0:
            lost_frames += final_fsn
            print frame_no_list[step] + ": " + str(final_fsn)

        step += 1

    if lost_frames > 0:
        print "Total lost frames: " + str(lost_frames)
    return lost_frames


def analyze_fsn_with_improvement(fsn_list, frame_no_list):
    # To be implemented
    return True


def collect_frame_information(base_dir, file):
    file_dir = base_dir + '/' + file
    fsn_list = []
    frame_no_list = []
    drt_list = []
    time_stamp_list = []
    with open(file_dir, 'rb') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',', quotechar='|')
        csv_line = 0
        fsn_index = 0
        type_index = 0
        frame_no_index = 0
        drt_index = 0
        time_stamp_index = 0
        for row in csv_reader:
            line = ','.join(row)
            column  = line.split(',')
            if csv_line == 0:
                cell_index = 0
                for one_cell in column:
                    if one_cell == 'drt(ms)':
                        drt_index = cell_index
                        break
                    elif one_cell == 'FrameNo':
                        frame_no_index = cell_index
                    elif one_cell == 'Timestamp':
                        time_stamp_index = cell_index
                    elif one_cell == 'Type':
                        type_index = cell_index
                    elif one_cell == 'fsn':
                        fsn_index = cell_index
                    cell_index += 1
            else:
                if column[type_index] == 'DF type2' or column[type_index] == 'DF type1 336' or column[type_index] == 'DF type1 656':
                    frame_no_list.append(column[frame_no_index])
                    time_stamp_list.append(column[time_stamp_index])
                    fsn_list.append(column[fsn_index])
                    drt_list.append(column[drt_index])
            csv_line += 1

    return fsn_list, frame_no_list, time_stamp_list, drt_list


instance_group = group_emulator()
instance_statistic = analysis_statistic()


def analyze_csv_files(analyze_dir, analyze_fsn, analyze_delay):
    file_list = os.listdir(analyze_dir)
    for one_file in file_list:
        if one_file != 'Hsdsch_per_connect_stat.csv' and one_file != 'Hsdsch_per_second_stat.csv':
            fsn_list, frame_no_list, time_stamp_list, drt_list = collect_frame_information(analyze_dir, one_file)
            if analyze_fsn is True:
                fsn_result = analyze_fsn_without_improvement(fsn_list, frame_no_list)
                if fsn_result > 0:
                    instance_statistic.update_frame_loss_statistic(fsn_result)
                    print one_file

            if analyze_delay is True:
                local_instance = delay_analyzer(instance_group, instance_statistic)
                delay_result = local_instance.analyze_delay(time_stamp_list, drt_list, fsn_list, frame_no_list)
                if delay_result != 0:
                    print "Delay detected in file " + one_file
                    instance_statistic.update_delay_statistic()


def parse_input_parameter(argv):
    options = "hd:t:"
    long_options = []
    analyze_dir = ""
    analyze_fsn = False
    analyze_delay = False
    print_help="python frame_loss_and_delay_analyse.py -d <analyze_folder> -t <analyze_type>\r\n" \
                "Options:\r\n" \
                "-d\r\n" \
                "       directory to analyze\r\n" \
                "-t\r\n" \
                "       fsn or delay or both if not specified"

    # Arguments not specified
    if len(argv) < 2:
        print print_help
        sys.exit(2)

    try:
        opts, args = getopt.getopt(argv[1:], options, long_options)
    except getopt.GetoptError:
        print print_help
        print
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print print_help
        elif opt in ("-d", "--directory"):
            analyze_dir=arg
        elif opt in ("-t", "--type"):
            if arg == "fsn":
                analyze_fsn=True
            elif arg == "delay":
                analyze_delay = True

    # Directory not specified
    if analyze_dir == '':
        print print_help
        sys.exit(2)

    # If option doesn't specify, check fsn and delay both by default
    if analyze_fsn is False and  analyze_delay == False:
        analyze_fsn = True
        analyze_delay = True

    return analyze_dir, analyze_fsn, analyze_delay


def main():
    analyze_dir, analyze_fsn, analyze_delay = parse_input_parameter(sys.argv)
    analyze_csv_files(analyze_dir, analyze_fsn, analyze_delay)
    instance_statistic.show_statistic_result()


if __name__ == "__main__":
    main()
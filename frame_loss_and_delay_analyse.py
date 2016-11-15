########################################################################################################################
# Tool to analyse down link data frame loss and delay
# Author: Feng Jin
# Data: 2016.11.15
#
########################################################################################################################


import os
import sys
import csv

def analyze_fsn_without_improvement(fsn_list, frame_no_list):
    fsnlistlen = len(fsn_list)
    if fsnlistlen == 0:
        return True
    step = 0
    pre_fsn = 0
    cur_fsn = 0
    dist_fsn = 0
    lost_frames = 0
    while(step < fsnlistlen):
        if step == 0:
            pre_fsn = int(fsn_list[step])
            step = step + 1
            continue
        
        if int(fsn_list[step]) == 0:
            pre_fsn = int(fsn_list[step])
            step = step + 1
            continue
        else:
            cur_fsn = int(fsn_list[step])

        dist_fsn = cur_fsn - pre_fsn
        if dist_fsn <= 0:
            dist_fsn = dist_fsn + 15

        pre_fsn = int(fsn_list[step])
        
        final_fsn = dist_fsn - 1
        if final_fsn > 0:
            lost_frames = lost_frames + final_fsn
            print frame_no_list[step] + ": " + str(final_fsn)

        step = step + 1

    if lost_frames > 0:
        print lost_frames
        return False
    else:
        return True

def analyze_fsn_with_improvement(fsn_list, frame_no_list):
    # To be implemented
    return True

def collect_fsn_and_frame_no(base_dir, file):
    file_dir = base_dir + '/' + file
    fsn_list = []
    frame_no_list = []
    with open(file_dir, 'rb') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        csv_line = 0
        fsn_index = 0
        type_index = 0
        frame_no_index = 0
        for row in csv_reader:
            line = ','.join(row)
            column  = line.split(',')
            if csv_line == 0:
                set_index = 0
                for set in column:
                    if set == 'fsn':
                        fsn_index = set_index
                        break
                    if set == 'Type':
                        type_index = set_index
                    if set == 'FrameNo':
                        frame_no_index = set_index
                    set_index = set_index + 1
            else:
                if column[type_index] == 'DF type2' or column[type_index] == 'DF type1 336' or column[type_index] == 'DF type1 656':
                    fsn_list.append(column[fsn_index])
                    frame_no_list.append(column[frame_no_index])
            csv_line = csv_line + 1
    return fsn_list, frame_no_list

def analyze_csv_files(basedir, filelist ):
    for file in filelist:
        if file != 'Hsdsch_per_connect_stat.csv' and file != 'Hsdsch_per_second_stat.csv':
        #if file.startswith('DschFrame'):
            fsn_list, frame_no_list = collect_fsn_and_frame_no(basedir, file)
            result = analyze_fsn_without_improvement(fsn_list, frame_no_list)
            if result == False:
                print file

def main():
    args = sys.argv
    if len(args) == 2:
        filelist = os.listdir(args[1])
        analyze_csv_files(args[1], filelist )
    else:
        print "No selected directory!"

if __name__ == "__main__":
    main()
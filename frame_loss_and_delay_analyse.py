########################################################################################################################
# Tool to analyse down link data frame loss and delay
# Author: Feng Jin
# Data: 2016.11.15
#
########################################################################################################################


import os
import sys
import csv


class group_emulator:
    def __init__(self):
        self.delay_average_seconds = 0
        self.delay_average_micro_seconds = 0
        self.delay_build_up_threshold = 50
        self.delay_build_up_severe_threshold = 150
        # delay_state 0: no delay, 1: delay buildup 2: delay buildup severe

    def update_delay_average(self, delay):
        self.delay_average_micro_seconds = \
            (self.delay_average_micro_seconds - self.delay_average_micro_seconds*26 >> 7) + (delay*26000 >> 7)
        self.delay_average_seconds = self.delay_average_micro_seconds / 1000

    def check_delay_result(self):
        delay_state = 0
        if self.delay_average_seconds > self.delay_build_up_severe_threshold:
            # delay_state 0: no delay, 1: delay buildup 2: delay buildup severe
            delay_state = 2
        elif self.delay_average_seconds > self.delay_build_up_threshold:
            delay_state = 1

        return delay_state

    def reset_delay_average(self):
        self.delay_average_seconds = 0
        self.delay_average_micro_seconds = 0


class delay_analyzer_routine:
    def __init__(self):
        self.delay_hns = 0              # in hundred nano seconds: ms*10000
        self.previous_drt = 0
        self.previous_toa = 0
        self.list_len = 0
        self.first_frame_after_fsn_reset = True

    def analyze_delay(self, time_stamp_list, drt_list, fsn_list, frame_no_list):
        instance_group.reset_delay_average()
        self.list_len = len(drt_list)
        delay_detect = 0
        step = 0
        while step < self.list_len:
            if drt_list[step] == 'N/A':              # Data type changed from Type2 -> Type1, vise varsa
                step += 1
                continue
            current_drt = int(drt_list[step])
            current_toa = float(time_stamp_list[step])*1000

            if int(fsn_list[step]) == 0:
                self.first_frame_after_fsn_reset = True

            if self.first_frame_after_fsn_reset is True:
                self.update_previous_time(current_drt, current_toa)
                self.first_frame_after_fsn_reset = False
                step += 1
                continue

            data_delay = int(self.calculate_delay(current_drt, current_toa))
            if data_delay > 20000:
                instance_statistic.update_delay_packet_detail(0, 0, 0, 1)
            elif data_delay > 10000:
                instance_statistic.update_delay_packet_detail(0, 0, 1, 0)
            elif data_delay > 5000:
                instance_statistic.update_delay_packet_detail(0, 1, 0, 0)
            elif data_delay > 1000:
                instance_statistic.update_delay_packet_detail(1, 0, 0, 0)
            instance_group.update_delay_average(data_delay)
            delay_state = instance_group.check_delay_result()
            if delay_state != 0:
                if delay_detect == 0:
                    delay_detect = 1

                if delay_state == 2:
                    instance_statistic.update_delay_buildup_severe_frame_no()
                    #print frame_no_list[step] + ": " + str(data_delay)
            self.update_previous_time(current_drt, current_toa)
            step += 1

        return delay_detect

    def calculate_delay(self, current_drt, current_toa):
        if self.previous_drt > current_drt:
            current_drt += 40960
        drt_diff = current_drt - self.previous_drt
        if drt_diff > 40000:
            print "Wrong drt value!!"
            return 0

        toa_diff = (current_toa - self.previous_toa) % 40960

        temp_delay_hns = self.delay_hns + (toa_diff - drt_diff)*10000
        if temp_delay_hns > 0:
            self.delay_hns = temp_delay_hns
        else:
            self.delay_hns = 0

        driftRedHns = 2*toa_diff
        if self.delay_hns > driftRedHns:
            self.delay_hns -= driftRedHns
        else:
            self.delay_hns = 0

        return self.delay_hns / 10000

    def update_previous_time(self, current_drt, current_toa):
        self.previous_drt = current_drt
        self.previous_toa = current_toa


class analysis_statistic:
    def __init__(self):
        self.delay_detected_udp_connections = 0
        self.delay_more_than_20_seconds_packet_no = 0
        self.delay_more_than_10_seconds_packet_no = 0
        self.delay_more_than_5_seconds_packet_no = 0
        self.delay_more_than_1_seconds_packet_no = 0
        self.delay_buildup_severe_frame_no = 0
        self.frame_loss_detected_udp_connections = 0
        self.total_lost_frame_no = 0

    def update_delay_statistic(self):
        self.delay_detected_udp_connections += 1

    def update_delay_packet_detail(self, over_1_sec, over_5_secs, over_10_secs, over_20_secs):
        self.delay_more_than_20_seconds_packet_no += over_20_secs
        self.delay_more_than_10_seconds_packet_no += over_10_secs
        self.delay_more_than_5_seconds_packet_no += over_5_secs
        self.delay_more_than_1_seconds_packet_no += over_1_sec

    def update_delay_buildup_severe_frame_no(self):
        self.delay_buildup_severe_frame_no += 1

    def update_frame_loss_statistic(self, lost_frame_no):
        self.frame_loss_detected_udp_connections += 1
        self.total_lost_frame_no += lost_frame_no

    def show_statistic_result(self):
        print "#############################################################################"
        print "Frame loss detected udp connection no    : " + str(self.frame_loss_detected_udp_connections)
        print "Total lost frame no                      : " + str(self.total_lost_frame_no)
        print "Delay detected udp connection no         : " + str(self.delay_detected_udp_connections)
        #print "Delay buildup severe packet no           : " + str(self.delay_buildup_severe_frame_no)
        print "Delay over 20 seconds packet no          : " + str(self.delay_more_than_20_seconds_packet_no)
        print "Delay over 10 seconds packet no          : " + str(self.delay_more_than_10_seconds_packet_no)
        print "Delay over 5 seconds packet no           : " + str(self.delay_more_than_5_seconds_packet_no)
        print "Delay over 1 seconds packet no           : " + str(self.delay_more_than_1_seconds_packet_no)
        print "#############################################################################"

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


def analyze_csv_files(base_dir, file_list):
    for one_file in file_list:
        if one_file != 'Hsdsch_per_connect_stat.csv' and one_file != 'Hsdsch_per_second_stat.csv':
            fsn_list, frame_no_list, time_stamp_list, drt_list = collect_frame_information(base_dir, one_file)
            fsn_result = analyze_fsn_without_improvement(fsn_list, frame_no_list)
            if fsn_result > 0:
                instance_statistic.update_frame_loss_statistic(fsn_result)
                print one_file

            local_instance = delay_analyzer_routine()
            delay_result = local_instance.analyze_delay(time_stamp_list, drt_list, fsn_list, frame_no_list)
            if delay_result != 0:
                print "Delay detected in file " + one_file
                instance_statistic.update_delay_statistic()


instance_group = group_emulator()
instance_statistic = analysis_statistic()

def main():
    args = sys.argv
    args_len = len(args)
    if args_len < 2:
        print "Choose directory to analyze!!"
    else:
        file_list = os.listdir(args[1])
        analyze_csv_files(args[1], file_list)
        instance_statistic.show_statistic_result()


if __name__ == "__main__":
    main()
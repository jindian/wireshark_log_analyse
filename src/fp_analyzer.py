########################################################################################################################
# FP analyzer
#       Delay analyzer
#       fsn analyzer
# Author: Feng Jin
# Data: 2016.11.17
#
########################################################################################################################


class delay_analyzer:
    def __init__(self, instance_group, instance_statistic):
        self.delay_hns = 0              # in hundred nano seconds: ms*10000
        self.previous_drt = 0
        self.previous_toa = 0
        self.list_len = 0
        self.first_frame_after_fsn_reset = True
        self.group = instance_group
        self.statistic = instance_statistic

    def analyze_delay(self, time_stamp_list, drt_list, fsn_list, frame_no_list):
        self.group.reset_delay_average()
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
            if self.statistic != 0:
                if data_delay > 20000:
                    self.statistic.update_delay_packet_detail(0, 0, 0, 1)
                    print frame_no_list[step] + ": " + str(data_delay)
                elif data_delay > 10000:
                    self.statistic.update_delay_packet_detail(0, 0, 1, 0)
                elif data_delay > 5000:
                    self.statistic.update_delay_packet_detail(0, 1, 0, 0)
                elif data_delay > 1000:
                    self.statistic.update_delay_packet_detail(1, 0, 0, 0)
            self.group.update_delay_average(data_delay)
            delay_state = self.group.check_delay_result()
            if delay_state != 0:
                if delay_detect == 0:
                    delay_detect = 1

                if delay_state == 2:
                    self.statistic.update_delay_buildup_severe_frame_no()
                    print frame_no_list[step] + ": " + str(data_delay)
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


#!/usr/bin/python

import sys

"""
Entrance
"""

from group_emulator import group_emulator
from analysis_statistic import analysis_statistic
from hspa_connection import hspa_connection
import fp_analyzer
import parse_command_line

instance_statistic = analysis_statistic()
instance_group = group_emulator(instance_statistic)


def fsn_analyze(ins_conn):
    file_list = ins_conn.get_file_list()
    for __file in file_list:
        fsn_list = ins_conn.get_column(__file, "fsn")
        frame_no_list = ins_conn.get_column(__file, "FrameNo")
        fsn_result = fp_analyzer.analyze_fsn_without_improvement(fsn_list, frame_no_list)
        if fsn_result > 0:
            instance_statistic.update_frame_loss_statistic(fsn_result)
            print __file


def delay_analyze(ins_conn):
    file_list = ins_conn.get_file_list()
    for __file in file_list:
        bts_port = ins_conn.get_column(__file, "BtsPort")
        rnc_port = ins_conn.get_column(__file, "RncPort")
        time_stamp_list = ins_conn.get_column(__file, "Timestamp")
        drt_list = ins_conn.get_column(__file, "drt(ms)")
        fsn_list = ins_conn.get_column(__file, "fsn")
        frame_no_list = ins_conn.get_column(__file, "FrameNo")
        index_row = 0
        for port in bts_port:
            user = instance_group.find_user(port, rnc_port[index_row])
            delay = user.analyze_delay(time_stamp_list[index_row], drt_list[index_row], \
                                       fsn_list[index_row], frame_no_list[index_row])
            if delay is not -1:
                instance_group.update_delay_average(delay)
            index_row += 1

        instance_group.reset_user_dict()
        instance_group.reset_delay_average()


def main():
    analyze_dir, analyze_fsn, analyze_delay, find_hsfach_connections = \
        parse_command_line.parse_input_parameter(sys.argv)
    ins_conn = hspa_connection(analyze_dir)
    if find_hsfach_connections is True:
        ins_conn.get_hsfach_connections()
        return

    if analyze_fsn is True:
        fsn_analyze(ins_conn)

    if analyze_delay is True:
        delay_analyze(ins_conn)

    instance_statistic.show_statistic_result()


if __name__ == "__main__":
    main()

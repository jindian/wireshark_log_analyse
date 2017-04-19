#!/usr/bin/python

import sys

"""
Entrance
"""

from group_emulator import group_emulator
from analysis_statistic import analysis_statistic
from hspa_connection import hspa_connection
from fp_analyzer import fsn_analyzer
from parse_command_line import *
import analysis_output

instance_statistic = analysis_statistic()
instance_group = group_emulator(instance_statistic)

def fsn_analyze(ins_conn):
    file_list = ins_conn.get_file_list()
    for __file in file_list:
        fsn_column = ins_conn.get_column(__file, "fsn")
        frame_no_column = ins_conn.get_column(__file, "FrameNo")
        column_index = 0
        fsn_helper = fsn_analyzer()
        for fsn in fsn_column:
            if fsn != "N/A":
                fsn_helper.analyze_fsn_without_improvement(fsn_column[column_index], frame_no_column[column_index])
            column_index += 1

        lost_frames = fsn_helper.get_lost_frames()
        if lost_frames > 0:
            analysis_output.write_analysis(__file)
            instance_statistic.update_frame_loss_statistic(lost_frames)


def delay_analyze(ins_conn):
    file_list = ins_conn.get_file_list()
    for __file in file_list:
        bts_port = ins_conn.get_column(__file, "BtsPort")
        rnc_port = ins_conn.get_column(__file, "RncPort")
        time_stamp = ins_conn.get_column(__file, "Timestamp")
        drt = ins_conn.get_column(__file, "drt(ms)")
        fsn = ins_conn.get_column(__file, "fsn")
        frame_no = ins_conn.get_column(__file, "FrameNo")
        index_row = 0
        for port in bts_port:
            if fsn[index_row] != "N/A":
                user = instance_group.find_user(port, rnc_port[index_row])
                delay = user.analyze_delay(time_stamp[index_row], drt[index_row], \
                                           fsn[index_row], frame_no[index_row])
                if delay is not -1:
                    instance_group.update_delay_average(delay)
            index_row += 1

        instance_group.reset_user_dict()
        instance_group.reset_delay_average()


def register_suppored_options(cmd_line_obj):
    # All supported options are registered here
    # Make sure help object should be registered ahead of others
    help_obj = option_help()
    dir_obj = option_directory()
    fach_obj = option_fach_indicator()
    merge_obj = option_merge_hsdpa()
    type_obj = option_type()

    cmd_line_obj.register_option(help_obj)
    cmd_line_obj.register_option(dir_obj)
    cmd_line_obj.register_option(fach_obj)
    cmd_line_obj.register_option(merge_obj)
    cmd_line_obj.register_option(type_obj)

    return


def main():
    cmd = command_line()
    register_suppored_options(cmd)
    cmd.parse_input_parameter(sys.argv)
    analysis_output.output_open()
    ins_conn = hspa_connection(cmd.get_dir())
    if cmd.has_option("fach_indicator") is True:
        ins_conn.get_hsfach_connections()
        return

    if cmd.has_option("merge_hsdpa") is True:
        ins_conn.merge_hsdpa_connections()
        return

    if cmd.has_option("fsn") is True:
        fsn_analyze(ins_conn)

    if cmd.has_option("delay") is True:
        delay_analyze(ins_conn)

    instance_statistic.show_statistic_result()
    analysis_output.output_close()


if __name__ == "__main__":
    main()

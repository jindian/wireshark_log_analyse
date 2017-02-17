########################################################################################################################
# Anslysis statistic
# Author: Feng Jin
# Data: 2016.11.17
#
########################################################################################################################


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
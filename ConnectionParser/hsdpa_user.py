from fp_analyzer import delay_analyzer


"""
Class:
            hsdpa_user
Usage:
            One udp connection of user
Interfaces:
            N/A
Variables:
            bts_port                    : BTS port
            rnc_port                    : RNC port
"""


class hsdpa_user(delay_analyzer):

    def __init__(self, bts_port, rnc_port, statistics):
        delay_analyzer.__init__(self, statistics)
        self.bts_port = bts_port
        self.rnc_port = rnc_port


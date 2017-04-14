"""
HSDPA user
one port mapping with a user
"""

from fp_analyzer import delay_analyzer


class hsdpa_user(delay_analyzer):

    def __init__(self, bts_port, rnc_port, statistics):
        delay_analyzer.__init__(self, statistics)
        self.bts_port = bts_port
        self.rnc_port = rnc_port


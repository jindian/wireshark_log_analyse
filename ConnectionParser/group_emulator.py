from hsdpa_user import hsdpa_user


"""
Class:
            group_emulator
Usage:
            Emulator of single RNC group
Interfaces:
            update_delay_average        : update average delay
            check_delay_result          : check if delay exist
            reset_delay_average         : reset average delay
            reset_user_dict             : reset dictionary of user
            add_user                    : add a user
            find_user                   : find user with specified port pair
Variables:
            delay_average_milli_seconds : average delay in milli seconds
            delay_average_micro_seconds : average delay in micro seconds
            delay_build_up_threshold    : threshold of delay build up
            delay_build_up_severe_threshold
                                        : threshold of delay build up severe
            port2user                   : dictionary of user with port pair as its key
            statistics                  : object of statistic
"""


class group_emulator:

    def __init__(self, statistics):
        self.delay_average_milli_seconds = 0
        self.delay_average_micro_seconds = 0
        self.delay_build_up_threshold = 50
        self.delay_build_up_severe_threshold = 150
        self.port2user = {}
        self.statistics = statistics
        # delay_state 0: no delay, 1: delay buildup 2: delay buildup severe

    def update_delay_average(self, delay):
        self.delay_average_micro_seconds = \
            (self.delay_average_micro_seconds - self.delay_average_micro_seconds*26 >> 7) + (delay*26000 >> 7)
        self.delay_average_milli_seconds = self.delay_average_micro_seconds / 1000

    def check_delay_result(self):
        delay_state = 0
        if self.delay_average_milli_seconds > self.delay_build_up_severe_threshold:
            # delay_state 0: no delay, 1: delay buildup 2: delay buildup severe
            delay_state = 2
        elif self.delay_average_milli_seconds > self.delay_build_up_threshold:
            delay_state = 1

        return delay_state

    def reset_delay_average(self):
        self.statistics.update_delay_average(self.delay_average_micro_seconds)
        self.delay_average_milli_seconds = 0
        self.delay_average_micro_seconds = 0

    def reset_user_dict(self):
        self.port2user.clear()

    def add_user(self, bts_port, rnc_port):
        user = hsdpa_user(int(bts_port), int(rnc_port), self.statistics)
        port_pair = bts_port + "_" + rnc_port
        self.port2user[port_pair] = user
        return user

    def find_user(self, bts_port, rnc_port):
        user = None
        port_pair = bts_port + "_" + rnc_port
        try:
            user = self.port2user[port_pair]
        except KeyError:
            user = self.add_user(bts_port, rnc_port)
        return user
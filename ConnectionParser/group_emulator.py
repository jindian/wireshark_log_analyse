########################################################################################################################
# Group emulator
# Author: Feng Jin
# Data: 2016.11.17
#
########################################################################################################################


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
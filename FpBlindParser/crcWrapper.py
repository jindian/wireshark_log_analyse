#!/usr/bin/python

##
# @file crcWrapper.py
# @brief Based on Crc class from pycrc packet, refactor to speed up
#        table_driven algo. if use this wrapper, please make sure use
#        table_driven algo, otherwise you will not get any benefit
# @author Eric - eric.xia@nsn.com
# @version 1.0
# @date 2013-04-25

from crc_algorithms import Crc

class CrcWrapper(Crc):
    """add self.table to record table info"""
    def __init__(self, width, poly, reflect_in, xor_in, reflect_out, xor_out, table_idx_width = None):
        super(CrcWrapper, self).__init__(width, poly, reflect_in, xor_in, reflect_out, xor_out, table_idx_width)
        self.table = None

    def gen_table(self):
        """crc lookup table only create once"""
        if not self.table:
            self.table = super(CrcWrapper, self).gen_table()
        return self.table

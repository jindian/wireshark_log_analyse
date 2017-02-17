#!/usr/bin/python

##
# @file ca_type2.py
# @brief Define HSDSCH type2 CA control msg fields
#        Organized as (field name, bits)
# @author Eric - eric.xia@nsn.com
# @version 1.0
# @date 2013-04-12


import pkt

class CA_TYPE2(pkt.Packet):
    """docstring for CA_TYPE2"""
    __fields__ = [
            ('spare', 2),
            ('congest', 2),
            ('cmchpi', 4),
            ('spare2', 5),
            ('maxpdulen', 11),
            ('credit', 16),
            ('interval', 8),
            ('rep', 8),
            #('spareext', 8),
            ]

    def getGrantedbps(self):
        """docstring for getgrantedbps"""
        if self.credit == 65535:
            return -1
        if self.interval == 0:
            # TS 25.435: Value 0 shall be interpreted that none
            # of the credits shall be used
            return 0
        return (self.maxpdulen<<3) * self.credit * 100/self.interval

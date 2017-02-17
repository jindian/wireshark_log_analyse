#!/usr/bin/python

##
# @file hsdschdata_type1.py
# @brief Define HSDSCH type1 data frame msg fields
#        Organized as (field name, bits)
# @author Eric - eric.xia@nsn.com
# @version 1.0
# @date 2013-04-12


from pkt import Packet

class HSDSCHDATA_TYPE1(Packet):
    """ Maps for HSDSCHDATA type 1"""
    __fields__ = [
            ('frmcrc', 7),
            ('ft', 1),

            ('fsn', 4),
            ('cmchpi', 4),

            ('macdlen', 13),
            ('flush', 1),
            ('drtrest', 1),
            ('spare', 1),

            ('nrpdu', 8),
            ('usrbufsize', 16)
            ]

    def __init__(self, *args):
        """docstring for __init__"""
        self.__dyn_fields__ = []
        super(HSDSCHDATA_TYPE1, self).__init__(*args)

    def unpack(self, buf):
        super(HSDSCHDATA_TYPE1, self).unpack(buf)
        self._parseNewIEFlag(buf)

    def _parseNewIEFlag(self, buf):
        tot_len = len(buf[:-2]) # -2 is for crc

        PAD_4_MACD = 4 # 4 bits padding for macd pdu contents
        per_macd_len = (PAD_4_MACD + self.macdlen)>>3 #padding is 4
        if (PAD_4_MACD + self.macdlen) & 0x7:
            per_macd_len += 1

        dyn_len = tot_len - self.getHdrLen() - per_macd_len * self.nrpdu

        DRT_FLG = 0x1
        SN1_FLG = 0x2
        SN2_FLG = 0x4
        pos = tot_len - dyn_len
        # newieflag field can only detected by packet length
        if dyn_len >= 3: # at least need enough space for 1 byte newie and 2 bytes for other fields
            self.newieflag = int(buf[pos].encode('hex'), 16)
            self.__dyn_fields__.append('newieflag')
            pos += 1
            dyn_len -= 1
            if self.newieflag & DRT_FLG:
                self.drt = int(buf[pos:pos+2].encode('hex'), 16)
                self.__dyn_fields__.append('drt')
                pos += 2
                dyn_len -= 2

            # according to 3GPP TS 25.435 V11.2.0, 2 SN fields may exist
            # in current implementation, this 2 fields seems doesn't exist
            # in case it's needed, please comments them out
            '''
            if self.newieflag & SN1_FLG and dyn_len >= 2:
                tmp = int(buf[pos:pos+2].encode('hex'), 16)
                self.sn1 = tmp >> 1
                self.sd1 = tmp & 0x1
                self.__dyn_fields__.append('sn1')
                self.__dyn_fields__.append('sd1')
                pos += 2
                dyn_len -= 2

            if self.newieflag & SN2_FLG and dyn_len >= 2:
                tmp = int(buf[pos:pos+2].encode('hex'), 16)
                self.sn2 = tmp >> 1
                self.sd2 = tmp & 0x1
                self.__dyn_fields__.append('sn2')
                self.__dyn_fields__.append('sd2')
            '''

    def getHdrLen(self):
        '''Get Hdr len by bytes'''
        return self.__pkt_fields_len__

    def getPyloadCrc(self):
        '''pyload locate at the end of pkt'''
        return int(self.data[-2:].encode('hex'), 16)

    def getDataAmount(self):
        '''get macd data amount'''
        return self.macdlen * self.nrpdu

    def dumppkt(self):
        """Return packet all fields name and values in a list"""
        try:
            return ( (k, getattr(self,k)) for k in self.__pkt_fields__ + self.__dyn_fields__ )
        except AttributeError:
            raise KeyError


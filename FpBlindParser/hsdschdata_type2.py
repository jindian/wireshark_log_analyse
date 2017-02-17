#!/usr/bin/python

##
# @file hsdschdata_type2.py
# @brief Define HSDSCH type2 data frame msg fields
#        Organized as (field name, bits)
# @author Eric - eric.xia@nsn.com
# @version 1.0
# @date 2013-04-12


from pkt import Packet, UnpackError, NeedData
import itertools
from bitstring import BitArray

class HSDSCHDATA_TYPE2(Packet):
    """ Maps for HSDSCHDATA type 2 """
    __fields__ = [
            ('frmcrc', 7),
            ('ft', 1),

            ('fsn', 4),
            ('cmchpi', 4),

            ('nrpdu', 5),
            ('flush', 1),
            ('drtrest', 1),
            ('drtflag', 1),

            ('fi', 1),
            ('edrx', 1),
            ('ts0', 1),
            ('mi', 1),
            ('spare', 4),

            ('usrbufsize',16)
            ]

    __dyn_fields_template__ = [
            ('macdleninblk', 11),
            ('spare', 1),
            ('nrpduinblk', 4),
            ('logicchid', 4)
            ]

    def __init__(self, *args):
        """docstring for __init__"""
        self.__dyn_fields__ = []
        self.__dyn_fields_fmt__ = ''
        self.__dyn_fields_len__ = 0
        try:
            self.unpack(args[0])
        except:
            if len(args[0]) < self.__pkt_fields_len__ + self.__dyn_fields_len__:
                raise NeedData
            raise UnpackError('invalid %s: %r' %
                              (self.__class__.__name__, args[0].encode('hex')))

    def getHdrLen(self):
        '''Get Hdr len by bytes'''
        return self.__pkt_fields_len__ + (self.nrpdu >> 1) * 5 + (self.nrpdu & 0x01) * 3

    def getPyloadCrc(self):
        '''pyload locate at the end of pkt'''
        return int(self.data[-2:].encode('hex'), 16)

    def unpack(self, buf):
        super(HSDSCHDATA_TYPE2, self).unpack(buf)

        self._generateDynFlds()

        for k, v in itertools.izip(self.__dyn_fields__,
                BitArray(bytes=self.data[:self.__dyn_fields_len__]).unpack(self.__dyn_fields_fmt__)):
            setattr(self, k, v)

        self.data = self.data[self.__dyn_fields_len__:]

        if self.drtflag and (len(buf) >= self.getHdrLen() + 4): # at least enough space for 2 bytes drt and 2 bytes crc
            self.drt = int(self.data[0:2].encode('hex'), 16)
            self.data = self.data[2:]
            self.__dyn_fields__.append('drt')


    def _generateDynFlds(self):
        dynflds = []
        for i in xrange(1, self.nrpdu+1):
            for j in self.__dyn_fields_template__:
                dynflds.append((j[0]+str(i), j[1]))

        self.__dyn_fields__ = [ x[0] for x in dynflds ]
        self.__dyn_fields_fmt__ = ','.join([ str(x[1]) for x in dynflds ])

        len_in_bit = sum([ x[1] for x in dynflds ])
        self.__dyn_fields_len__ = len_in_bit >> 3
        if len_in_bit & 0x7:
            self.__dyn_fields_len__ += 1

    def getDynFlds(self):
        return self.__dyn_fields__

    def dumppkt(self):
        """Return packet all fields name and values in a list"""
        try:
            return ( (k, getattr(self,k)) for k in self.__pkt_fields__ + self.__dyn_fields__ )
        except AttributeError:
            raise KeyError

    def getDataAmount(self):
        dataamount = 0
        for i in xrange(1, self.nrpdu+1):
            dataamount += (getattr(self, 'macdleninblk'+str(i)) * getattr(self, 'nrpduinblk'+str(i))) << 3
        return dataamount

#!/usr/bin/python

##
# @file hsdsch.py
# @brief Define base class for HSDSCH
# @author Eric - eric.xia@nsn.com
# @version 1.0
# @date 2013-04-12


import pkt

# only can parse ctrl frame here
HSDSCH_TYPE_HSDSCHCTRL = 1

class Hsdsch(pkt.Packet):
    """docstring for hsdsch"""
    __fields__ = [
            ('frmcrc', 7),
            ('ft', 1)
            ]
    _typesw = {}

    def unpack(self, buf):
        pkt.Packet.unpack(self, buf)
        buf = buf[self.__pkt_fields_len__:]
        try:
            self.data = self._typesw[self.ft](buf)
            setattr(self, self.data.__class__.__name__.lower(), self.data)
        except (KeyError, pkt.UnpackError):
            self.data = buf

    @classmethod
    def set_type(cls, t, pktclass):
        cls._typesw[t] = pktclass

    @classmethod
    def get_type(cls, t):
        return cls._typesw[t]

def __load_types():
    g = globals()
    for k, v in g.iteritems():
        if k.startswith('HSDSCH_TYPE_'):
            name = k[12:]
            modname = name.lower()
            try:
                mod = __import__(modname, g)
            except ImportError:
                continue
            Hsdsch.set_type(v, getattr(mod, name))

if not Hsdsch._typesw:
    __load_types()



if __name__ == '__main__':
    pass

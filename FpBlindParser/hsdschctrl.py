#!/usr/bin/python

##
# @file hsdschctrl.py
# @brief Define base class for HSDSCH contrl msg
# @author Eric - eric.xia@nsn.com
# @version 1.0
# @date 2013-04-12


import pkt

# only CA response msg parsed
HSDSCHCTRL_TYPE_CA_TYPE1 = 0xb # type 1 capacity allocation response
HSDSCHCTRL_TYPE_CA_TYPE2 = 0xc # type 2 capacity allocation response

HSDSCHCTRL_TYPE_CR = 0xa # Capacity Request 
HSDSCHCTRL_TYPE_DL_NODE_SYNC = 0x6 # DL Node Sync Control Frame Type
HSDSCHCTRL_TYPE_UL_NODE_SYNC = 0x7 # UL Node Sync Control Frame Type

class HSDSCHCTRL(pkt.Packet):
    """docstring for HSDSCHCTRL"""
    __fields__ = [
            ('ctrlft', 8) # ctrl frame type
            ]
    _typesw = {}

    def unpack(self, buf):
        """docstring for unpack"""
        pkt.Packet.unpack(self, buf)
        buf = buf[self.__pkt_fields_len__:]
        try:
            self.data = self._typesw[self.ctrlft](buf)
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
        if k.startswith('HSDSCHCTRL_TYPE_'):
            name = k[16:]
            modname = name.lower()
            try:
                mod = __import__(modname, g)
            except ImportError:
                continue
            HSDSCHCTRL.set_type(v, getattr(mod, name))

if not HSDSCHCTRL._typesw:
    __load_types()



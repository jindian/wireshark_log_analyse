#!/usr/bin/python

##
# @file pkt.py
# @brief Define base class for all pkt format.
#        The main idea of packet fields decoding is inspired by python dpkt lib,
#        except using "bitstring" module other than "struct" module to do unpack
#        thing, since "bitstring" offers a more flexible way to parse the fields
#        which cross bytes.
#
# @author Eric - eric.xia@nsn.com
# @version 1.0
# @date 2013-04-12


from bitstring import BitArray
import itertools

class Error(Exception): pass
class UnpackError(Error): pass
class NeedData(UnpackError): pass

class _MetaPacket(type):
    def __new__(cls, clsname, clsbase, clsdict):
        """docstring for __new__"""
        t = type.__new__(cls, clsname, clsbase, clsdict)
        st = getattr(t, '__fields__', None)
        if st is not None:
            clsdict['__slots__'] = [ x[0] for x in st ] + [ 'data' ]
            t = type.__new__(cls, clsname, clsbase, clsdict)
            t.__pkt_fields__ = [ x[0] for x in st ]
            t.__pkt_fields_fmt__ = ','.join([ str(x[1]) for x in st ])
            t.__pkt_fields_len__ = sum([ x[1] for x in st ]) >> 3
        return t

class Packet(object):
    """docstring for Packet"""
    __metaclass__ = _MetaPacket

    def __init__(self, *args):
        """docstring for __init__"""
        try:
            self.unpack(args[0])
        except:
            if len(args[0]) < self.__pkt_fields_len__:
                raise NeedData
            raise UnpackError('invalid %s: %r' %
                              (self.__class__.__name__, args[0].encode('hex')))

    def unpack(self, buf):
        """Unpack packet header fields from buf, and set self.data."""
        for k, v in itertools.izip(self.__pkt_fields__,
                BitArray(bytes=buf[:self.__pkt_fields_len__]).unpack(self.__pkt_fields_fmt__)):
            setattr(self, k, v)
        self.data = buf[self.__pkt_fields_len__:]

    def dumppkt(self):
        """Return packet all fields name and values in a list"""
        try:
            return ( (k, getattr(self,k)) for k in self.__pkt_fields__ )
        except AttributeError:
            raise KeyError


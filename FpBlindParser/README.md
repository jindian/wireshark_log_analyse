==============
FpBlindParser
==============

It's a Python script to parse Hsdsch packets from wireshark/tcpdump libpcap file.

Design inspiration:
------------------------------------
The main logic of Hsdsch packets detecting and processing is inspired by old FpBlindParser
script written by Daniel, pls refer to file decription of FpBlindParser.py.

The main idea of packet fields decoding is inspired by python dpkt lib,
except using "bitstring" module other than "struct" module to do unpack thing,
since "bitstring" offers a more flexible way to parse the fields which cross bytes.


Python Lib Dependence requirement:
------------------------------------
    dpkt              http://dpkt.googlecode.com/
    bitstring         http://python-bitstring.googlecode.com
                      http://packages.python.org/bitstring
    Tkinter(Optional)


Usage:
------------------------------------
Usage: FpBlindParser.py [options]

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -f FILENAME, --file=FILENAME
                        specify pcap file to process
  -c, --crc             check crc while process pcap file
  -a, --caonly          decode CA only while process pcap file

If no pcap file specified, the script will ask for input file at startup.


Tips:
------------------------------------
pypy can speed up python scripts execution by times, in case pcap file is too big and
consume too much time to parse, please try pypy.
Download from pypy.org, unzip it, either run it directly from its location, "pypy FpBlindParser.py"
or use python-virtualenv to run it from virualenv(refer to pypy.org).
You need re-install dpkt/bitstring for pypy.


Note!!
------------------------------------
Packets capture file has various format, if your file is not libpcap format,
please use "editcap" utility from wireshark to do format conversion first.


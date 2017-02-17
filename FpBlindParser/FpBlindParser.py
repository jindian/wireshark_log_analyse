#!/usr/bin/python

##
# @file FpBlindParser.py
# @brief Based on old FpBlindParser script written by Daniel.Yang
#        Parse hsdsch packets from pcap file
#        1. find out udp packets
#        2. 1st loop detect CA control msg and decode it
#        3. record CA msg type and its ip,port info
#        4. scan the pcap over to parse data based on step 3 info
# @author Eric - eric.xia@nsn.com
# @version 2.0
# @date 2013-04-24


"""
"""

# Need dpkt module
import dpkt
import sys
import os
import hsdsch
import hsdschctrl
import hsdschdata_type2
import hsdschdata_type1
import socket
import datetime
from crcWrapper import CrcWrapper
from optparse import OptionParser
import pkt


# Counters
counter=0
udpcounter=0

HSDSCH_CR_LEN = 5
HSDSCH_CA_TYPE1_LEN = 8
HSDSCH_CA_TYPE2_LEN = 9
HSDSCH_DL_NODE_SYNC_LEN = 5
HSDSCH_UL_NODE_SYNC_LEN = 11

hsdsch_ctrl_type_len = [
#        HSDSCH_CR_LEN,
        HSDSCH_CA_TYPE1_LEN,
        HSDSCH_CA_TYPE2_LEN,
#        HSDSCH_DL_NODE_SYNC_LEN,
#        HSDSCH_UL_NODE_SYNC_LEN
	]

typeFPDict = {}

FPHandler = {
        hsdschctrl.HSDSCHCTRL_TYPE_CA_TYPE1 : hsdschdata_type1.HSDSCHDATA_TYPE1,
        hsdschctrl.HSDSCHCTRL_TYPE_CA_TYPE2 : hsdschdata_type2.HSDSCHDATA_TYPE2
        }

def parseOpt():
    global inputfilename
    global crccheck
    global caonly
    parser = OptionParser(usage="%prog [options]", version="%prog 2.0")
    parser.add_option("-f", "--file",
                          action="store", type="string", dest="filename",
                          help="specify pcap file to process")
    parser.add_option("-c", "--crc",
                          action="store_true", dest="crccheck",
                          help="check crc while process pcap file")
    parser.add_option("-a", "--caonly",
                          action="store_true", dest="caonly",
                          help="decode CA only while process pcap file")
    (options, args) = parser.parse_args()
    if options.filename:
        inputfilename = options.filename

    if options.crccheck:
        crccheck = True

    if options.caonly:
        caonly = True


def getInputFile():
    '''
    If no pcap file specified from arg at startup, ask for inputting.
    if Tkinter is installed on machine, pop out a dialog window for inputting
    otherwise, prompt msg from cmd for inputting
    '''
    if inputfilename:
            filename = inputfilename
    else:
        try:
            import Tkinter, tkFileDialog

            ftypes = [("pcap files", ".pcap"), ("All files", ".*")]
            master = Tkinter.Tk()
            master.withdraw() #hiding tkinter window
            filename = tkFileDialog.askopenfilename(title="Choose your pcap file", filetypes=ftypes)
        except ImportError:
            filename = raw_input("Enter the pcap trace file: ")

    if os.path.isfile(filename):
        print "Present: ",filename
    else:
        print "Absent: ",filename
        sys.stderr.write("Cannot open file for reading\n")
        sys.exit(-1)

    try:
        f = open(filename,'rb')
    except:
        err = "Failed to open %s for reading input\n" % filename
        sys.stderr.write(err)
        sys.exit(-1)
    return f


OUTPUT_FILE_SIZE_LIMIT = 20 * 1024 * 1024
outputfdict = {}

def ts2str(ts):
    '''convert timestamp to str, keep ms level precision'''
    #return datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d%H%M%S%f')
    return '%.3f' % ts

def addr2str(addr):
    '''convert ((sip, sport), (dip, dport)) to str'''
    return '_'.join([ i for t in addr for i in t ])

BIT_CRCERR = 0x1
BIT_DFTYPE1_336 = 0x1 << 1
BIT_DFTYPE1_656 = 0x1 << 2
BIT_DFTYPE2 = 0x1 << 3
BIT_CATYPE1_336 = 0x1 << 4
BIT_CATYPE1_656 = 0x1 << 5
BIT_CATYPE2 = 0x1 << 6
BIT_UL_NODE_SYNC = 0x1<<7
BIT_DL_NODE_SYNC = 0x1<<8
BIT_CR = 0x1<<9

def newFileNameAppendix(flag):
    tmp = ''
    strmap = {
            BIT_CATYPE1_336: '_catype1_336_only',
            BIT_CATYPE1_656: '_catype1_656_only',
            BIT_CATYPE2: '_catype2_only',
            BIT_CATYPE1_336 | BIT_CATYPE2: '_catype1_336_catype2',
            BIT_CATYPE1_656 | BIT_CATYPE2: '_catype1_656_catype2',
            BIT_CATYPE1_336 | BIT_CATYPE1_656: '_catype1_336_656'
            }
    try:
        tmp += strmap[flag & ~BIT_CRCERR]
    except KeyError:
        if flag & BIT_DFTYPE1_336:
            tmp += '_type1_336'
        if flag & BIT_DFTYPE1_656:
            tmp += '_type1_656'
        if flag & BIT_DFTYPE2:
            tmp += '_type2'
        if flag & BIT_UL_NODE_SYNC:
            #tmp += '_ul_sync'
            pass
        if flag & BIT_DL_NODE_SYNC:
            #tmp += '_dl_sync'
            pass

    if flag & BIT_CRCERR:
        tmp += '_crcerr'
    return tmp

def getOutputFile(ts, addr, flag=0):
    '''
    opened file associated with addr are recorded in outputfdict.
    if file found in outputfdict, check its size, if its size little
    than limitation, return the opened file hander. Otherwise open
    a new file and return its handler.
    '''
    # outputfdict = { ((sip, sport), (dip, dport)):[f, flag] }
    if addr in outputfdict:
        newflag = outputfdict[addr][1] | flag
        # if file already open, check its size
        f = outputfdict[addr][0]
        filename = f.name
        if f.closed:
            try:
                del outputfdict[addr]
                f = open(filename, 'a')
            except:
                err = "Failed to open %s for writing output\n" % f.name
                sys.stderr.write(err)
                sys.exit(-1)


        outputfdict[addr] = [f, newflag]
        f.seek(0, 2)
        if f.tell() >= OUTPUT_FILE_SIZE_LIMIT:
            f.close()
            tmpflag = outputfdict[addr][1]
            if tmpflag:
                fn = os.path.splitext(f.name)[0] + newFileNameAppendix(tmpflag) + '.csv'
                if os.path.exists(fn):
                    os.remove(fn)
                os.rename(f.name, fn)
            del outputfdict[addr]
        else:
            return f

    # in case too many files opened
    if sum(( 1 if not fo[0].closed else 0 for fo in outputfdict.values() )) >= 512:
        closeAllOutputFile()

    fname = addr2str(addr) + '_' + ts2str(ts) + '.csv'
    try:
        f = open(fname, 'w')
    except:
        err = "Failed to open %s for writing output\n" % fname
        sys.stderr.write(err)
        sys.exit(-1)

    writeHdr2Output(f)
    outputfdict[addr] = [f, flag]
    return f


def closeAllOutputFile():
    '''close all output files'''
    for f in outputfdict.values():
        if not f[0].closed:
            f[0].close()

def createOutputDir(fn):
    '''create output directory, dir name base on input filename'''
    dirname = os.path.splitext(fn)[0] + '_Parsed'
    if not os.path.exists(dirname):
        os.mkdir(dirname)
    abspth = os.path.abspath(dirname)
    os.chdir(dirname)
    #for i in os.listdir('.'):
    #    os.remove(i)
    print "Output will write to directory %s\n" % abspth

DATA_AMOUNT = 'dataamount'
outputfields = [
        'congest', 'cmchpi', 'maxpdulen', 'credit', 'interval',
        'rep', 'fsn', 'macdlen', 'flush', 'drtrest', 'drtflag', 'newieflag',
        'drt', 'nrpdu', 'fi', 'edrx', 'ts2', 'mi', 'usrbufsize', 'grantedbps',
        DATA_AMOUNT,
        'T1', 'T2', 'T3'
        ]

# below fields may not exist or more than 1
# put it to hdr just for reading
dynflds = [
        'macdleninblk1', 'spare1', 'nrpduinblk1', 'logicchid1',
        ]

def calibrateHdr(hdr_in_list):
    L = ['maxpdulen', 'macdlen', DATA_AMOUNT]
    for i in L:
        if i in hdr_in_list:
            hdr_in_list[hdr_in_list.index(i)] += '(bits)'

    L = ['drt']
    for i in L:
        if i in hdr_in_list:
            hdr_in_list[hdr_in_list.index(i)] += '(ms)'

    L = ['interval']
    for i in L:
        if i in hdr_in_list:
            hdr_in_list[hdr_in_list.index(i)] += '(10ms)'

    L = ['FPLen', 'usrbufsize', 'macdleninblk1']
    for i in L:
        if i in hdr_in_list:
            hdr_in_list[hdr_in_list.index(i)] += '(bytes)'

def writeHdr2Output(f):
    '''write hdr to opened output file'''
    common = [ 'FrameNo', 'Timestamp', 'BtsIP', 'BtsPort', 'RncIP', 'RncPort', 'FPLen', 'Type' ]

    crcinfo = []
    if crccheck:
        crcinfo = crcfields
    # calibrate header, add unit: bytes, bits, ms, s
    hdr = common + crcinfo + outputfields + dynflds
    calibrateHdr(hdr)

    f.write(','.join(hdr) + '\n')

class FrmTypeError(Exception): pass

def writeData2Output(frameno, ts, addr, length, typestr, data, crcdata):
    '''write output to csv'''
    flag = 0
    try:
        flag |= TYPE_STR_BIT_MAP[typestr]
    except KeyError:
        raise FrmTypeError

    statfld = typestr
    macdSize = 0
    if crcdata and crcdata['crccheck'] == 'ERR':
        if flag & (BIT_CATYPE1_336 | BIT_CATYPE1_656 | BIT_CATYPE2):
            statfld = CA_CRC_ERR
        elif flag & (BIT_DFTYPE1_336 | BIT_DFTYPE1_656 | BIT_DFTYPE2):
            statfld = DF_CRC_ERR
        flag |= BIT_CRCERR
    else:
        if hasattr(data, 'getDataAmount'):
            macdSize = data.getDataAmount()

    updateStat(addr, statfld, ts, length<<3, macdSize)

    f = getOutputFile(ts, addr, flag)
    # patch for type2 dynamic part
    dynfields = []
    if hasattr(data, 'getDynFlds'):
        dynfields.extend(data.getDynFlds())
    # fill all fields to 'N/A' as default value
    outputdata = dict.fromkeys(outputfields, 'N/A')
    outputdata.update(data.dumppkt())

    calibrateOutput(outputdata, data, flag)

    outlist = []
    outlist.append(str(frameno))
    outlist.append(ts2str(ts))
    outlist.extend([ i for t in addr for i in t ])
    outlist.append(str(length))
    outlist.append(typestr)
    if crcdata:
        outlist.extend([crcdata[i] for i in crcfields])

    outlist.extend([ str(outputdata[it]) for it in outputfields + dynfields ])
    outlist.append('\n')

    f.write(','.join(outlist))


# congestion field conversion
#0 No Congestion
#1 Reserved
#2 Delay Buildup
#3 Frameloss Or Overload
congest_conv = { 'N/A':'N/A', 0:'No Congestion', 1:'Reserved', 2:'Delay Buildup', 3:'Frameloss Or Overload'}
def calibrateOutput(outputdata, data, flag=0):
    outputdata['congest'] = congest_conv[outputdata['congest']]

    if (flag & (BIT_CATYPE1_336|BIT_CATYPE1_656)) and outputdata['credit'] == 2047:
        outputdata['credit'] = 'unlimited'

    if (flag & BIT_CATYPE2) and outputdata['credit'] == 65535:
        outputdata['credit'] = 'unlimited'

    if hasattr(data, 'getGrantedbps'):
        tmp = data.getGrantedbps()
        if tmp == -1:
            tmp = 'unlimited'
        outputdata['grantedbps'] = tmp

    if (not (flag & BIT_CRCERR)) and hasattr(data, 'getDataAmount'):
        outputdata[DATA_AMOUNT] = data.getDataAmount()


crcfields = [ 'crccheck', 'hdrcrc', 'expected hdrcrc','pycrc', 'expected pycrc']

def mkCrcData(hdrcrc, calhdrcrc, pycrc=None, calpycrc=None):
    """docstring for mkCrcData"""
    crcdata= dict.fromkeys(crcfields, 'N/A')
    if hdrcrc != calhdrcrc or pycrc != calpycrc:
        crcdata['crccheck'] = "ERR"
    else:
        crcdata['crccheck'] = "OK"

    crcdata['hdrcrc'] = hex(hdrcrc)
    crcdata['expected hdrcrc'] = hex(calhdrcrc)

    if pycrc is not None :
        crcdata['pycrc'] = hex(pycrc)
    if calpycrc is not None:
        crcdata['expected pycrc'] = hex(calpycrc)

    return crcdata


HDR_POLY = 1<<7 | 1<<6 | 1<<2 | 1
PYL_POLY = 1<<16 | 1<<15 | 1<<2 | 1

# refactor: by introducing CrcWrapper and crc_algo_inst
# process speed get significantly improved(^*^)
# the more packet processed, the more time saved
crc_algo_inst = {}
def generateCrc(buf, poly):
    if poly not in crc_algo_inst:
        crc = CrcWrapper(width = len(bin(poly))-3, poly = poly,
                reflect_in = 0, xor_in = 0x0000,
                reflect_out = 0, xor_out = 0x0000)
        crc_algo_inst[poly] = crc
    else:
        crc = crc_algo_inst[poly]
    return crc.table_driven(buf)

CA_TYPE1_STR = 'CA type1'
CA_TYPE1_STR_336 = 'CA type1 336'
CA_TYPE1_STR_656 = 'CA type1 656'
CA_TYPE2_STR = 'CA type2'

CA_TYPE_LIST = [ CA_TYPE1_STR_336, CA_TYPE1_STR_656, CA_TYPE2_STR ]

DF_TYPE1_STR = 'DF type1'
DF_TYPE1_STR_336 = 'DF type1 336'
DF_TYPE1_STR_656 = 'DF type1 656'
DF_TYPE2_STR = 'DF type2'
DF_DL_NODE_SYNC_STR = 'DL Node Sync'
DF_UL_NODE_SYNC_STR = 'UL Node Sync'

DF_TYPE_LIST = [ DF_TYPE1_STR, DF_TYPE1_STR_336, DF_TYPE1_STR_656, DF_TYPE2_STR ]

TYPE_STR_BIT_MAP = {
        CA_TYPE1_STR_336: BIT_CATYPE1_336, CA_TYPE1_STR_656: BIT_CATYPE1_656,
        CA_TYPE2_STR: BIT_CATYPE2,
        DF_TYPE1_STR_336: BIT_DFTYPE1_336, DF_TYPE1_STR_656: BIT_DFTYPE1_656,
        DF_TYPE2_STR: BIT_DFTYPE2,
        #No need to add extra information for ul and dl node sync
        DF_UL_NODE_SYNC_STR: 0, 
        DF_DL_NODE_SYNC_STR: 0
        }

CA_TYPE_BIT_STR_MAP = {
        BIT_CATYPE1_336:CA_TYPE1_STR_336, BIT_CATYPE1_656:CA_TYPE1_STR_656,
        BIT_CATYPE2:CA_TYPE2_STR,
        }

DF_TOT_LEN_ERR = 'DF total len too short'
DF_PYL_LEN_ERR = 'DF pyload len too short'
DF_MACD_LEN_ERR = 'DF Type 1 macdlen mismatch'
DF_CRC_ERR = 'DF crc error'
CA_CRC_ERR = 'CA crc error'

ERR_LIST = [ DF_TOT_LEN_ERR, DF_PYL_LEN_ERR, DF_MACD_LEN_ERR, DF_CRC_ERR, CA_CRC_ERR ]

DF_DURATION = 'Data conn duration(s)'
DF_TOT_DATA = 'Total DF data amount(bits)'
AVG_DATA_RATE = 'Avg DF data rate(bps)'
DF_FIRST_TS = 'First DF timestamp'
DF_LAST_TS = 'Last DF timestamp'
perconn_stat_fields = [
        CA_TYPE1_STR_336, CA_TYPE1_STR_656, CA_TYPE2_STR,
        DF_TYPE1_STR_336, DF_TYPE1_STR_656, DF_TYPE2_STR,
        CA_CRC_ERR, DF_CRC_ERR, DF_TOT_LEN_ERR, DF_PYL_LEN_ERR, DF_MACD_LEN_ERR,
        DF_FIRST_TS, DF_LAST_TS, DF_DURATION, DF_TOT_DATA, AVG_DATA_RATE,
        DF_DL_NODE_SYNC_STR, DF_UL_NODE_SYNC_STR]
hsdsch_perconn_stat = {}

AVG_RAWDATA_RATE = 'Avg DF raw data rate(bps)(with FP hdr and err frame)'
DF_OTHER_ERR = 'DF other error'
persec_stat_fields = [
        AVG_RAWDATA_RATE, AVG_DATA_RATE, DF_CRC_ERR, DF_OTHER_ERR
        ]
hsdsch_persec_stat = {}

def updateStat(addr, typestr, ts, udp_len, macd_pdu_len):
    updatePerConnStat(addr, typestr, ts, macd_pdu_len)
    updatePerSecStat(typestr, ts, udp_len, macd_pdu_len)

def writeStat():
    return writePerConnStat() + ', ' + writePerSecStat()

def updatePerSecStat(typestr, ts, udp_len, pyload_len):
    # only process Data frame
    if typestr not in CA_TYPE_LIST and typestr != CA_CRC_ERR:
        if not updatePerSecStat.first_df_ts:
            updatePerSecStat.first_df_ts = ts
        updatePerSecStat.last_df_ts = ts
        ts_int = int(ts)
        if ts_int not in hsdsch_persec_stat:
            hsdsch_persec_stat[ts_int] = dict.fromkeys(persec_stat_fields, 0)
        hsdsch_persec_stat[ts_int][AVG_RAWDATA_RATE] += udp_len
        hsdsch_persec_stat[ts_int][AVG_DATA_RATE] += pyload_len

        if typestr in ERR_LIST:
            if typestr != DF_CRC_ERR:
                typestr = DF_OTHER_ERR
            hsdsch_persec_stat[ts_int][typestr] += 1

updatePerSecStat.first_df_ts = None
updatePerSecStat.last_df_ts = None

def writePerSecStat():
    with open('Hsdsch_per_second_stat.csv', 'w') as f:
        name = f.name
        out_hdr = ['Timestamp'] + persec_stat_fields
        out_hdr.append('\n')
        f.write(','.join(out_hdr))

        for ts in hsdsch_persec_stat:
            out_data = []
            out_data.append(str(ts))
            out_data.extend([ str(hsdsch_persec_stat[ts][it]) for it in persec_stat_fields ])
            f.write(','.join(out_data) + '\n')

        sum_f = lambda fld, stat=hsdsch_persec_stat: str(sum(stat[ts][fld] for ts in stat)/len(stat))
        f.write('\nSummary:\n')
        out_total = []
        out_total.append(str(len(hsdsch_persec_stat)))
        out_total.extend(map(sum_f, persec_stat_fields))
        f.write(','.join(out_total) + '\n')

    return os.path.abspath(name)

def updatePerConnStat(addr, typestr, ts, macd_pdu_len):
    '''update Hsdsch pkt statistic'''
    if addr not in hsdsch_perconn_stat:
        hsdsch_perconn_stat[addr] = dict.fromkeys(perconn_stat_fields, 0)
    hsdsch_perconn_stat[addr][typestr] += 1

    if typestr in DF_TYPE_LIST:
        if addr not in updatePerConnStat.startConn:
            updatePerConnStat.startConn[addr] = ts
            hsdsch_perconn_stat[addr][DF_FIRST_TS] = '%.6f' % ts
        hsdsch_perconn_stat[addr][DF_LAST_TS] = '%.6f' % ts
        hsdsch_perconn_stat[addr][DF_DURATION] = ts - updatePerConnStat.startConn[addr]

        hsdsch_perconn_stat[addr][DF_TOT_DATA] += macd_pdu_len
        if hsdsch_perconn_stat[addr][DF_DURATION]:
            hsdsch_perconn_stat[addr][AVG_DATA_RATE] = hsdsch_perconn_stat[addr][DF_TOT_DATA]/\
                    hsdsch_perconn_stat[addr][DF_DURATION]

# used as static variable compare to C language
updatePerConnStat.startConn = {}


PerConnStatFile = 'Hsdsch_per_connect_stat.csv'

def writePerConnStat():
    '''write Hsdsch pkt statistic to HsdschStatFile'''
    with open(PerConnStatFile, 'w') as f:
        name = f.name
        outlist = [ 'BtsIP', 'BtsPort', 'RncIP', 'RncPort' ]
        if crccheck:
            tmp_stat_fields = perconn_stat_fields
        else:
            tmp_stat_fields = [ i for i in perconn_stat_fields \
                    if i != CA_CRC_ERR and i != DF_CRC_ERR]

        outlist.extend(tmp_stat_fields)
        outlist.append('\n')
        f.write(','.join(outlist))

        for addr in hsdsch_perconn_stat:
            outlist = []
            outlist.extend([ i for t in addr for i in t ])
            outlist.extend([ str(hsdsch_perconn_stat[addr][i]) for i in tmp_stat_fields ])
            outlist.append('\n')
            f.write(','.join(outlist))

    return os.path.abspath(name)

def writeErrHsdschDataFrm2Output(frameno, ts, addr, typestr, buf, errstr):
    if not writeErrHsdschDataFrm2Output.f:
        # write Hdr
        errfrmfile = 'Hsdsch_err_frm.csv'
        f = open(errfrmfile, 'w')
        f.write('FrameNo, ts, BtsIP, BtsPort, RncIP, RncPort,')
        f.write('fptype, data, errstr,')
        f.write('\n')
        writeErrHsdschDataFrm2Output.f = f
    else:
        f = writeErrHsdschDataFrm2Output.f

    updateStat(addr, errstr.split(',')[0], ts, len(buf)<<3, 0)
    # write data
    outlist = []
    outlist.append(str(frameno))
    outlist.append(ts2str(ts))
    outlist.extend([ i for t in addr for i in t ])
    outlist.append(typestr)
    outlist.append(buf)
    outlist.append(errstr)
    outlist.append('\n')

    f.write(','.join(outlist))

writeErrHsdschDataFrm2Output.f = None

def CAOnlyDecoder(frameno, ts, addr, length, catypestr, hsdschpkt_ctrl):
    """docstring for CAOnlyDecoder"""
    if hsdschpkt_ctrl.ctrlft == hsdschctrl.HSDSCHCTRL_TYPE_CA_TYPE1:
        fnstr = 'ca_type1_' + str(hsdschpkt_ctrl.ca_type1.maxpdulen)
        flag = eval('BIT_CATYPE1_%d' % hsdschpkt_ctrl.ca_type1.maxpdulen)
    else:
        fnstr = 'ca_type2'
        flag = BIT_CATYPE2

    data = hsdschpkt_ctrl.data
    outputdata = {}
    outputdata.update(data.dumppkt())

    updatePerConnStat(addr, catypestr, ts, 0)

    # add a new field not exist in pkg
    outputdata['grantedbps'] = 0
    calibrateOutput(outputdata, data, flag)

    # always write to ca_all.csv file
    L = [ 'ca_all', fnstr ]
    for fname in L:
        if fname not in CAOnlyDecoder.fdict:
            f = open(fname + '.csv', 'w')
            # write HDR
            hdr = ['FrameNo', 'Timestamp', 'BtsIP', 'BtsPort', 'RncIP', 'RncPort', 'FPLen', 'Type']
            hdr += outputdata.keys()

            calibrateHdr(hdr)
            f.write(','.join(hdr) + '\n')

            CAOnlyDecoder.fdict[fname] = f
        else:
            f = CAOnlyDecoder.fdict[fname]

        outlist = []
        outlist.append(str(frameno))
        outlist.append(ts2str(ts))
        outlist.extend([ i for t in addr for i in t ])
        outlist.append(str(length))
        outlist.append(fnstr)
        outlist.extend([ str(outputdata[it]) for it in outputdata ])
        outlist.append('\n')

        f.write(','.join(outlist))


CAOnlyDecoder.fdict = {}

def parseBts2RncHsdschPkt(frameno, scantimes, buf, ts, addr):
    '''
    parse BTS to RNC Hsdsch pkt, CA msg get processed
    and record its RncIP, RncPort, BtsIP, BtsPort info
    '''
    if scantimes == 0: # scantime 0
        if len(buf) in hsdsch_ctrl_type_len:
            hsdschpkt = hsdsch.Hsdsch(buf)

            if hsdschpkt.ft == hsdsch.HSDSCH_TYPE_HSDSCHCTRL:
                hsdschpkt_ctrl = hsdschpkt.data

                # fix the bug when frame happen to be wrong with len and type
                if validateCtrlFpType(len(buf), hsdschpkt_ctrl.ctrlft)!=0:
                    return -1

                if hsdschpkt_ctrl.ctrlft == hsdschctrl.HSDSCHCTRL_TYPE_CA_TYPE1 or \
                    hsdschpkt_ctrl.ctrlft == hsdschctrl.HSDSCHCTRL_TYPE_CA_TYPE2:

                    if hsdschpkt_ctrl.ctrlft == hsdschctrl.HSDSCHCTRL_TYPE_CA_TYPE1:
                        maxpdulen = hsdschpkt_ctrl.ca_type1.maxpdulen
                        if maxpdulen == 336:
                            catypestr = CA_TYPE1_STR_336
                        elif maxpdulen == 656:
                            catypestr = CA_TYPE1_STR_656
                        else:
                            # do simple validation
                            # maxpdulen is wrong, may not be CA msg
                            return -1
                    else:
                        maxpdulen = hsdschpkt_ctrl.ca_type2.maxpdulen
                        if maxpdulen > 1505:
                            # do simple validation
                            # {0, 1505}, 0 - not used from TS 25.435
                            # maxpdulen is wrong, may not be CA msg
                            return -1
                        catypestr = CA_TYPE2_STR

                    # always to crc check no matter crc check specified
                    # to avoid wrong ca info used
                    tmpbuf = buf[1:]
                    tmpbuf = b'\x01' + tmpbuf
                    crcdata = mkCrcData(hsdschpkt.frmcrc, generateCrc(tmpbuf, HDR_POLY))
                    if crcdata['crccheck'] == "ERR":
                        return -1

                    if caonly:
                        CAOnlyDecoder(frameno, ts, addr, len(buf), catypestr, hsdschpkt_ctrl)
                    else:
                        # in case type change happen, the list hold all type changed info
                        # e.g. ((sip,sport), (dip, dport)):[ (type1, ts1), (type2, ts2), (type1, ts3) ]
                        # the index 0 hold the biggest timestamp
                        if addr not in typeFPDict:
                            typeFPDict[addr] = [ (hsdschpkt_ctrl.ctrlft, ts) ]
                        elif hsdschpkt_ctrl.ctrlft != typeFPDict[addr][0][0]:
                            # okey, type changed
                            typeFPDict[addr].insert(0, (hsdschpkt_ctrl.ctrlft, ts))
                        parseBts2RncHsdschPkt.ca_frmno_dict[frameno] = TYPE_STR_BIT_MAP[catypestr]
                elif hsdschpkt_ctrl.ctrlft == hsdschctrl.HSDSCHCTRL_TYPE_UL_NODE_SYNC :
                    tmpbuf = buf[1:]
                    tmpbuf = b'\x01' + tmpbuf
                    crcdata = mkCrcData(hsdschpkt.frmcrc, generateCrc(tmpbuf, HDR_POLY))
                    if crcdata['crccheck'] == "ERR":
                        return -1
                    parseBts2RncHsdschPkt.ctrl_frmno_dict[frameno] = crcdata
    else:
        if frameno in parseBts2RncHsdschPkt.ca_frmno_dict:
            hsdschpkt = hsdsch.Hsdsch(buf)
            hsdschpkt_ctrl = hsdschpkt.data

            catypestr = CA_TYPE_BIT_STR_MAP[parseBts2RncHsdschPkt.ca_frmno_dict[frameno]]
            crcdata = None
            if crccheck:
                tmpbuf = buf[1:]
                tmpbuf = b'\x01' + tmpbuf
                crcdata = mkCrcData(hsdschpkt.frmcrc, generateCrc(tmpbuf, HDR_POLY))

            writeData2Output(frameno, ts, addr, len(buf), catypestr, hsdschpkt_ctrl.data, crcdata)
            del parseBts2RncHsdschPkt.ca_frmno_dict[frameno]
        elif frameno in parseBts2RncHsdschPkt.ctrl_frmno_dict:
            hsdschpkt = hsdsch.Hsdsch(buf)
            hsdschpkt_ctrl = hsdschpkt.data
            ctrlFrmTypeStr = DF_UL_NODE_SYNC_STR
            crcdata = None
            if crccheck:
                crcdata = parseBts2RncHsdschPkt.ctrl_frmno_dict[frameno]
            writeData2Output(frameno, ts, addr, len(buf), ctrlFrmTypeStr, hsdschpkt_ctrl.data, crcdata)
            del parseBts2RncHsdschPkt.ctrl_frmno_dict[frameno]

parseBts2RncHsdschPkt.ca_frmno_dict = {}
parseBts2RncHsdschPkt.ctrl_frmno_dict = {}

CTRL_FP_TYPE_LEN_DIC = {
#        10 : HSDSCH_CR_LEN,
        11 : HSDSCH_CA_TYPE1_LEN, 
        12 : HSDSCH_CA_TYPE2_LEN, 
        6 : HSDSCH_DL_NODE_SYNC_LEN, 
        7 : HSDSCH_UL_NODE_SYNC_LEN
        }

CTRL_FP_TYPE_STR_DIC = {
        11 : CA_TYPE1_STR,
        12 : CA_TYPE2_STR,
        6  : DF_DL_NODE_SYNC_STR,
        7  : DF_UL_NODE_SYNC_STR
        }

def validateCtrlFpType(fplen, fptype):
    if fptype in CTRL_FP_TYPE_LEN_DIC.keys() :
        if fplen == CTRL_FP_TYPE_LEN_DIC[fptype]:
            return 0
        else:
            return -1
    else :
        return -1

def getCtrlFpStr(fptype):
    return CTRL_FP_TYPE_STR_DIC[fptype]


def parseRnc2BtsHsdschPkt(frameno, buf, ts, addr):
    '''
    parse RNC to BTS Hsdsch pkt based on RncIP, RncPort, BtsIP, BtsPort info from CA msg
    '''
    # CA msg and data frame is in reverse direction
    # From Rnc to Bts
    # addr[::-1] reverse the position sip,sport and dip,dport
    addr = addr[::-1]
    crcdata = None
    if addr in typeFPDict: # minimal length of datafrm is ??

        # filter out ctrl msg
        hsdschpkt = hsdsch.Hsdsch(buf)
        if hsdschpkt.ft == hsdsch.HSDSCH_TYPE_HSDSCHCTRL:
            # TODO: if Credit Request msg need to be parsed, add code here
            if len(buf) in hsdsch_ctrl_type_len:
                hsdschpkt_ctrl = hsdschpkt.data
                #TODO: Add CR FpFrame Frame Here, Temp Leave CR FpFrames 
                if hsdschpkt_ctrl.ctrlft == 10 :
                    return 0
                if validateCtrlFpType(len(buf), hsdschpkt_ctrl.ctrlft)!=0:
                    return -1
                ctrl_Fp_Type_Str = getCtrlFpStr(hsdschpkt_ctrl.ctrlft) 
                
                if crccheck:
                    tmpbuf = buf[1:]
                    tmpbuf = b'\x01' + tmpbuf
                    crcdata = mkCrcData(hsdschpkt.frmcrc, generateCrc(tmpbuf, HDR_POLY))
                    if crcdata['crccheck'] == "ERR":
                        return -1
                writeData2Output(frameno, ts, addr, len(buf), ctrl_Fp_Type_Str, hsdschpkt_ctrl.data, crcdata)
            return 0 

        fptype = None
        # find out suitable type info

        # anyway, init with the smallest (ts, type) at first
        # so that if no ca before this data frm the first ca type used
        fptype = typeFPDict[addr][-1][0]

        if len(typeFPDict[addr]) > 1:
            # find out the nearest ca msg type before this packet
            # fttuple is (fptype, ts)
            for fttuple in typeFPDict[addr]:
                if ts > fttuple[1]:
                    fptype = fttuple[0]
                    break

        if fptype == hsdschctrl.HSDSCHCTRL_TYPE_CA_TYPE1:
            fptypestr = DF_TYPE1_STR
        else:
            fptypestr = DF_TYPE2_STR

        try:
            fpframe = FPHandler[fptype](buf)
        except pkt.NeedData:
            errstr = DF_TOT_LEN_ERR
            writeErrHsdschDataFrm2Output(frameno, ts, addr, fptypestr, buf.encode('hex'), errstr)
            return 0


        tmplen = fpframe.getHdrLen() + 2

        if tmplen >= len(buf):
            errstr = DF_PYL_LEN_ERR + ", hdr len %d, frm len %d" % (tmplen - 2, len(buf))
            writeErrHsdschDataFrm2Output(frameno, ts, addr, fptypestr, buf.encode('hex'), errstr)
            return 0

        if crccheck:
            # get rid of crc field
            hdrbuf = buf[1:fpframe.getHdrLen()]
            hdrbuf = b'\x00' + hdrbuf
            pybuf = buf[fpframe.getHdrLen():-2]
            calpycrc = generateCrc(pybuf, PYL_POLY)
            crcdata = mkCrcData(hsdschpkt.frmcrc, generateCrc(hdrbuf, HDR_POLY),\
                    fpframe.getPyloadCrc(), calpycrc)

        # update counter
        if fptype == hsdschctrl.HSDSCHCTRL_TYPE_CA_TYPE1:
            if fpframe.macdlen == 336:
                fptypestr = DF_TYPE1_STR_336
            elif fpframe.macdlen == 656:
                fptypestr = DF_TYPE1_STR_656
            else:
                errstr = DF_MACD_LEN_ERR + ", not 336 or 656, macdlen %d" % fpframe.macdlen
                writeErrHsdschDataFrm2Output(frameno, ts, addr, fptypestr, buf.encode('hex'), errstr)
                return 0

        writeData2Output(frameno, ts, addr, len(buf), fptypestr, fpframe, crcdata)

        return 0

inputfilename = ''
crccheck = False
caonly = False
# Main logic
def main():
    global counter
    global udpcounter

    parseOpt()

    f = getInputFile()

    fname = os.path.abspath(f.name)

    starttime = datetime.datetime.now()
    inputFileSize = os.stat(fname).st_size

    createOutputDir(fname)

    try:
        import subprocess
        from progressbar import ProgressBar, Percentage, Bar
        output = subprocess.check_output('capinfos -c %s' % (fname), shell=True)
        nrstr = output.split(':')[-1].strip(' \r\n')
        nr = int(nrstr)
        if caonly:
            maxval = nr
        else:
            maxval = 2*nr
        pbar = ProgressBar(widgets=[Percentage(), Bar()], maxval=maxval).start()
    except ImportError:
        pbar = None

    discard_frmno_list = []
    for i in range(2):
        # twice scan of input files from the beginning
        f.seek(0)


        if i == 1:
            # get no CA msg from 1st scan, just break
            if not typeFPDict:
                break

        frameno = 0
        for ts,pkt in dpkt.pcap.Reader(f):
            frameno += 1
            #print '{0}\r'.format(frameno),
            if pbar:
                pbar.update(frameno + i*nr)

            if i == 0:
                counter+=1
            else:
                if frameno in discard_frmno_list:
                    discard_frmno_list.remove(frameno)
                    continue

            # Parse packet
            eth = dpkt.ethernet.Ethernet(pkt)
            ip = eth.data


            if eth.type == dpkt.ethernet.ETH_TYPE_IP and ip.p == dpkt.ip.IP_PROTO_UDP:
                udp = ip.data

                if i == 0: udpcounter += 1

                sip = socket.inet_ntoa(ip.src)
                dip = socket.inet_ntoa(ip.dst)
                sport = str(udp.sport)
                dport = str(udp.dport)

                addr = ((sip, sport), (dip, dport))
                buf = udp.data

                # 2nd scan process all data frame and record them to csv
                if i == 1 and 0 == parseRnc2BtsHsdschPkt(frameno, buf, ts, addr):
                    continue

                # 1st scan find out all ca msgs and record their info
                # 2nd scan find out all ca msgs and record them to csv
                if -1 == parseBts2RncHsdschPkt(frameno, i, buf, ts, addr):
                    # it can't be CA or DF frame
                    discard_frmno_list.append(frameno)
        #print

    f.close()
    closeAllOutputFile()
    if writeErrHsdschDataFrm2Output.f:
        writeErrHsdschDataFrm2Output.f.close()

    for addr in outputfdict:
        tmpflag = outputfdict[addr][1]
        tmpfname = outputfdict[addr][0].name
        if tmpflag:
            fn =  os.path.splitext(tmpfname)[0] + newFileNameAppendix(tmpflag) + '.csv'
            if os.path.exists(fn):
                os.remove(fn)
            os.rename(tmpfname, fn)

    if not caonly:
        statFilePath = writeStat()
    else:
        for i in CAOnlyDecoder.fdict.values():
            i.close()

    sumstat = lambda fld, st=hsdsch_perconn_stat: sum(st[addr][fld] for addr in st)
    L = [ CA_TYPE1_STR_336, CA_TYPE1_STR_656, CA_TYPE2_STR, DF_TYPE1_STR_336,
            DF_TYPE1_STR_656, DF_TYPE2_STR ]
    cnt_dict = dict(zip(L, map(sumstat, L)))

    endtime = datetime.datetime.now()

    if pbar:
        pbar.finish()

    print "All Parse works are done!!"
    print "Input pcap file size %.2f MB" % (int(inputFileSize)/(1024 * 1024.0))
    print "Consumed %s\n" % (endtime - starttime)

    # Print packet totals
    print "Total number of packets in the pcap file :", counter
    print "Total number of UDP packets :", udpcounter
    print "Total number of HSDSCH CA type1 packets :", (cnt_dict[CA_TYPE1_STR_336]+cnt_dict[CA_TYPE1_STR_656])
    print "             ... CA type1 maxpdulen 336 :", cnt_dict[CA_TYPE1_STR_336]
    print "             ... CA type1 maxpdulen 656 :", cnt_dict[CA_TYPE1_STR_656]
    print "Total number of HSDSCH CA type2 packets :", cnt_dict[CA_TYPE2_STR]
    if not caonly:
        print "Total number of HSDSCH DF type1 packets :", (cnt_dict[DF_TYPE1_STR_336]+cnt_dict[DF_TYPE1_STR_656])
        print "Total number of HSDSCH DF type2 packets :", cnt_dict[DF_TYPE2_STR]
        print
        print "First detected HSDSCH DF time stamp: %.6f" % updatePerSecStat.first_df_ts
        print "Last detected HSDSCH DF time stamp: %.6f" % updatePerSecStat.last_df_ts
        duration = updatePerSecStat.last_df_ts - updatePerSecStat.first_df_ts
        print "Duration between first and last detected HSDSCH DF:", duration
        if duration:
            print "Avg HSDSCH DF raw data rate(bps) in whole pcap:", \
                    (sumstat(AVG_RAWDATA_RATE, hsdsch_persec_stat)/duration)
            print "Avg HSDSCH DF data rate(bps) in whole pcap:",\
                    (sumstat(AVG_DATA_RATE, hsdsch_persec_stat)/duration)
        print
        print "Detailed HSDSCH packets statistic can be found in", statFilePath
    print

if __name__ == '__main__':
    main()

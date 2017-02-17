#!/usr/bin/python

##
# @file: ul_node_sync.py
# @brief: Define DL Node Sync frame fields
#          Organized as (field name, bits)
# @author: Kaijie-daniel.yang@nsn.com
# @version: 1.0
# @data 2013-07-01

import pkt

class UL_NODE_SYNC(pkt.Packet):
	"""docstring for UL NODE SYNC.
	T1, extraced from correspondent DL Node Synchronisation control frame
	T2, NodeB specific frame number(BFN) indicate when BTS recieved DL SYNC
	T3, BFN when the frame is sent
	value range: {0..327679}
	Granularity: 0.125ms
	Field length: 24bits
	"""
	__fields__ = [
			('T1', 24),
			('T2', 24),
			('T3', 24)
			]

	def getT1Time(self):
		"""docstring for function getT1Time"""
		return self.T1*0.125

	def getT2Time(self):
		"""docstring for function getT2Time"""
		return self.T2*0.125

	def getT3Time(self):
		"""docstring for function getT3Time"""
		return self.T3*0.125

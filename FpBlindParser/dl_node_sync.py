#!/usr/bin/python

##
# @file: dl_node_sync.py
# @brief: Define DL Node Sync frame fields
#          Organized as (field name, bits)
# @author: Kaijie-daniel.yang@nsn.com
# @version: 1.0
# @data 2013-07-01

import pkt

class DL_NODE_SYNC(pkt.Packet):
	"""docstring for DL NODE SYNC.
	T1 value range: {0..327679}
	Granularity: 0.125ms
	Field length: 24bits
	"""
	__fields__ = [('T1', 24)]

	def getT1Time(self):
		"""docstring for function getT1Time"""
		return self.T1*0.125

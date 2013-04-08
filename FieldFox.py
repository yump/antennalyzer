#   Copyright 2012,2013 Russell Haley
#   (Please add yourself if you make changes)
#
#   This file is part of swr-recorder.
#
#   swr-recorder is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   swr-recorder is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with swr-recorder.  If not, see <http://www.gnu.org/licenses/>.

import telnetlib
from QAMRadio import QAMRadio
import numpy as np

class FieldFox(QAMRadio):

	"""A class to communicate with the Agilent FieldFox network analyzer."""

	def __init__(self, host, port=5025, numpoints=1001, lo=2.35e9, hi=2.55e9):
		self.numpoints = numpoints
		self.conn = telnetlib.Telnet(host, port)
		#self.scpi("*RST")                 # apparently this breaks calbration
		self.barrier()
		self.scpi("CALC:PAR1:DEF S11")     # measure S11
		self.scpi("CALC:SEL:FORM SWR")     # SWR
		self.scpi("INIT:CONT 1")           # continuous sweep for interactivity
		self.scpi("SENS:SWE:POIN {}".format(numpoints)) # number of points
		self.scpi("SENS:FREQ:STAR {}".format(lo))
		self.scpi("SENS:FREQ:STOP {}".format(hi))
		self.scpi(":BWID 10e3")             # 10kHz IF bandwidth
		self.sync()

	def __del__(self):
		self.conn.close()

	def sample(self, avg=3):
		"""
		Collect the SWR for a range of values.  Result is a 1 dimensional
		numpy array.

		Parameters
		----------
		avg : int
			Number of sweeps to average.
		"""
		accum = np.zeros(self.numpoints)
		self.scpi("INIT:CONT 0")           # single sweep mode
		self.barrier()
		for ix in range(avg):
			self.scpi("INIT")
			self.barrier()
			self.scpi("CALC:DATA:FDAT?")    # SWR sample
			answer =  self.conn.read_until(b'\n').decode('ascii')
			parsed = answer.strip().split(",")
			accum += [float(sym) for sym in parsed]
		self.scpi("INIT:CONT 1")           # back to continuous sweep
		return accum / avg

	def sync(self):        
		"""
		Wait for completion of pending commands.
		"""
		self.scpi("*OPC?")
		self.conn.read_until(b'\n')

	def barrier(self):
		"""
		Force previous commands to finish before subsequent commands..
		"""
		self.scpi("*WAI")

	def scpi(self, command):
		"""
		Send a string to the SCPI instrument.
		Handles encoding and termination.
		"""
		self.conn.write(command.encode('ascii') + b'\n')

	def command(self, command):
		"""
		Send an SCPI command and return the result. For human interactive use.
		"""
		self.scpi(command)
		return conn.read_until(b'\n').decode('ascii')


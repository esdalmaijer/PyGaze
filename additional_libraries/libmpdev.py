# -*- coding: utf-8 -*-
#
# This file is part of PyGaze - the open-source toolbox for eye tracking
#
#	PyGaze is a Python module for easily creating gaze contingent experiments
#	or other software (as well as non-gaze contingent experiments/software)
#	Copyright (C) 2012-2014 Edwin S. Dalmaijer
#	
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#	
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#	GNU General Public License for more details.
#	
#	You should have received a copy of the GNU General Public License
#	along with this program. If not, see <http://www.gnu.org/licenses/>

import os
import time
from ctypes import windll, c_int, c_double, byref
from threading import Thread, Lock


# load DLL
mpdev = windll.LoadLibrary('mpdev.dll')


# error handling
def check_returncode(returncode):

	"""
	desc:
		Checks a BioPac MP150 returncode, and returns it's meaning as a human readable string

	arguments:
		returncode:
			desc:	A code returned by one of the functions from the mpdev DLL
			type:	int

	returns:
		desc:	A string describing the error
		type:	str
	"""

	if returncode == 1:
		meaning = "MPSUCCESS"
	else:
		meaning = "UNKNOWN"

	return meaning


# class definition
class MP150:
	
	"""
	desc:
		Class to communicate with BioPax MP150 Squeezies.
	"""
	
	def __init__(self, logfile='default', samplerate=5.0):
		
		"""
		desc:
			Finds an MP150, and initializes a connection.
		
		keywords:
			logfile:
				desc:Name of the logfile (optionally with path), which will
					be used to create a textfile, e.g.
					'default_MP150_data.tsv' (default = 'default')
				type:str
			samplerate:
				desc:The amount of time (milliseconds) between samples
					(default = 5.0).
				type:float
		"""
		
		# settings
		self._sampletime = float(samplerate)
		self._sampletimesec = self._sampletime / 1000.0
		self._samplerate = 1000.0 / self._sampletime
		self._logfilename = "%s_MP150_data.tsv" % (logfile)

		# connect to the MP150
		# (101 is the code for the MP150, 103 for the MP36R)
		try:
			result = mpdev.connectMPDev(c_int(101), c_int(11), b'auto')
		except:
			result = "failed to call connectMPDev"
		if check_returncode(result) != "MPSUCCESS":
			raise Exception("Error in libmp150: failed to connect to the MP150: %s" % result)
		
		# get starting time
		self._starting_time = time.time()
		
		# set sampling rate
		try:
			result = mpdev.setSampleRate(c_double(self._sampletime))
		except:
			result = "failed to call setSampleRate"
		if check_returncode(result) != "MPSUCCESS":
			raise Exception("Error in libmp150: failed to set samplerate: %s" % result)
		
		# set Channels to acquire
		try:
			channels = [1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
			channels = (c_int * len(channels))(*channels)
			result = mpdev.setAcqChannels(byref(channels))
		except:
			result = "failed to call setAcqChannels"
		if check_returncode(result) != "MPSUCCESS":
			raise Exception("Error in libmp150: failed to set channels to acquire: %s" % result)
		
#		# start acquisition daemon (NOT for getMPBuffer and getMostRecentSample!)
#		try:
#			result = mpdev.startMPAcqDaemon()
#		except:
#			result = "failed to call startMPAcqDaemon"
#		if check_returncode(result) != "MPSUCCESS":
#			raise Exception("Error in libmp150: failed to start acquisition daemon: %s" % result)
		
		# start acquisition
		try:
			result = mpdev.startAcquisition()
		except:
			result = "failed to call startAcquisition"
		if check_returncode(result) != "MPSUCCESS":
			raise Exception("Error in libmp150: failed to start acquisition: %s" % result)
		
		# open log file
		self._logfile = open(self._logfilename, 'w')
		# write header
		header = "\t".join(["timestamp","channel_1","channel_2","channel_3"])
		self._logfile.write(header + "\n")
		
		# create logging lock
		self._loglock = Lock()
		
		# start sample processing Thread
		self._recording = False
		self._connected = True
		self._spthread = Thread(target=self._sampleprocesser)
		self._spthread.daemon = True
		self._spthread.name = "sampleprocesser"
		self._spthread.start()
	
	
	def start_recording(self):
		
		"""
		desc:
			Starts writing MP150 samples to the log file
		"""
		
		self._recording = True
	
	
	def stop_recording(self):
		
		"""
		desc:
			Stops writing MP150 samples to the log file
		"""
		
		self._recording = False
	
	
	def sample(self):
		
		"""
		desc:
			Returns the most recent sample provided by the MP150
		
		returns:
			desc:The latest MP150 output values for three channels
				(as a list of floats)
			type:list
		"""
		
		# get data
		try:
			#data = [0.0,0.0,0.0]
			#result, data = mpdev.getMPBuffer(1, data) # 1 for one sample
			data = [0.0, 0.0, 0.0]
			data = (c_double * len(data))(*data)
			result = mpdev.getMostRecentSample(byref(data))
		except:
			result = "failed to call getMPBuffer"
		if check_returncode(result) != "MPSUCCESS":
			raise Exception("Error in libmp150: failed to obtain a sample from the MP150: %s" % result)
		
		return (data[0], data[1], data[2])

	
	def log(self, msg):
		
		"""
		desc:
			Writes a message to the log file.
		
		arguments:
			msg:
				desc:The message that is to be written to the log file.
				type:str
		"""
		
		# wait for the logging lock to be released, then lock it
		self._loglock.acquire(True)
		
		# write log message, including timestamp
		self._logfile.write("MSG\t%d\t%s\n" % (self.get_timestamp(), msg))
		
		# release the logging lock
		self._loglock.release()

	
	def close(self):
		
		"""
		desc:
			Closes the connection to the MP150.
		"""
		
		# stop recording
		if self._recording:
			self.stop_recording()
		# close log file
		self._logfile.close()
		# stop sample processing thread
		self._connected = False
		
		# close connection
		try:
			result = mpdev.disconnectMPDev()
		except:
			result = "failed to call disconnectMPDev"
		if check_returncode(result) != "MPSUCCESS":
			raise Exception("Error in libmp150: failed to close the connection to the MP150: %s" % result)

	
	def get_timestamp(self):
		
		"""
		desc:
			Returns the time in milliseconds since the connection was opened
		
		returns:
			desc:Time (milliseconds) since connection was opened
			type:int
		"""
		
		return int((time.time()-self._starting_time) * 1000)
	
	
	def _sampleprocesser(self):
		
		"""
		desc:
			Processes samples while self._recording is True (INTERNAL USE!)
		"""
		
		# run until the connection is closed
		while self._connected:
			# get new sample
			ch1, ch2, ch3 = self.sample()
			# write sample to file
			if self._recording:
				# wait for the logging lock to be released, then lock it
				self._loglock.acquire(True)
				# log data
				self._logfile.write("%d\t%.3f\t%.3f\t%.3f\n" % (self.get_timestamp(), ch1, ch2, ch3))
				self._logfile.flush() # internal buffer to RAM
				os.fsync(self._logfile.fileno()) # RAM file cache to disk
				# release the logging lock
				self._loglock.release()
			# pause until the next sample is available
			time.sleep(self._sampletimesec)

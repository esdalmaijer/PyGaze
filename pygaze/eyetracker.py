## This file is part of PyGaze - the open-source toolbox for eye tracking
##
##	PyGaze is a Python module for easily creating gaze contingent experiments
##	or other software (as well as non-gaze contingent experiments/software)
##	Copyright (C) 2012-2013  Edwin S. Dalmaijer
##
##	This program is free software: you can redistribute it and/or modify
##	it under the terms of the GNU General Public License as published by
##	the Free Software Foundation, either version 3 of the License, or
##	(at your option) any later version.
##
##	This program is distributed in the hope that it will be useful,
##	but WITHOUT ANY WARRANTY; without even the implied warranty of
##	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##	GNU General Public License for more details.
##
##	You should have received a copy of the GNU General Public License
##	along with this program.  If not, see <http://www.gnu.org/licenses/>
#
# version: 0.4 (25-03-2013)
#
#
# Many thanks to Sebastiaan Mathot. libeyelink is a slightly modified version of
# libeyelink.py, part of the eyelink plugins for the OpenSesame experiment builder
# (see: www.cogsci.nl/opensesame).
# OpenSesame is free software, redistributable under the terms of the GNU Public
# License as published by the Free Software Foundation.

from defaults import *
try:
	from constants import *
except:
	pass


class EyeTracker:

	"""EyeTracker class, which morphes into either an Eyelink, SMItracker or DummyTracker object"""

	def __init__(self, display, trackertype=TRACKERTYPE, resolution=DISPSIZE, eyedatafile=LOGFILENAME, logfile=LOGFILE, fgc=FGC, bgc=BGC, saccvelthresh=SACCVELTHRESH, saccaccthresh=SACCACCTHRESH, ip=SMIIP, sendport=SMISENDPORT, receiveport=SMIRECEIVEPORT):

		"""Initializes an EyeTracker object"""

		# set trackertype to dummy in dummymode
		if DUMMYMODE:
			trackertype = 'dummy'
	
		# correct wrong input
		if trackertype not in ['eyelink','smi','tobii','dummy']:
			trackertype = 'dummy'
			raise Exception("Error in eyetracker.EyeTracker: trackertype not recognized; it should be one of 'eyelink', 'smi', 'tobii', 'dummy'")

		# EyeLink
		if trackertype == 'eyelink':
			# import libraries
			from libeyelink import libeyelink
			# morph class
			self.__class__ = libeyelink
			# initialize
			self.__class__.__init__(self, display, resolution=resolution, data_file=eyedatafile+".edf", fg_color=fgc, bg_color=bgc, eventdetection=EVENTDETECTION, saccade_velocity_threshold=saccvelthresh, saccade_acceleration_threshold=saccaccthresh)
			
		# SMI
		elif trackertype == 'smi':
			# import libraries
			from libsmi import SMItracker
			# morph class
			self.__class__ = SMItracker
			# initialize
			self.__class__.__init__(self, display, ip=ip, sendport=sendport, receiveport=receiveport, logfile=logfile, eventdetection=EVENTDETECTION, saccade_velocity_threshold=saccvelthresh, saccade_acceleration_threshold=saccaccthresh)

		# Tobii
		elif trackertype == 'tobii':
			# import libraries
			from libtobii import TobiiTracker
			# morph class
			self.__class__ = TobiiTracker
			# initialize
			self.__class__.__init__(self, display, logfile=logfile, eventdetection=EVENTDETECTION, saccade_velocity_threshold=saccvelthresh, saccade_acceleration_threshold=saccaccthresh)

		# dummy mode
		elif trackertype == 'dummy':
			# import libraries
			from libdummytracker import Dummy
			# morph class
			self.__class__ = Dummy
			# initialize
			self.__class__.__init__(self, display)

		else:
			raise Exception("Error in eyetracker.EyeTracker.__init__: trackertype not recognized, this should not happen!")

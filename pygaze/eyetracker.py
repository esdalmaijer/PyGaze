# -*- coding: utf-8 -*-
#
# This file is part of PyGaze - the open-source toolbox for eye tracking
#
#	PyGaze is a Python module for easily creating gaze contingent experiments
#	or other software (as well as non-gaze contingent experiments/software)
#	Copyright (C) 2012-2013  Edwin S. Dalmaijer
#
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with this program.  If not, see <http://www.gnu.org/licenses/>

from pygaze.defaults import *
try:
	from constants import *
except:
	pass

class EyeTracker:

	"""
	Generic EyeTracker class, which morphs into an eye-tracker specific class.
	"""

	def __init__(self, display, trackertype=TRACKERTYPE, **args):

		"""
		Initializes an EyeTracker object.
		
		Arguments:
		display			--	A pygaze.screen.Display object.
		trackertype		--	The type of eye tracker.
		
		Keyword arguments:
		**args			--	A keyword-argument dictionary that contains
							eye-tracker-specific options.
		"""

		# set trackertype to dummy in dummymode
		if DUMMYMODE:
			trackertype = u'dummy'
	
		# correct wrong input
		if trackertype not in [u'eyelink', u'smi', u'tobii', u'dummy']:
			raise Exception( \
				u"Error in eyetracker.EyeTracker: trackertype not recognized; it should be one of 'eyelink', 'smi', 'tobii', 'dummy'")

		# EyeLink
		if trackertype == u'eyelink':
			# import libraries
			from pygaze._eyetracker.libeyelink import libeyelink
			# morph class
			self.__class__ = libeyelink
			# initialize
			self.__class__.__init__(self, display, **args)
			
		# SMI
		elif trackertype == u'smi':
			# import libraries
			from pygaze._eyetracker.libsmi import SMItracker
			# morph class
			self.__class__ = SMItracker
			# initialize
			self.__class__.__init__(self, display, **args)

		# Tobii
		elif trackertype == u'tobii':
			# import libraries
			from pygaze._eyetracker.libtobii import TobiiTracker
			# morph class
			self.__class__ = TobiiTracker
			# initialize
			self.__class__.__init__(self, display, **args)

		# dummy mode
		elif trackertype == u'dummy':
			# import libraries
			from pygaze._eyetracker.libdummytracker import Dummy
			# morph class
			self.__class__ = Dummy
			# initialize
			self.__class__.__init__(self, display)

		else:
			raise Exception( \
				u"Error in eyetracker.EyeTracker.__init__: trackertype not recognized, this should not happen!")

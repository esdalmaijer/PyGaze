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

import pygame
import time
import sys

class PyGameTime:
	
	"""Class for keeping track of the current time"""
	
	def __init__(self):
		
		"""Initializes the Time object
		
		arguments
		None
		
		keyword arguments
		None
		"""
		
		# On Windows, `time.clock()` provides higher accuracy than
		# `time.time()`.
		if sys.platform == 'win32':
			self._cpu_time = time.clock
		else:
			self._cpu_time = time.time

		pygame.init()



	def expstart(self):

		"""Time is set to 0 when calling this
		
		arguments
		None

		returns
		Nothing
		"""

		global expbegintime
		
		expbegintime = self._cpu_time() * 1000


	def get_time(self):

		"""Returns current time in milliseconds
		
		arguments
		None
		
		returns
		time		-- current time in milliseconds, as measured since
					expbegintime
		"""

		ctime = self._cpu_time()*1000 - expbegintime

		return ctime


	def pause(self, pausetime):

		"""Pauses the experiment for given number of milliseconds
		
		arguments
		pausetime	-- time to pause in milliseconds
		
		returns
		pausetime	-- actual time the system paused (in milliseconds)
		"""

		realpause = pygame.time.delay(pausetime)

		return realpause


	def expend(self):

		"""Completely ends the experiment (only call this at the end!)
		
		arguments
		None
		
		returns
		endtime	-- ending time of the experiment (in milliseconds since
					expbegintime
		"""

		endtime = self.get_time()

		pygame.quit()

		return endtime
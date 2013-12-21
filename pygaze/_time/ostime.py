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

from pygaze.defaults import osexperiment
try:
	from constants import osexperiment
except:
	pass

class OSTime:
	
	"""Class for keeping track of the current time"""
	
	def __init__(self):
		
		"""Initializes the Time object
		
		arguments
		None
		
		keyword arguments
		None
		"""
		
		pass


	def expstart(self):
		
		"""See _time.pygametime"""

		global expbegintime
		
		expbegintime = 0


	def get_time(self):

		"""See _time.pygametime"""

		return osexperiment.time()


	def pause(self, pausetime):

		"""See _time.pygametime"""

		return osexperiment.sleep(pausetime)


	def expend(self):

		"""See _time.pygametime"""

		return osexperiment.time()
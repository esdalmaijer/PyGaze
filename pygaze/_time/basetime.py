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

# The BaseClasses are meant to store the documentation on all methods of a
# class, but not to contain any functionality whatsoever. BaseClass is
# inherited by all of the subclasses, and the documentation is copied using
# pygaze.copy_docstr. If you intend to make your own subclass for the current
# baseclass, be sure to inherit BaseClass, copy the documentation, and
# redefine the methods as you see fit, e.g.:
#
#import pygaze
#from pygaze._display.basedisplay import BaseDisplay
#
#class DummyDisplay(BaseDisplay):
#	
#	"""An example child of BaseDisplay"""
#	
#	def __init__(self, *args, **kwargs):
#		
#		"""Initializes a DummyDisplay instance"""
#		
#		pygaze.copy_docstring(BaseDisplay,DummyDisplay)
#	
#	def show(self):
#		
#		# note that here no docstring is provided, as it is copied from
#		# the parent class
#		
#		print("Display.show call at %d" % int(pygaze.clock.get_time()))
#


class BaseTime:
	
	"""Class for keeping track of time"""
	
	def __init__(self):
		
		"""
		Initializes a Time instance
		
		arguments

		None
		
		keyword arguments

		None
		"""
		
		pass


	def expstart(self):

		"""
		Time is set to 0 when calling this
		
		arguments

		None
		
		keyword arguments
		
		None

		returns

		Nothing
		"""

		pass


	def get_time(self):

		"""
		Returns current time in milliseconds
		
		arguments
		
		None
		
		keyword arguments
		
		None
		
		returns
		
		time		--	current time in milliseconds, as measured since
					expbegintime
		"""

		pass


	def pause(self):

		"""
		Pauses the experiment for given number of milliseconds
		
		arguments

		pausetime	--	time to pause in milliseconds
		
		keyword arguments
		
		None
		
		returns
		
		pausetime	--	actual time the system paused (in milliseconds)
		"""

		pass


	def expend(self):

		"""
		Completely ends the experiment (only call this at the end!)
		
		arguments

		None
		
		keyword arguments
		
		None
		
		returns

		endtime	--	ending time of the experiment (in milliseconds since
					expbegintime
		"""

		pass
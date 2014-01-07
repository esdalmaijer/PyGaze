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
#		print("Display.show call at %d" % int(clock.get_time()))
#


class BaseKeyboard:

	"""A keyboard for collecting responses"""

	def __init__(self):

		"""
		Initializes the Keyboard object
		
		arguments

		None
		
		keyword arguments

		keylist	--	list of keys that are allowed, e.g. ['1','a','enter']
					for the 1, A and Enter keys (default =
					KEYLIST)
		timeout	--	time in milliseconds after which None is returned
					on a call to the get_key method when no keypress is
					registered (default = KEYTIMEOUT)
		"""

		pass

	
	def set_keylist(self):

		"""
		Set a list of accepted keys
		
		arguments

		None
		
		keyword arguments

		keylist	--	list of keys that are allowed (e.g.
					['1','a','enter']) or None to allow all keys
					(default = None)
		
		returns

		None		--	sets klist property
		"""
		
		pass


	def set_timeout(self):

		"""
		Set a timeout (in milliseconds)
		
		arguments

		None
		
		keyword arguments

		timeout	--	time in milliseconds after which None is returned
					on a call to get_key method when no keypress is
					registered (default = None)
		
		returns
		
		None	--	sets timeout property
		"""

		pass


	def get_key(self):

		"""
		Wait for keyboard input
		
		arguments

		None
		
		keyword arguments

		keylist	--	list of keys that are allowed (e.g.
					['1','a','enter']), None to allow all keys or
					'default' to use klist property (default = 'default')
		timeout	--	time in milliseconds after which None is returned
					when no keypress is registered (default = None);
					None for no timeout or 'default' to use the timeout
					property (default = 'default')
		flush		--	Boolean indicating if all input from before
					calling get_key should be ignored, if set to
					False keypresses from before calling this
					function will be registered, otherwise every
					keyboard input from before calling this function
					will be flushed (default = False)
		
		returns

		key, presstime	--	key is a string, indicating which button has
						been pressed or None when no key has been
						pressed
						presstime is the time (measured from
						expbegintime) a keypress or a timeout occured
		"""
		
		pass

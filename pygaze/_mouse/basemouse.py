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


class BaseMouse:

	"""A mouse for collecting responses"""

	def __init__(self):

		"""
		Initializes mouse object
		
		arguments

		None
		
		keyword arguments

		mousebuttonlist	--	list of mouse buttons that are allowed (e.g.
						[1,3] for left and right button) or None to
						allow all buttons (default =
						MOUSEBUTTONLIST)
		timeout	--		time in milliseconds after which None is returned
						on a call to get_clicked method when no click is
						registered (default = MOUSETIMEOUT)
		visible	--		Boolean indicating if mouse should be visible or not
						(default = False)
		"""

		pass


	def set_mousebuttonlist(self):

		"""
		Set a list of accepted mouse buttons
		
		arguments
		
		None
		
		keyword arguments

		mousebuttonlist	--	list of mouse buttons that are allowed (e.g.
						[1,3] for left and right button) or None to
						allow all buttons (default = None)
		
		returns
		
		None		--	 sets mbuttonlist property
		"""
		
		pass


	def set_timeout(self):

		"""
		Set a timeout (in milliseconds)
		
		arguments

		None
		
		keyword arguments
		
		timeout	--	time in milliseconds after which None is returned
					on a call to get_clicked method when no click is
					registered (default = None)
		
		returns
		None		--	sets timeout property
		"""

		pass


	def set_visible(self):

		"""
		Sets the visibility of the cursor
		
		arguments
		
		None
		
		keyword arguments

		visible	--	Boolean indicating if mouse should be visible or not
					(default = False)
		
		returns
		
		None		--	sets visible property
		"""

		pass


	def set_pos(self):

		"""
		Set the mouse position
		
		arguments
		
		None
		
		keyword arguments

		pos		--	an (x,y) position tuple, assuming top left is (0,0)
					(default = (0,0))
		
		returns
		
		None		--	sets the mouse position
		"""

		pass


	def get_pos(self):

		"""
		Returns mouse position
		
		arguments

		None
		
		keyword arguments
		
		None
		
		returns
		
		mpos		--	a (x,y) position tuple, assuming top left is (0,0)
		"""

		pass


	def get_clicked(self):

		"""
		Waits for mouse clicks
		
		arguments
		
		None
		
		keyword arguments

		mousebuttonlist	--	list of mouse buttons that are allowed (e.g.
						[1,3] for left and right button); None to
						allow all buttons or 'default' to use the
						mbuttonlist property (default = 'default')
		timeout	--	time in milliseconds after which None is returned
					when no click is registered; None for no timeout or
					'default' to use the timeout property (default =
					'default')
		
		returns
		
		mousebutton, clickpos, clicktime	--	mousebutton is an integer,
									indicating which button has
									been pressed or None when no
									button has been pressed;
									clickpos is an (x,y) position
									tuple or None when no click
									was registered;
									clicktime is the time
									(measured from expbegintime) a
									buttonpress or a timeout
									occured
		"""

		pass


	def get_pressed(self):

		"""
		Returns the current state of the mouse buttons
		
		arguments
		
		None
		
		keyword arguments
		
		None
		
		returns

		statelist	--	a list of Booleans indicating which mousebutton is
					down (e.g. [1,0,0] when only button 1 is pressed on
					a three-button-mouse)
		"""

		pass
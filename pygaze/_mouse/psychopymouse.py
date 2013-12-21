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
	
import pygaze
from pygaze.screen import pos2psychopos, psychopos2pos

import psychopy.event

class PsychoPyMouse:

	"""A mouse for collecting responses"""

	def __init__(self, mousebuttonlist=MOUSEBUTTONLIST, timeout=MOUSETIMEOUT, visible=False):

		"""Initializes mouse object
		
		arguments
		None
		
		keyword arguments
		disptype	-- display type, either 'psychopy' or 'pygame' (default
				   = DISPTYPE)
		mousebuttonlist	-- list of mouse buttons that are allowed (e.g.
					   [1,3] for left and right button) or None to
					   allow all buttons (default =
					   MOUSEBUTTONLIST)
		timeout	-- time in milliseconds after which None is returned
				   on a call to get_clicked method when no click is
				   registered (default = MOUSETIMEOUT)
		visible	-- Boolean indicating if mouse should be visible or not
				   (default = False)
		"""

		# create mouse object
		self.mouse = psychopy.event.Mouse(visible=False,win=psychopy.visual.openWindows[SCREENNR])
		
		# set mouse characteristics
		self.set_mousebuttonlist(mousebuttonlist)
		self.set_timeout(timeout)
		self.set_visible(visible=visible)


	def set_mousebuttonlist(self, mousebuttonlist=None):

		"""Set a list of accepted mouse buttons
		
		arguments
		None
		
		keyword arguments
		mousebuttonlist	-- list of mouse buttons that are allowed (e.g.
					   [1,3] for left and right button) or None to
					   allow all buttons (default = None)
		
		returns
		Nothing	-- sets mbuttonlist property
		"""
		
		if mousebuttonlist == None or mousebuttonlist == []:
			self.mbuttonlist = None
		else:
			self.mbuttonlist = []
			for mbutton in mousebuttonlist:
				self.mbuttonlist.append(mbutton)


	def set_timeout(self, timeout=None):

		"""Set a timeout (in milliseconds)
		
		arguments
		None
		
		keyword arguments
		timeout	-- time in milliseconds after which None is returned
				   on a call to get_clicked method when no click is
				   registered (default = None)
		
		returns
		Nothing	-- sets timeout property
		"""

		self.timeout = timeout


	def set_visible(self, visible=True):

		"""Sets the visibility of the cursor
		
		arguments
		None
		
		keyword arguments
		visible	-- Boolean indicating if mouse should be visible or not
				   (default = False)
		
		returns
		Nothing	-- sets visible property
		"""

		self.visible = visible
		self.mouse.setVisible(self.visible)


	def set_pos(self, pos=(0,0)):

		"""Set the mouse position
		
		arguments
		None
		
		keyword arguments
		pos		-- an (x,y) position tuple, assuming top left is (0,0)
				   (default = (0,0))
		
		returns
		Nothing	-- sets the mouse position
		"""

		self.mouse.setPos(newPos=pos2psychopos(pos))


	def get_pos(self):

		"""Returns mouse position
		
		arguments
		None
		
		returns
		mpos		-- an (x,y) position tuple, assuming top left is (0,0)
		"""

		return psychopos2pos(self.mouse.getPos())


	def get_clicked(self, mousebuttonlist='default', timeout='default'):

		"""Waits for mouse clicks
		
		arguments
		None
		
		keyword arguments
		mousebuttonlist	-- list of mouse buttons that are allowed (e.g.
					   [1,3] for left and right button); None to
					   allow all buttons or 'default' to use the
					   mbuttonlist property (default = 'default')
		timeout	-- time in milliseconds after which None is returned
				   when no click is registered; None for no timeout or
				   'default' to use the timeout property (default =
				   'default')
		
		returns
		mousebutton, clickpos, clicktime	-- mousebutton is an integer,
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

		# set buttonlist and timeout
		if mousebuttonlist == 'default':
			mousebuttonlist = self.mbuttonlist
		if timeout == 'default':
			timeout = self.timeout
		# starttime
		starttime = pygaze.clock.get_time()
		time = pygaze.clock.get_time()
		# wait for mouse clicks
		while timeout == None or time - starttime <= timeout:
			time = pygaze.clock.get_time()
			pressed = self.mouse.getPressed()
			if sum(pressed) > 0:
				for b in range(0,len(pressed)):
					if pressed[b] == 1:
						if mousebuttonlist == None or b+1 in mousebuttonlist:
							return b+1, self.get_pos(), time
		# in case of timeout
		return None, None, time


	def get_pressed(self):

		"""Returns the current state of the mouse buttons
		
		arguments
		None
		
		returns
		statelist	-- a list of Booleans indicating which mousebutton is
				   down (e.g. [1,0,0] when only button 1 is pressed on
				   a three-button-mouse)
		"""

		return self.mouse.getPressed()


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
from pygaze import libtime
from pygaze._screen.psychopyscreen import rgb2psychorgb

import copy
import math
import os.path

import psychopy
from psychopy.visual import Window, GratingStim, Circle, Line, ShapeStim, \
	TextStim, ImageStim

class PsychoPyDisplay:

	"""A class for Display objects, to present Screen objects on a monitor"""

	def __init__(self, dispsize=DISPSIZE, fgc=FGC, bgc=BGC, screennr=SCREENNR, \
		screen=None, **args):

		"""Initializes the Display object
		
		arguments
		None

		keyword arguments
		disptype	-- type of display: either 'pygame' or 'psychopy'
				   (default = DISPTYPE)
		dispsize	-- size of the display in pixels: a (width, height)
				   tuple (default = DISPSIZE)
		fgc		-- the foreground colour: a colour name (e.g. 'red') or 
				   a RGB(A) tuple (e.g. (255,0,0) or (255,0,0,255))
				   (default = FGC)
		bgc		-- the background colour: a colour name (e.g. 'red') or 
				   a RGB(A) tuple (e.g. (255,0,0) or (255,0,0,255))
				   (default = BGC)
		screennr	-- the screen number: 0, 1 etc. (default = SCREENNR)
		screen	-- a Screen object to be presented on the new Display
				   (default=None)
		"""

		self.dispsize = dispsize
		self.fgc = fgc
		self.bgc = bgc
		self.screennr = screennr
		self.mousevis = False

		# create window
		pygaze.expdisplay = Window(size=self.dispsize, pos=None, color= \
			rgb2psychorgb(self.bgc), colorSpace='rgb', fullscr=True, screen= \
			self.screennr, units='pix')
		# set mouse visibility
		pygaze.expdisplay.setMouseVisible(self.mousevis)
		# get screen in window
		if screen:
			for s in screen.screen:
				s.draw()

	def show(self):

		"""Updates ('flips') the display
		
		arguments
		None
		
		returns
		time		-- the exact refresh time when disptype is PsychoPy, an
				   estimate when disptype is PyGame
		"""

		pygaze.expdisplay.flip()
		return libtime.get_time()

	def show_part(self, rect, screen=None):

		"""Updates part(s) of the screen to given specified screen (only
		works when disptype is PyGame; when this is set to PsychoPy
		the entire display is updated)
		
		arguments
		rect		-- a single or a list of rects; a rect is a (x,y,w,h)
				   tuple or list
		
		keyword arguments
		screen	-- the screen of which the specified rects should be
				   updated to the display (default = None)
		
		returns
		time		-- the exact refresh time when disptype is PsychoPy, an
				   estimate when disptype is PyGame
		"""
		if screen:
			for s in screen.screen:
				s.draw()
		self.show()
		print("WARNING! libscreen.Display.show_part not available for PsychoPy display type; show is used instead")
		
		return libtime.get_time()


	def fill(self, screen=None):

		"""Fills the screen with the background colour or specified screen,
		NOT updating it (call Display.show() to actually show the new
		display contents)
		
		arguments
		None
		
		keyword arguments
		screen	-- the screen that should be drawn to the display or
				   None to fill the display with its background colour
		"""

		pygaze.expdisplay.clearBuffer()
		if screen != None:
			for s in screen.screen:
				s.draw()

	def close(self):

		"""Closes the display
		
		arguments
		None
		
		returns
		Nothing"""

		pygaze.expdisplay.close()


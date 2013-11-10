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

import copy
import math
import os.path

import pygame
import pygame.display
import pygame.draw
import pygame.image

class PyGameDisplay:

	"""A class for Display objects, to present Screen objects on a monitor"""

	def __init__(self, dispsize=DISPSIZE, fgc=FGC, bgc=BGC, screen=None, **args):

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

		# initialize PyGame display-module
		pygame.display.init()
		# make mouse invisible (should be so per default, but you never know)
		pygame.mouse.set_visible(self.mousevis)
		# create surface for full screen displaying
		pygaze.expdisplay = pygame.display.set_mode(self.dispsize, \
			pygame.FULLSCREEN|pygame.HWSURFACE|pygame.DOUBLEBUF)

		# blit screen to display surface (if user entered one)
		if screen:
			pygaze.expdisplay.blit(screen.screen,(0,0))
		else:
			pygaze.expdisplay.fill(self.bgc)

	def show(self):

		"""Updates ('flips') the display
		
		arguments
		None
		
		returns
		time		-- the exact refresh time when disptype is PsychoPy, an
				   estimate when disptype is PyGame
		"""

		pygame.display.flip()
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

		if len(rect) > 1:
			for r in rect:
				pygaze.expdisplay.set_clip(r)
				if screen:
					pygaze.expdisplay.blit(screen.screen, (0,0))
				pygame.display.update(r)
				pygaze.expdisplay.set_clip(None)
				
		elif len(rect) == 1:
			pygaze.expdisplay.clip(rect)
			if screen:
				pygaze.expdisplay.blit(screen.screen, (0,0))
			pygame.display.update(rect)
			pygaze.expdisplay.set_clip(None)

		else:
			raise Exception("Error in libscreen.Display.show_part: rect should be a single rect (i.e. a (x,y,w,h) tuple) or a list of rects!")
		
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

		pygaze.expdisplay.fill(self.bgc)
		if screen != None:
			pygaze.expdisplay.blit(screen.screen,(0,0))

	def close(self):

		"""Closes the display
		
		arguments
		None
		
		returns
		Nothing"""

		pygame.display.quit()

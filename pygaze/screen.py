
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

from pygaze import defaults
from pygaze.defaults import *
try:
	from constants import *
except:
	pass

class Screen:

	"""
	A class for Screen objects, for visual stimuli (to be displayed via a
	Display object)
	"""

	def __init__(self, disptype=DISPTYPE, **args):

		"""
		Initializes the Screen object.
		
		Keyword arguments:
		disptype	--	Type of display: either 'pygame' or 'psychopy'
					(default = DISPTYPE)
		dispsize	-- size of the display in pixels: a (width, height)
				   tuple (default = DISPSIZE)
		fgc		-- the foreground colour: a colour name (e.g. 'red') or 
				   a RGB(A) tuple (e.g. (255,0,0) or (255,0,0,255))
				   (default = FGC)
		bgc		-- the background colour: a colour name (e.g. 'red') or 
				   a RGB(A) tuple (e.g. (255,0,0) or (255,0,0,255))
				   (default = BGC)
		screennr	-- the screen number: 0, 1 etc. (default =
				   SCREENNR)
		mousevisible	-- Boolean indicating mouse visibility (default = 
					   MOUSEVISIBLE)
		screen	-- a Screen object to be presented on the new Display
				   (default=None)
		"""

		if disptype == u'pygame':
			from pygaze._screen.pygamescreen import PyGameScreen as Screen
		elif disptype == u'psychopy':
			from pygaze._screen.psychopyscreen import PsychoPyScreen as Screen
		elif disptype == u'opensesame':
			from pygaze._screen.osscreen import OSScreen as Screen
		else:
			raise Exception(u'Unexpected disptype : %s' % disptype)
		self.__class__ = Screen
		self.__class__.__init__(self, **args)

		
# # # # #
# helper functions

def pos2psychopos(pos, dispsize=None):

	"""Returns a converted position tuple (x,y) (internal use)
	
	arguments
	pos		-- a (x,y) position tuple, assuming (0,0) is top left
	
	keyword arguments
	dispsize	-- a (width, height) tuple for the display resolution or None
			   for autodetecting the size of current active window
			   (default = None)
	
	returns
	pos		-- a (x,y) tuple that makes sense to PsychoPy (i.e. (0,0) is
			   display center; bottom left is (-,-) and top right is
			   (+,+))
	"""

	if dispsize == None:
		dispsize = DISPSIZE[:]

	x = pos[0] - dispsize[0]/2
	y = (pos[1] - dispsize[1]/2) * -1

	return (x,y)


def psychopos2pos(pos, dispsize=None):

	"""Returns a converted position tuple (x,y) (internal use)
	
	arguments
	pos		-- a (x,y) tuple that makes sense to PsychoPy (i.e. (0,0) is
			   display center; bottom left is (-,-) and top right is
			   (+,+))
	
	keyword arguments
	dispsize	-- a (width, height) tuple for the display resolution or None
			   for autodetecting the size of current active window
			   (default = None)
	
	returns
	pos		-- a (x,y) position tuple, assuming (0,0) is top left
	"""

	if dispsize == None:
		dispsize = DISPSIZE[:]

	x = pos[0] + dispsize[0]/2
	y = (pos[1] * -1) + dispsize[1]/2

	return (x,y)


def rgb2psychorgb(rgbgun):

	"""Returns a converted RGB gun
	
	arguments
	rgbgun	-- a (R,G,B) or (R,G,B,A) tuple containing values between 0
			   and 255; other values (e.g. 'red' or hex values) may be
			   passed as well, but will be returned as they were
	returns
	psyrgb	-- a (R,G,B) tuple containing values between -1 and 1; or
			   rgbgun when passed rgbgun was not a tuple or a list
	"""
	
	if type(rgbgun) not in [tuple,list]:
		return rgbgun

	psyrgb = []

	for val in rgbgun:
		psyrgb.append((val/127.5)-1)
	
	# return (R,G,B), since PsychoPy does not like alpha channels anymore
	
	return tuple(psyrgb[0:3])

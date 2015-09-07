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

from inspect import ismethod
from pygaze import settings

# # # # #
# helper functions

def copy_docstr(src, target):

	"""
	Copies docstrings from the methods of a source class to the methods of a
	target class.
	
	arguments:
	src		--	source class (e.g. BaseDisplay)
	target	--	target class (e.g. PyGameDisplay)
	"""
	
	for attr_name in dir(target):
		if not hasattr(src, attr_name) or not ismethod(getattr(src, attr_name)):
			continue
		getattr(target, attr_name).__func__.__doc__ = getattr(src, attr_name).__func__.__doc__


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
		dispsize = settings.DISPSIZE[:]

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
		dispsize = settings.DISPSIZE[:]

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

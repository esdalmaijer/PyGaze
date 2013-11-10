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
			from pygaze._screen.pygamescreen import PyGameScreen
			self.__class__ = PyGameScreen
		elif disptype == u'psychopy':
			from pygaze._screen.psychopyscreen import PsychoPyScreen
			self.__class__ = PsychoPyScreen
		else:
			raise Exception(u'Unexpected disptype : %s' % disptype)
		self.__class__.__init__(self, **args)



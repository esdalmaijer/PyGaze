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

from pygaze import settings
if settings.DISPTYPE == 'psychopy':
	try:
		from psychopy.visual import Aperture
	except:
		raise Exception("Error in plugins.frl: PsychoPy could not be loaded!")

else:
	try:
		import pygame
	except:
		raise Exception("Error in plugins.frl: PyGame could not be loaded!")

import pygaze
from pygaze._misc.misc import pos2psychopos, psychopos2pos


class FRL:
	
	"""Gaze contingent FRL"""
	
	def __init__(self, disptype=settings.DISPTYPE, pos='centre', dist=125, size=200):

		"""Initializes FRL object
		
		arguments
		None
		
		keyword arguments
		disptype	--	display type, either 'psychopy' or 'pygame'
					(default = DISPTYPE)
		pos		--	a string indicating the FRL position in relation to
					gaze position; allowed are 'centre', 'top',
					'topright', 'right', 'bottomright', 'bottom',
					'bottomleft', 'left', 'topleft' (default =
					'centre')
		dist		--	distance between gaze position and FRL center in
					pixels (default = 125)
		size		--	FRL diameter in pixels (default = 200)
		"""

		# FRL characteristics
		self.pos = pos
		self.dist = dist
		self.size = size

		# FRL distance
		self.frlxdis = ((self.dist**2)/2)**0.5 # horizontal distance between gaze position and FRL-centre
		self.frlydis = ((self.dist**2)/2)**0.5 # vertical distance between gaze position and FRL-centre
		# FRL position
		if pos in ['center','centre']:
			self.frlcor = (0, 0)
		elif pos == 'top':
			self.frlcor = (0, -self.dist)
		elif pos == 'topright':
			self.frlcor = (-self.frlxdis, self.frlydis)
		elif pos == 'right':
			self.frlcor = (self.dist, 0)
		elif pos == 'bottomright':
			self.frlcor = (-self.frlxdis, -self.frlydis)
		elif pos == 'bottom':
			self.frlcor = (0, self.dist)
		elif pos == 'bottomleft':
			self.frlcor = (self.frlxdis, -self.frlydis)
		elif pos == 'left':
			self.frlcor = (-self.dist, 0)
		elif pos == 'topleft':
			self.frlcor = (self.frlxdis, self.frlydis)
		else:
			print("WARNING! plugins.frl.__init__: FRL position argument '%s' not recognized; FRL position set to 'centre'." % pos)
			self.frlcor = (0, 0)

		if disptype in ['pygame','psychopy']:
			self.disptype = disptype
		else:
			raise Exception("Error in plugins.frl.__init__: disptype '%s' not recognized" % disptype)

		if self.disptype == 'pygame':
			self.__class__ = PyGameFRL
		elif self.disptype == 'psychopy':
			self.__class__ = PsychoPyFRL
			self.frl = Aperture(pygaze.expdisplay, self.size, pos=pos2psychopos(self.frlcor), shape='circle', units='pix')


class PyGameFRL:

	"""Gaze contingent FRL based on PyGame"""
	
	def get_pos(self, gazepos):
		
		"""Returns FRL position tuple, based on gaze position; for internal
		use
		
		arguments
		gazepos	-- a (x,y) gaze position tuple
		
		returns
		frlpos	-- a (x,y) position tuple, indicating the FRL center
				   coordinate
		"""

		return (gazepos[0]-self.frlcor[0], gazepos[1]-self.frlcor[1])


	def update(self, display, stimscreen, gazepos):

		"""Updates display with FRL, showing part of the stimulus screen
		inside of a FRL and backgroundcolour everywhere else
		
		arguments
		display	-- a libscreen.Display object
		stimscreen	-- a libscreen.Screen object containing the stimuli
				   that are to be presented
		gazepos	-- current gaze position
		
		returns
		disptime	-- directly updates display and returns refresh time
				   (PsychoPy) or an estimate (PyGame)
		"""

		# frl position
		frlpos = self.get_pos(gazepos)

		# reset display surface
		display.fill()
		
		# draw new FRL
		r = self.size/2
		h = 1 # pixel, updaterectheight (FRL actually consists of a stack of rectangles, h is the height of an individual rectangle)
		# top side
		for y in range(0,r):
			# right end of rectangle
			y = r - y # reverse y
			x = (r**2-y**2)**0.5
			# rectangle coordinates
			updaterect = [frlpos[0]-x,frlpos[1]-h*y,2*x,h]
			# update screen part
			pygaze.expdisplay.set_clip(updaterect)
			pygaze.expdisplay.blit(stimscreen.screen,(0,0))
		# bottom side
		for y in range(0,r+1):
			# right end of rectangle
			x = (r**2-y**2)**0.5
			# rectangle coordinates
			updaterect = [frlpos[0]-x,frlpos[1]+h*y,2*x,h]
			# update screen part
			pygaze.expdisplay.set_clip(updaterect)
			pygaze.expdisplay.blit(stimscreen.screen,(0,0))

		# unset clip and update display
		pygaze.expdisplay.set_clip(None)
		disptime = display.show()
		
		return disptime


class PsychoPyFRL:

	"""Gaze contingent FRL based on PsychoPy"""
	
	def get_pos(self, gazepos):
		
		"""Returns FRL position tuple, based on gaze position; for internal
		use
		
		arguments
		gazepos	-- a (x,y) gaze position tuple
		
		returns
		frlpos	-- a (x,y) position tuple, indicating the FRL center
				   coordinate
		"""

		return gazepos[0]-self.frlcor[0], gazepos[1]-self.frlcor[1]


	def update(self, display, stimscreen, gazepos):

		"""Updates display with FRL, showing part of the stimulus screen
		inside of a FRL and backgroundcolour everywhere else
		
		arguments
		display	-- a libscreen.Display object
		stimscreen	-- a libscreen.Screen object containing the stimuli
				   that are to be presented
		gazepos	-- current gaze position (a (x,y) tuple)
		
		returns
		disptime	-- directly updates display and returns refresh time
				   (PsychoPy) or an estimate (PyGame)
		"""

		# FRL position
		frlpos = pos2psychopos(self.get_pos(gazepos))

		# set FRL
		self.frl.setPos(frlpos)
		self.frl.enable()

		# draw stimuli
		display.fill(stimscreen)

		# update screen
		disptime = display.show()

		# unset FRL
		self.frl.disable()
		
		return disptime

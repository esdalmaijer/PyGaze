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

if DISPTYPE == 'psychopy':
	try:
		import psychopy
		from psychopy.visual import Aperture
	except:
		raise Exception("Error in libgazecon: PsychoPy could not be loaded!")

else:
	try:
		import pygame
		import pygame.display
		import pygame.draw
	except:
		raise Exception("Error in libgazecon: PyGame could not be loaded!")

from pygaze.libscreen import pos2psychopos, psychopos2pos


class AOI:
	
	"""Area Of Interest"""
	
	def __init__(self, aoitype, pos, size):
		
		"""Initializes an AOI object
		
		arguments
		aoitype	--	string specifying the type of AOI; should be
					'rectangle', 'circle' or 'ellipse'
		pos		--	a (x,y) position tuple
		size		--	either a single integer or a [width,height] list
					of integers
		
		keyword arguments
		None
		"""
		
		# check AOI type
		if aoitype not in ['rect','circle','ellipse']:
			raise Exception("Error in libgazecon.AOI.__init__: aoitype %s not recognized; use one of 'rect', 'circle', 'ellipse'" % aoitype)
		self.aoitype = aoitype
		
		# check AOI position
		if type(pos) not in [tuple, list]:
			raise Exception("Error in libgazecon.AOI.__init__: pos should be an (x,y) tuple or list")
		else:
			self.pos = pos
		
		# check AOI size
		if type(size) in [int,float]:
			size = [size, size]
		elif type(size) == tuple:
			size = [size[0],size[1]]
		elif type(size) == list:
			pass
		else:
			raise Exception("Error in libgazecon.AOI.__init__: size should be either an integer value or a [width,height] list of integer values")
		self.size = [int(size[0]),int(size[1])]
		
		# check if aoitype and size match
		if self.aoitype == 'circle' and self.size[0] != self.size[1]:
			raise Exception("Error in libgazecon.AOI.__init__: libgazecon.AOI.__init__: a circle does not have different width and height arguments! Either use 'ellipse' as aoitype or a single integer size value")
		
		# calculate radius (used for circle)
		self.r = self.size[0]/2

	
	def contains(self, pos):
		
		"""Checks if a position is within the AOI
		
		arguments
		pos		--	a (x,y) position tuple
		
		keyword arguments
		None
		
		returns
		True/False	--	True if the passed position is within the AOI,
					False if not
		"""
		
		if self.aoitype == 'circle':
			
			if (self.pos[0]-pos[0])**2 + (self.pos[1]-pos[1])**2 < self.r**2:
				return True
			else:
				return False
		
		elif self.aoitype == 'rectangle':
			
			if (pos[0] > self.pos[0] and pos[0] < self.pos[0]+self.size[0]) and (pos[1] > self.pos[1] and pos[1] < self.pos[1]+self.size[1]):
				return True
			else:
				return False
		
		elif self.aoitype == 'ellipse':
			
			if ((self.pos[0]-pos[0])/(self.size[0]/2))**2 + ((self.pos[1]-pos[1])/(self.size[1]/2))**2 <= 1:
				return True
			else:
				return False
		
		else:
			raise Exception("Error in libgazecon.AOI.contains: unknown aoitype %s; use one of 'rectangle', 'circle', 'ellipse'" % self.aoitype)


class FRL:
	
	"""Gaze contingent FRL"""
	
	def __init__(self, disptype=DISPTYPE, pos=FRLPOS, dist=FRLDIST, size=FRLSIZE):

		"""Initializes FRL object
		
		arguments
		None
		
		keyword arguments
		disptype	-- display type, either 'psychopy' or 'pygame' (default
				   = DISPTYPE)
		pos		-- a string indicating the FRL position in relation to
				   gaze position; allowed are 'center', 'top',
				   'topright', 'right', 'bottomright', 'bottom',
				   'bottomleft', 'left', 'topleft' (default =
				   FRLPOS)
		dist		-- distance between gaze position and FRL center in
				   pixels (default = FRLDIST)
		size		-- FRL diameter in pixels
		"""

		# FRL characteristics
		self.pos = pos
		self.dist = dist
		self.size = size

		# FRL distance
		self.frlxdis = ((FRLDIST**2)/2)**0.5 # horizontal distance between gaze position and FRL-centre
		self.frlydis = ((FRLDIST**2)/2)**0.5 # vertical distance between gaze position and FRL-centre
		# FRL position
		if pos == 'center':
			self.frlcor = (0, 0)
		elif pos == 'top':
			self.frlcor = (0, -FRLDIST)
		elif pos == 'topright':
			self.frlcor = (-self.frlxdis, self.frlydis)
		elif pos == 'right':
			self.frlcor = (FRLDIST, 0)
		elif pos == 'bottomright':
			self.frlcor = (-self.frlxdis, -self.frlydis)
		elif pos == 'bottom':
			self.frlcor = (0, FRLDIST)
		elif pos == 'bottomleft':
			self.frlcor = (self.frlxdis, -self.frlydis)
		elif pos == 'left':
			self.frlcor = (-FRLDIST, 0)
		elif pos == 'topleft':
			self.frlcor = (self.frlxdis, self.frlydis)
		else:
			print("WARNING! libgazecon.FRL.__init__: FRL position argument %s not recognized." % pos)
			print("FRL position set to center.")
			self.frlcor = (0, 0)

		if disptype in ['pygame','psychopy']:
			self.disptype = disptype
		else:
			self.disptype = 'pygame'
			print("WARNING! libgazecon.FRL.__init__: disptype not recognized; set to default ('pygame')")

		if self.disptype == 'pygame':
			self.__class__ = PyGameFRL
		elif self.disptype == 'psychopy':
			self.__class__ = PsychoPyFRL
			self.frl = Aperture(psychopy.visual.openWindows[SCREENNR], self.size, pos=pos2psychopos(self.frlcor), shape='circle', units='pix')
		else:
			self.__class__ = PyGameFRL
			print("WARNING! libgazecon.FRL.__init__: self.disptype was not recognized, which is very unexpected and should not happen! PyGameFRL is used")


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
			display.expdisplay.set_clip(updaterect)
			display.expdisplay.blit(stimscreen.screen,(0,0))
		# bottom side
		for y in range(0,r+1):
			# right end of rectangle
			x = (r**2-y**2)**0.5
			# rectangle coordinates
			updaterect = [frlpos[0]-x,frlpos[1]+h*y,2*x,h]
			# update screen part
			display.expdisplay.set_clip(updaterect)
			display.expdisplay.blit(stimscreen.screen,(0,0))

		# unset clip and update display
		display.expdisplay.set_clip(None)
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

	
class Cursor:
	
	"""Gaze contingent cursor"""

	def __init__(self, disptype=DISPTYPE, ctype=CURSORTYPE, size=CURSORSIZE, colour=CURSORCOLOUR, pw=CURSORPENWIDTH, fill=CURSORFILL):

		"""Initializes cursor object
		
		arguments
		None
		
		keyword arguments
		disptype	-- string indicating which display type is used; should
				   be either 'pygame' or 'psychopy' (default =
				   DISPTYPE)
		ctype		-- string indicating the cursor type; should be one of
				   the following: 'rectangle', 'ellipse', 'plus',
				   'cross' or 'arrow' (default = CURSORTYPE)
		size		-- cursor size in pixels (default =
				   CURSORSIZE)
		colour	-- colour for the cursor (a colour name (e.g. 'red') or
				   a RGB(A) tuple (e.g. (255,0,0) or (255,0,0,255)))
				   (default = CURSORCOLOUR)
		pw		-- cursor line thickness in pixels (default =
				   CURSORPENWIDTH)
		fill		-- Boolean indicating if cursor should be filled or not;
				   only applies for cursortypes with a body, e.g.
				   'rectangle' (default = CURSORFILL)
		"""

		# cursor characteristics
		if ctype in ['rectangle', 'ellipse', 'plus', 'cross', 'arrow']:
			self.ctype = ctype
		else:
			self.ctype = 'arrow'
			print("WARNING! libgazecon.Cursor.__init__: Cursor type could not be recognized; Cursor type set to 'arrow'")
			
		self.fill = fill
		self.pw = pw
		
		if type(size) == int:
			self.size = (size, size)
		elif type(size) == tuple or type(size) == list:
			if len(size) == 2:
				self.size = size
		else:
			self.size = (size[0], size[1])
			print("WARNING! libgazecon.Cursor.__init__: too many entries for cursor size; only the first two are used")
			
		if type(colour) == tuple or type(colour) == list:
			if len(colour) == 3 or len(colour) == 4:
				self.colour = colour
			else:
				self.colour = colour[:4]
				print("WARNING! libgazecon.Cursor.__init__: too many list entries for cursor colour; only the first four are used")
		else:
			if disptype == 'pygame':
				if colour in pygame.colordict.THECOLORS:
					self.colour = pygame.colordict.THECOLORS[colour]
				else:
					self.colour = (0,0,0)
					print("WARNING! libgazecon.Cursor.__init__: colour could not be recognized; Cursor colour set to 'black'")
			else:
				self.colour = colour
			


	def update(self, screen, gazepos):

		"""Adds the cursor to specified screen; does NOT directly update
		the display
		
		arguments
		display	-- a libscreen.Display object
		gazepos	-- current gaze position (a (x,y) tuple)
		
		returns
		screen	-- same screen as was used as an input, but with the
				   addition of a cursor at the gaze position
		"""

		# draw cursor
		if self.ctype == 'rectangle':
			screen.draw_rect(colour=self.colour, x=gazepos[0]-(self.size[0]/2), y=gazepos[1]-(self.size[1]/2), w=self.size[0], h=self.size[1], pw=self.pw, fill=self.fill)
			#pygame.draw.rect(screen, self.colour, [gazepos[0]-(self.size[0]/2), gazepos[1]-(self.size[1]/2), self.size[0], self.size[1]], self.figpenw)
		if self.ctype == 'ellipse':
			screen.draw_ellipse(colour=self.colour, x=gazepos[0]-(self.size[0]/2), y=gazepos[1]-(self.size[1]/2), w=self.size[0], h=self.size[1], pw=self.pw, fill=self.fill)
			#pygame.draw.ellipse(screen, self.colour, [gazepos[0]-(self.size[0]/2), gazepos[1]-(self.size[1]/2), self.size[0], self.size[1]], self.figpenw)
		if self.ctype == 'plus':
			screen.draw_fixation(fixtype='cross', colour=self.colour, pos=gazepos, pw=self.pw, diameter=self.size)
			#pygame.draw.line(screen, self.colour, (gazepos[0]-(self.size[0]/2),gazepos[1]), (gazepos[0]+(self.size[0]/2),gazepos[1]), self.penw)
			#pygame.draw.line(screen, self.colour, (gazepos[0],gazepos[1]-(self.size[1]/2)), (gazepos[0],gazepos[1]+(self.size[1]/2)), self.penw)
		if self.ctype == 'cross':
			screen.draw_fixation(fixtype='x', colour=self.colour, pos=gazepos, pw=self.pw, diameter=self.size)
			#pygame.draw.line(screen, self.colour, (gazepos[0]-(self.size[0]/2),gazepos[1]-(self.size[1]/2)), (gazepos[0]+(self.size[0]/2),gazepos[1]+(self.size[1]/2)), self.penw)
			#pygame.draw.line(screen, self.colour, (gazepos[0]-(self.size[0]/2),gazepos[1]+(self.size[1]/2)), (gazepos[0]+(self.size[0]/2),gazepos[1]-(self.size[1]/2)), self.penw)
		if self.ctype == 'arrow':
			screen.draw_polygon([(gazepos[0]+self.size[0],gazepos[1]+(0.5*self.size[1])),(gazepos[0],gazepos[1]),(gazepos[0]+(0.5*self.size[0]),gazepos[1]+self.size[1])], colour=self.colour, pw=self.pw, fill=self.fill)
			screen.draw_line(colour=self.colour, spos=(gazepos[0],gazepos[1]), epos=(gazepos[0]+self.size[0],gazepos[1]+self.size[1]), pw=self.pw)
			#pygame.draw.polygon(screen, self.colour, [(gazepos[0]+self.size[0],gazepos[1]+(0.5*self.size[1])),(gazepos[0],gazepos[1]),(gazepos[0]+(0.5*self.size[0]),gazepos[1]+self.size[1])], self.figpenw)
			#pygame.draw.line(screen, self.colour, (gazepos[0],gazepos[1]), (gazepos[0]+self.size[0],gazepos[1]+self.size[1]), self.penw)

		return screen


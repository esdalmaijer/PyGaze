## This file is part of PyGaze - the open-source toolbox for eye tracking
##
##	PyGaze is a Python module for easily creating gaze contingent experiments
##	or other software (as well as non-gaze contingent experiments/software)
##	Copyright (C) 2012-2013  Edwin S. Dalmaijer
##
##	This program is free software: you can redistribute it and/or modify
##	it under the terms of the GNU General Public License as published by
##	the Free Software Foundation, either version 3 of the License, or
##	(at your option) any later version.
##
##	This program is distributed in the hope that it will be useful,
##	but WITHOUT ANY WARRANTY; without even the implied warranty of
##	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##	GNU General Public License for more details.
##
##	You should have received a copy of the GNU General Public License
##	along with this program.  If not, see <http://www.gnu.org/licenses/>
#
# version: 0.4 (25-03-2013)

from defaults import *
try:
	from constants import *
except:
	pass

import pygaze
import libtime

import copy
import math
import os.path

if DISPTYPE == 'psychopy':
	try:
		import psychopy
		from psychopy.visual import Window
		from psychopy.visual import GratingStim
		from psychopy.visual import Circle
		from psychopy.visual import Line
		from psychopy.visual import ShapeStim
		from psychopy.visual import TextStim
		from psychopy.visual import ImageStim
	except:	
		print("Error in libscreen: PsychoPy could not be loaded!")

else:
	try:
		import pygame
		import pygame.display
		import pygame.draw
		import pygame.image
	except:
		print("Error in libscreen: PyGame could not be loaded!")

# try importing PIL
try:
	from PIL import Image
	pilimp = True
except:
	try:
		import Image
		pilimp = True
	except:
		pilimp = False
		print("Warning in libscreen: PIL's Image class could not be loaded; image scaling with PsychoPy disptype is now impossible!")
	
	
global expdisplay


class Display:

	"""A class for Display objects, to present Screen objects on a monitor"""

	def __init__(self, disptype=DISPTYPE, dispsize=DISPSIZE, fgc=FGC, bgc=BGC, screennr=SCREENNR, screen=None):

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
		screennr	-- the screen number: 0, 1 etc. (default =
				   SCREENNR)
		screen	-- a Screen object to be presented on the new Display
				   (default=None)
		"""

		global expdisplay

		self.dispsize = dispsize
		self.fgc = fgc
		self.bgc = bgc
		self.screennr = screennr
		self.mousevis = False

		if disptype in ['pygame','psychopy']:
			self.disptype = disptype
		else:
			self.disptype = 'pygame'
			print("Error in libscreen.Display.__init__: disptype not recognized; set to default ('pygame')")

		# pygame
		if self.disptype == 'pygame':
			# initialize PyGame display-module
			pygame.display.init()
			# make mouse invisible (should be so per default, but you never know)
			pygame.mouse.set_visible(self.mousevis)
			# create surface for full screen displaying
			expdisplay = pygame.display.set_mode(self.dispsize,pygame.FULLSCREEN|pygame.HWSURFACE|pygame.DOUBLEBUF)

			# blit screen to display surface (if user entered one)
			if screen:
				expdisplay.blit(screen.screen,(0,0))
			else:
				expdisplay.fill(self.bgc)

		# psychopy
		elif self.disptype == 'psychopy':
			# create window
			expdisplay = Window(size=self.dispsize, pos=None, color=rgb2psychorgb(self.bgc), colorSpace='rgb', fullscr=True, screen=self.screennr, units='pix')
			# set mouse visibility
			expdisplay.setMouseVisible(self.mousevis)
			# get screen in window
			if screen:
				for s in screen.screen:
					s.draw()

		# display
		self.expdisplay = expdisplay
		
		# functions
		if self.disptype == 'pygame':
			self.showfunc = pygame.display.flip
		elif self.disptype == 'psychopy':
			self.showfunc = self.expdisplay.flip


	def show(self):

		"""Updates ('flips') the display
		
		arguments
		None
		
		returns
		time		-- the exact refresh time when disptype is PsychoPy, an
				   estimate when disptype is PyGame
		"""

		self.showfunc()
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

		if self.disptype == 'pygame':
			if len(rect) > 1:
				for r in rect:
					self.expdisplay.set_clip(r)
					if screen:
						self.expdisplay.blit(screen.screen, (0,0))
					pygame.display.update(r)
					self.expdisplay.set_clip(None)
					
			elif len(rect) == 1:
				self.expdisplay.clip(rect)
				if screen:
					self.expdisplay.blit(screen.screen, (0,0))
				pygame.display.update(rect)
				self.expdisplay.set_clip(None)

			else:
				print("Error in libscreen.Display.show_part: rect should be a single rect (i.e. a (x,y,w,h) tuple) or a list of rects!")

		elif self.disptype == 'psychopy':
			if screen:
				for s in screen.screen:
					s.draw()
			self.show()
			print("Display.show_part not available for psychopy display type; show is used instead")
		
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

		if self.disptype == 'pygame':
			self.expdisplay.fill(self.bgc)
			if screen != None:
				self.expdisplay.blit(screen.screen,(0,0))

		elif self.disptype == 'psychopy':
			self.expdisplay.clearBuffer()
			if screen != None:
				for s in screen.screen:
					s.draw()


	def close(self):

		"""Closes the display
		
		arguments
		None
		
		returns
		Nothing"""

		if self.disptype == 'pygame':
			pygame.display.quit()
			
		elif self.disptype == 'psychopy':
			self.expdisplay.close()


class Screen:

	"""A class for Screen objects, for visual stimuli (to be displayed via a Display object)"""

	def __init__(self, disptype=DISPTYPE, dispsize=DISPSIZE, fgc=FGC, bgc=BGC, screennr=SCREENNR, mousevisible=MOUSEVISIBLE, screen=None):

		"""Initializes the Screen object
		
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
		screennr	-- the screen number: 0, 1 etc. (default =
				   SCREENNR)
		mousevisible	-- Boolean indicating mouse visibility (default = 
					   MOUSEVISIBLE)
		screen	-- a Screen object to be presented on the new Display
				   (default=None)
		"""

		# properties
		self.dispsize = dispsize
		self.fgc = fgc
		self.bgc = bgc
		self.screennr = screennr
		self.mousevis = mousevisible

		if disptype in ['pygame','psychopy']:
			self.disptype = disptype
		else:
			self.disptype = 'pygame'
			print("Error in libscreen.Screen.__init__: disptype not recognized; set to default ('pygame')")

		if self.disptype == 'pygame':
			self.__class__ = PyGameScreen
		elif self.disptype == 'psychopy':
			self.__class__ = PsychoPyScreen
		else:
			self.__class__ = PyGameScreen
			print("Error in libscreen.Screen.__init__: self.disptype was not recognized, which is very unexpected and should not happen! PyGameScreen is used")

		# create screen
		self.create(screen=screen)


class PyGameScreen:

	"""A class for PyGame Screen objects, for visual stimuli (to be displayed via a Display object)"""

	def create(self, screen=None):

		"""Creates a new Screen object, filled with either the background
		colour or specified screen
		
		arguments
		None
		
		keyword arguments
		screen	-- a libscreen.Screen object, to be displayed on the
				   new screen or None for the background colour
		returns
		Nothing	-- sets the self.screen property to a PyGame Surface
				   or a list of PsychoPy stimuli, depening on the
				   disptype
		"""

		self.screen = pygame.Surface(self.dispsize)
		self.screen.fill(self.bgc)

		if screen != None:
			self.screen.blit(screen.screen,(0,0))


	def clear(self, colour=None):

		"""Clears the screen and fills it with a colour
		
		arguments
		None
		
		keyword arguments
		colour	-- the colour to fill the screen with (a colour name
				   (e.g. 'red') or a RGB(A) tuple (e.g. (255,0,0) or 
				   (255,0,0,255))) or None for the default background
				   colour, self.bgc (default = None)
		
		returns
		Nothing	-- clears self.screen property
		"""

		if colour == None:
			colour = self.bgc
		
		self.screen.fill(colour)


	def copy(self, screen):

		"""Copies a screen to the current screen
		
		arguments
		screen	-- a libscreen.Screen object
		
		returns
		Nothing	-- sets the self.screen property to a copy of
				   screen.screen
		"""

		self.screen = copy.copy(screen.screen)
			

	def draw_circle(self, colour=None, pos=None, r=50, pw=1, fill=False):

		"""Draws a circle on the screen
		
		arguments
		None
		
		keyword arguments
		colour	-- colour for the circle (a colour name (e.g. 'red') or
				   a RGB(A) tuple (e.g. (255,0,0) or (255,0,0,255))) or
				   None for the default foreground colour, self.fgc
				   (default = None)
		pos		-- circle center, an (x,y) position tuple or None for a
				   central position (default = None)
		r		-- circle radius (default = 50)
		pw		-- penwidth: circle line thickness (default = 1)
		fill		-- Boolean indicating whether circle should be filled or
				   not (default = False)
		
		returns
		Nothing	-- draws a circle on (PyGame) or adds a Circle stimulus
				   to (PsychoPy) the self.screen property
		"""

		if colour == None:
			colour = self.fgc
		if pos == None:
			pos = (self.dispsize[0]/2, self.dispsize[1]/2)
		if fill:
			pw = 0

		pygame.draw.circle(self.screen, colour, pos, r, pw)
		

	def draw_ellipse(self, colour=None, x=None, y=None, w=50, h=50, pw=1, fill=False):

		"""Draws an ellipse on the screen
		
		arguments
		None
		
		keyword arguments
		colour	-- colour for the circle (a colour name (e.g. 'red') or
				   a RGB(A) tuple (e.g. (255,0,0) or (255,0,0,255))) or
				   None for the default foreground colour, self.fgc
				   (default = None)
		x		-- x coordinate of the rectangle in which the ellipse is
				   drawn or None for a horizontal centrally drawn
				   ellipse (default = None)
		y		-- y coordinate of the rectangle in which the ellipse is
				   drawn or None for a vertical centrally drawn
				   ellipse (default = None)
		w		-- width of the rectangle in which the ellipse is drawn
				   (default = 50)
		h		-- height of the rectangle in which the ellipse is drawn
				   (default = 50)
		pw		-- penwidth: circle line thickness (default = 1)
		fill		-- Boolean indicating whether ellipse should be filled
				   or not (default = False)
		
		returns
		Nothing	-- draws an ellipse on (PyGame) or adds a GratinsStim
				   stimulus to (PsychoPy) the self.screen property
		"""

		if colour == None:
			colour = self.fgc
		if x == None:
			x = self.dispsize[0]/2 - w/2
		if y == None:
			y = self.dispsize[1]/2 - h/2
		if fill:
			pw = 0

		pygame.draw.ellipse(self.screen, colour, [x,y,w,h], pw)

		
	def draw_rect(self, colour=None, x=None, y=None, w=50, h=50, pw=1, fill=False):

		"""Draws a rectangle on the screen
		
		arguments
		None
		
		keyword arguments
		colour	-- colour for the circle (a colour name (e.g. 'red') or
				   a RGB(A) tuple (e.g. (255,0,0) or (255,0,0,255))) or
				   None for the default foreground colour, self.fgc
				   (default = None)
		x		-- x coordinate of the rectangle or None for a
				   horizontal centrally drawn rectangle (default = None)
		y		-- y coordinate of the rectangle or None for a
				   vertical centrally drawn rectangle (default = None)
		w		-- width of the rectangle (default = 50)
		h		-- height of the rectangle (default = 50)
		pw		-- penwidth: ellipse line thickness (default = 1)
		fill		-- Boolean indicating whether rectangle should be filled
				   or not (default = False)
		
		returns
		Nothing	-- draws a rectangle on (PyGame) or adds a GratinsStim
				   stimulus to (PsychoPy) the self.screen property
		"""

		if colour == None:
			colour = self.fgc
		if x == None:
			x = self.dispsize[0]/2 - w/2
		if y == None:
			y = self.dispsize[1]/2 - h/2
		if fill:
			pw = 0

		pygame.draw.rect(self.screen, colour, [x,y,w,h], pw)

	def draw_line(self, colour=None, spos=None, epos=None, pw=1):

		"""Draws a line on the screen
		
		arguments
		None
		
		keyword arguments
		colour	-- colour for the circle (a colour name (e.g. 'red') or
				   a RGB(A) tuple (e.g. (255,0,0) or (255,0,0,255))) or
				   None for the default foreground colour, self.fgc
				   (default = None)
		spos		-- line start, an (x,y) position tuple or None for a
				   quarter x and a central y position (default = None)
		epos		-- line end, an (x,y) position tuple or None for a
				   three-quarter x and a central y position (default =
				   None)
		pw		-- penwidth: line thickness (default = 1)
		
		returns
		Nothing	-- draws a line on (PyGame) or adds a Line stimulus to
				   (PsychoPy) the self.screen property
		"""

		if colour == None:
			colour = self.fgc
		if spos == None:
			spos = (int(self.dispsize[0]*0.25), self.dispsize[1]/2)
		if epos == None:
			epos = (int(self.dispsize[0]*0.75), self.dispsize[1]/2)

		pygame.draw.line(self.screen, colour, spos, epos, pw)


	def draw_polygon(self, pointlist, colour=None, pw=1, fill=True):

		"""Draws a polygon on the screen
		
		arguments
		pointlist	-- a list of (x,y) tuples resembling the cornerpoints
				   of the polygon
		
		keyword arguments
		colour	-- colour for the circle (a colour name (e.g. 'red') or
				   a RGB(A) tuple (e.g. (255,0,0) or (255,0,0,255))) or
				   None for the default foreground colour, self.fgc
				   (default = None)
		pw		-- penwidth: polygon line thickness (default = 1)
		fill		-- Boolean indicating whether polygon should be filled
				   or not (default = False)
		
		returns
		Nothing	-- draws a polygon on (PyGame) or adds a ShapeStim
				   stimulus to (PsychoPy) the self.screen property
		"""

		if colour == None:
			colour = self.fgc
		if fill:
			pw = 0

		pygame.draw.polygon(self.screen, colour, pointlist, pw)


	def draw_fixation(self, fixtype='cross', colour=None, pos=None, pw=1, diameter=12):

		"""Draws a fixation (cross, x or dot) on the screen
		
		arguments
		None
		
		keyword arguments
		fixtype	-- type of fixation mark, should be either of the
				   following strings:
					'cross'	-- a '+'
					'x'		-- a 'x'
					'dot'		-- a filled circle
				   (default = 'cross')
		colour	-- colour for the circle (a colour name (e.g. 'red') or
				   a RGB(A) tuple (e.g. (255,0,0) or (255,0,0,255))) or
				   None for the default foreground colour, self.fgc
				   (default = None)
		pos		-- fixation center, an (x,y) position tuple or None for
				   a central position (default = None)
		pw		-- penwidth: fixation line thickness (default = 1)
		diameter	-- diameter of the fixation mark in pixels (default =
				   12)
		
		returns
		Nothing	-- draws on (PyGame) or adds stimuli to (PsychoPy) the
				   self.screen property
		"""

		if fixtype not in ['cross','x','dot']:
			fixtype == 'cross'
			print("Error in libscreen.Screen.draw_fixation: fixtype not recognized; fixtype set to default ('cross')")
		if colour == None:
			colour = self.fgc
		if pos == None:
			pos = (self.dispsize[0]/2, self.dispsize[1]/2)

		r = diameter/2
		if fixtype == 'cross':
			pygame.draw.line(self.screen, colour, (pos[0]-r, pos[1]), (pos[0]+r, pos[1]), pw)
			pygame.draw.line(self.screen, colour, (pos[0], pos[1]-r), (pos[0], pos[1]+r), pw)
		elif fixtype == 'x':
			x = math.cos(math.radians(45)) * r
			y = math.sin(math.radians(45)) * r
			pygame.draw.line(self.screen, colour, (pos[0]-x, pos[1]-y), (pos[0]+x, pos[1]+y), pw)
			pygame.draw.line(self.screen, colour, (pos[0]-x, pos[1]+y), (pos[0]+x, pos[1]-y), pw)
		elif fixtype == 'dot':
			pygame.draw.circle(self.screen, colour, pos, r, 0)


	def draw_text(self, text='text', colour=None, pos=None, center=True, font='mono', fontsize=12, antialias=True):

		"""Draws a text on the screen
		
		arguments
		None
		
		keyword arguments
		text		-- string to be displayed (newlines are allowed and will
				   be recognized) (default = 'text')
		colour	-- colour for the circle (a colour name (e.g. 'red') or
				   a RGB(A) tuple (e.g. (255,0,0) or (255,0,0,255))) or
				   None for the default foreground colour, self.fgc
				   (default = None)
		pos		-- text position, an (x,y) position tuple or None for a
				   central position (default = None)
		center	-- Boolean indicating is the pos keyword argument should
				   indicate the text center (True) or the top right
				   coordinate (False) (default = True)
		font		-- font name (a string value); should be the name of a
				   font included in the PyGaze resources/fonts directory
				   (default = 'mono')
		fontsize	-- fontsize in pixels (an integer value) (default = 12)
		antialias	-- Boolean indicating whether text should be antialiased
				   or not (default = True)
		
		returns
		Nothing	-- renders and draws a surface with text on (PyGame) or
				   adds a TextStim to (PsychoPy) the self.screen
				   property
		"""

		if colour == None:
			colour = self.fgc
		if pos == None:
			pos = (self.dispsize[0]/2, self.dispsize[1]/2)

		if not pygame.font.get_init():
			pygame.font.init()
		
		fontname = os.path.join(pygaze.FONTDIR, font) + '.ttf'
		font = pygame.font.Font(fontname, fontsize)
		
		lines = text.split("\n")
		lineh = font.get_linesize()
		
		for lnr in range(0,len(lines)):
			txtsurf = font.render(lines[lnr], antialias, self.fgc)
			if center and len(lines) == 1:
				linepos = (pos[0] - font.size(lines[lnr])[0]/2, pos[1] - font.size(lines[lnr])[1]/2)
			elif center:
				linepos = (pos[0] - font.size(lines[lnr])[0]/2, pos[1] + lineh * (2 * (lnr - (len(lines)/2.0) + 0.5)))
			else:
				linepos = (pos[0], pos[1] + 2 * lnr)
			self.screen.blit(txtsurf, linepos)
	
	
	def draw_image(self, image, pos=None, scale=None):
		
		"""Draws an image on the screen
		
		arguments
		image		-- a full path to an image file
		
		keyword arguments
		pos		-- image center position, an (x,y) position tuple or
				   None for a central position (default = None)
		scale	-- scale factor for the image or None for no scaling
				   (default = None)
		
		returns
		Nothing	-- loads and draws an image surface on (PyGame) or
				   adds SimpleImageStim to (PsychoPy) the self.screen
				   property
		"""
		
		if pos == None:
			pos = (self.dispsize[0]/2, self.dispsize[1]/2)
		
		img = pygame.image.load(image)
		
		if scale != None:
			pygame.transform.scale(img, (int(img.get_width()*scale), int(img.get_height()*scale)))
		
		imgpos = (pos[0] - img.get_width()/2, pos[1] - img.get_height()/2)
		
		self.screen.blit(img, imgpos)


	def set_background_colour(self, colour=None):

		"""Set the background colour to colour
		
		arguments
		None
		
		keyword arguments
		colour	-- colour for the circle (a colour name (e.g. 'red') or
				   a RGB(A) tuple (e.g. (255,0,0) or (255,0,0,255))) or
				   None for the default foreground colour, self.fgc
				   (default = None)
		
		returns
		Nothing	-- sets bgc property to specified colour
		"""

		if colour != None:
			self.bgc = colour


class PsychoPyScreen:

	"""A class for PsychoPy Screen objects, for visual stimuli (to be displayed via a Display object)"""

	def create(self, screen=None):

		"""Creates a new Screen object, filled with either the background
		colour or specified screen
		
		arguments
		None
		
		keyword arguments
		screen	-- a libscreen.Screen object, to be displayed on the
				   new screen or None for the background colour
		returns
		Nothing	-- sets the self.screen property to a PyGame Surface
				   or a list of PsychoPy stimuli, depening on the
				   disptype
		"""

		self.screen = []
		self.clear()

		if screen != None:
			self.copy(screen)


	def clear(self, colour=None):

		"""Clears the screen and fills it with a colour
		
		arguments
		None
		
		keyword arguments
		colour	-- the colour to fill the screen with (a colour name
				   (e.g. 'red') or a RGB(A) tuple (e.g. (255,0,0) or 
				   (255,0,0,255))) or None for the default background
				   colour, self.bgc (default = None)
		
		returns
		Nothing	-- clears self.screen property
		"""

		if colour == None:
			colour = self.bgc
		
		self.screen = []
		self.draw_rect(colour=colour, x=0, y=0, w=self.dispsize[0], h=self.dispsize[1], fill=True)


	def copy(self, screen):

		"""Copies a screen to the current screen
		
		arguments
		screen	-- a libscreen.Screen object
		
		returns
		Nothing	-- sets the self.screen property to a copy of
				   screen.screen
		"""

		self.screen = copy.copy(screen.screen)
			

	def draw_circle(self, colour=None, pos=None, r=50, pw=1, fill=False):

		"""Draws a circle on the screen
		
		arguments
		None
		
		keyword arguments
		colour	-- colour for the circle (a colour name (e.g. 'red') or
				   a RGB(A) tuple (e.g. (255,0,0) or (255,0,0,255))) or
				   None for the default foreground colour, self.fgc
				   (default = None)
		pos		-- circle center, an (x,y) position tuple or None for a
				   central position (default = None)
		r		-- circle radius (default = 50)
		pw		-- penwidth: circle line thickness (default = 1)
		fill		-- Boolean indicating whether circle should be filled or
				   not (default = False)
		
		returns
		Nothing	-- draws a circle on (PyGame) or adds a Circle stimulus
				   to (PsychoPy) the self.screen property
		"""

		if colour == None:
			colour = self.fgc
		if pos == None:
			pos = (self.dispsize[0]/2, self.dispsize[1]/2)

		colour = rgb2psychorgb(colour)
		pos = pos2psychopos(pos,dispsize=self.dispsize)

		if fill:
			self.screen.append(Circle(expdisplay, radius=r, edges=32, pos=pos, lineColor=colour, lineColorSpace='rgb', fillColor=colour, fillColorSpace='rgb'))
		else:
			self.screen.append(Circle(expdisplay, radius=r-pw, edges=32, pos=pos, lineColor=colour, lineColorSpace='rgb'))
		

	def draw_ellipse(self, colour=None, x=None, y=None, w=50, h=50, pw=1, fill=False):

		"""Draws an ellipse on the screen
		
		arguments
		None
		
		keyword arguments
		colour	-- colour for the circle (a colour name (e.g. 'red') or
				   a RGB(A) tuple (e.g. (255,0,0) or (255,0,0,255))) or
				   None for the default foreground colour, self.fgc
				   (default = None)
		x		-- x coordinate of the rectangle in which the ellipse is
				   drawn or None for a horizontal centrally drawn
				   ellipse (default = None)
		y		-- y coordinate of the rectangle in which the ellipse is
				   drawn or None for a vertical centrally drawn
				   ellipse (default = None)
		w		-- width of the rectangle in which the ellipse is drawn
				   (default = 50)
		h		-- height of the rectangle in which the ellipse is drawn
				   (default = 50)
		pw		-- penwidth: circle line thickness (default = 1)
		fill		-- Boolean indicating whether ellipse should be filled
				   or not (default = False)
		
		returns
		Nothing	-- draws an ellipse on (PyGame) or adds a GratinsStim
				   stimulus to (PsychoPy) the self.screen property
		"""

		if colour == None:
			colour = self.fgc
		if x == None:
			x = 0
		if y == None:
			y = 0

		pos = x,y
		colour = rgb2psychorgb(colour)
		pos = pos2psychopos(pos,dispsize=self.dispsize)
		pos = pos[0] + w/2, pos[1] - h/2

		self.screen.append(GratingStim(expdisplay, tex=None, mask="circle", pos=pos, size=(w,h), color=colour))
		if not fill:
			self.screen.append(GratingStim(expdisplay, tex=None, mask="circle", pos=pos, size=(w-2*pw,h-2*pw), color=rgb2psychorgb(self.bgc)))

		
	def draw_rect(self, colour=None, x=None, y=None, w=50, h=50, pw=1, fill=False):

		"""Draws a rectangle on the screen
		
		arguments
		None
		
		keyword arguments
		colour	-- colour for the circle (a colour name (e.g. 'red') or
				   a RGB(A) tuple (e.g. (255,0,0) or (255,0,0,255))) or
				   None for the default foreground colour, self.fgc
				   (default = None)
		x		-- x coordinate of the rectangle or None for a
				   horizontal centrally drawn rectangle (default = None)
		y		-- y coordinate of the rectangle or None for a
				   vertical centrally drawn rectangle (default = None)
		w		-- width of the rectangle (default = 50)
		h		-- height of the rectangle (default = 50)
		pw		-- penwidth: ellipse line thickness (default = 1)
		fill		-- Boolean indicating whether rectangle should be filled
				   or not (default = False)
		
		returns
		Nothing	-- draws a rectangle on (PyGame) or adds a GratinsStim
				   stimulus to (PsychoPy) the self.screen property
		"""

		if colour == None:
			colour = self.fgc
		if x == None:
			x = self.dispsize[0]/2
		if y == None:
			y = self.dispsize[1]/2

		pos = x,y
		colour = rgb2psychorgb(colour)
		pos = pos2psychopos(pos,dispsize=self.dispsize)
		pos = pos[0] + w/2, pos[1] - h/2

		self.screen.append(GratingStim(expdisplay, tex=None, mask=None, pos=pos, size=[w,h], color=colour))
		if not fill:
			self.screen.append(GratingStim(expdisplay, tex=None, mask=None, pos=pos, size=[w-2,h-2], color=rgb2psychorgb(self.bgc)))


	def draw_line(self, colour=None, spos=None, epos=None, pw=1):

		"""Draws a line on the screen
		
		arguments
		None
		
		keyword arguments
		colour	-- colour for the circle (a colour name (e.g. 'red') or
				   a RGB(A) tuple (e.g. (255,0,0) or (255,0,0,255))) or
				   None for the default foreground colour, self.fgc
				   (default = None)
		spos		-- line start, an (x,y) position tuple or None for a
				   quarter x and a central y position (default = None)
		epos		-- line end, an (x,y) position tuple or None for a
				   three-quarter x and a central y position (default =
				   None)
		pw		-- penwidth: line thickness (default = 1)
		
		returns
		Nothing	-- draws a line on (PyGame) or adds a Line stimulus to
				   (PsychoPy) the self.screen property
		"""

		if colour == None:
			colour = self.fgc
		if spos == None:
			spos = (int(self.dispsize[0]*0.25), self.dispsize[1]/2)
		if epos == None:
			epos = (int(self.dispsize[0]*0.75), self.dispsize[1]/2)

		colour = rgb2psychorgb(colour)
		spos = pos2psychopos(spos,dispsize=self.dispsize)
		epos = pos2psychopos(epos,dispsize=self.dispsize)
		
		self.screen.append(Line(expdisplay, start=spos, end=epos, lineColor=colour, lineColorSpace='rgb', lineWidth=pw))


	def draw_polygon(self, pointlist, colour=None, pw=1, fill=True):

		"""Draws a polygon on the screen
		
		arguments
		pointlist	-- a list of (x,y) tuples resembling the cornerpoints
				   of the polygon
		
		keyword arguments
		colour	-- colour for the circle (a colour name (e.g. 'red') or
				   a RGB(A) tuple (e.g. (255,0,0) or (255,0,0,255))) or
				   None for the default foreground colour, self.fgc
				   (default = None)
		pw		-- penwidth: polygon line thickness (default = 1)
		fill		-- Boolean indicating whether polygon should be filled
				   or not (default = False)
		
		returns
		Nothing	-- draws a polygon on (PyGame) or adds a ShapeStim
				   stimulus to (PsychoPy) the self.screen property
		"""

		if colour == None:
			colour = self.fgc

		colour = rgb2psychorgb(colour)
		pl = []
		for pos in pointlist:
			pl.append(pos2psychopos(pos,dispsize=self.dispsize))

		if fill:
			self.screen.append(ShapeStim(expdisplay, lineWidth=pw, lineColor=colour, lineColorSpace='rgb', fillColor=colour, fillColorSpace='rgb',vertices=pointlist, closeShape=True))
		else:
			self.screen.append(ShapeStim(expdisplay, lineWidth=pw, lineColor=colour, lineColorSpace='rgb', fillColor=rgb2psychorgb(self.bgc), fillColorSpace='rgb',vertices=pointlist, closeShape=True))

			
	def draw_fixation(self, fixtype='cross', colour=None, pos=None, pw=1, diameter=12):

		"""Draws a fixation (cross, x or dot) on the screen
		
		arguments
		None
		
		keyword arguments
		fixtype	-- type of fixation mark, should be either of the
				   following strings:
					'cross' -- a '+'
					'x'	 -- a 'x'
					'dot'	   -- a filled circle
				   (default = 'cross')
		colour	-- colour for the circle (a colour name (e.g. 'red') or
				   a RGB(A) tuple (e.g. (255,0,0) or (255,0,0,255))) or
				   None for the default foreground colour, self.fgc
				   (default = None)
		pos		-- fixation center, an (x,y) position tuple or None for
				   a central position (default = None)
		pw		-- penwidth: fixation line thickness (default = 1)
		diameter	-- diameter of the fixation mark in pixels (default =
				   12)
		
		returns
		Nothing	-- draws on (PyGame) or adds stimuli to (PsychoPy) the
				   self.screen property
		"""
		
		if fixtype not in ['cross','x','dot']:
			fixtype == 'cross'
			print("Error in libscreen.Screen.draw_fixation: fixtype not recognized; fixtype set to default ('cross')")
		if colour == None:
			colour = self.fgc
		if pos == None:
			pos = (self.dispsize[0]/2, self.dispsize[1]/2)

		r = diameter/2
		if fixtype == 'cross':
			self.draw_line(colour=colour, spos=(pos[0]-r, pos[1]), epos=(pos[0]+r, pos[1]), pw=pw)
			self.draw_line(colour=colour, spos=(pos[0], pos[1]+r), epos=(pos[0], pos[1]-r), pw=pw)
		elif fixtype == 'x':
			x = math.cos(math.radians(45)) * r
			y = math.sin(math.radians(45)) * r
			self.draw_line(colour=colour, spos=(pos[0]-x, pos[1]-y), epos=(pos[0]+x, pos[1]+y), pw=pw)
			self.draw_line(colour=colour, spos=(pos[0]-x, pos[1]+y), epos=(pos[0]+x, pos[1]-y), pw=pw)
		elif fixtype == 'dot':
			self.draw_circle(colour=colour, pos=pos, r=r, pw=0, fill=True)


	def draw_text(self, text='text', colour=None, pos=None, center=True, font='mono', fontsize=12, antialias=True):

		"""Draws a text on the screen
		
		arguments
		None
		
		keyword arguments
		text		-- string to be displayed (newlines are allowed and will
				   be recognized) (default = 'text')
		colour	-- colour for the circle (a colour name (e.g. 'red') or
				   a RGB(A) tuple (e.g. (255,0,0) or (255,0,0,255))) or
				   None for the default foreground colour, self.fgc
				   (default = None)
		pos		-- text position, an (x,y) position tuple or None for a
				   central position (default = None)
		center	-- Boolean indicating is the pos keyword argument should
				   indicate the text center (True) or the top right
				   coordinate (False) (default = True)
		font		-- font name (a string value); should be the name of a
				   font included in the PyGaze resources/fonts directory
				   (default = 'mono')
		fontsize	-- fontsize in pixels (an integer value) (default = 12)
		antialias	-- Boolean indicating whether text should be antialiased
				   or not (default = True)
		
		returns
		Nothing	-- renders and draws a surface with text on (PyGame) or
				   adds SimpleTextStim to (PsychoPy) the self.screen
				   property
		"""

		if colour == None:
			colour = self.fgc
		if pos == None:
			pos = (self.dispsize[0]/2, self.dispsize[1]/2)

		if center:
			align = 'center'
		else:
			align = 'left'

		colour = rgb2psychorgb(colour)
		pos = pos2psychopos(pos,dispsize=self.dispsize)

		self.screen.append(TextStim(expdisplay, text=str(text), font=font, pos=pos, color=colour, height=fontsize, antialias=antialias, alignHoriz=align, fontFiles=pygaze.FONTFILES, wrapWidth=None))
	
	
	def draw_image(self, image, pos=None, scale=None):
		
		"""Draws an image on the screen
		
		arguments
		image		-- a full path to an image file
		
		keyword arguments
		pos		-- image center position, an (x,y) position tuple or
				   None for a central position (default = None)
		scale	-- scale factor for the image or None for no scaling
				   (default = None)
		
		returns
		Nothing	-- loads and draws an image surface on (PyGame) or
				   adds SimpleImageStim to (PsychoPy) the self.screen
				   property
		"""
		
		if pos == None:
			pos = (self.dispsize[0]/2, self.dispsize[1]/2)
		
		pos = pos2psychopos(pos,dispsize=self.dispsize)
		
		if scale == None:
			imgsize = None
		else:
			if pilimp:
				img = Image.open(image)
				imgsize = (img.size[0]*scale, img.size[1]*scale)
			else:
				imgsize = None
				print("Warning in libscreen.Screen: PIL's Image class could not be loaded; image scaling with PsychoPy disptype is now impossible!")
			
		self.screen.append(ImageStim(expdisplay, image=image, pos=pos, size=imgsize))


	def set_background_colour(self, colour=None):

		"""Set the background colour to colour
		
		arguments
		None
		
		keyword arguments
		colour	-- colour for the circle (a colour name (e.g. 'red') or
				   a RGB(A) tuple (e.g. (255,0,0) or (255,0,0,255))) or
				   None for the default foreground colour, self.fgc
				   (default = None)
		
		returns
		Nothing	-- sets bgc property to specified colour
		"""

		if colour != None:
			self.bgc = colour


# # # # # # #
# functions #
# # # # # # #

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
		dispsize = tuple(psychopy.visual.openWindows[SCREENNR].size)

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
		dispsize = tuple(psychopy.visual.openWindows[SCREENNR].size)

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
	psyrgb	-- a (R,G,B) or (R,G,B,A) tuple containing values between -1
			   and 1; or rgbgun when passed rgbgun was not a tuple or a
			   list
	"""
	
	if type(rgbgun) not in [tuple,list]:
		return rgbgun

	psyrgb = []

	for val in rgbgun:
		psyrgb.append((val/127.5)-1)

	return tuple(psyrgb)

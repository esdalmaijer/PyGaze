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
import pygaze

from pygaze._screen.basescreen import BaseScreen
# we try importing the copy_docstr function, but as we do not really need it
# for a proper functioning of the code, we simply ignore it when it fails to
# be imported correctly
try:
	from pygaze._misc.misc import copy_docstr
except:
	pass

import copy
import math
import os.path

import pygame
import pygame.display
import pygame.draw
import pygame.image

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


class PyGameScreen(BaseScreen):

	"""A class for PyGame Screen objects, for visual stimuli (to be displayed via a Display object)"""
	
	def __init__(self, dispsize=settings.DISPSIZE, fgc=settings.FGC,
		bgc=settings.BGC, mousevisible=settings.MOUSEVISIBLE, screen=None,
		**args):
		
		"""
		Constructor.
	
		TODO: docstring
		"""

		# try to copy docstring (but ignore it if it fails, as we do
		# not need it for actual functioning of the code)
		try:
			copy_docstr(BaseScreen, PyGameScreen)
		except:
			# we're not even going to show a warning, since the copied
			# docstring is useful for code editors; these load the docs
			# in a non-verbose manner, so warning messages would be lost
			pass
		
		self.dispsize = dispsize
		self.fgc = fgc
		self.bgc = bgc
		self.mousevis = mousevisible
		self.create(screen=screen)

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

		pygame.draw.circle(self.screen, colour, (int(pos[0]),int(pos[1])), int(r), int(pw))
		

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

		pygame.draw.ellipse(self.screen, colour, [int(x),int(y),int(w),int(h)], int(pw))

		
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

		pygame.draw.rect(self.screen, colour, [int(x),int(y),int(w),int(h)], int(pw))

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

		pygame.draw.line(self.screen, colour, (int(spos[0]),int(spos[1])), (int(epos[0]),int(epos[1])), int(pw))


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
		
		for i in range(len(pointlist)):
			pointlist[i] = [int(pointlist[i][0]),int(pointlist[i][1])]

		pygame.draw.polygon(self.screen, colour, pointlist, int(pw))


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
			raise Exception("Error in libscreen.Screen.draw_fixation: fixtype %s not recognized; fixtype should be one of 'cross','x','dot'" % fixtype)
		if colour == None:
			colour = self.fgc
		if pos == None:
			pos = (self.dispsize[0]/2, self.dispsize[1]/2)
		
		pos = [int(pos[0]),int(pos[1])]
		r = int(diameter/2)
		pw = int(pw)

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
		if not os.path.isfile(fontname):
			print("WARNING: screen.Screen: could not find font '%s'; using default instead" % fontname)
			font = pygame.font.get_default_font()
		if os.path.isfile(fontname):			
			font = pygame.font.Font(fontname, fontsize)
		else:
			font = pygame.font.SysFont(font, fontsize)
		
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
			self.screen.blit(txtsurf, (int(linepos[0]),int(linepos[1])))
	
	
	def draw_image(self, image, pos=None, scale=None):
		
		"""Draws an image on the screen
		
		arguments
		image		--	a full path to an image file, or a pygame Surface
					(if image is neither of these, this function will
					attempt to treat the image as a PIL Image)
		
		keyword arguments
		pos		--	image center position, an (x,y) position tuple or
					None for a central position (default = None)
		scale		--	scale factor for the image or None for no scaling
					(default = None)
		
		returns
		Nothing	--	loads and draws an image surface on (PyGame) or
					adds SimpleImageStim to (PsychoPy) the self.screen
					property
		"""
		
		if pos == None:
			pos = (self.dispsize[0]/2, self.dispsize[1]/2)
		
		# check if image is a path name
		if type(image) == str:
			# check if the image file exists
			if os.path.isfile(image):
				# load image from file
				try:
					img = pygame.image.load(image)
				except:
					raise Exception("Error in libscreen.PyGameScreen.draw_image: could not load image file %s" % image)
			else:
				raise Exception("Error in libscreen.PyGameScreen.draw_image: path %s is not a file!" % image)
		
		# check if image is a PyGame Surface
		elif type(image) == pygame.Surface:
			# since image is already a PyGame Surface, we needn't do anything with it
			img = image
		# finally, try if the image is supported by PIL
		else:
			try:
				# PIL Image to PyGame Surface
				img = pygame.image.fromstring(image.tostring(), (image.size[0],image.size[1]), 'RGB', False)
			except:
				raise Exception("Error in libscreen.PyGameScreen.draw_image: image format not recognized!")
		
		if scale != None:
			img = pygame.transform.scale(img, (int(img.get_width()*scale), int(img.get_height()*scale)))
		
		imgpos = (int(pos[0] - img.get_width()/2), int(pos[1] - img.get_height()/2))
		
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

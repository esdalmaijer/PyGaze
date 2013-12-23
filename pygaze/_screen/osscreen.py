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

from libopensesame.exceptions import osexception
from openexp.canvas import canvas
from pygaze.defaults import osexperiment
try:
	from constants import osexperiment
except:
	pass

from pygaze._screen.basescreen import BaseScreen
# we try importing the copy_docstr function, but as we do not really need it
# for a proper functioning of the code, we simply ignore it when it fails to
# be imported correctly
try:
	from pygaze._misc.misc import copy_docstr
except:
	pass

	
class OSScreen(BaseScreen):

	"""See _display.pygamescreen.PyGameScreen"""
	
	def __init__(self, screen=None, **args):
		
		"""See _display.pygamescreen.PyGameScreen"""

		# try to copy docstring (but ignore it if it fails, as we do
		# not need it for actual functioning of the code)
		try:
			copy_docstr(BaseScreen, OSScreen)
		except:
			# we're not even going to show a warning, since the copied
			# docstring is useful for code editors; these load the docs
			# in a non-verbose manner, so warning messages would be lost
			pass

		self.experiment = osexperiment
		self.create(screen=screen)

	def create(self, screen=None):
		
		"""See _display.pygamescreen.PyGameScreen"""

		if screen != None:
			self.canvas = screen.copy()
		else:
			self.canvas = canvas(self.experiment)

	def clear(self, colour=None):

		"""See _display.pygamescreen.PyGameScreen"""

		self.canvas.clear()

	def copy(self, screen):

		"""See _display.pygamescreen.PyGameScreen"""

		self.canvas = screen.copy()

	def draw_circle(self, colour=None, pos=None, r=50, pw=1, fill=False):

		"""See _display.pygamescreen.PyGameScreen"""
		
		if pos == None:
			x = self.canvas.xcenter()
			y = self.canvas.ycenter()
		else:
			x, y = pos
		self.canvas.set_penwidth(pw)
		self.canvas.circle(x, y, r, fill=fill, color=colour)

	def draw_ellipse(self, colour=None, x=None, y=None, w=50, h=50, pw=1, \
		fill=False):

		"""See _display.pygamescreen.PyGameScreen"""

		if x == None:
			x = self.canvas.xcenter()
		if y == None:
			y = self.canvas.ycenter()
		self.canvas.set_penwidth(pw)
		self.canvas.ellipse(x, y, w, h, fill=fill, color=colour)

	def draw_rect(self, colour=None, x=None, y=None, w=50, h=50, pw=1, \
		fill=False):
		
		"""See _display.pygamescreen.PyGameScreen"""

		if x == None:
			x = self.canvas.xcenter()
		if y == None:
			y = self.canvas.ycenter()
		self.canvas.set_penwidth(pw)
		self.canvas.rect(x, y, w, h, fill=fill, color=colour)

	def draw_line(self, colour=None, spos=None, epos=None, pw=1):

		"""See _display.pygamescreen.PyGameScreen"""

		if spos == None:
			sx = self.canvas.xcenter() * .5
			sy = self.canvas.ycenter()
		else:
			sx, sy = spos
		if epos == None:
			ex = self.canvas.xcenter() * 1.5
			ey = self.canvas.ycenter()
		else:
			ex, ey = epos
		self.canvas.set_penwidth(pw)
		self.canvas.rect(sx, sy, ex, ey, color=colour)

	def draw_polygon(self, pointlist, colour=None, pw=1, fill=True):

		"""See _display.pygamescreen.PyGameScreen"""

		self.canvas.set_penwidth(pw)
		self.canvas.polygon(pointlist, fill=fill, color=colour)


	def draw_fixation(self, fixtype='cross', colour=None, pos=None, pw=1, \
		diameter=12):

		"""See _display.pygamescreen.PyGameScreen"""

		# TODO: Respect the fixtype argument
		if pos == None:
			x = self.canvas.xcenter()
			y = self.canvas.ycenter()
		else:
			x, y = pos
		self.canvas.fixdot(x, y, color=colour)

	def draw_text(self, text='text', colour=None, pos=None, center=True, \
		font='mono', fontsize=12, antialias=True):

		"""See _display.pygamescreen.PyGameScreen"""

		if pos == None:
			x = self.canvas.xcenter()
			y = self.canvas.ycenter()
		else:
			x, y = pos
		self.canvas.set_font(style=font, size=fontsize)
		self.canvas.text(text, center=center, color=colour, x=x, y=y, \
			html=False)
	
	def draw_image(self, image, pos=None, scale=None):
		
		"""See _display.pygamescreen.PyGameScreen"""
		
		if pos == None:
			x = self.canvas.xcenter()
			y = self.canvas.ycenter()
		else:
			x, y = pos
		self.canvas.image(image, x=x, y=y, scale=scale)

	def set_background_colour(self, colour=None):

		"""See _display.pygamescreen.PyGameScreen"""

		if colour != None:
			self.canvas.set_bgcolor(colour)

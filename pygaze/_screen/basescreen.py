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

# The BaseClasses are meant to store the documentation on all methods of a
# class, but not to contain any functionality whatsoever. BaseClass is
# inherited by all of the subclasses, and the documentation is copied using
# pygaze.copy_docstr. If you intend to make your own subclass for the current
# baseclass, be sure to inherit BaseClass, copy the documentation, and
# redefine the methods as you see fit, e.g.:
#
#import pygaze
#from pygaze._display.basedisplay import BaseDisplay
#
#class DummyDisplay(BaseDisplay):
#	
#	"""An example child of BaseDisplay"""
#	
#	def __init__(self, *args, **kwargs):
#		
#		"""Initializes a DummyDisplay instance"""
#		
#		pygaze.copy_docstring(BaseDisplay,DummyDisplay)
#	
#	def show(self):
#		
#		# note that here no docstring is provided, as it is copied from
#		# the parent class
#		
#		print("Display.show call at %d" % int(clock.get_time()))
#


class BaseScreen:

	"""A class for PyGame Screen objects, for visual stimuli (to be displayed via a Display object)"""
	
	def __init__(self):
		
		"""
		Initializes a Screen instance
		
		arguments
		
		None
		
		keyword arguments
		
		dispsize	--	a (width, height) tuple indicating the display
					resolution (default = DISPSIZE)
		fgc		--	foreground colour: a RGB tuple, e.g. (255,0,0)
					for red or (0,0,0) for black (default = FGC)
		bgc		--	background colour: a RGB tuple, e.g. (255,0,0)
					for red or (0,0,0) for black (default = BGC)
		mousevisible	--	Boolean indicating if the mouse should be
						visible or not (default = MOUSEVISIBLE)
						WARNING: DEPRECATED
		screen	--	a pygaze.screen.Screen instance that is to be
					copied onto the current screen
		"""
		
		pass


	def create(self):

		"""
		Creates a new Screen instance, filled with either the background
		colour or specified screen (this method is sort of a secondary
		constructor and intended for internal use; calling it will reset
		the Screen)
		
		arguments
		
		None
		
		keyword arguments

		screen	--	a screen.Screen instance, to be displayed on the
					new Screen or None for the background colour
		
		returns

		None		--	sets the self.screen property to a PyGame Surface
					or a list of PsychoPy stimuli, depening on the
					disptype
		"""

		pass


	def clear(self):

		"""
		Clears the screen and fills it with a colour
		
		arguments

		None
		
		keyword arguments

		colour	--	drawing colour colour: a RGB tuple, e.g. (255,0,0)
					for red or (0,0,0) for black; or None for the
					default foreground colour, self.fgc (default = None)
		
		returns

		None		--	clears self.screen property
		"""

		pass


	def copy(self):

		"""
		Copies a screen to the current screen
		
		arguments

		screen	--	a screen.Screen instance
		
		keyword arguments
		
		None
		
		returns

		None		--	sets the self.screen property to a copy of
					screen.screen
		"""

		pass
			

	def draw_circle(self):

		"""
		Draws a circle on the Screen
		
		arguments

		None
		
		keyword arguments

		colour	--	drawing colour colour: a RGB tuple, e.g. (255,0,0)
					for red or (0,0,0) for black; or None for the
					default foreground colour, self.fgc (default = None)
		pos		--	circle center, a (x,y) position tuple or None for a
					central position (default = None)
		r		--	circle radius (default = 50)
		pw		--	penwidth: line thickness (default = 1)
		fill		--	Boolean indicating whether stimulus should be
					filled or not (default = False)
		
		returns
		
		None		--	draws a circle on the Screen
		"""

		pass
		

	def draw_ellipse(self):

		"""
		Draws an ellipse on the Screen
		
		arguments

		None
		
		keyword arguments

		colour	--	drawing colour colour: a RGB tuple, e.g. (255,0,0)
					for red or (0,0,0) for black; or None for the
					default foreground colour, self.fgc (default = None)
		x		--	x coordinate of the rectangle in which the ellipse is
					drawn or None for a horizontal centrally drawn
					ellipse (default = None)
		y		--	y coordinate of the rectangle in which the ellipse is
					drawn or None for a vertical centrally drawn
					ellipse (default = None)
		w		--	width of the rectangle in which the ellipse is drawn
					(default = 50)
		h		--	height of the rectangle in which the ellipse is drawn
					(default = 50)
		pw		--	penwidth: line thickness (default = 1)
		fill		--	Boolean indicating whether stimulus should be
					filled or not (default = False)
		
		returns
		
		None		--	draws an ellipse on the Screen
		"""

		pass

		
	def draw_rect(self):

		"""
		Draws a rectangle on the Screen
		
		arguments

		None
		
		keyword arguments

		colour	--	drawing colour colour: a RGB tuple, e.g. (255,0,0)
					for red or (0,0,0) for black; or None for the
					default foreground colour, self.fgc (default = None)
		x		--	x coordinate of the rectangle or None for a
					horizontal centrally drawn rectangle (default = None)
		y		--	y coordinate of the rectangle or None for a
					vertical centrally drawn rectangle (default = None)
		w		--	width of the rectangle (default = 50)
		h		--	height of the rectangle (default = 50)
		pw		--	penwidth: line thickness (default = 1)
		fill		--	Boolean indicating whether stimulus should be
					filled or not (default = False)
		
		returns

		None		-- draws a rectangle on the Screen
		"""

		pass


	def draw_line(self):

		"""
		Draws a line on the Screen
		
		arguments

		None
		
		keyword arguments

		colour	--	drawing colour colour: a RGB tuple, e.g. (255,0,0)
					for red or (0,0,0) for black; or None for the
					default foreground colour, self.fgc (default = None)
		spos		--	line start, a (x,y) position tuple or None for a
					quarter x and a central y position (default = None)
		epos		--	line end, a	 (x,y) position tuple or None for a
					three-quarter x and a central y position (default =
					None)
		pw		--	penwidth: line thickness (default = 1)
		
		returns

		None		-- draws a line on the Screen
		"""

		pass


	def draw_polygon(self):

		"""
		Draws a polygon on the Screen
		
		arguments

		pointlist	--	a list of (x,y) tuples resembling the cornerpoints
					of the polygon
		
		keyword arguments

		colour	--	drawing colour colour: a RGB tuple, e.g. (255,0,0)
					for red or (0,0,0) for black; or None for the
					default foreground colour, self.fgc (default = None)
		pw		--	penwidth: line thickness (default = 1)
		fill		--	Boolean indicating whether stimulus should be
					filled or not (default = False)
		
		returns

		None		--	draws a polygon on the Screen
		"""

		pass


	def draw_fixation(self):

		"""
		Draws a fixation target (cross, x or dot) on the Screen
		
		arguments
		
		None
		
		keyword arguments

		fixtype	--	type of fixation mark, should be either of the
					following strings:
						'cross'	-- a '+'
						'x'		-- a 'x'
						'dot'		-- a filled circle
					(default = 'cross')
		colour	--	drawing colour colour: a RGB tuple, e.g. (255,0,0)
					for red or (0,0,0) for black; or None for the
					default foreground colour, self.fgc (default = None)
		pos		--	fixation center, a (x,y) position tuple or None for
					a central position (default = None)
		pw		--	penwidth: line thickness (default = 1)
		diameter	--	diameter of the fixation mark in pixels (default = 12)
		
		returns

		None		-- draws a fixation target on the Screen
		"""

		pass


	def draw_text(self):

		"""
		Draws a text on the Screen
		
		arguments

		None
		
		keyword arguments

		text		--	string to be displayed (newlines are allowed and
					will be recognized) (default = 'text')
		colour	--	drawing colour colour: a RGB tuple, e.g. (255,0,0)
					for red or (0,0,0) for black; or None for the
					default foreground colour, self.fgc (default = None)
		pos		--	text position, a (x,y) position tuple or None for a
					central position (default = None)
		center	--	Boolean indicating is the pos keyword argument should
					indicate the text center (True) or the top left
					coordinate (False) (default = True)
		font		--	font name (a string value); should be the name of a
					font included in the PyGaze resources/fonts directory
					(default = 'mono')
		fontsize	--	fontsize in pixels (an integer value) (default = 12)
		antialias	--	Boolean indicating whether text should be antialiased
					or not (default = True)
		
		returns

		None		--	renders and draws text on the Screen
		"""

		pass
	
	
	def draw_image(self):
		
		"""
		Draws an image on the Screen
		
		arguments

		image		--	a full path to an image file, a PIL Image, or a
					pygame Surface (pygame Surface only recognized if
					disptype == 'pygame'); NOTE: if image is neither of
					these, this function will attempt to treat the
					image as a PIL Image, and will raise an Exception
					if this fails
		
		keyword arguments

		pos		--	image center position, an (x,y) position tuple or
					None for a central position (default = None)
		scale		--	scale factor for the image or None for no scaling
					(default = None)
		
		returns

		None		--	loads and draws an image on the Screen
		"""
		
		pass


	def set_background_colour(self):

		"""
		Set the background colour
		
		arguments
		
		None
		
		keyword arguments

		colour	--	intended colour: a RGB tuple, e.g. (255,0,0)
					for red or (0,0,0) for black; or None for the
					default foreground colour, self.fgc (default = None)
		
		returns

		None		--	sets bgc property to specified colour
		"""

		pass

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


class GazeCursor:
	
	"""Gaze contingent cursor"""

	def __init__(self, disptype='', ctype='cross', size=20, colour=(200,100,100), pw=3, fill=True):

		"""Initializes cursor object
		
		arguments
		None
		
		keyword arguments
		disptype	--	string indicating which display type is used;
					DEPRECATED: disptype is ignored (default = '')
		ctype		--	string indicating the cursor type; should be one of
					the following: 'rectangle', 'ellipse', 'plus',
					'cross' or 'arrow' (default = 'cross')
		size		--	cursor size in pixels (default = 20)
		colour		--	colour for the cursor (a RGB tuple, e.g. (255,0,0))
					(default = (0,0,0))
		pw		--	cursor line thickness in pixels (default = 3)
		fill		--	Boolean indicating if cursor should be filled or not;
					only applies for cursortypes with a body, e.g.
					'rectangle' (default = True)
		"""

		# cursor characteristics
		if ctype in ['rectangle', 'ellipse', 'plus', 'cross', 'arrow']:
			self.ctype = ctype
		else:
			self.ctype = 'arrow'
			print("WARNING! plugins.gazecursor.__init__: GazeCursor type could not be recognized; Cursor type set to 'arrow'")
			
		self.fill = fill
		self.pw = pw
		
		if type(size) in [int,float]:
			self.size = (int(size), int(size))
		elif type(size) == tuple or type(size) == list:
			if len(size) == 2:
				self.size = map(int, size)
			else:
				self.size = (int(size[0]), int(size[1]))
				print("WARNING! plugins.gazecursor.__init__: too many entries for cursor size; only the first two are used")
			
		if type(colour) == tuple or type(colour) == list:
			if len(colour) <= 4:
				self.colour = colour
			else:
				self.colour = colour[:4]
				print("WARNING! plugins.gazecursor.__init__: too many list entries for cursor colour; only the first four are used")
		else:
			raise Exception("Error in plugins.gazecursor: colour argument '%s' not recognized, please use a RGB tuple (e.g. (255,0,0) for 'red')" % colour)


	def update(self, screen, gazepos):

		"""Adds the cursor to specified screen; does NOT directly update
		the display
		
		arguments
		screen	--	a libscreen.Screen instance
		gazepos	--	current gaze position (a (x,y) tuple)
		
		returns
		screen	--	same Screen as was used as an input, but with the
				addition of a cursor at the gaze position
		"""

		# draw cursor
		if self.ctype == 'rectangle':
			screen.draw_rect(colour=self.colour, x=gazepos[0]-(self.size[0]/2), y=gazepos[1]-(self.size[1]/2), w=self.size[0], h=self.size[1], pw=self.pw, fill=self.fill)
		if self.ctype == 'ellipse':
			screen.draw_ellipse(colour=self.colour, x=gazepos[0]-(self.size[0]/2), y=gazepos[1]-(self.size[1]/2), w=self.size[0], h=self.size[1], pw=self.pw, fill=self.fill)
		if self.ctype == 'plus':
			screen.draw_fixation(fixtype='cross', colour=self.colour, pos=gazepos, pw=self.pw, diameter=self.size)
		if self.ctype == 'cross':
			screen.draw_fixation(fixtype='x', colour=self.colour, pos=gazepos, pw=self.pw, diameter=self.size)
		if self.ctype == 'arrow':
			screen.draw_polygon([(gazepos[0]+self.size[0],gazepos[1]+(0.5*self.size[1])),(gazepos[0],gazepos[1]),(gazepos[0]+(0.5*self.size[0]),gazepos[1]+self.size[1])], colour=self.colour, pw=self.pw, fill=self.fill)
			screen.draw_line(colour=self.colour, spos=(gazepos[0],gazepos[1]), epos=(gazepos[0]+self.size[0],gazepos[1]+self.size[1]), pw=self.pw)

		return screen


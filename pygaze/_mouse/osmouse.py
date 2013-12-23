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
from openexp.mouse import mouse
from pygaze.defaults import *
try:
	from constants import *
except:
	pass

class OSMouse:

	"""See _mouse.pygamemouse.PyGameMouse"""

	def __init__(self, mousebuttonlist=MOUSEBUTTONLIST, timeout=MOUSETIMEOUT, \
		visible=False):

		"""See _mouse.pygamemouse.PyGameMouse"""
		
		self.experiment = osexperiment
		self.mouse = mouse(self.experiment, buttonlist=mousebuttonlist, \
			timeout=timeout)

	def set_mousebuttonlist(self, mousebuttonlist=None):

		"""See _mouse.pygamemouse.PyGameMouse"""
		
		self.mouse.set_buttonlist(mousebuttonlist)

	def set_timeout(self, timeout=None):

		"""See _mouse.pygamemouse.PyGameMouse"""
		
		self.mouse.set_timeout(timeout)

	def set_visible(self, visible=True):

		"""See _mouse.pygamemouse.PyGameMouse"""
		
		self.mouse.set_visible(visible)

	def set_pos(self, pos=(0,0)):

		"""See _mouse.pygamemouse.PyGameMouse"""
		
		self.mouse.set_pos(pos)

	def get_pos(self):
		
		"""See _mouse.pygamemouse.PyGameMouse"""
		
		return self.mouse.get_pos()[0]

	def get_clicked(self, mousebuttonlist='default', timeout='default'):

		"""See _mouse.pygamemouse.PyGameMouse"""

		# set buttonlist and timeout
		if mousebuttonlist == 'default':
			mousebuttonlist = None
		if timeout == 'default':
			timeout = None
		return self.mouse.get_click(buttonlist=mousebuttonlist, timeout=timeout)

	def get_pressed(self):

		"""See _mouse.pygamemouse.PyGameMouse"""

		return self.mouse.get_pressed()

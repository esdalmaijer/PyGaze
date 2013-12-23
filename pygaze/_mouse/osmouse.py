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

from pygaze._mouse.basemouse import BaseMouse
# we try importing the copy_docstr function, but as we do not really need it
# for a proper functioning of the code, we simply ignore it when it fails to
# be imported correctly
try:
	from pygaze._misc.misc import copy_docstr
except:
	pass


class OSMouse(BaseMouse):

	# See _mouse.basemouse.BaseMouse

	def __init__(self, mousebuttonlist=MOUSEBUTTONLIST, timeout=MOUSETIMEOUT, \
		visible=False):

		# See _mouse.basemouse.BaseMouse

		# try to copy docstring (but ignore it if it fails, as we do
		# not need it for actual functioning of the code)
		try:
			copy_docstr(BaseMouse, OSMouse)
		except:
			# we're not even going to show a warning, since the copied
			# docstring is useful for code editors; these load the docs
			# in a non-verbose manner, so warning messages would be lost
			pass
		
		self.experiment = osexperiment
		self.mouse = mouse(self.experiment, buttonlist=mousebuttonlist, \
			timeout=timeout)

	def set_mousebuttonlist(self, mousebuttonlist=None):

		# See _mouse.basemouse.BaseMouse
		
		self.mouse.set_buttonlist(mousebuttonlist)

	def set_timeout(self, timeout=None):

		# See _mouse.basemouse.BaseMouse
		
		self.mouse.set_timeout(timeout)

	def set_visible(self, visible=True):

		# See _mouse.basemouse.BaseMouse
		
		self.mouse.set_visible(visible)

	def set_pos(self, pos=(0,0)):

		# See _mouse.basemouse.BaseMouse
		
		self.mouse.set_pos(pos)

	def get_pos(self):
		
		# See _mouse.basemouse.BaseMouse
		
		return self.mouse.get_pos()[0]

	def get_clicked(self, mousebuttonlist='default', timeout='default'):

		# See _mouse.basemouse.BaseMouse

		# set buttonlist and timeout
		if mousebuttonlist == 'default':
			mousebuttonlist = None
		if timeout == 'default':
			timeout = None
		return self.mouse.get_click(buttonlist=mousebuttonlist, timeout=timeout)

	def get_pressed(self):

		# See _mouse.basemouse.BaseMouse

		return self.mouse.get_pressed()

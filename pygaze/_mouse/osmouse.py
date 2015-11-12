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

from pygaze.py3compat import *
from pygaze import settings
from libopensesame.exceptions import osexception
from openexp.mouse import mouse
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

	def __init__(self, mousebuttonlist=settings.MOUSEBUTTONLIST,
		timeout=settings.MOUSETIMEOUT, visible=False):

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

		self.experiment = settings.osexperiment
		self.uniform_coordinates = \
			self.experiment.var.uniform_coordinates == u'yes'
		self.mouse = mouse(self.experiment, buttonlist=mousebuttonlist,
			timeout=timeout)

	def _from_pos(self, pos):

		"""Convert OpenSesame coordinates to PyGaze coordinates."""

		if not self.uniform_coordinates:
			return pos
		return pos[0]+self.mouse._xcenter, pos[1]+self.mouse._ycenter

	def _to_pos(self, pos):

		"""Convert PyGaze coordinates to OpenSesame coordinates."""

		if not self.uniform_coordinates:
			return pos
		return pos[0]-self.mouse._xcenter, pos[1]-self.mouse._ycenter

	def set_mousebuttonlist(self, mousebuttonlist=None):

		# See _mouse.basemouse.BaseMouse

		self.mouse.buttonlist = mousebuttonlist

	def set_timeout(self, timeout=None):

		# See _mouse.basemouse.BaseMouse

		self.mouse.timeout = timeout

	def set_visible(self, visible=True):

		# See _mouse.basemouse.BaseMouse

		self.mouse.show_cursor(visible)

	def set_pos(self, pos=(0,0)):

		# See _mouse.basemouse.BaseMouse

		self.mouse.set_pos(self._to_pos(pos))

	def get_pos(self):

		# See _mouse.basemouse.BaseMouse

		return self._from_pos(self.mouse.get_pos()[0])

	def get_clicked(self, mousebuttonlist=u'default', timeout=u'default'):

		# See _mouse.basemouse.BaseMouse

		# set buttonlist and timeout
		kwdict = {}
		if mousebuttonlist != u'default':
			kwdict[u'buttonlist'] = mousebuttonlist
		if timeout != u'default':
			kwdict[u'buttonlist'] = timeout
		button, pos, t = self.mouse.get_click(**kwdict)
		return button, self._from_pos(pos), t

	def get_pressed(self):

		# See _mouse.basemouse.BaseMouse

		return self.mouse.get_pressed()

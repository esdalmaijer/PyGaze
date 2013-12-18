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

class OSDisplay:

	"""See _display.pygamedisplay.PyGameDisplay"""

	def __init__(self, **args):

		"""See _display.pygamedisplay.PyGameDisplay"""

		self.experiment = osexperiment
		self.canvas = canvas(self.experiment)

	def show(self):

		"""See _display.pygamedisplay.PyGameDisplay"""

		return self.canvas.show()

	def show_part(self, rect, screen=None):

		"""See _display.pygamedisplay.PyGameDisplay"""

		return self.canvas.show()

	def fill(self, screen=None):

		"""See _display.pygamedisplay.PyGameDisplay"""

		self.canvas = screen.canvas

	def close(self):

		"""See _display.pygamedisplay.PyGameDisplay"""

		pass

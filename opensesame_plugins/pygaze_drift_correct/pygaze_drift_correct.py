#-*- coding:utf-8 -*-

"""
This file is part of PyGaze.

PyGaze is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

PyGaze is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with PyGaze.  If not, see <http://www.gnu.org/licenses/>.
"""

from libopensesame.item import item
from libqtopensesame.items.qtautoplugin import qtautoplugin
from pygaze import EyeTracker, Display

class pygaze_drift_correct(item):
	
	"""Plug-in runtime definition."""

	description = u'Perform eye-tracker drift correction'

	def __init__(self, name, experiment, script=None):

		"""
		Constructor.
		
		Arguments:
		name		--	The name of the plug-in.
		experiment	--	The experiment object.
		
		Keyword arguments:
		script		--	A definition script. (default=None)
		"""

		self.xpos = 0
		self.ypos = 0
		self.fixation_triggered = u'no'
		item.__init__(self, name, experiment, script)

	def prepare(self):

		"""The preparation phase of the plug-in goes here."""

		item.prepare(self)

	def run(self):

		"""The run phase of the plug-in goes here."""

		self.set_item_onset()
		xpos = self.get(u'width') / 2 + self.get(u'xpos')
		ypos = self.get(u'height') / 2 + self.get(u'ypos')
		self.experiment.pygaze_eyetracker.drift_correction(pos=(xpos, ypos), \
			fix_triggered=self.get(u'fixation_triggered') == u'yes')

class qtpygaze_drift_correct(pygaze_drift_correct, qtautoplugin):
	
	"""Plug-in GUI definition."""
	
	def __init__(self, name, experiment, script=None):
		
		"""
		Constructor.
		
		Arguments:
		name		--	The name of the plug-in.
		experiment	--	The experiment object.
		
		Keyword arguments:
		script		--	A definition script. (default=None)
		"""

		pygaze_drift_correct.__init__(self, name, experiment, script)
		qtautoplugin.__init__(self, __file__)


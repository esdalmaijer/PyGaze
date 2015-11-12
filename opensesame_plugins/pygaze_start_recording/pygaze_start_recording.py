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
from pygaze.display import Display

class pygaze_start_recording(item):
	
	"""Plug-in runtime definition."""

	description = u'Puts the eye tracker into recording mode'

	def reset(self):

		"""
		desc:
			Resets plug-in settings.
		"""

		self.var.status_msg = u'start_trial'
	
	def run(self):

		"""The run phase of the plug-in goes here."""

		self.set_item_onset()
		self.experiment.pygaze_eyetracker.start_recording()
		self.experiment.pygaze_eyetracker.status_msg(self.var.status_msg)
		self.experiment.pygaze_eyetracker.log(self.var.status_msg)

class qtpygaze_start_recording(pygaze_start_recording, qtautoplugin):
	
	def __init__(self, name, experiment, script=None):
		
		pygaze_start_recording.__init__(self, name, experiment, script)
		qtautoplugin.__init__(self, __file__)

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
from libopensesame.exceptions import osexception
from libqtopensesame.items.qtautoplugin import qtautoplugin
from pygaze.display import Display

class pygaze_wait(item):
	
	"""Plug-in runtime definition."""

	description = u'Waits for an eye-tracker event'

	def reset(self):

		"""
		desc:
			Resets plug-in settings.
		"""
		
		self.var.event = u'Saccade start'

	def prepare(self):

		"""The preparation phase of the plug-in goes here."""

		item.prepare(self)
		if self.var.event == u'Saccade start':
			self.wait_func = self.experiment.pygaze_eyetracker. \
				wait_for_saccade_start
		elif self.var.event == u'Saccade end':
			self.wait_func = self.experiment.pygaze_eyetracker. \
				wait_for_saccade_end
		elif self.var.event == u'Fixation start':
			self.wait_func = self.experiment.pygaze_eyetracker. \
				wait_for_fixation_start
		elif self.var.event == u'Fixation end':
			self.wait_func = self.experiment.pygaze_eyetracker. \
				wait_for_fixation_end
		elif self.var.event == u'Blink start':
			self.wait_func = self.experiment.pygaze_eyetracker. \
				wait_for_blink_start
		elif self.var.event == u'Blink end':
			self.wait_func = self.experiment.pygaze_eyetracker. \
				wait_for_blink_start
		else:
			raise osexception(u'Unknown event: %s' % self.var.event)
		
	def run(self):

		"""The run phase of the plug-in goes here."""

		self.wait_func()
		self.set_item_onset()

class qtpygaze_wait(pygaze_wait, qtautoplugin):
	
	def __init__(self, name, experiment, script=None):
		
		pygaze_wait.__init__(self, name, experiment, script)
		qtautoplugin.__init__(self, __file__)

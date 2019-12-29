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

import inspect
from openexp.canvas import canvas
from libopensesame.item import item
from libqtopensesame.items.qtautoplugin import qtautoplugin
from pygaze.display import Display

class pygaze_drift_correct(item):

	"""Plug-in runtime definition."""

	description = u'Perform eye-tracker drift correction'

	def reset(self):

		"""
		desc:
			Resets plug-in settings.
		"""

		self.var.xpos = 0
		self.var.ypos = 0
		self.var.fixation_triggered = u'no'
		self.var.target_color = u'[foreground]'
		self.var.target_style = u'default'
		self.var.draw_target = u'yes'

	def prepare_drift_correction_canvas(self):

		"""A hook to prepare the canvas with the drift-correction target."""

		if self.var.draw_target == u'yes':
			self.dc_canvas = canvas(self.experiment)
			self.dc_canvas.fixdot(self.var.xpos, self.var.ypos,
				color=self.var.target_color, style=self.var.target_style)
		else:
			self.dc_canvas = None

	def draw_drift_correction_canvas(self, x, y):

		"""
		A hook to show the canvas with the drift-correction target.

		Arguments:
		x	--	The X coordinate (unused).
		y	--	The Y coordinate (unused).
		"""

		if self.dc_canvas is not None:
			self.dc_canvas.show()

	def prepare(self):

		"""The preparation phase of the plug-in goes here."""

		item.prepare(self)
		self.prepare_drift_correction_canvas()
		self.experiment.pygaze_eyetracker.set_draw_drift_correction_target_func(
			self.draw_drift_correction_canvas)

	def run(self):

		"""The run phase of the plug-in goes here."""

		self.set_item_onset()
		if self.var.uniform_coordinates == u'yes':
			xpos = self.var.width / 2 + self.var.xpos
			ypos = self.var.height / 2 + self.var.ypos
		else:
			xpos = self.var.xpos
			ypos = self.var.ypos
		while True:
			success = self.experiment.pygaze_eyetracker.drift_correction(
				pos=(xpos, ypos),
				fix_triggered=self.var.fixation_triggered==u'yes')
			if success:
				break

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

	def init_edit_widget(self):

		qtautoplugin.init_edit_widget(self)
		self.custom_interactions()

	def apply_edit_changes(self):

		"""Apply the controls"""

		if not qtautoplugin.apply_edit_changes(self) or self.lock:
			return False
		self.custom_interactions()

	def custom_interactions(self):

		"""
		Disables the target-style combobox if no target display should be drawn.
		"""

		draw_target = self.var.draw_target == u'yes'
		self.combobox_target_style.setEnabled(draw_target)
		self.line_edit_target_color.setEnabled(draw_target)

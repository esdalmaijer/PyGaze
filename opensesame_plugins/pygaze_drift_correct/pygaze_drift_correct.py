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
		self.target_color = u'[foreground]'
		self.target_style = u'default'
		self.draw_target = u'yes'
		item.__init__(self, name, experiment, script)
		
	def prepare_drift_correction_canvas(self):
		
		"""A hook to prepare the canvas with the drift-correction target."""
		
		if self.get(u'draw_target') == u'yes':
			self.dc_canvas = canvas(self.experiment)
			x = self.get(u'xpos') + self.dc_canvas.xcenter()
			y = self.get(u'ypos') + self.dc_canvas.ycenter()
			if u'style' in inspect.getargspec(self.dc_canvas.fixdot).args:
				self.dc_canvas.fixdot(x, y, color=self.get(u'target_color'), \
					style=self.get(u'target_style'))
			else:
				self.dc_canvas.fixdot(x, y, color=self.get(u'target_color'))
		else:
			self.dc_canvas = None
		
	def draw_drift_correction_canvas(self, x, y):
		
		"""
		A hook to show the canvas with the drift-correction target.
		
		Arguments:
		x	--	The X coordinate (unused).
		y	--	The Y coordinate (unused).
		"""
		
		if self.dc_canvas != None:
			self.dc_canvas.show()

	def prepare(self):

		"""The preparation phase of the plug-in goes here."""

		item.prepare(self)
		self.prepare_drift_correction_canvas()
		self.experiment.pygaze_eyetracker \
			.set_draw_drift_correction_target_func( \
			self.draw_drift_correction_canvas)

	def run(self):

		"""The run phase of the plug-in goes here."""

		self.set_item_onset()
		xpos = self.get(u'width') / 2 + self.get(u'xpos')
		ypos = self.get(u'height') / 2 + self.get(u'ypos')
		while True:
			success = self.experiment.pygaze_eyetracker.drift_correction(
				pos=(xpos, ypos),
				fix_triggered=self.get(u'fixation_triggered') == u'yes')
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
		self.custom_interactions()

	def apply_edit_changes(self):

		"""Apply the controls"""

		if not qtautoplugin.apply_edit_changes(self) or self.lock:
			return False
		self.custom_interactions()
		return True
			
	def custom_interactions(self):
		
		"""
		Disables the target-style combobox if no target display should be drawn.
		"""
		
		draw_target = self.get(u'draw_target') == u'yes'
		self.combobox_target_style.setEnabled(draw_target)
		self.line_edit_target_color.setEnabled(draw_target)

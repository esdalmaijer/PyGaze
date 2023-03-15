"""This file is part of PyGaze.

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
from openexp.canvas import Canvas
from libopensesame.item import Item
from libqtopensesame.items.qtautoplugin import QtAutoPlugin
from pygaze.display import Display


class PygazeDriftCorrect(Item):

    def reset(self):
        self.var.xpos = 0
        self.var.ypos = 0
        self.var.fixation_triggered = u'no'
        self.var.target_color = u'[foreground]'
        self.var.target_style = u'default'
        self.var.draw_target = u'yes'

    def prepare_drift_correction_canvas(self):
        """A hook to prepare the canvas with the drift-correction target."""
        if self.var.draw_target == u'yes':
            self.dc_canvas = Canvas(self.experiment)
            self.dc_canvas.fixdot(
                self.var.xpos, self.var.ypos, color=self.var.target_color,
                style=self.var.target_style)
        else:
            self.dc_canvas = None

    def draw_drift_correction_canvas(self, x, y):
        """A hook to show the canvas with the drift-correction target."""
        if self.dc_canvas is not None:
            self.dc_canvas.show()

    def prepare(self):
        super().prepare()
        self.prepare_drift_correction_canvas()
        self.experiment.pygaze_eyetracker. \
            set_draw_drift_correction_target_func(
                self.draw_drift_correction_canvas)

    def run(self):
        self.set_item_onset()
        xpos = self.var.width / 2 + self.var.xpos
        ypos = self.var.height / 2 + self.var.ypos
        while True:
            success = self.experiment.pygaze_eyetracker.drift_correction(
                pos=(xpos, ypos),
                fix_triggered=self.var.fixation_triggered == 'yes')
            if success:
                break


class QtPygazeDriftCorrect(PygazeDriftCorrect, QtAutoPlugin):

    def __init__(self, name, experiment, script=None):
        PygazeDriftCorrect.__init__(self, name, experiment, script)
        QtAutoPlugin.__init__(self, __file__)

    def init_edit_widget(self):
        super().init_edit_widget()
        self.custom_interactions()

    def apply_edit_changes(self):
        if not super().apply_edit_changes() or self.lock:
            return False
        self.custom_interactions()

    def custom_interactions(self):
        """Disables the target-style combobox if no target display should be
        drawn
        """
        draw_target = self.var.draw_target == u'yes'
        self.combobox_target_style.setEnabled(draw_target)
        self.line_edit_target_color.setEnabled(draw_target)

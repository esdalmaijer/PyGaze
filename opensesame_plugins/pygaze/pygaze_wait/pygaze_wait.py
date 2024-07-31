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

from libopensesame.item import Item
from libopensesame.exceptions import InvalidValue
from pygaze.display import Display


class PygazeWait(Item):
    
    def reset(self):
        self.var.event = 'Saccade start'

    def prepare(self):
        super().prepare()
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
            raise InvalidValue(f'Unknown event: {self.var.event}')
        
    def run(self):
        self.wait_func()
        self.set_item_onset()

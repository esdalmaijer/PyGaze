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
from pygaze.display import Display


class PygazeLog(Item):
    
    def reset(self):
        self.var.msg = ''
        self.var.auto_log = 'no'
        self.var.throttle = 2
    
    def run(self):
        self.set_item_onset()
        for msg in self.var.msg.split(u'\n'):
            self.experiment.pygaze_eyetracker.log(self.syntax.eval_text(msg))
            self.clock.sleep(self.var.throttle)
        if self.var.auto_log == u'yes':
            for logvar, info in self.experiment.var.inspect().items():
                self.experiment.pygaze_eyetracker.log_var(
                    logvar, info[u'value'])
                self.clock.sleep(self.var.throttle)

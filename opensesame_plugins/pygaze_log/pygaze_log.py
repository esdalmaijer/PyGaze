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

class pygaze_log(item):

    """Plug-in runtime definition."""

    description = u'Writes information to the eye-tracker logfile'

    def __init__(self, name, experiment, script=None):

        """
        Constructor.

        Arguments:
        name        --    The name of the plug-in.
        experiment    --    The experiment object.

        Keyword arguments:
        script        --    A definition script. (default=None)
        """

        self.msg = u''
        self.auto_log = u'no'
        self.throttle = 2
        item.__init__(self, name, experiment, script)

    def prepare(self):

        """The preparation phase of the plug-in goes here."""

        item.prepare(self)

    def run(self):

        """The run phase of the plug-in goes here."""

        self.set_item_onset()
        for msg in self.msg.split(u'\n'):
            self.experiment.pygaze_eyetracker.log(self.eval_text(msg))
            self.sleep(self.throttle)
        if self.auto_log == u'yes':
            for logvar, _val, item in self.experiment.var_list():
                val = self.get_check(logvar, default=u'NA')
                self.experiment.pygaze_eyetracker.log_var(logvar, val)
                self.sleep(self.throttle)
        return True

class qtpygaze_log(pygaze_log, qtautoplugin):

    """Plug-in GUI definition."""

    def __init__(self, name, experiment, script=None):

        """
        Constructor.

        Arguments:
        name        --    The name of the plug-in.
        experiment    --    The experiment object.

        Keyword arguments:
        script        --    A definition script. (default=None)
        """

        pygaze_log.__init__(self, name, experiment, script)
        qtautoplugin.__init__(self, __file__)


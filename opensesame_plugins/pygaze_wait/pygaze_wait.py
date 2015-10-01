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

    def __init__(self, name, experiment, script=None):

        """
        Constructor.

        Arguments:
        name        --    The name of the plug-in.
        experiment    --    The experiment object.

        Keyword arguments:
        script        --    A definition script. (default=None)
        """

        self.event = u'Saccade start'
        item.__init__(self, name, experiment, script)

    def prepare(self):

        """The preparation phase of the plug-in goes here."""

        item.prepare(self)
        if self.get(u'event') == u'Saccade start':
            self.wait_func = self.experiment.pygaze_eyetracker. \
                wait_for_saccade_start
        elif self.get(u'event') == u'Saccade end':
            self.wait_func = self.experiment.pygaze_eyetracker. \
                wait_for_saccade_end
        elif self.get(u'event') == u'Fixation start':
            self.wait_func = self.experiment.pygaze_eyetracker. \
                wait_for_fixation_start
        elif self.get(u'event') == u'Fixation end':
            self.wait_func = self.experiment.pygaze_eyetracker. \
                wait_for_fixation_end
        elif self.get(u'event') == u'Blink start':
            self.wait_func = self.experiment.pygaze_eyetracker. \
                wait_for_blink_start
        elif self.get(u'event') == u'Blink end':
            self.wait_func = self.experiment.pygaze_eyetracker. \
                wait_for_blink_start
        else:
            raise osexception(u'Unknown event: %s' % self.get(u'event'))

    def run(self):

        """The run phase of the plug-in goes here."""

        self.wait_func()
        self.set_item_onset()

class qtpygaze_wait(pygaze_wait, qtautoplugin):

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

        pygaze_wait.__init__(self, name, experiment, script)
        qtautoplugin.__init__(self, __file__)


# -*- coding: utf-8 -*-
from libopensesame.exceptions import osexception
from openexp.mouse import mouse
from pygaze.defaults import *
try:
    from constants import *
except Exception:
    pass

from pygaze._mouse.basemouse import BaseMouse
# we try importing the copy_docstr function, but as we do not really need it
# for a proper functioning of the code, we simply ignore it when it fails to
# be imported correctly
try:
    from pygaze._misc.misc import copy_docstr
except Exception:
    pass


class OSMouse(BaseMouse):

    # See _mouse.basemouse.BaseMouse

    def __init__(self, mousebuttonlist=MOUSEBUTTONLIST, timeout=MOUSETIMEOUT, \
        visible=False):

        # See _mouse.basemouse.BaseMouse

        # try to copy docstring (but ignore it if it fails, as we do
        # not need it for actual functioning of the code)
        try:
            copy_docstr(BaseMouse, OSMouse)
        except Exception:
            # we're not even going to show a warning, since the copied
            # docstring is useful for code editors; these load the docs
            # in a non-verbose manner, so warning messages would be lost
            pass

        self.experiment = osexperiment
        self.mouse = mouse(self.experiment, buttonlist=mousebuttonlist, \
            timeout=timeout)

    def set_mousebuttonlist(self, mousebuttonlist=None):

        # See _mouse.basemouse.BaseMouse

        self.mouse.set_buttonlist(mousebuttonlist)

    def set_timeout(self, timeout=None):

        # See _mouse.basemouse.BaseMouse

        self.mouse.set_timeout(timeout)

    def set_visible(self, visible=True):

        # See _mouse.basemouse.BaseMouse

        self.mouse.set_visible(visible)

    def set_pos(self, pos=(0,0)):

        # See _mouse.basemouse.BaseMouse

        self.mouse.set_pos(pos)

    def get_pos(self):

        # See _mouse.basemouse.BaseMouse

        return self.mouse.get_pos()[0]

    def get_clicked(self, mousebuttonlist='default', timeout='default'):

        # See _mouse.basemouse.BaseMouse

        # set buttonlist and timeout
        if mousebuttonlist == 'default':
            mousebuttonlist = None
        if timeout == 'default':
            timeout = None
        return self.mouse.get_click(buttonlist=mousebuttonlist, timeout=timeout)

    def get_pressed(self):

        # See _mouse.basemouse.BaseMouse

        return self.mouse.get_pressed()

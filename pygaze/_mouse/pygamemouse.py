# -*- coding: utf-8 -*-
from pygaze.libtime import clock
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

import pygaze
import pygame

class PyGameMouse(BaseMouse):

    # See _mouse.basemouse.BaseMouse

    import pygame.mouse

    def __init__(self, mousebuttonlist=MOUSEBUTTONLIST, timeout=MOUSETIMEOUT, visible=False):

        # See _mouse.basemouse.BaseMouse

        # try to copy docstring (but ignore it if it fails, as we do
        # not need it for actual functioning of the code)
        try:
            copy_docstr(BaseMouse, PyGameMouse)
        except Exception:
            # we're not even going to show a warning, since the copied
            # docstring is useful for code editors; these load the docs
            # in a non-verbose manner, so warning messages would be lost
            pass

        # set mouse characteristics
        self.set_mousebuttonlist(mousebuttonlist)
        self.set_timeout(timeout)
        self.set_visible(visible=visible)


    def set_mousebuttonlist(self, mousebuttonlist=None):

        # See _mouse.basemouse.BaseMouse

        if mousebuttonlist == None or mousebuttonlist == []:
            self.mbuttonlist = None
        else:
            self.mbuttonlist = []
            for mbutton in mousebuttonlist:
                self.mbuttonlist.append(mbutton)


    def set_timeout(self, timeout=None):

        # See _mouse.basemouse.BaseMouse

        self.timeout = timeout


    def set_visible(self, visible=True):

        # See _mouse.basemouse.BaseMouse

        self.visible = visible
        pygame.mouse.set_visible(visible)


    def set_pos(self, pos=(0,0)):

        # See _mouse.basemouse.BaseMouse

        pygame.mouse.set_pos(pos)


    def get_pos(self):

        # See _mouse.basemouse.BaseMouse

        mpos = pygame.mouse.get_pos()

        return mpos


    def get_clicked(self, mousebuttonlist='default', timeout='default'):

        # See _mouse.basemouse.BaseMouse

        # set buttonlist and timeout
        if mousebuttonlist == 'default':
            mousebuttonlist = self.mbuttonlist
        if timeout == 'default':
            timeout = self.timeout
        # starttime
        starttime = clock.get_time()
        time = clock.get_time()
        # wait for mouse clicks
        while timeout == None or time - starttime <= timeout:
            time = clock.get_time()
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    time = clock.get_time()
                    clickpos = self.get_pos()
                    if mousebuttonlist == None or event.button in mousebuttonlist:
                        pressed = event.button
                        return pressed, clickpos, time
        # in case of timeout
        return None, None, time


    def get_pressed(self):

        # See _mouse.basemouse.BaseMouse

        pygame.event.get()
        return pygame.mouse.get_pressed()


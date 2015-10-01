# -*- coding: utf-8 -*-
from pygaze.defaults import *
try:
    from constants import *
except Exception:
    pass

import pygaze
from pygaze._misc.misc import rgb2psychorgb
from pygaze.libtime import clock
#from pygaze._display.basedisplay import BaseDisplay

from psychopy.visual import Window

# we try importing the copy_docstr function, but as we do not really need it
# for a proper functioning of the code, we simply ignore it when it fails to
# be imported correctly
try:
    from pygaze._misc.misc import copy_docstr
except Exception:
    pass


#class PsychoPyDisplay(BaseDisplay):
class PsychoPyDisplay(object):

    # See _display.basedisplay.BaseDisplay for documentation

    def __init__(self, dispsize=DISPSIZE, fgc=FGC, bgc=BGC, screennr=SCREENNR, screen=None, **args):

        # See _display.basedisplay.BaseDisplay for documentation

        # try to import copy docstring (but ignore it if it fails, as we do
        # not need it for actual functioning of the code)
        try:
            copy_docstr(BaseDisplay, PsychoPyDisplay)
        except Exception:
            # we're not even going to show a warning, since the copied
            # docstring is useful for code editors; these load the docs
            # in a non-verbose manner, so warning messages would be lost
            pass

        self.dispsize = dispsize
        self.fgc = fgc
        self.bgc = bgc
        self.screennr = screennr
        self.mousevis = False

        # create window
        pygaze.expdisplay = Window(size=self.dispsize, pos=None, color= \
            rgb2psychorgb(self.bgc), colorSpace='rgb', fullscr=FULLSCREEN, \
            screen=self.screennr, units='pix')
        # set mouse visibility
        pygaze.expdisplay.setMouseVisible(self.mousevis)
        # get screen in window
        if screen:
            for s in screen.screen:
                s.draw()

    def show(self):

        # See _display.basedisplay.BaseDisplay for documentation

        pygaze.expdisplay.flip()
        return clock.get_time()

    def show_part(self, rect, screen=None):

        # See _display.basedisplay.BaseDisplay for documentation

        self.fill(screen)
        self.show()
        print("WARNING! screen.Display.show_part not available for PsychoPy display type; fill() and show() are used instead")

        return clock.get_time()


    def fill(self, screen=None):

        # See _display.basedisplay.BaseDisplay for documentation

        pygaze.expdisplay.clearBuffer()
        if screen != None:
            for s in screen.screen:
                s.draw()

    def close(self):

        # See _display.basedisplay.BaseDisplay for documentation

        pygaze.expdisplay.close()


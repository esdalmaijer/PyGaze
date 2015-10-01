# -*- coding: utf-8 -*-
from pygaze.defaults import *
try:
    from constants import *
except Exception:
    pass

import pygame
import pygame.display
import pygame.draw
import pygame.image

import pygaze
from pygaze._display.basedisplay import BaseDisplay
from pygaze.libtime import clock

# we try importing the copy_docstr function, but as we do not really need it
# for a proper functioning of the code, we simply ignore it when it fails to
# be imported correctly
try:
    from pygaze._misc.misc import copy_docstr
except Exception:
    pass


class PyGameDisplay(BaseDisplay):
    # See _display.basedisplay.BaseDisplay for documentation

    def __init__(self, dispsize=DISPSIZE, fgc=FGC, bgc=BGC, screen=None, **args):

        # See _display.basedisplay.BaseDisplay for documentation

        # try to import copy docstring (but ignore it if it fails, as we do
        # not need it for actual functioning of the code)
        try:
            copy_docstr(BaseDisplay, PyGameDisplay)
        except Exception:
            # we're not even going to show a warning, since the copied
            # docstring is useful for code editors; these load the docs
            # in a non-verbose manner, so warning messages would be lost
            pass

        self.dispsize = dispsize
        self.fgc = fgc
        self.bgc = bgc
        self.mousevis = False

        # initialize PyGame display-module
        pygame.display.init()
        # make mouse invisible (should be so per default, but you never know)
        pygame.mouse.set_visible(self.mousevis)
        if FULLSCREEN:
            mode = pygame.FULLSCREEN|pygame.HWSURFACE|pygame.DOUBLEBUF
        else:
            mode = pygame.HWSURFACE|pygame.DOUBLEBUF
        # create surface for full screen displaying
        pygaze.expdisplay = pygame.display.set_mode(self.dispsize, mode)

        # blit screen to display surface (if user entered one)
        if screen:
            pygaze.expdisplay.blit(screen.screen, (0, 0))
        else:
            pygaze.expdisplay.fill(self.bgc)


    def show(self):

        # See _display.basedisplay.BaseDisplay for documentation

        pygame.display.flip()
        return clock.get_time()


    def show_part(self, rect, screen=None):

        # See _display.basedisplay.BaseDisplay for documentation

        if len(rect) > 1:
            for r in rect:
                pygaze.expdisplay.set_clip(r)
                if screen:
                    pygaze.expdisplay.blit(screen.screen, (0, 0))
                pygame.display.update(r)
                pygaze.expdisplay.set_clip(None)

        elif len(rect) == 1:
            pygaze.expdisplay.clip(rect)
            if screen:
                pygaze.expdisplay.blit(screen.screen, (0, 0))
            pygame.display.update(rect)
            pygaze.expdisplay.set_clip(None)

        else:
            raise Exception("Error in libscreen.Display.show_part: rect should be a single rect (i.e. a (x,y,w,h) tuple) or a list of rects!")

        return clock.get_time()


    def fill(self, screen=None):
        # See _display.basedisplay.BaseDisplay for documentation

        pygaze.expdisplay.fill(self.bgc)
        if screen != None:
            pygaze.expdisplay.blit(screen.screen, (0, 0))


    def close(self):
        # See _display.basedisplay.BaseDisplay for documentation

        pygame.display.quit()

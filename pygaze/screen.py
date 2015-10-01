
# -*- coding: utf-8 -*-
from pygaze import defaults
from pygaze.defaults import *
try:
    from constants import *
except Exception:
    pass

from pygaze._misc.misc import copy_docstr
from pygaze._screen.basescreen import BaseScreen


class Screen(BaseScreen):

    """
    A class for Screen objects, for visual stimuli (to be displayed via a
    Display object)
    """

    def __init__(self, disptype=DISPTYPE, **args):

        """
        Initializes the Screen object.

        Keyword arguments:
        disptype    --    Type of display: either 'pygame' or 'psychopy'
                    (default = DISPTYPE)
        dispsize    -- size of the display in pixels: a (width, height)
                   tuple (default = DISPSIZE)
        fgc        -- the foreground colour: a colour name (e.g. 'red') or
                   a RGB(A) tuple (e.g. (255,0,0) or (255,0,0,255))
                   (default = FGC)
        bgc        -- the background colour: a colour name (e.g. 'red') or
                   a RGB(A) tuple (e.g. (255,0,0) or (255,0,0,255))
                   (default = BGC)
        screennr    -- the screen number: 0, 1 etc. (default =
                   SCREENNR)
        mousevisible    -- Boolean indicating mouse visibility (default =
                       MOUSEVISIBLE)
        screen    -- a Screen object to be presented on the new Display
                   (default=None)
        """

        if disptype == u'pygame':
            from pygaze._screen.pygamescreen import PyGameScreen as Screen
        elif disptype == u'psychopy':
            from pygaze._screen.psychopyscreen import PsychoPyScreen as Screen
        elif disptype == u'opensesame':
            from pygaze._screen.osscreen import OSScreen as Screen
        else:
            raise Exception(u'Unexpected disptype : %s' % disptype)
        self.__class__ = Screen
        self.__class__.__init__(self, **args)
        copy_docstr(BaseScreen, Screen)

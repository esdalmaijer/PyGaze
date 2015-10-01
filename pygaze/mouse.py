# -*- coding: utf-8 -*-
from pygaze.defaults import *
try:
    from constants import *
except Exception:
    pass

from pygaze._misc.misc import copy_docstr
from pygaze._mouse.basemouse import BaseMouse


class Mouse(BaseMouse):

    """A mouse for collecting responses"""

    def __init__(self, disptype=DISPTYPE, **args):

        """
        Initializes the Mouse object.

        TODO: docstring.
        """

        if disptype == u'pygame':
            from pygaze._mouse.pygamemouse import PyGameMouse as Mouse
        elif disptype == u'psychopy':
            from pygaze._mouse.psychopymouse import PsychoPyMouse as Mouse
        elif disptype == u'opensesame':
            from pygaze._mouse.osmouse import OSMouse as Mouse
        else:
            raise Exception(u'Unexpected disptype : %s' % disptype)
        self.__class__ = Mouse
        self.__class__.__init__(self, **args)
        copy_docstr(BaseMouse, Mouse)

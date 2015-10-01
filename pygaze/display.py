# -*- coding: utf-8 -*-
from pygaze.defaults import *
try:
    from constants import *
except Exception:
    pass

from pygaze._misc.misc import copy_docstr
from pygaze._display.basedisplay import BaseDisplay


class Display(BaseDisplay):

    # see BaseDisplay

    def __init__(self, disptype=DISPTYPE, **args):

        # see BaseDisplay

        if disptype == u'pygame':
            from pygaze._display.pygamedisplay import PyGameDisplay as Display
        elif disptype == u'psychopy':
            from pygaze._display.psychopydisplay import PsychoPyDisplay  as Display
        elif disptype == u'opensesame':
            from pygaze._display.osdisplay import OSDisplay as Display
        else:
            raise Exception(u'Unexpected disptype : %s' % disptype)
        self.__class__ = Display
        self.__class__.__init__(self, **args)
        copy_docstr(BaseDisplay, Display)

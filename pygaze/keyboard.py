# -*- coding: utf-8 -*-
from pygaze.defaults import *
try:
    from constants import *
except Exception:
    pass

from pygaze._misc.misc import copy_docstr
from pygaze._keyboard.basekeyboard import BaseKeyboard


class Keyboard(BaseKeyboard):

    # see BaseKeyboard

    def __init__(self, disptype=DISPTYPE, **args):

        # see BaseKeyboard

        if disptype == u'pygame':
            from pygaze._keyboard.pygamekeyboard import PyGameKeyboard as \
                Keyboard
        elif disptype == u'psychopy':
            from pygaze._keyboard.psychopykeyboard import PsychoPyKeyboard as \
                Keyboard
        elif disptype == u'opensesame':
            from pygaze._keyboard.oskeyboard import OSKeyboard as \
                Keyboard
        else:
            raise Exception(u'Unexpected disptype : %s' % disptype)
        self.__class__ = Keyboard
        self.__class__.__init__(self, **args)
        copy_docstr(BaseKeyboard, Keyboard)

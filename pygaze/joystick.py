# -*- coding: utf-8 -*-
from pygaze.defaults import *
try:
    from constants import *
except Exception:
    pass

from pygaze._misc.misc import copy_docstr
from pygaze._joystick.basejoystick import BaseJoystick


class Joystick(BaseJoystick):

    # see BaseJoystick

    def __init__(self, disptype=DISPTYPE, **args):

        # see BaseJoystick

        if disptype in (u'pygame', u'psychopy'):
            from pygaze._joystick.pygamejoystick import PyGameJoystick
            self.__class__ = PyGameJoystick
        else:
            raise Exception(u'Unexpected disptype : %s' % disptype)
        self.__class__.__init__(self, **args)
        copy_docstr(BaseJoystick, Joystick)

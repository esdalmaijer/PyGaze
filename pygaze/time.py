# -*- coding: utf-8 -*-
from pygaze.defaults import *
try:
    from constants import *
except Exception:
    pass

from pygaze._misc.misc import copy_docstr
from pygaze._time.basetime import BaseTime


class Time(BaseTime):

    """A mouse for collecting responses"""

    def __init__(self, disptype=DISPTYPE, **args):

        """
        Initializes the Time object.

        TODO: docstring.
        """

        if disptype == u'pygame':
            from pygaze._time.pygametime import PyGameTime as Time
        elif disptype == u'psychopy':
            from pygaze._time.psychopytime import PsychoPyTime as Time
        elif disptype == u'opensesame':
            from pygaze._time.ostime import OSTime as Time
        else:
            raise Exception(u'Unexpected disptype : %s' % disptype)
        self.__class__ = Time
        self.__class__.__init__(self, **args)
        copy_docstr(BaseTime, Time)

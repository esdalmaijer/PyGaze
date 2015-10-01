# -*- coding: utf-8 -*-
from pygaze.defaults import *
try:
    from constants import *
except Exception:
    pass

from pygaze._misc.misc import copy_docstr
from pygaze._sound.basesound import BaseSound


class Sound(BaseSound):

    """A mouse for collecting responses"""

    def __init__(self, disptype=DISPTYPE, **args):

        """
        Initializes the Mouse object.

        TODO: docstring.
        """

        if disptype in (u'pygame', u'psychopy', u'opensesame'):
            from pygaze._sound.pygamesound import PyGameSound as Sound
        else:
            raise Exception(u'Unexpected disptype : %s' % disptype)
        self.__class__ = Sound
        self.__class__.__init__(self, **args)
        copy_docstr(BaseSound, Sound)

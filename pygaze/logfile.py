# -*- coding: utf-8 -*-
from pygaze.defaults import *
try:
    from constants import *
except Exception:
    pass

from pygaze._misc.misc import copy_docstr
from pygaze._logfile.baselogfile import BaseLogfile

class Logfile(BaseLogfile):

    # See BaseLogfile

    def __init__(self, **args):

        # See BaseLogfile

        from pygaze._logfile.logfile import Logfile
        self.__class__ = Logfile
        self.__class__.__init__(self, **args)
        copy_docstr(BaseLogfile, Logfile)

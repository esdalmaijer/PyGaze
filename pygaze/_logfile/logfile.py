# -*- coding: utf-8 -*-
import os
from pygaze.defaults import *
try:
    from constants import *
except Exception:
    pass

from pygaze._logfile.baselogfile import BaseLogfile
# we try importing the copy_docstr function, but as we do not really need it
# for a proper functioning of the code, we simply ignore it when it fails to
# be imported correctly
try:
    from pygaze._misc.misc import copy_docstr
except Exception:
    pass


class Logfile(BaseLogfile):

    # See _logfile.baselogfile.BaseLogfile

    def __init__(self, filename=LOGFILE):

        # See _logfile.baselogfile.BaseLogfile

        # try to copy docstring (but ignore it if it fails, as we do
        # not need it for actual functioning of the code)
        try:
            copy_docstr(BaseLogfile, Logfile)
        except Exception:
            # we're not even going to show a warning, since the copied
            # docstring is useful for code editors; these load the docs
            # in a non-verbose manner, so warning messages would be lost
            pass

        self.filename = filename + ".txt"
        self.logfile = open(self.filename, "w")


    def write(self, vallist):

        # See _logfile.baselogfile.BaseLogfile

        # empty string
        line = ""

        # all values to string
        vallist = map(str, vallist)

        # insert tabs between values, end with newline character
        line = "\t".join(vallist) + "\n"

        # write line to file (on disk)
        self.logfile.write(line) # write to internal buffer
        self.logfile.flush() # internal buffer to RAM
        os.fsync(self.logfile.fileno()) # RAM file cache to disk


    def close(self):

        # See _logfile.baselogfile.BaseLogfile

        self.logfile.close()


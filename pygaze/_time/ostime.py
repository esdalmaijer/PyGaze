# -*- coding: utf-8 -*-
from pygaze.defaults import osexperiment
try:
    from constants import osexperiment
except Exception:
    pass

from pygaze._time.basetime import BaseTime
# we try importing the copy_docstr function, but as we do not really need it
# for a proper functioning of the code, we simply ignore it when it fails to
# be imported correctly
try:
    from pygaze._misc.misc import copy_docstr
except Exception:
    pass


class OSTime(BaseTime):

    # see pygaze._time.basetime.BaseTime

    def __init__(self):

        # see pygaze._time.basetime.BaseTime

        # try to copy docstring (but ignore it if it fails, as we do
        # not need it for actual functioning of the code)
        try:
            copy_docstr(BaseTime, OSTime)
        except Exception:
            # we're not even going to show a warning, since the copied
            # docstring is useful for code editors; these load the docs
            # in a non-verbose manner, so warning messages would be lost
            pass

        pass


    def expstart(self):

        # see pygaze._time.basetime.BaseTime

        global expbegintime

        expbegintime = 0


    def get_time(self):

        # see pygaze._time.basetime.BaseTime

        return osexperiment.time()


    def pause(self, pausetime):

        # see pygaze._time.basetime.BaseTime

        return osexperiment.sleep(pausetime)


    def expend(self):

        # see pygaze._time.basetime.BaseTime

        return osexperiment.time()

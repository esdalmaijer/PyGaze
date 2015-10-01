# -*- coding: utf-8 -*-
import psychopy.core

from pygaze._time.basetime import BaseTime
# we try importing the copy_docstr function, but as we do not really need it
# for a proper functioning of the code, we simply ignore it when it fails to
# be imported correctly
try:
    from pygaze._misc.misc import copy_docstr
except Exception:
    pass


class PsychoPyTime(BaseTime):

    # see pygaze._time.basetime.BaseTime

    def __init__(self):

        # see pygaze._time.basetime.BaseTime

        # try to copy docstring (but ignore it if it fails, as we do
        # not need it for actual functioning of the code)
        try:
            copy_docstr(BaseTime, PsychoPyTime)
        except Exception:
            # we're not even going to show a warning, since the copied
            # docstring is useful for code editors; these load the docs
            # in a non-verbose manner, so warning messages would be lost
            pass

        pass


    def expstart(self):

        # see pygaze._time.basetime.BaseTime

        global expbegintime

        expbegintime = psychopy.core.getTime() * 1000


    def get_time(self):

        # see pygaze._time.basetime.BaseTime

        return psychopy.core.getTime() * 1000 - expbegintime


    def pause(self, pausetime):

        # see pygaze._time.basetime.BaseTime

        t0 = psychopy.core.getTime()
        psychopy.core.wait(pausetime/1000.0)
        t1 = psychopy.core.getTime()

        return t1-t0


    def expend(self):

        # see pygaze._time.basetime.BaseTime

        endtime = self.get_time() * 1000

        psychopy.core.quit()

        return endtime

# -*- coding: utf-8 -*-
import pygame
import time
import sys

from pygaze._time.basetime import BaseTime
# we try importing the copy_docstr function, but as we do not really need it
# for a proper functioning of the code, we simply ignore it when it fails to
# be imported correctly
try:
    from pygaze._misc.misc import copy_docstr
except Exception:
    pass


class PyGameTime(BaseTime):

    # see pygaze._time.basetime.BaseTime

    def __init__(self):

        # see pygaze._time.basetime.BaseTime

        # try to copy docstring (but ignore it if it fails, as we do
        # not need it for actual functioning of the code)
        try:
            copy_docstr(BaseTime, PyGameTime)
        except Exception:
            # we're not even going to show a warning, since the copied
            # docstring is useful for code editors; these load the docs
            # in a non-verbose manner, so warning messages would be lost
            pass

        # On Windows, `time.clock()` provides higher accuracy than
        # `time.time()`.
        if sys.platform == 'win32':
            self._cpu_time = time.clock
        else:
            self._cpu_time = time.time

        pygame.init()



    def expstart(self):

        # see pygaze._time.basetime.BaseTime

        global expbegintime

        expbegintime = self._cpu_time() * 1000


    def get_time(self):

        # see pygaze._time.basetime.BaseTime

        ctime = self._cpu_time()*1000 - expbegintime

        return ctime


    def pause(self, pausetime):

        # see pygaze._time.basetime.BaseTime

        realpause = pygame.time.delay(pausetime)

        return realpause


    def expend(self):

        # see pygaze._time.basetime.BaseTime

        endtime = self.get_time()

        pygame.quit()

        return endtime

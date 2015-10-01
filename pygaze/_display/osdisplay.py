# -*- coding: utf-8 -*-
from openexp.canvas import canvas

try:
    from constants import osexperiment
except Exception:
    osexperiment = None

from pygaze._display.basedisplay import BaseDisplay
# we try importing the copy_docstr function, but as we do not really need it
# for a proper functioning of the code, we simply ignore it when it fails to
# be imported correctly
try:
    from pygaze._misc.misc import copy_docstr
except Exception:
    pass


class OSDisplay(BaseDisplay):

    # See _display.basedisplay.BaseDisplay for documentation

    def __init__(self, **args):

        # See _display.basedisplay.BaseDisplay for documentation

        # try to import copy docstring (but ignore it if it fails, as we do
        # not need it for actual functioning of the code)
        try:
            copy_docstr(BaseDisplay, OSDisplay)
        except Exception:
            # we're not even going to show a warning, since the copied
            # docstring is useful for code editors; these load the docs
            # in a non-verbose manner, so warning messages would be lost
            pass

        self.experiment = osexperiment
        self.canvas = canvas(self.experiment)
        self.dispsize = self.experiment.resolution()

    def show(self):

        # See _display.basedisplay.BaseDisplay for documentation

        return self.canvas.show()

    def show_part(self, rect, screen=None):

        # See _display.basedisplay.BaseDisplay for documentation

        return self.canvas.show()

    def fill(self, screen=None):

        # See _display.basedisplay.BaseDisplay for documentation

        if screen != None:
            self.canvas = screen.canvas
        else:
            self.canvas = canvas(self.experiment)

    def close(self):

        # See _display.basedisplay.BaseDisplay for documentation

        pass

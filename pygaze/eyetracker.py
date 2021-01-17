# -*- coding: utf-8 -*-
#
# This file is part of PyGaze - the open-source toolbox for eye tracking
#
#    PyGaze is a Python module for easily creating gaze contingent experiments
#    or other software (as well as non-gaze contingent experiments/software)
#    Copyright (C) 2012-2013  Edwin S. Dalmaijer
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>

from pygaze.py3compat import *
from pygaze import settings
from pygaze._misc.misc import copy_docstr
from pygaze._eyetracker.baseeyetracker import BaseEyeTracker


class EyeTracker(BaseEyeTracker):

    """
    Generic EyeTracker class, which morphs into an eye-tracker specific class.
    """

    def __init__(self, display, trackertype=settings.TRACKERTYPE, **args):

        """
        Initializes an EyeTracker object.

        arguments

        display        --    a pygaze.display.Display instance

        keyword arguments

        trackertype        --    the type of eye tracker; choose from:
                        "dumbdummy", "dummy", "eyelink", "eyelogic", "smi",
                        "tobii", "eyetribe" (default = TRACKERTYPE)
        **args        --    A keyword-argument dictionary that contains
                        eye-tracker-specific options
        """

        # set trackertype to dummy in dummymode
        if settings.DUMMYMODE:
            trackertype = "dummy"

        # correct wrong input
        allowed_trackers = ["dumbdummy", "dummy", "eyelink", "eyelogic", "smi", \
            "eyetribe", "opengaze", "alea", "tobii", "tobii-legacy", \
            "tobiiglasses"]
        if trackertype not in allowed_trackers:
            raise Exception( \
                "Error in eyetracker.EyeTracker: trackertype {} not recognized; it should be one of {}".format(trackertype,allowed_trackers))

        # EyeLink
        if trackertype == "eyelink":
            # import libraries
            from pygaze._eyetracker.libeyelink import libeyelink
            # morph class
            self.__class__ = libeyelink
            # initialize
            self.__class__.__init__(self, display, **args)

        # EyeLogic
        elif trackertype == "eyelogic":
            # import libraries
            from pygaze._eyetracker.libeyelogic import EyeLogicTracker
            # morph class
            self.__class__ = EyeLogicTracker
            # initialize
            self.__class__.__init__(self, display, **args)

		# SMI
        elif trackertype == "smi":
            # import libraries
            from pygaze._eyetracker.libsmi import SMItracker
            # morph class
            self.__class__ = SMItracker
            # initialize
            self.__class__.__init__(self, display, **args)

        # Tobii Legacy
        elif trackertype == "tobii-legacy":
            # import libraries
            from pygaze._eyetracker.libtobiilegacy import TobiiTracker
            # morph class
            self.__class__ = TobiiTracker
            # initialize
            self.__class__.__init__(self, display, **args)

        # Tobii
        elif trackertype == "tobii":
            # import libraries
            from pygaze._eyetracker.libtobii import TobiiProTracker
            # morph class
            self.__class__ = TobiiProTracker
            # initialize
            self.__class__.__init__(self, display, **args)

        # Tobii Pro Glasses 2
        elif trackertype == "tobiiglasses":
            # import libraries
            from pygaze._eyetracker.libtobiiglasses import TobiiGlassesTracker
            # morph class
            self.__class__ = TobiiGlassesTracker
            # initialize
            self.__class__.__init__(self, display, **args)

        # EyeTribe
        elif trackertype == "eyetribe":
            # import libraries
            from pygaze._eyetracker.libeyetribe import EyeTribeTracker
            # morph class
            self.__class__ = EyeTribeTracker
            # initialize
            self.__class__.__init__(self, display, **args)

        # OpenGaze
        elif trackertype == "opengaze":
            # import libraries
            from pygaze._eyetracker.libopengaze import OpenGazeTracker
            # morph class
            self.__class__ = OpenGazeTracker
            # initialize
            self.__class__.__init__(self, display, **args)

        # OpenGaze
        elif trackertype == "alea":
            # import libraries
            from pygaze._eyetracker.libalea import AleaTracker
            # morph class
            self.__class__ = AleaTracker
            # initialize
            self.__class__.__init__(self, display, **args)

        # dummy mode
        elif trackertype == "dummy":
            # import libraries
            from pygaze._eyetracker.libdummytracker import Dummy
            # morph class
            self.__class__ = Dummy
            # initialize
            self.__class__.__init__(self, display)

        # dumb dummy mode
        elif trackertype == "dumbdummy":
            # import libraries
            from pygaze._eyetracker.libdumbdummy import DumbDummy
            # morph class
            self.__class__ = DumbDummy
            # initialize
            self.__class__.__init__(self, display)

        else:
            raise Exception( \
                "Error in eyetracker.EyeTracker.__init__: trackertype {} not recognized, this should not happen!".format(trackertype))

        # copy docstrings
        copy_docstr(BaseEyeTracker, EyeTracker)

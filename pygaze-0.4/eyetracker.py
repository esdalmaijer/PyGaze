## This file is part of the Gaze Contingent Extension for Python
##
##    PyGACE is a Python module for easily creating gaze contingent experiments
##    or other software (as well as non-gaze contingent experiments/software)
##    Copyright (C) 2012-2013  Edwin S. Dalmaijer
##
##    This program is free software: you can redistribute it and/or modify
##    it under the terms of the GNU General Public License as published by
##    the Free Software Foundation, either version 3 of the License, or
##    (at your option) any later version.
##
##    This program is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.
##
##    You should have received a copy of the GNU General Public License
##    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
# version: 0.4 (25-03-2013), NOT RELEASED FOR USE OUTSIDE OF UTRECHT UNIVERSITY)
#
#
# Many thanks to Sebastiaan Mathot. libeyelink is a slightly modified version of
# libeyelink.py, part of the eyelink plugins for the OpenSesame experiment builder
# (see: www.cogsci.nl/opensesame).
# OpenSesame is free software, redistributable under the terms of the GNU Public
# License as published by the Free Software Foundation.

try:
    import constants
except:
    import defaults as constants


class EyeTracker:

    """EyeTracker class, which morphes into either an Eyelink, SMItracker or DummyTracker object"""

    def __init__(self, display, trackertype=constants.TRACKERTYPE, resolution=constants.DISPSIZE, eyedatafile=constants.LOGFILENAME, logfile=constants.LOGFILE, fgc=constants.FGC, bgc=constants.BGC, saccvelthresh=constants.SACCVELTHRESH, saccaccthresh=constants.SACCACCTHRESH, ip=constants.SMIIP, sendport=constants.SMISENDPORT, receiveport=constants.SMIRECEIVEPORT):

        """Initializes an EyeTracker object"""

        # set trackertype to dummy in dummymode
        if constants.DUMMYMODE:
            trackertype = 'dummy'
    
        # correct wrong input
        if trackertype not in ['eyelink','smi','dummy']:
            trackertype = 'dummy'
            print("Error in eyetracker.EyeTracker: trackertype not recognized; trackertype set to 'dummy'")

        # EyeLink
        if trackertype == 'eyelink':
            # import libraries
            from libeyelink import libeyelink
            # morph class
            self.__class__ = libeyelink
            # initialize
            self.__class__.__init__(self, display, resolution=resolution, data_file=eyedatafile+".edf", fg_color=fgc, bg_color=bgc, saccade_velocity_threshold=saccvelthresh, saccade_acceleration_threshold=saccaccthresh)
            
        # SMI
        elif trackertype == 'smi':
            # import libraries
            from libsmi import SMItracker
            # morph class
            self.__class__ = SMItracker
            # initialize
            self.__class__.__init__(self, ip=ip, sendport=sendport, receiveport=receiveport, logfile=logfile)

        # dummy mode
        elif trackertype == 'dummy':
            # import libraries
            from libdummytracker import Dummy
            # morph class
            self.__class__ = Dummy
            # initialize
            self.__class__.__init__(self)

        else:
            print("Error in eyetracker.EyeTracker: trackertype not recognized, this should not happen!")


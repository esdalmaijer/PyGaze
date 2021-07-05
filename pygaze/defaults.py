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

# MAIN
# Boolean that indicates whether we should operate in DUMMYMODE (where the
# mouse simulates eye movements) or communicate to the eye tracker defined
# under TRACKERTYPE.
DUMMYMODE = False
# Name of the log file, without path or extension.
LOGFILENAME = "default" 
# Path to the log file.
LOGFILE = LOGFILENAME[:]

# DISPLAY
# Number of the screen used for displaying experiment. (Relevant in PsychoPy.)
SCREENNR = 0
# Back-end for the display. Choose either "psychopy" or "pygame".
DISPTYPE = "psychopy"
# Display resolution in pixels as (width,height). Needs to be integers!
DISPSIZE = (1280,1024)
# Physical display size in centimeters as (width,height). Can be floats.
SCREENSIZE = (33.8,27.1)
# Distance between the eye and the display in centimeters. Float.
SCREENDIST = 57.0
# Boolean indicating whether the experiment is executed in fullscreen.
FULLSCREEN = True
# Boolean indicating mouse visibility.
MOUSEVISIBLE = False
# Background colour in (red,green,blue); use integer values in range [0,255].
BGC = (125,125,125) # backgroundcolour
# Foreground colour in (red,green,blue); use integer values in range [0,255].
FGC = (0,0,0)

# SOUND
# Default oscillator for Sound instances, choose between:
# "sine", "saw", "square" or "whitenoise"
SOUNDOSCILLATOR = "sine"
# Default sound frequency in Herz.
SOUNDFREQUENCY = 440
# Default sound duration in milliseconds.
SOUNDLENGTH = 100
# Default sound "attack" (linear fade-in) in milliseconds.
SOUNDATTACK = 0
# Default sound "decay" (linear fade-out) in milliseconds.
SOUNDDECAY = 5
# Default sound buffer size (power of 2). Increase if playback is choppy.
SOUNDBUFFERSIZE = 1024
# Default sound sampling frequency in samples per second.
SOUNDSAMPLINGFREQUENCY = 48000
# Default bit depth (negative depth allow for signed values).
SOUNDSAMPLESIZE = -16
# Default sound channels. 1 for mono, 2 for stereo.
SOUNDCHANNELS = 2

# INPUT
# Default allowed mouse button list. None to allow all buttons, or a list for
# buttons of choice, e.g. [1,3] for buttons 1 and 3 (left and right click on a
# mouse with a scroll wheel).
MOUSEBUTTONLIST = None
# Default mouse response timeout in milliseconds. Set to None for no timeout.
MOUSETIMEOUT = None
# Default allowed key list. None to allow all keys, or a list for keys of your
# choice, e.g. ["space","9",";"] for space, 9 and ; keys.
KEYLIST = None
# Default keyboard response timeout in milliseconds. Set to None for no timeout.
KEYTIMEOUT = None
# Default allowed joystick button list. None to allow all joystick buttons; or
# a list of button numbers (start counting at 0) for buttons of choice, e.g.
# [0,3] for buttons 0 and 3 (these could be reffered to as 1 and 4 in software
# that starts counting at 1).
JOYBUTTONLIST = None
# Default joystick response timeout in milliseconds. Set to None for no timeout.
JOYTIMEOUT = None

# EYETRACKER
# Tracker type. Choose from: "alea", "eyelink", "eyelogic", "eyetribe", "opengaze",
# "smi", "tobii", "tobii-legacy", "dummy", or "dumbdummy". (Note: if DUMMYMODE==True,
# TRACKERTYPE will be set to "dummy" automatically.)
TRACKERTYPE = "eyelink"
# Default saccade velocity threshold in degrees per second; used for PyGaze
# event detection.
SACCVELTHRESH = 35
# Default saccade acceleration threshold in degrees per second**2; used for
# PyGaze event detection.
SACCACCTHRESH = 9500
# Default blink threshold in milliseconds; used for PyGaze event detection.
BLINKTHRESH = 150
# Default event-detection method. Set to "pygaze" for PyGaze event detection,
# or "native" for the eye tracker's built-in event detection. Note that not
# all trackers have a native option, in which case we will fall back to the
# "pygaze" event detection.
EVENTDETECTION = "pygaze"

# EyeLink only
# Boolean indicating whether a beep should be played on each jump of the
# target during calibration.
EYELINKCALBEEP = True
# String indicating the EyeLink pupil size mode. Choose between "diameter" and
# "area".
EYELINKPUPILSIZEMODE = "area"

# EyeTribe only
# Default duration of the calibration in milliseconds for each calibration
# target (collected while target is stationary).
EYETRIBECALIBDUR = 750
# Default duration of the time (in milliseconds) before starting data
# collection for each calibration target.
EYETRIBEPRECALIBDUR = 500

# SMI only
# IP address for both the sending and receiving port. Here for legacy reasons.
SMIIP = "127.0.0.1"
# IP address for iViewX sending.
SMISENDIP = "127.0.0.1"
# IP address for iViewX receiving. (This can be the same IP if iViewX is
# running locally.)
SMIRECEIVEIP = "127.0.0.1" 
# Port number for iViewX sending.
SMISENDPORT = 4444
# Port number for iViewX receiving.
SMIRECEIVEPORT = 5555

# Alea only
# SDK key. This is user-specific, so needs to be user defined.
ALEAKEY = "Contact Alea for an API key"
# Boolean that determines whether an animated calibration should be used. This
# is a friendly parrot; ideal for children.
ALEAALEAANIMATEDCALIBRATION = False
# Alea offers their own specific type of logging with a specific output 
# location and file layout. PyGaze offers a different way that relies on 
# streaming data. Alea prefer their own way, which is why the default is set
# to that. The PyGaze way of logging produces files that are more similar to
# those of other trackers.
ALEALOGGING = True


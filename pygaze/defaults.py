# -*- coding: utf-8 -*-
# MAIN
DUMMYMODE = False # False for gaze contingent display, True for dummy mode (using mouse or joystick)
LOGFILENAME = 'default' # logfilename, without path
LOGFILE = LOGFILENAME[:] # .txt; adding path before logfilename is optional; logs responses (NOT eye movements, these are stored in a different (EDF/IDF/TXT) file!)

# DISPLAY
SCREENNR = 0 # number of the screen used for displaying experiment
DISPTYPE = 'psychopy' # either 'psychopy' or 'pygame'
DISPSIZE = (1280, 1024) # canvas size
SCREENSIZE = (33.8, 27.1) # physical screen size in centimeters
SCREENDIST = 57.0 # centimeters; distance between screen and participant's eyes
FULLSCREEN = True # Indicates whether the experiment is executed in fullscreen
MOUSEVISIBLE = False # mouse visibility
BGC = (125, 125, 125) # backgroundcolour
FGC = (0, 0, 0) # foregroundcolour

# SOUND
SOUNDOSCILLATOR = 'sine' # 'sine', 'saw', 'square' or 'whitenoise'
SOUNDFREQUENCY = 440 # Herz
SOUNDLENGTH = 100 # milliseconds (duration)
SOUNDATTACK = 0 # milliseconds (fade-in)
SOUNDDECAY = 5 # milliseconds (fade-out)
SOUNDBUFFERSIZE = 1024 # increase if playback is choppy
SOUNDSAMPLINGFREQUENCY = 48000 # samples per second
SOUNDSAMPLESIZE = -16 # determines bit depth (negative is signed
SOUNDCHANNELS = 2 # 1 = mono, 2 = stereo

# INPUT
MOUSEBUTTONLIST = None # None for all mouse buttons; list of numbers for buttons of choice (e.g. [1,3] for buttons 1 and 3)
MOUSETIMEOUT = None # None for no timeout, or a value in milliseconds
KEYLIST = None # None for all keys; list of keynames for keys of choice (e.g. ['space','9',':'] for space, 9 and ; keys)
KEYTIMEOUT = 1 # None for no timeout, or a value in milliseconds
JOYBUTTONLIST = None # None for all joystick buttons; list of button numbers (start counting at 0) for buttons of choice (e.g. [0,3] for buttons 0 and 3 - may be reffered to as 1 and 4 in other programs)
JOYTIMEOUT = None # None for no timeout, or a value in milliseconds

# EYETRACKER
# general
TRACKERTYPE = 'eyelink' # either 'smi', 'eyelink' or 'dummy' (NB: if DUMMYMODE is True, trackertype will be set to dummy automatically)
SACCVELTHRESH = 35 # degrees per second, saccade velocity threshold
SACCACCTHRESH = 9500 # degrees per second, saccade acceleration threshold
EVENTDETECTION = 'pygaze' # either 'pygaze' for PyGaze detection algorithms, or 'native' for manufacturer's event detection (if available)
# EyeLink only
EYELINKCALBEEP = True # Calibration beep with each jump
EYELINKPUPILSIZEMODE = 'area'
# SMI only
SMIIP = '127.0.0.1'
SMISENDPORT = 4444
SMIRECEIVEPORT = 5555


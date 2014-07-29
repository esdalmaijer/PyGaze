import os.path

# FILES AND FOLDERS
# the DIR constant contains the full path to the current directory, which will
# be used to determine where to store and retrieve data files
DIR = os.path.dirname(__file__)
# the DATADIR is the path to the directory where data files will be stored
DATADIR = os.path.join(DIR, 'data')
# the IMGDIR is the path to the directory that contains the image files
IMGDIR = os.path.join(DIR, 'imgs')
# the INSTFILE is the path to the file that contains the instructions
INSTFILE = os.path.join(DIR, 'instructions.txt')
# ask for the participant name, to use as the name for the logfile...
LOGFILENAME = input("Participant name: ")
# ...then use the LOGFILENAME to make create the path to the logfile
LOGFILE = os.path.join(DATADIR, LOGFILENAME)

# DISPLAY
# for the DISPTYPE, you can choose between 'pygame' and 'psychopy'; go for
# 'psychopy' if you need millisecond accurate display refresh timing, and go
# for 'pygame' if you experience trouble using PsychoPy
DISPTYPE = 'psychopy'
# the DISPSIZE is the monitor resolution, e.g. (1024,768)
DISPSIZE = (1024,768)
# the SCREENSIZE is the physical screen size in centimeters, e.g. (39.9,29.9)
SCREENSIZE = (39.9,29.9)
# the SCREENDIST is the distance in centimeters between the participant and the
# display
SCREENDIST = 60.0
# set FULLSCREEN to True for fullscreen displaying, or to False for a windowed
# display
FULLSCREEN = True
# BGC is for BackGroundColour, FGC for ForeGroundColour; both are RGB guns,
# which contain three values between 0 and 255, representing the intensity of
# Red, Green, and Blue respectively, e.g. (0,0,0) for black, (255,255,255) for
# white, or (255,0,0) for the brightest red
BGC = (0,0,0)
FGC = (255,255,255)
# the TEXTSIZE determines the size of the text in the experiment
TEXTSIZE = 24

# TIMING
# the TRIALTIME is the time each image is visible
TRIALTIME = 10000 # ms
# the intertrial interval (ITI) is the minimal amount of time between the
# presentation of two consecutive images
ITI = 2000 # ms

# EYE TRACKING
# the TRACKERTYPE indicates the brand of eye tracker, and should be one of the
# following: 'eyelink', 'smi', 'tobii' 'dumbdummy', 'dummy'
TRACKERTYPE = 'eyelink'
# the EYELINKCALBEEP constant determines whether a beep should be sounded on
# the appearance of every calibration target (EyeLink only)
EYELINKCALBEEP = True
# set DUMMYMODE to True if no tracker is attached
DUMMYMODE = False

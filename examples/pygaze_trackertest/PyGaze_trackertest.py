# This script tests all eyetracker functions of PyGaze; run it to see if
# your installation is working as it is supposed to. Remember to adjust the
# constants in the attached constants.py script to the relevant values for
# your system and preference!
#
# contents of the directory in which this script should come:
# PyGaze_supertest.py (this script)
# constants.py (script containing constants)
# bark.ogg (soundfile)
# kitten.png (image file)
#
# version: 22 Dec 2013

import os
import random

from pygaze.defaults import *
from constants import *

from pygaze.display import Display
from pygaze.screen import Screen
from pygaze.eyetracker import EyeTracker
from pygaze.keyboard import Keyboard
from pygaze.sound import Sound
from pygaze.time import Time
from pygaze.logfile import Logfile

from pygaze.plugins.aoi import AOI
from pygaze.plugins.frl import FRL
from pygaze.plugins.gazecursor import GazeCursor


# # # # #
# directory stuff

DIR = os.path.split(os.path.abspath(__file__))[0]
soundfile = os.path.join(DIR, 'bark.ogg')
imagefile = os.path.join(DIR, 'kitten.png')


# # # # #
# create instances

# initialize the display
disp = Display()

# initialize a screen
scr = Screen()

# initialize an EyeTracker
tracker = EyeTracker(disp)

# initialize a keyboard
kb = Keyboard(keylist=['space'],timeout=None)

# initialize a sound
snd = Sound(soundfile=soundfile)

# initialize a Timer
timer = Time()

# create a new logfile
log = Logfile(filename="test")
log.write(["test", "time"])


# # # # #
# welcome

scr.draw_text("Welcome to the PyGaze Supertest!\n\nYou're going to be testing \
your PyGaze installation today, using this interactive tool. Press Space \
to start!\n\n\nP.S. If you see this, the following functions work: \
\n- Screen.draw_text \
\n- Disp.fill \
\n- Disp.show \
\nAwesome!")
disp.fill(scr)
t1 = disp.show()
log.write(["welcome", t1])
kb.get_key()


# # # # #
# test EyeTracker

#EyeTracker.connected
#EyeTracker.log_var
#EyeTracker.pupil_size
#EyeTracker.send_command
#EyeTracker.wait_for_event

scr.clear()
scr.draw_text("We're now going to test the eyetracker module. Press Space to start!")
disp.fill(scr)
t1 = disp.show()
log.write(["EyeTracker", t1])
kb.get_key()

# tracker.calibrate
tracker.calibrate()

# tracker.sample()
scr.clear()
scr.draw_text("The dot should follow your eye movements")
disp.fill(scr)
disp.show()
tracker.log("now testing sample function")
tracker.status_msg("now testing sample function")
tracker.start_recording()
key = None
while not key == 'space':
	# get new key
	key, presstime = kb.get_key(timeout=1)
	# new states
	gazepos = tracker.sample()
	# draw to screen
	scr.clear()
	scr.draw_text("The dot should follow your eye movements")
	scr.draw_fixation(fixtype='dot', pos=gazepos, pw=3, diameter=15)
	disp.fill(scr)
	disp.show()
tracker.stop_recording()
scr.clear()

# tracker.drift_correction
scr.clear()
scr.draw_text("Next is a drift check. Press Space to start!")
disp.fill(scr)
disp.show()
kb.get_key()
tracker.drift_correction()

# tracker.fix_triggered_drift_correction
scr.clear()
scr.draw_text("Next is a fixation triggered drift check. Press Space to start!")
disp.fill(scr)
disp.show()
kb.get_key()
tracker.fix_triggered_drift_correction()

# events
eventfuncs = [
	tracker.wait_for_fixation_start,
	tracker.wait_for_fixation_end,
	tracker.wait_for_saccade_start,
	tracker.wait_for_saccade_end,
	tracker.wait_for_blink_start,
	tracker.wait_for_blink_end,
	]
tracker.log("now testing wait_for_event functions")
tracker.status_msg("now testing wait_for_event functions")
for i in range(len(eventfuncs)):
	scr.clear()
	scr.draw_text("Test function: %s(); press Space to start" % str(eventfuncs[i]))
	scr.draw_fixation(fixtype='dot', pos=(DISPSIZE[0]*0.75,DISPSIZE[1]*0.75))
	disp.fill(scr)
	disp.show()
	kb.get_key()
	eventfuncs[i]()
	scr.clear()
	scr.draw_text("Function %s works! Press space to test the next" % str(eventfuncs[i]))
	disp.fill(scr)
	disp.show()
	kb.get_key()


# # # # #
# test gaze contingency

# AOI
scr.clear()
scr.draw_text("There should be an image in the centre of the screen", pos=(DISPSIZE[0]/2, DISPSIZE[1]/10))
scr.draw_image(imagefile) # imginfo: 400x600 px; kitten head position relative to image x=40, y=160, w=130, h=140
x = (DISPSIZE[0]/2 - 200) + 40 # centre minus half of the image width, plus kitten head X position in image
y = (DISPSIZE[1]/2 - 300) + 160 # centre minus half of the image height, plus kitten head Y position in image
aoi = AOI('rectangle',(x,y),(130,140))
disp.fill(scr)
t1 = disp.show()
log.write(["AOI", t1])
key = None
tracker.start_recording()
while key != 'space':
	# check for key input
	key, presstime = kb.get_key(keylist=['space'],timeout=1)
	# get gaze position
	gazepos = tracker.sample()
	# check if the gaze position is within the aoi
	if aoi.contains(gazepos):
		# play barking sound if gaze position is on kitten's head
		snd.play(repeats=-1)
	else:
		# do not play sound if gaze is somewhere else
		snd.stop()
snd.stop()
tracker.stop_recording()

# FRL
scr.clear()
scr.draw_text("There should be an image in the centre of the screen", pos=(DISPSIZE[0]/2, DISPSIZE[1]/10))
scr.draw_image(imagefile)
frl = FRL(pos='centre', dist=125, size=200)
disp.fill(scr)
t1 = disp.show()
log.write(["FRL", t1])
key = None
tracker.start_recording()
while key != 'space':
	# check for key input
	key, presstime = kb.get_key(keylist=['space'],timeout=1)
	# get gaze position
	gazepos = tracker.sample()
	# update FRL
	frl.update(disp, scr, gazepos)
tracker.stop_recording()

# GazeCursor
scr.clear()
scr.draw_text("The cursor should follow your gaze")
cursor = GazeCursor(ctype='arrow',size=20,colour=(0,0,0), pw=3, fill=True)
disp.fill(scr)
t1 = disp.show()
log.write(["GazeCursor", t1])
key = None
tracker.start_recording()
while key != 'space':
	# check for key input
	key, presstime = kb.get_key(keylist=['space'],timeout=1)
	# get gaze position
	gazepos = tracker.sample()
	# add new cursor to cleared screen
	scr.clear() # remove previous cursor
	scr.draw_text("The cursor should follow your gaze")
	scr = cursor.update(scr, gazepos) # adds new cursor
	# update display
	disp.fill(scr)
	disp.show()
tracker.stop_recording()


# # # # #
# close down

# ending screen
scr.clear()
scr.draw_text("That's all folks! Press Space to quit.")
disp.fill(scr)
t1 = disp.show()
log.write(["ending", t1])
kb.get_key()

# close
log.close()
tracker.close()
disp.close()
timer.expend()
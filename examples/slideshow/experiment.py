# natural viewing experiment
#
# Edwin S. Dalmaijer, University of Oxford
# contact: edwin.dalmaijer@psy.ox.ac.uk
#
# version 1 (28 Feb 2014)

# native
import os
import random

# PyGaze
from constants import *
from pygaze.libscreen import Display, Screen
from pygaze.libinput import Keyboard
from pygaze.eyetracker import EyeTracker
from pygaze.liblog import Logfile
import pygaze.libtime as timer


# # # # #
# SETUP

# visuals
disp = Display()
scr = Screen()

# input
kb = Keyboard()
tracker = EyeTracker(disp)

# output
log = Logfile()
log.write(["trialnr","image","imgtime"])


# # # # #
# PREPARE

# load instructions from file
instfile = open(INSTFILE)
instructions = instfile.read()
instfile.close()

# read all image names
images = os.listdir(IMGDIR)

# display instructions
scr.draw_text(text="Press any key to start the calibration.", fontsize=TEXTSIZE)
disp.fill(scr)
disp.show()

# wait for a keypress
kb.get_key(keylist=None, timeout=None, flush=True)

# calibrate the eye tracker
tracker.calibrate()


# # # # #
# RUN

# display task instructions
scr.clear()
scr.draw_text(text=instructions, fontsize=TEXTSIZE)
disp.fill(scr)
disp.show()

# wait for a keypress
kb.get_key(keylist=None, timeout=None, flush=True)

# loop through all trials
ntrials = len(images)
for trialnr in range(ntrials):
	
	# PREPARE TRIAL
	# draw the image
	scr.clear()
	scr.draw_image(os.path.join(IMGDIR,images[trialnr]))

	# perform a drift check
	tracker.drift_correction()
	
	# RUN TRIAL
	# start tracking
	tracker.start_recording()
	tracker.log("TRIALSTART %d" % trialnr)
	tracker.log("IMAGENAME %s" % images[trialnr])
	tracker.status_msg("trial %d/%d" % (trialnr+1, ntrials))
	
	# present image
	disp.fill(scr)
	t0 = disp.show()
	tracker.log("image online at %d" % t0)
	
	# wait for a bit
	timer.pause(TRIALTIME)
	
	# reset screen
	disp.fill()
	t1 = disp.show()
	tracker.log("image offline at %d" % t1)
	
	# stop recording
	tracker.log("TRIALEND %d" % trialnr)
	tracker.stop_recording()
	
	# TRIAL AFTERMATH
	# bookkeeping
	log.write([trialnr, images[trialnr], t1-t0])
	
	# inter trial interval
	timer.pause(ITI)


# # # # #
# CLOSE

# loading message
scr.clear()
scr.draw_text(text="Transferring the data file, please wait...", fontsize=TEXTSIZE)
disp.fill(scr)
disp.show()

# neatly close connection to the tracker
# (this will close the data file, and copy it to the stimulus PC)
tracker.close()

# close the logfile
log.close()

# exit message
scr.clear()
scr.draw_text(text="This is the end of this experiment. Thank you for participating!\n\n(press any key to exit)", fontsize=TEXTSIZE)
disp.fill(scr)
disp.show()

# wait for a keypress
kb.get_key(keylist=None, timeout=None, flush=True)

# close the Display
disp.close()

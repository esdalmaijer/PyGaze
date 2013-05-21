# example script for using PyGaze

# # # # #
# importing the relevant libraries
import random
from pygaze import libscreen
from pygaze import libtime
from pygaze import liblog
from pygaze import eyetracker

# # # # #
# setup the experiment

# start timing
libtime.expstart()

# create display object
disp = libscreen.Display()

# create eyetracker object
tracker = eyetracker.EyeTracker(disp, trackertype='dummy')

# create logfile object
log = liblog.Logfile()
log.write(["trialnr", "trialtype", "endpos", "latency", "correct"])

# create screens
fixscreen = libscreen.Screen()
fixscreen.draw_fixation(fixtype='cross',pw=2)
targetscreens = {}
targetscreens['left'] = libscreen.Screen()
targetscreens['left'].draw_circle(pos=(256,384), fill=True)
targetscreens['right'] = libscreen.Screen()
targetscreens['right'].draw_circle(pos=(768,384), fill=True)
feedbackscreens = {}
feedbackscreens[1] = libscreen.Screen()
feedbackscreens[1].draw_text(text='correct', colour=(0,255,0))
feedbackscreens[0] = libscreen.Screen()
feedbackscreens[0].draw_text(text='incorrect', colour=(255,0,0))

# # # # #
# run the experiment

# calibrate eye tracker
tracker.calibrate()

# run 20 trials
for trialnr in range(1,21):
	# prepare trial
	trialtype = random.choice(['left','right'])
	
	# drift correction
	disp.fill(fixscreen)
	disp.show()
	while not tracker.drift_correction():
		tracker.calibrate()
	
	# start eye tracking
	tracker.start_recording()
	tracker.status_msg("trial %d" % trialnr)
	tracker.log("start_trial %d trialtype %s" % (trialnr, trialtype))
	
	# present fixation
	disp.fill(screen=fixscreen)
	disp.show()
	tracker.log("fixation")
	libtime.pause(random.randint(750, 1250))
	
	# present target
	disp.fill(targetscreens[trialtype])
	t0 = disp.show()
	tracker.log("target %s" % trialtype)
	
	# wait for eye movement
	t1, startpos = tracker.wait_for_saccade_start()
	endtime, startpos, endpos = tracker.wait_for_saccade_end()
	
	# stop eye tracking
	tracker.stop_recording()
	
	# process input:
	if (trialtype == 'left' and endpos[0] < 512) or (trialtype == 'right' and endpos[0] > 512):
		correct = 1
	else:
		correct = 0
	
	# present feedback
	disp.fill(feedbackscreens[correct])
	disp.show()
	libtime.pause(500)
	
	# log stuff
	log.write([trialnr, trialtype, endpos, t1-t0, correct])

# end the experiment
log.close()
tracker.close()
disp.close()
libtime.expend()
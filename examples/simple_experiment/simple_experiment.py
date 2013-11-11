# example script for using PyGaze

# # # # #
# importing the relevant libraries
import random
import constants
from pygaze import libscreen
from pygaze import libtime
from pygaze import libinput
from pygaze import liblog

# # # # #
# setup the experiment

# create display object
disp = libscreen.Display()

# create keyboard object
kb = libinput.Keyboard(keylist=['left','right','escape'], timeout=2000)

# create logfile object
log = liblog.Logfile()
log.write(["trialnr", "trialtype", "response", "RT", "correct"])

# create screens
fixscreen = libscreen.Screen()
fixscreen.draw_fixation(fixtype='cross',pw=2)
targetscreens = {}
targetscreens['left'] = libscreen.Screen()
targetscreens['left'].draw_circle(pos=(constants.DISPSIZE[0]*0.25,constants.DISPSIZE[1]/2), fill=True)
targetscreens['right'] = libscreen.Screen()
targetscreens['right'].draw_circle(pos=(constants.DISPSIZE[0]*0.75,constants.DISPSIZE[1]/2), fill=True)
feedbackscreens = {}
feedbackscreens[1] = libscreen.Screen()
feedbackscreens[1].draw_text(text='correct', colour=(0,255,0))
feedbackscreens[0] = libscreen.Screen()
feedbackscreens[0].draw_text(text='incorrect', colour=(255,0,0))

# # # # #
# run the experiment

# run 20 trials
for trialnr in range(1,21):
	# prepare trial
	trialtype = random.choice(['left','right'])
	
	# present fixation
	disp.fill(screen=fixscreen)
	disp.show()
	libtime.pause(random.randint(750, 1250))
	
	# present target
	disp.fill(targetscreens[trialtype])
	t0 = disp.show()
	
	# wait for input
	response, t1 = kb.get_key()

	# end the experiment when 'escape' is pressed
	if response == 'escape':
		break
	
	# process input
	if response == trialtype:
		correct = 1
	else:
		correct = 0
	
	# present feedback
	disp.fill(feedbackscreens[correct])
	disp.show()
	libtime.pause(500)
	
	# log stuff
	log.write([trialnr, trialtype, response, t1-t0, correct])

# end the experiment
log.close()
disp.close()
libtime.expend() 

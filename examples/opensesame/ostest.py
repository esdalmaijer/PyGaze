# example script for using PyGaze
import random
from pygaze import Display, Screen, Keyboard, defaults, EyeTracker, libtime
from libopensesame.experiment import experiment

src = '/home/sebastiaan/git/opensesame/resources/templates/default.opensesame'
exp = experiment(string=src)
exp.init_display()
defaults.DISPTYPE = 'opensesame'
defaults.osexperiment = exp
defaults.FGC = 255,255,255
defaults.BGC = 0,0,0
w, h = defaults.DISPSIZE = exp.resolution()

# # # # #
# setup the experiment

# create display object
disp = Display(disptype='opensesame')

tracker = EyeTracker(disp, trackertype='dummy')
tracker.calibrate()

# create keyboard object
kb = Keyboard(disptype='opensesame', keylist=['left','right', \
	'escape'], timeout=2000)

# create screens
fixscreen = Screen(disptype='opensesame')
fixscreen.draw_fixation(fixtype='cross',pw=2)
targetscreens = {}
targetscreens['left'] = Screen(disptype='opensesame')
targetscreens['left'].draw_circle(pos=(w*0.25,h/2), fill=True)
targetscreens['right'] = Screen(disptype='opensesame')
targetscreens['right'].draw_circle(pos=(w*0.75,h/2), fill=True)
feedbackscreens = {}
feedbackscreens[1] = Screen(disptype='opensesame')
feedbackscreens[1].draw_text(text='correct', colour=(0,255,0))
feedbackscreens[0] = Screen(disptype='opensesame')
feedbackscreens[0].draw_text(text='incorrect', colour=(255,0,0))

# # # # #
# run the experiment

# run 20 trials
for trialnr in range(1,21):
	# prepare trial
	trialtype = random.choice(['left','right'])
	
	# Drift correction
	tracker.drift_correction()
	
	tracker.start_recording()
	
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
	
	tracker.stop_recording()
	

# end the experiment
disp.close()
libtime.expend() 

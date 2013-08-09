# PyGaze demo: simple gaze guided shooter
# version 2 (09-08-2013)
# E.S. Dalmaijer (edwin.dalmaijer@gmail.com)

import highscores
from constants import *

from pygaze import libtime
from pygaze.libscreen import Display, Screen
from pygaze.libinput import Keyboard
from pygaze.eyetracker import EyeTracker

import random

# # # # #
# prep

# create keyboard object
keyboard = Keyboard()

# display object
disp = Display()

# screen objects
screen = Screen()
blankscreen = Screen()
hitscreen = Screen()
hitscreen.clear(colour=(0,255,0))
misscreen = Screen()
misscreen.clear(colour=(255,0,0))

# create eyelink objecy
eyetracker = EyeTracker(disp)

# eyelink calibration
eyetracker.calibrate()

# display surface
disp.fill(screen=blankscreen)
disp.show()

# # # # #
# game

# run several rounds
for trialnr in range(0,TRIALS):
	
	# start eye tracking
	eyetracker.start_recording()
	eyetracker.log("start_trial %d" % trialnr)
	trialstart = libtime.get_time()

	# run game
	points = 0
	stimpos = STIMPOS
	t0 = libtime.get_time()
	tstim = libtime.get_time()
	while libtime.get_time() - t0 < GAMEDURATION:
		# get gaze position
		gazepos = eyetracker.sample()
		# get keypress
		key, presstime = keyboard.get_key()
		# handle input
		if key:
			if key == 'escape':
				break
			if ((gazepos[0]-stimpos[0])**2 + (gazepos[1]-stimpos[1])**2)**0.5 < STIMSIZE/2:
				screen.copy(hitscreen)
				points += PPH
			else:
				screen.copy(misscreen)
				points += PPM
		else:
			screen.copy(blankscreen)
		# draw stimulus
		screen.draw_circle(colour=STIMCOL, pos=stimpos, r=STIMSIZE/2, fill=True)
		# draw crosshair
		screen.draw_circle(colour=FGC, pos=gazepos, r=13, pw=2, fill=False)
		screen.draw_line(colour=FGC, spos=(gazepos[0]-15, gazepos[1]), epos=(gazepos[0]+15, gazepos[1]), pw=2)
		screen.draw_line(colour=FGC, spos=(gazepos[0], gazepos[1]-15), epos=(gazepos[0], gazepos[1]+15), pw=2)
		# draw point total
		screen.draw_text(text=str(points), colour=FGC, pos=(DISPSIZE[0]*0.9, DISPSIZE[1]*0.1), fontsize=FONTSIZE)
		# update display
		disp.fill(screen=screen)
		disp.show()
		# calculate new stimulus position
		if libtime.get_time() - tstim > STIMREFRESH:
			stimpos = (random.randint(int(DISPSIZE[0]*0.1),int(DISPSIZE[0]*0.9)), random.randint(int(DISPSIZE[1]*0.1),int(DISPSIZE[1]*0.9)))
			tstim = libtime.get_time()

	# stop eye tracking
	trialend = libtime.get_time()
	eyetracker.log("stop_trial %d" % trialnr)
	eyetracker.stop_recording()	


# # # # #
# end

# score display
screen.clear()
screen.draw_text(text="You have scored %d points!" % points, colour=FGC, pos=(DISPSIZE[0]/2, DISPSIZE[1]/2), fontsize=FONTSIZE)
disp.fill(screen=screen)
disp.show()

# wait for keypress
keyboard.get_key(keylist=None, timeout=None)

# highscore display
scorestring = highscores.update(LOGFILENAME, points)
screen.clear()
screen.draw_text(text=scorestring, colour=FGC, pos=(DISPSIZE[0]/2, DISPSIZE[1]/2), fontsize=FONTSIZE)
disp.fill(screen=screen)
disp.show()

# wait for keypress
keyboard.get_key(keylist=None, timeout=None)

# end connection to eye tracker
eyetracker.close()

# end timing and quit
libtime.expend()
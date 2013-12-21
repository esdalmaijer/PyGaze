# This script tests all non-eyetracker functions of PyGaze; run it to see if
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
# version: 21 Dec 2013

import os
import random

from pygaze.defaults import *
from constants import *

from pygaze.display import Display
from pygaze.screen import Screen
from pygaze.keyboard import Keyboard
from pygaze.mouse import Mouse
from pygaze.sound import Sound
from pygaze.time import Time
from pygaze.logfile import Logfile


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

# initialize a keyboard
kb = Keyboard(keylist=['space'],timeout=None)

# initialize a mouse
mouse = Mouse(mousebuttonlist=None, timeout=None)

# initialize a sound
snd = Sound(osc='sine', freq=4400, length=3000)
sounds = {
	'a sine wave (slightly oscillating)':Sound(osc='sine', freq=440, length=5000, attack=1000, decay=1000),
	'a saw wave':Sound(osc='saw', freq=880, length=5000, attack=0, decay=0),
	'a square wave':Sound(osc='square', freq=1760, length=5000, attack=0, decay=0),
	'white noise':Sound(osc='whitenoise'),
	'soundfile':Sound(soundfile=soundfile)
	}

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
# test Keyboard

# test set_keylist, set_timeout and get_key
scr.clear()
scr.draw_text("The keylist has been set to ['1','5','e','s','left','space']; \
please confirm that you can press these keys and not any other key. Note that \
if you press Space, the test will advance to the next phase! \
\n\n\nThis tests: \
\n- Keyboard.set_keylist \
\n- Keyboard.get_key \
\n- Keyboatd.set_timeout")
disp.fill(scr)
t1 = disp.show()
log.write(["Keyboard", t1])
kb.set_keylist(keylist=['1','5','e','s','left','space'])
kb.set_timeout(timeout=0.1)
key, presstime = kb.get_key()
kb.set_timeout(timeout=None)
while not key == 'space':
	# get new key
	key, presstime = kb.get_key()
	# draw the key name
	scr.clear()
	scr.draw_text("keylist = ['1','5','e','s','left','space']\n\nYou pressed:\n\n%s" % key)
	disp.fill(scr)
	disp.show()
kb.set_keylist(keylist=['space'])


# # # # #
# test Screen

scr.clear()
scr.draw_text("We're now going to test the screen module. Press Space to start!")
disp.fill(scr)
t1 = disp.show()
log.write(["Screem", t1])
kb.get_key()

#scr.copy()
# scr.draw_circle()
scr.clear()
scr.draw_text("There should be two circles on the screen: \
\nred filled on the left, and green unfilled on the right", pos=(DISPSIZE[0]/2, DISPSIZE[1]/4))
scr.draw_circle(colour=(255,0,0), pos=(DISPSIZE[0]*0.25,DISPSIZE[1]/2), r=DISPSIZE[0]/10, pw=5, fill=True)
scr.draw_circle(colour=(0,255,0), pos=(DISPSIZE[0]*0.75,DISPSIZE[1]/2), r=DISPSIZE[0]/10, pw=5, fill=False)
disp.fill(scr)
disp.show()
kb.get_key()

#scr.draw_ellipse()
scr.clear()
scr.draw_text("There should be two ellipses on the screen: \
\nred filled on the left, and green unfilled on the right", pos=(DISPSIZE[0]/2, DISPSIZE[1]/4))
scr.draw_ellipse(colour=(255,0,0), x=DISPSIZE[0]*0.25, y=DISPSIZE[1]/2, w=DISPSIZE[0]/10, h=DISPSIZE[0]/5, pw=5, fill=True)
scr.draw_ellipse(colour=(0,255,0), x=DISPSIZE[0]*0.75, y=DISPSIZE[1]/2, w=DISPSIZE[0]/10, h=DISPSIZE[0]/5, pw=5, fill=False)
disp.fill(scr)
disp.show()
kb.get_key()

#scr.draw_rect()
scr.clear()
scr.draw_text("There should be two rectangles on the screen: \
\nred filled on the left, and green unfilled on the right", pos=(DISPSIZE[0]/2, DISPSIZE[1]/4))
scr.draw_rect(colour=(255,0,0), x=DISPSIZE[0]*0.25, y=DISPSIZE[1]/2, w=DISPSIZE[0]/10, h=DISPSIZE[0]/5, pw=5, fill=True)
scr.draw_rect(colour=(0,255,0), x=DISPSIZE[0]*0.75, y=DISPSIZE[1]/2, w=DISPSIZE[0]/10, h=DISPSIZE[0]/5, pw=5, fill=False)
disp.fill(scr)
disp.show()
kb.get_key()

#scr.draw_line()
scr.clear()
scr.draw_text("There should be three lines on the screen: \
\nred oblique on the left, green horizontal in the centre, and blue vertical on the right", pos=(DISPSIZE[0]/2, DISPSIZE[1]/4))
scr.draw_line(colour=(255,0,0), spos=(DISPSIZE[0]*0.20,DISPSIZE[1]*0.45), epos=(DISPSIZE[0]*0.30,DISPSIZE[1]*0.55), pw=5)
scr.draw_line(colour=(0,255,0), spos=(DISPSIZE[0]*0.45,DISPSIZE[1]/2), epos=(DISPSIZE[0]*0.55,DISPSIZE[1]/2), pw=5)
scr.draw_line(colour=(0,0,255), spos=(DISPSIZE[0]*0.75,DISPSIZE[1]*0.45), epos=(DISPSIZE[0]*0.75,DISPSIZE[1]*0.55), pw=5)
disp.fill(scr)
disp.show()
kb.get_key()

#scr.draw_polygon()
scr.clear()
scr.draw_text("There should be two polygons on the screen: \
\nred filled triangle on the left, and green unfilled hexagon on the right", pos=(DISPSIZE[0]/2, DISPSIZE[1]/4))
pl = [(DISPSIZE[0]*0.25, DISPSIZE[1]*0.45), (DISPSIZE[0]*0.2, DISPSIZE[1]*0.55), (DISPSIZE[0]*0.3, DISPSIZE[1]*0.55)]
scr.draw_polygon(pl, colour=(255,0,0), pw=5, fill=True)
# topleft, topright, centreright, bottomright, bottomleft, centreleft
pl = [(DISPSIZE[0]*0.70, DISPSIZE[1]*0.40), (DISPSIZE[0]*0.80, DISPSIZE[1]*0.40), (DISPSIZE[0]*0.85, DISPSIZE[1]*0.5), (DISPSIZE[0]*0.80, DISPSIZE[1]*0.60), (DISPSIZE[0]*0.70, DISPSIZE[1]*0.60), (DISPSIZE[0]*0.65, DISPSIZE[1]*0.5)]
scr.draw_polygon(pl, colour=(0,255,0), pw=5, fill=False)
disp.fill(scr)
disp.show()
kb.get_key()

#scr.draw_fixation()
scr.clear()
scr.draw_text("There should be three fixation targets on the screen: \
\nred cross on the left, green X in the centre, and blue dot on the right", pos=(DISPSIZE[0]/2, DISPSIZE[1]/4))
scr.draw_fixation(fixtype='cross', colour=(255,0,0), pos=(DISPSIZE[0]*0.25,DISPSIZE[1]/2), pw=3, diameter=15)
scr.draw_fixation(fixtype='x', colour=(0,255,0), pos=(DISPSIZE[0]/2,DISPSIZE[1]/2), pw=3, diameter=15)
scr.draw_fixation(fixtype='dot', colour=(0,0,255), pos=(DISPSIZE[0]*0.75,DISPSIZE[1]/2), pw=3, diameter=15)
disp.fill(scr)
disp.show()
kb.get_key()

#scr.draw_image()
scr.clear()
scr.draw_text("There should be an image in the centre of the screen", pos=(DISPSIZE[0]/2, DISPSIZE[1]/10))
scr.draw_image(imagefile)
disp.fill(scr)
disp.show()
kb.get_key()

#scr.set_background_colour()
scr.set_background_colour(colour=(200,100,100))
scr.clear()
scr.draw_text("This screen should a different background colour than the previous screen", pos=(DISPSIZE[0]/2, DISPSIZE[1]/4))
disp.fill(scr)
disp.show()
kb.get_key()
scr.set_background_colour(BGC)


# # # # #
# test Mouse

scr.clear()
scr.draw_text("We're now going to test the mouse module. Press Space to start!")
t1 = disp.fill(scr)
log.write(["Mouse", t1])
disp.show()
kb.get_key()

#mouse.set_mousebuttonlist()
scr.clear()
scr.draw_text("The mousebuttonlist has been set to [1,2]; \
please confirm that you can press these buttons and not any other. Note that \
if you press Space, the test will advance to the next phase! \
\n\n\nThis tests: \
\n- mouse.set_mousebuttonlist \
\n- mouse.get_clicked \
\n- mouse.set_timeout")
disp.fill(scr)
disp.show()
mouse.set_mousebuttonlist(mousebuttonlist=[1,2])
mouse.set_timeout(timeout=1)
button, clickpos, clicktime = mouse.get_clicked()
key = None
while not key == 'space':
	# get new key
	key, presstime = kb.get_key(timeout=1)
	# get new button
	button, clickpos, clicktime = mouse.get_clicked()
	if button != None:
		# draw the key name
		scr.clear()
		scr.draw_text("mousebuttonlist = [1,2]\n\nYou pressed:\n\n%s" % str(button))
		disp.fill(scr)
		disp.show()
mouse.set_timeout(timeout=None)
mouse.set_mousebuttonlist(mousebuttonlist=None)

#mouse.set_visible()
scr.clear()
scr.draw_text("The mouse should now be visible.")
disp.fill(scr)
disp.show()
mouse.set_visible(visible=True)
kb.get_key()

#mouse.set_pos()
scr.clear()
scr.draw_text("The mouse should now jump to random positions.")
disp.fill(scr)
disp.show()
key = None
while not key == 'space':
	# get new key
	key, presstime = kb.get_key(timeout=1)
	# new position
	x = random.randint(1,DISPSIZE[0]-1)
	y = random.randint(1,DISPSIZE[1]-1)
	# set mouse position
	mouse.set_pos(pos=(x,y))

#mouse.get_pos()
scr.clear()
scr.draw_text("The dot should follow your mouse movements")
disp.fill(scr)
disp.show()
mouse.set_visible(visible=True)
key = None
while not key == 'space':
	# get new key
	key, presstime = kb.get_key(timeout=1)
	# new states
	mpos = mouse.get_pos()
	# draw to screen
	scr.clear()
	scr.draw_text("The dot should follow your mouse movements")
	scr.draw_fixation(fixtype='dot', pos=mpos, pw=3, diameter=15)
	disp.fill(scr)
	disp.show()
mouse.set_visible(visible=False)
scr.clear()

#mouse.get_pressed()
key = None
while not key == 'space':
	# get new key
	key, presstime = kb.get_key(timeout=1)
	# new position
	state = mouse.get_pressed()
	# draw to screen
	scr.clear()
	scr.draw_text("The current mouse state is %s; press any buttons to test" % str(state))
	scr.draw_fixation(fixtype='dot', pos=mpos, pw=3, diameter=15)
	disp.fill(scr)
	disp.show()


# # # # #
# test Sound

scr.clear()
scr.draw_text("We're now going to test the sound module. Press Space to start!")
disp.fill(scr)
t1 = disp.show()
log.write(["Sound", t1])
kb.get_key()

# loop through sound waves
for sound in sounds.keys():
	scr.clear()
	scr.draw_text("You should now hear %s. Press Space to continue." % sound)
	disp.fill(scr)
	disp.show()
	sounds[sound].play(repeats=-1)
	kb.get_key()
	sounds[sound].stop()

#snd.pan()
panning = 'right'
key = None
while not key == 'space':
	# new panning
	if panning == 'left':
		panning = 'right'
	elif panning == 'right':
		panning = 'left'
	# apply panning
	snd.stop()
	snd.pan(panning)
	snd.play(repeats=-1)
	# show text
	scr.clear()
	scr.draw_text("The sound should come from your %s." % panning)
	disp.fill(scr)
	disp.show()
	# get new key
	key, presstime = kb.get_key(timeout=2000)
snd.stop()
snd.pan(0)

#snd.set_volume()
scr.clear()
scr.draw_text("The sound should now be oscillating in volume.")
disp.fill(scr)
disp.show()
snd.play(repeats=-1)
volume = 0
volfactor = 0.05
key = None
while not key == 'space':
	# get new key
	key, presstime = kb.get_key(timeout=20)
	# new volume
	volume += volfactor
	# correct volume
	if volume < 0:
		volume = 0
		volfactor *= -1
	elif volume > 1:
		volume = 1
		volfactor *= -1
	# apply volume
	snd.set_volume(volume)
snd.stop()


# # # # #
# test timing module

scr.clear()
scr.draw_text("We're now going to test the time module. Press Space to start!")
disp.fill(scr)
t1 = disp.show()
log.write(["Time", t1])
kb.get_key()

#time.get_time()
scr.clear()
scr.draw_text("The time passed from the experiment beginning is: %s" % '00:00:00:000')
disp.fill(scr)
disp.show()
key = None
while not key == 'space':
	# get new key
	key, presstime = kb.get_key(timeout=1)
	# get time (in milliseconds)
	ms = timer.get_time()
	# hours, minutes, seconds, milliseconds
	h = int(ms / 3600000); ms -= h*3600000
	m = int(ms / 60000); ms -= m*60000
	s = int(ms / 1000); ms -= s*1000
	ms = int(ms)
	# timestring
	timestring = "%s:%s:%s:%s" % (h, m, s, ms)
	# display
	scr.clear()
	scr.draw_text("The time passed from the experiment beginning is: %s" % timestring)
	disp.fill(scr)
	disp.show()

#time.pause()
scr.clear()
scr.draw_text("After you press space, the PyGaze test will pause for three seconds")
disp.fill(scr)
disp.show()
kb.get_key()
timer.pause(3000)


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
disp.close()
timer.expend()
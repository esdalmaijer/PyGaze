# Display a message on your display until space is pressed
#
# handy for when you're away from your desk and want your
# co-workers to REALLY know (and possibly have a seizure)
#
# E.S. Dalmaijer, 2013

# your message
MESSAGE = "AFK; BRB"

# import stuff
import random
from pygaze.defaults import *
from pygaze.libscreen import Display, Screen
from pygaze.libinput import Keyboard

# objects
disp = Display()
scr = Screen()
kb = Keyboard(keylist=['space'],timeout=1)

# run annoying message
while kb.get_key()[0] == None:
	# colour
	col = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
	# position
	pos = (random.randint(0,DISPSIZE[0]), random.randint(0,DISPSIZE[1]))
	# text
	scr.draw_text(text=MESSAGE, colour=col, pos=pos, fontsize=84)
	# display
	disp.fill(scr)
	disp.show()
	# reset screen
	scr.clear()
	
# stop the madness
disp.close()

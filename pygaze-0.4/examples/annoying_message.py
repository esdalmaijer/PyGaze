import random

from pygaze.defaults import *
from pygaze import libtime
from pygaze.libscreen import Display, Screen
from pygaze.libinput import Keyboard

# start timing
libtime.expstart()

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
	scr.draw_text(text="AFK; BRB", colour=col, pos=pos, fontsize=84)
	# display
	disp.fill(scr)
	disp.show()
	# reset screen
	scr.clear()
	
# stop the madness
disp.close()
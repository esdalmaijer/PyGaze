# This file is a PyGaze experiment designed to demonstrate the webcam library.
# It assumes you have installed the webcam library in the PyGaze directory,
# along with all the other libraries (e.g. libscreen). Alternatively, you
# could include libwebcam in the directory that this file is in.
#
# author: Edwin S. Dalmaijer
# date: 09-10-2013


from constants import *
from pygaze.libscreen import Display, Screen
from pygaze.libinput import Keyboard

# first, we try to import libwebcam from PyGaze
try:
	from pygaze import libwebcam
# if importing from PyGaze fails, we try to import from the current directory
except:
	import libwebcam


# # # # #
# preparation

# visual
disp = Display()
scr = Screen()

# input
kb = Keyboard()

# webcam
camlist = libwebcam.available_devices()
cam = libwebcam.Camera(dev=camlist[0], devtype=DEVTYPE, resolution=CAMRES, verflip=VFLIP, horflip=HFLIP)


# # # # #
# run camera display

# some variables
stopped = False

# loop until a key is pressed
while not stopped:
	# get new image
	img = cam.get_image()
	# draw it on the Screen
	scr.draw_image(img)
	# update Display
	disp.fill(scr)
	disp.show()
	# check input
	stopped, stoptime = kb.get_key()


# # # # #
# quit

# neatly close
cam.close()
disp.close()
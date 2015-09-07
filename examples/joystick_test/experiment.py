import ctypes

from constants import *
from pygaze.display import Display
from pygaze.screen import Screen
from pygaze.joystick import Joystick
import pygaze.libtime as timer


# # # # #
# VIBRATION

if RUMBLE:
	# define necessary structure
	class XINPUT_VIBRATION(ctypes.Structure):
		_fields_ = [("wLeftMotorSpeed", ctypes.c_ushort),
			("wRightMotorSpeed", ctypes.c_ushort)]
	# load Xinput.dll
	try:
		print("trying to import xinput1_1.dll")
		xinput = ctypes.windll.xinput1_1
	except:
		try:
			print("trying to import xinput1_3.dll")
			xinput = ctypes.windll.xinput1_3
		except:
			try:
				print("trying to import XInput9_1_0.dll")
				xinput = ctypes.windll.XInput9_1_0
			except:
				print("ERROR: No xinput DLL found, cannot use rumble function.")
				RUMBLE = False
	# set up function argument types and return type
	XInputSetState = xinput.XInputSetState
	XInputSetState.argtypes = [ctypes.c_uint, ctypes.POINTER(XINPUT_VIBRATION)]
	XInputSetState.restype = ctypes.c_uint
	# define helper function
	def set_vibration(controller, left_motor, right_motor):
	    vibration = XINPUT_VIBRATION(int(left_motor * 65535), int(right_motor * 65535))
	    XInputSetState(controller, ctypes.byref(vibration))


# # # # #
# PYGAZE INSTANCES

# visual
disp = Display()
scr = Screen()
# input
js = Joystick()


# # # # #
# RUN

# run until a minute has passed
t0 = timer.get_time()
t1 = timer.get_time()
text = "Test the joystick!"
while t1 - t0 < 60000:
	# get joystick input
	event, value, t1 = js.get_joyinput(timeout=10)
	# update text
	if event != None:
		text = text="%s: %s" % (event, value)
		if event == 'joyaxismotion' and RUMBLE:
			set_vibration(0, max(0, value[2]), max(0, -value[2]))
	# display on screen
	scr.clear()
	scr.draw_text(text="%s\n\n(%.2f)" % (text, float(t1-t0)/1000.0), fontsize=24)
	# show text
	disp.fill(scr)
	disp.show()


# # # # #
# CLOSE

# reset rumble to 0
if RUMBLE:
	set_vibration(0, 0, 0)
# close the Display
disp.close()

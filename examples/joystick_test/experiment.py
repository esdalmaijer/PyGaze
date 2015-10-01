import ctypes
import os

import pygaze.libtime as timer
from pygaze.display import Display
from pygaze.joystick import Joystick
from pygaze.screen import Screen


DISPTYPE = 'pygame'
DISPSIZE = (1920, 1080)

VIBRATION = os.name == u'nt'


if VIBRATION:
    class XINPUT_VIBRATION(ctypes.Structure):
        _fields_ = [('wLeftMotorSpeed', ctypes.c_ushort),
                    ('wRightMotorSpeed', ctypes.c_ushort)]


    try:
        print 'trying to import xinput1_1.dll'
        xinput = ctypes.windll.xinput1_1
    except Exception:
        try:
            print 'trying to import xinput1_3.dll'
            xinput = ctypes.windll.xinput1_3
        except Exception:
            try:
                print 'trying to import XInput9_1_0.dll'
                xinput = ctypes.windll.XInput9_1_0
            except Exception:
                print 'ERROR: No xinput DLL found, cannot use rumble function.'
                VIBRATION = False

    # set up function argument types and return type
    XInputSetState = xinput.XInputSetState
    XInputSetState.argtypes = [ctypes.c_uint, ctypes.POINTER(XINPUT_VIBRATION)]
    XInputSetState.restype = ctypes.c_uint

    # define helper function
    def set_vibration(controller, left_motor, right_motor):
        vibration = XINPUT_VIBRATION(int(left_motor * 65535),
                                     int(right_motor * 65535))
        XInputSetState(controller, ctypes.byref(vibration))


disp = Display()
scr = Screen()

js = Joystick()


t0 = timer.get_time()
t1 = timer.get_time()
text = 'Test the joystick!'
while t1 - t0 < 60000:
    # get joystick input
    event, value, t1 = js.get_joyinput(timeout=10)
    # update text
    if event:
        text = '%s: %s' % (event, value)
        if event == 'joyaxismotion' and VIBRATION:
            set_vibration(0, max(0, value[2]), max(0, -value[2]))

    scr.clear()
    scr.draw_text(text='%s\n\n(%.2f)' % (text, float(t1-t0)/1000.0),
                  fontsize=24)

    disp.fill(scr)
    disp.show()


if VIBRATION:
    set_vibration(0, 0, 0)

disp.close()

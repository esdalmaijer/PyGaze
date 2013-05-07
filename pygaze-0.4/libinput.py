## This file is part of PyGaze - the open-source toolbox for eye tracking
##
##    PyGaze is a Python module for easily creating gaze contingent experiments
##    or other software (as well as non-gaze contingent experiments/software)
##    Copyright (C) 2012-2013  Edwin S. Dalmaijer
##
##    This program is free software: you can redistribute it and/or modify
##    it under the terms of the GNU General Public License as published by
##    the Free Software Foundation, either version 3 of the License, or
##    (at your option) any later version.
##
##    This program is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.
##
##    You should have received a copy of the GNU General Public License
##    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
# version: 0.4 (25-03-2013), NOT RELEASED FOR USE OUTSIDE OF UTRECHT UNIVERSITY)
#
# Many thanks to Sebastiaan Mathot. The libinput is a modified version of parts of
# the OpenSesame experiment builder (www.cogsci.nl/opensesame) and the joystick
# plugin for OpenSesame (by Edwin Dalmaijer and Sebastiaan Mathot).

try:
    import constants
except:
    import defaults as constants
    
import libtime
from libscreen import pos2psychopos, psychopos2pos

if constants.DISPTYPE == 'psychopy':
    import psychopy.event
else:
    import pygame


class Mouse:

    """A mouse for collecting responses"""

    def __init__(self, disptype=constants.DISPTYPE, mousebuttonlist=constants.MOUSEBUTTONLIST, timeout=constants.MOUSETIMEOUT, visible=False):

        """Initializes the Mouse object"""

        if disptype in ['pygame','psychopy']:
            self.disptype = disptype
        else:
            self.disptype = 'pygame'
            print("Error in libinput.Mouse.__init__: disptype not recognized; set to default ('pygame')")

        if self.disptype == 'pygame':
            self.__class__ = PyGameMouse
        elif self.disptype == 'psychopy':
            self.__class__ = PsychoPyMouse
        else:
            self.__class__ = PyGameMouse
            print("Error in libscreen.Mouse.__init__: self.disptype was not recognized, which is very unexpected and should not happen! PyGameMouse is used")

        # create mouse
        self.__init__(mousebuttonlist=mousebuttonlist, timeout=timeout, visible=visible)


class PyGameMouse:

    """A mouse for collecting responses"""

    import pygame.mouse

    def __init__(self, mousebuttonlist=constants.MOUSEBUTTONLIST, timeout=constants.MOUSETIMEOUT, visible=False):

        """Initializes mouse object (mousebuttonlist: list of buttons; timeout: timeout in ms)"""

        # set mouse characteristics
        self.set_mousebuttonlist(mousebuttonlist)
        self.set_timeout(timeout)
        self.set_visible(visible=visible)


    def set_mousebuttonlist(self, mousebuttonlist=None):

        """Set a list of accepted mouse buttons"""
        
        if mousebuttonlist == None or mousebuttonlist == []:
            self.mbuttonlist = None
        else:
            self.mbuttonlist = []
            for mbutton in mousebuttonlist:
                self.mbuttonlist.append(mbutton)


    def set_timeout(self, timeout=None):

        """Set a timeout (in milliseconds)"""

        self.timeout = timeout


    def set_visible(self, visible=True):

        """Sets the visibility of the cursor (visible=True or False)"""

        self.visible = visible
        pygame.mouse.set_visible(visible)


    def set_pos(self, pos=(0,0)):

        """Set the mouse position (pos=(x,y))"""

        pygame.mouse.set_pos(pos)


    def get_pos(self):

        """Returns mouse position (x,y)"""

        mpos = pygame.mouse.get_pos()

        return mpos


    def get_clicked(self, mousebuttonlist='default', timeout='default'):

        """Waits for mouse clicks (returns: mousebutton, clickpos, clicktime)"""

        # set buttonlist and timeout
        if mousebuttonlist == 'default':
            mousebuttonlist = self.mbuttonlist
        if timeout == 'default':
            timeout = self.timeout
        # starttime
        starttime = libtime.get_time()
        time = libtime.get_time()
        # wait for mouse clicks
        while timeout == None or time - starttime <= timeout:
            time = libtime.get_time()
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    time = libtime.get_time()
                    clickpos = self.get_pos()
                    if mousebuttonlist == None or event.button in mousebuttonlist:
                        pressed = event.button
                        return pressed, clickpos, time
        # in case of timeout
        return None, None, time


    def get_pressed(self):

        """Returns the current state of the mouse buttons (e.g. [1,0,0] when only button 1 is pressed)"""

        pygame.event.get()
        return pygame.mouse.get_pressed()


class PsychoPyMouse:

    """A mouse for collecting responses"""

    def __init__(self, mousebuttonlist=constants.MOUSEBUTTONLIST, timeout=constants.MOUSETIMEOUT, visible=False):

        """Initializes mouse object (mousebuttonlist: list of buttons; timeout: timeout in ms)"""

        # create mouse object
        self.mouse = psychopy.event.Mouse(visible=False,win=psychopy.visual.openWindows[constants.SCREENNR])
        
        # set mouse characteristics
        self.set_mousebuttonlist(mousebuttonlist)
        self.set_timeout(timeout)
        self.set_visible(visible=visible)


    def set_mousebuttonlist(self, mousebuttonlist=None):

        """Set a list of accepted mouse buttons"""
        
        if mousebuttonlist == None or mousebuttonlist == []:
            self.mbuttonlist = None
        else:
            self.mbuttonlist = []
            for mbutton in mousebuttonlist:
                self.mbuttonlist.append(mbutton)


    def set_timeout(self, timeout=None):

        """Set a timeout (in milliseconds)"""

        self.timeout = timeout


    def set_visible(self, visible=True):

        """Sets the visibility of the cursor (visible=True or False)"""

        self.visible = visible
        self.mouse.setVisible(self.visible)


    def set_pos(self, pos=(0,0)):

        """Set the mouse position (pos=(x,y))"""

        self.mouse.setPos(newPos=pos2psychopos(pos))


    def get_pos(self):

        """Returns mouse position (x,y)"""

        return psychopos2pos(self.mouse.getPos())


    def get_clicked(self, mousebuttonlist='default', timeout='default'):

        """Waits for mouse clicks (returns: mousebutton, clickpos, clicktime)"""

        # set buttonlist and timeout
        if mousebuttonlist == 'default':
            mousebuttonlist = self.mbuttonlist
        if timeout == 'default':
            timeout = self.timeout
        # starttime
        starttime = libtime.get_time()
        time = libtime.get_time()
        # wait for mouse clicks
        while timeout == None or time - starttime <= timeout:
            time = libtime.get_time()
            pressed = self.mouse.getPressed()
            if sum(pressed) > 0:
                for b in range(0,len(pressed)):
                    if pressed[b] == 1:
                        if mousebuttonlist == None or b+1 in mousebuttonlist:
                            return b+1, self.get_pos(), time
        # in case of timeout
        return None, None, time


    def get_pressed(self):

        """Returns the current state of the mouse buttons (e.g. [1,0,0] when only button 1 is pressed)"""

        return self.mouse.getPressed()


class Keyboard:

    """A keyboard for collecting responses"""

    def __init__(self, disptype=constants.DISPTYPE, keylist=constants.KEYLIST, timeout=constants.KEYTIMEOUT):

        """Initializes the Keyboard object"""

        if disptype in ['pygame','psychopy']:
            self.disptype = disptype
        else:
            self.disptype = 'pygame'
            print("Error in libinput.Keyboard.__init__: disptype not recognized; set to default ('pygame')")

        if self.disptype == 'pygame':
            self.__class__ = PyGameKeyboard
        elif self.disptype == 'psychopy':
            self.__class__ = PsychoPyKeyboard
        else:
            self.__class__ = PyGameKeyboard
            print("Error in libscreen.Keyboard.__init__: self.disptype was not recognized, which is very unexpected and should not happen! PyGameKeyboard is used")

        # create keyboard
        self.__init__(keylist=keylist, timeout=timeout)


class PyGameKeyboard:

    """A keyboard for collecting responses"""

    import pygame.key

    def __init__(self, keylist=constants.KEYLIST, timeout=constants.KEYTIMEOUT):

        """Initializes keyboard object (keylist: list of keys; timeout: timeout in ms)"""

        # dictionary for keynames and codes
        self.key_codes = {}
        for i in dir(pygame):
            if i[:2] == "K_":
                code = eval("pygame.%s" % i)
                name1 = pygame.key.name(code).lower()
                name2 = name1.upper()
                name3 = i[2:].lower()
                name4 = name3.upper()
                self.key_codes[name1] = code
                self.key_codes[name2] = code
                self.key_codes[name3] = code
                self.key_codes[name4] = code

        # set keyboard characteristics
        self.set_keylist(keylist)
        self.set_timeout(timeout)
    
    def set_keylist(self, keylist=None):

        """Set a list of accepted keys"""
        
        if keylist == None or keylist == []:
            self.klist = None
        else:
            self.klist = []
            for key in keylist:
                self.klist.append(self.to_int(key))


    def set_timeout(self, timeout=None):

        """Set a timeout (in milliseconds)"""

        self.timeout = timeout


    def get_key(self, keylist='default', timeout='default'):

        """Wait for keyboard input (returns: key pressed, presstime)"""
        
        # set keylist and timeout
        if keylist == 'default':
            keylist = self.klist
        if timeout == 'default':
            timeout = self.timeout
            
        # starttime
        starttime = libtime.get_time()
        time = libtime.get_time()

        # wait for input
        while timeout == None or time - starttime <= timeout:
            time = libtime.get_time()
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    time = libtime.get_time()
                    key = pygame.key.name(event.key)
                    if keylist == None or key in keylist:
                        return key, time
                    
        # in case of timeout
        return None, time


class PsychoPyKeyboard:

    """A keyboard for collecting responses"""

    def __init__(self, keylist=constants.KEYLIST, timeout=constants.KEYTIMEOUT):

        """Initializes keyboard object (keylist: list of keys; timeout: timeout in ms)"""

        # keymap
	self.keymap = {
		'!' : 'exclamation',
		'"' : 'doublequote',
		'#' : 'hash',
		'$' : 'dollar',
		'&' : 'ampersand',
		'\'' : 'quoteleft',
		'(' : None,
		')' : None,
		'*' : 'asterisk',
		'+' : 'plus',
		',' : 'comma',
		'-' : 'minus',
		'.' : None,
		'/' : 'slash',
		':' : 'colin',
		';' : 'semicolon',
		'=' : 'equal',
		'>' : 'greater',
		'?' : 'question',
		'@' : 'at',
		'[' : 'bracketleft',
		'\\' : 'backslash',
		']' : 'bracketright',
		'^' : None,
		'_' : 'underscore'
		}

        # set keyboard characteristics
        self.set_keylist(keylist)
        self.set_timeout(timeout)
    
    def set_keylist(self, keylist=None):

        """Set a list of accepted keys"""
        
        if keylist == None or keylist == []:
            self.klist = None
        else:
            self.klist = []
            for key in keylist:
                if key in self.keymap:
                    self.klist.append(self.keymap[key])
                else:
                    self.klist.append(key)


    def set_timeout(self, timeout=None):

        """Set a timeout (in milliseconds)"""

        self.timeout = timeout


    def get_key(self, keylist='default', timeout='default'):

        """Wait for keyboard input (returns: key pressed, presstime)"""
        
        # set keylist and timeout
        if keylist == 'default':
            keylist = self.klist
        if timeout == 'default':
            timeout = self.timeout

        # starttime
        starttime = libtime.get_time()
        time = libtime.get_time()

        # wait for input
        while timeout == None or time - starttime <= timeout:
            keys = psychopy.event.getKeys(keyList=keylist,timeStamped=True)
            for key, time in keys:
                time = time * 1000.0
                if keylist == None or key in keylist:
                    return key, time
            time = libtime.get_time()

        return None, time


class Joystick:

    from pygame.joystick import Joystick

    """A joystick for collecting responses"""

    def __init__(self, joybuttonlist=constants.JOYBUTTONLIST, timeout=constants.JOYTIMEOUT):

        """Initializes joystick object (joybuttonlist: list of buttons; timeout: timeout in ms)"""

        # initialize joystick
        pygame.init()
        self.js = pygame.joystick.Joystick(0)

        # set joystick characteristics
        self.set_joybuttonlist(joybuttonlist)
        self.set_timeout(timeout)


    def set_joybuttonlist(self, joybuttonlist=None):

        """Set a list of accepted joystick buttons"""

        if joybuttonlist == None or joybuttonlist == []:
            self.jbuttonlist = None
        else:
            self.jbuttonlist = []
            for joybutton in joybuttonlist:
                self.jbuttonlist.append(joybutton)


    def set_timeout(self, timeout=None):

        """Set a timeout (in milliseconds)"""

        self.timeout = timeout


    def get_joybutton(self, joybuttonlist='default', timeout='default'):

        """Waits for joystick buttonpress (returns: button, press time)"""

        # set joybuttonlist and timeout
        if joybuttonlist == 'default':
            joybuttonlist = self.jbuttonlist
        if timeout == 'default':
            timeout = self.timeout
        # register start time
        starttime = libtime.get_time()
        time = starttime
        # wait for button press
        while timeout == None or time - starttime <= timeout:
            time = libtime.get_time()
            for event in pygame.event.get():
                if event.type == JOYBUTTONDOWN:
                    time = libtime.get_time()
                    if joybuttonlist == None or event.button in joybuttonlist:
                        pressed = event.button
                        return pressed, time
        # in case of timeout
        return None, time


    def get_joyaxes(self, timeout='default'):

        """Waits for joystick axis movement (returns: position list [x,y,z], movement time)"""

        # set timeout
        if timeout == 'default':
            timeout = self.timeout
        # start time and pos
        pos = []
        starttime = libtime.get_time()
        time = starttime
        # wait for axis movement
        while timeout == None or time - starttime <= timeout:
            time = libtime.get_time()
            for event in pygame.event.get():
                if event.type == JOYAXISMOTION:
                    time = libtime.get_time()
                    for axis in range(self.js.get_numaxes()):
                        pos.append(self.js.get_axis(axis))
                    return pos, time
        # in case of timeout
        return None, time


    def get_joyballs(self, timeout='default'):

        """Waits for joystick trackball movement (returns: position list [ball1,ball2,...ballN], movement time)"""

        # set timeout
        if timeout == 'default':
            timeout = self.timeout
        # start time and pos
        ballpos = []
        starttime = libtime.get_time()
        time = starttime
        # wait for axis movement
        while timeout == None or time - starttime <= timeout:
            time = libtime.get_time()
            for event in pygame.event.get():
                if event.type == JOYBALLMOTION:
                    time = libtime.get_time()
                    for ball in range(self.js.get_numballs()):
                        ballpos.append(self.js.get_ball(ball))
                    return ballpos, time
        # in case of timeout
        return None, time


    def get_joyhats(self, timeout='default'):

        """Waits for joystick hat movement (returns: position list [ball1,ball2,...ballN], movement time)"""

        # set timeout
        if timeout == 'default':
            timeout = self.timeout
        # start time and pos
        hatpos = []
        starttime = libtime.get_time()
        time = starttime
        # wait for axis movement
        while timeout == None or time - starttime <= timeout:
            time = libtime.get_time()
            for event in pygame.event.get():
                if event.type == JOYHATMOTION:
                    time = libtime.get_time()
                    for hat in range(self.js.get_numhats()):
                        hatpos.append(self.js.get_hat(hat))
                    return hatpos, time
        # in case of timeout
        return None, time


    def get_joyinput(self, buttonlist='default', timeout='default'):

        """Waits for any kind of joystick input (returns: eventtype*, button or position list, input time)
        *eventtypes: 'joybuttonpress', 'joyaxismotion', 'joyballmotion', 'joyhatmotion' or None (after timeout)"""

        # set joybuttonlist and timeout
        if joybuttonlist == 'default':
            joybuttonlist = self.jbuttonlist
        if timeout == 'default':
            timeout = self.timeout
        # start values
        pos = []
        ballpos = []
        hatpos = []
        eventtype = None
        starttime = libtime.get_time()
        time = starttime
        # wait for input
        while timeout == None or time - starttime <= timeout:
            time = libtime.get_time()
            for event in pygame.event.get():
                if event.type == JOYBUTTONDOWN:
                    time = libtime.get_time()
                    if joybuttonlist == None or event.button in joybuttonlist:
                        eventtype = 'joybuttonpress'
                        pressed = event.button
                        return eventtype, pressed, time
                if event.type == JOYAXISMOTION:
                    time = libtime.get_time()
                    eventtype = 'joyaxismotion'
                    for axis in range(self.js.get_numaxes()):
                        pos.append(self.js.get_axis(axis))
                    return eventtype, pos, time
                if event.type == JOYBALLMOTION:
                    time = libtime.get_time()
                    eventtype = 'joyballmotion'
                    for ball in range(self.js.get_numballs()):
                        ballpos.append(self.js.get_ball(ball))
                    return eventtype, ballpos, time
                if event.type == JOYHATMOTION:
                    time = libtime.get_time()
                    eventtype = 'joyhatmotion'
                    for hat in range(self.js.get_numhats()):
                        hatpos.append(self.js.get_hat(hat))
                    return eventtype, hatpos, time
        # in case of timeout
        return eventtype, None, time
    

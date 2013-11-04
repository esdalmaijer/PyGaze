# -*- coding: utf-8 -*-
#
# This file is part of PyGaze - the open-source toolbox for eye tracking
#
#	PyGaze is a Python module for easily creating gaze contingent experiments
#	or other software (as well as non-gaze contingent experiments/software)
#	Copyright (C) 2012-2013  Edwin S. Dalmaijer
#
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with this program.  If not, see <http://www.gnu.org/licenses/>

from defaults import *
try:
	from constants import *
except:
	pass
	
import libtime
from libscreen import pos2psychopos, psychopos2pos

if DISPTYPE == 'psychopy':
	import psychopy.event
else:
	import pygame


class Mouse:

	"""A mouse for collecting responses"""

	def __init__(self, disptype=DISPTYPE, mousebuttonlist=MOUSEBUTTONLIST, timeout=MOUSETIMEOUT, visible=False):

		"""Initializes the Mouse object
		
		arguments
		None
		
		keyword arguments
		disptype	-- display type, either 'psychopy' or 'pygame' (default
				   = DISPTYPE)
		mousebuttonlist	-- list of mouse buttons that are allowed (e.g.
					   [1,3] for left and right button) or None to
					   allow all buttons (default =
					   MOUSEBUTTONLIST)
		timeout	-- time in milliseconds after which None is returned
				   on a call to get_clicked method when no click is
				   registered (default = MOUSETIMEOUT)
		visible	-- Boolean indicating if mouse should be visible or not
				   (default = False)
		"""

		if disptype in ['pygame','psychopy']:
			self.disptype = disptype
		else:
			self.disptype = 'pygame'
			print("WARNING! libinput.Mouse.__init__: disptype not recognized; set to default ('pygame')")

		if self.disptype == 'pygame':
			self.__class__ = PyGameMouse
		elif self.disptype == 'psychopy':
			self.__class__ = PsychoPyMouse
		else:
			self.__class__ = PyGameMouse
			print("WARNING! libscreen.Mouse.__init__: self.disptype was not recognized, which is very unexpected and should not happen! PyGameMouse is used")

		# create mouse
		self.__init__(mousebuttonlist=mousebuttonlist, timeout=timeout, visible=visible)


class PyGameMouse:

	"""A mouse for collecting responses"""

	import pygame.mouse

	def __init__(self, mousebuttonlist=MOUSEBUTTONLIST, timeout=MOUSETIMEOUT, visible=False):

		"""Initializes mouse object
		
		arguments
		None
		
		keyword arguments
		mousebuttonlist	-- list of mouse buttons that are allowed (e.g.
					   [1,3] for left and right button) or None to
					   allow all buttons (default =
					   MOUSEBUTTONLIST)
		timeout	-- time in milliseconds after which None is returned
				   on a call to get_clicked method when no click is
				   registered (default = MOUSETIMEOUT)
		visible	-- Boolean indicating if mouse should be visible or not
				   (default = False)
		"""

		# set mouse characteristics
		self.set_mousebuttonlist(mousebuttonlist)
		self.set_timeout(timeout)
		self.set_visible(visible=visible)


	def set_mousebuttonlist(self, mousebuttonlist=None):

		"""Set a list of accepted mouse buttons
		
		arguments
		None
		
		keyword arguments
		mousebuttonlist	-- list of mouse buttons that are allowed (e.g.
					   [1,3] for left and right button) or None to
					   allow all buttons (default = None)
		
		returns
		Nothing	-- sets mbuttonlist property
		"""
		
		if mousebuttonlist == None or mousebuttonlist == []:
			self.mbuttonlist = None
		else:
			self.mbuttonlist = []
			for mbutton in mousebuttonlist:
				self.mbuttonlist.append(mbutton)


	def set_timeout(self, timeout=None):

		"""Set a timeout (in milliseconds)
		
		arguments
		None
		
		keyword arguments
		timeout	-- time in milliseconds after which None is returned
				   on a call to get_clicked method when no click is
				   registered (default = None)
		
		returns
		Nothing	-- sets timeout property
		"""

		self.timeout = timeout


	def set_visible(self, visible=True):

		"""Sets the visibility of the cursor
		
		arguments
		None
		
		keyword arguments
		visible	-- Boolean indicating if mouse should be visible or not
				   (default = False)
		
		returns
		Nothing	-- sets visible property
		"""

		self.visible = visible
		pygame.mouse.set_visible(visible)


	def set_pos(self, pos=(0,0)):

		"""Set the mouse position
		
		arguments
		None
		
		keyword arguments
		pos		-- an (x,y) position tuple, assuming top left is (0,0)
				   (default = (0,0))
		
		returns
		Nothing	-- sets the mouse position
		"""

		pygame.mouse.set_pos(pos)


	def get_pos(self):

		"""Returns mouse position
		
		arguments
		None
		
		returns
		mpos		-- an (x,y) position tuple, assuming top left is (0,0)
		"""

		mpos = pygame.mouse.get_pos()

		return mpos


	def get_clicked(self, mousebuttonlist='default', timeout='default'):

		"""Waits for mouse clicks
		
		arguments
		None
		
		keyword arguments
		mousebuttonlist	-- list of mouse buttons that are allowed (e.g.
					   [1,3] for left and right button); None to
					   allow all buttons or 'default' to use the
					   mbuttonlist property (default = 'default')
		timeout	-- time in milliseconds after which None is returned
				   when no click is registered; None for no timeout or
				   'default' to use the timeout property (default =
				   'default')
		
		returns
		mousebutton, clickpos, clicktime	-- mousebutton is an integer,
								   indicating which button has
								   been pressed or None when no
								   button has been pressed;
								   clickpos is an (x,y) position
								   tuple or None when no click
								   was registered;
								   clicktime is the time
								   (measured from expbegintime) a
								   buttonpress or a timeout
								   occured
		"""

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

		"""Returns the current state of the mouse buttons
		
		arguments
		None
		
		returns
		statelist	-- a list of Booleans indicating which mousebutton is
				   down (e.g. [1,0,0] when only button 1 is pressed on
				   a three-button-mouse)
		"""

		pygame.event.get()
		return pygame.mouse.get_pressed()


class PsychoPyMouse:

	"""A mouse for collecting responses"""

	def __init__(self, mousebuttonlist=MOUSEBUTTONLIST, timeout=MOUSETIMEOUT, visible=False):

		"""Initializes mouse object
		
		arguments
		None
		
		keyword arguments
		disptype	-- display type, either 'psychopy' or 'pygame' (default
				   = DISPTYPE)
		mousebuttonlist	-- list of mouse buttons that are allowed (e.g.
					   [1,3] for left and right button) or None to
					   allow all buttons (default =
					   MOUSEBUTTONLIST)
		timeout	-- time in milliseconds after which None is returned
				   on a call to get_clicked method when no click is
				   registered (default = MOUSETIMEOUT)
		visible	-- Boolean indicating if mouse should be visible or not
				   (default = False)
		"""

		# create mouse object
		self.mouse = psychopy.event.Mouse(visible=False,win=psychopy.visual.openWindows[SCREENNR])
		
		# set mouse characteristics
		self.set_mousebuttonlist(mousebuttonlist)
		self.set_timeout(timeout)
		self.set_visible(visible=visible)


	def set_mousebuttonlist(self, mousebuttonlist=None):

		"""Set a list of accepted mouse buttons
		
		arguments
		None
		
		keyword arguments
		mousebuttonlist	-- list of mouse buttons that are allowed (e.g.
					   [1,3] for left and right button) or None to
					   allow all buttons (default = None)
		
		returns
		Nothing	-- sets mbuttonlist property
		"""
		
		if mousebuttonlist == None or mousebuttonlist == []:
			self.mbuttonlist = None
		else:
			self.mbuttonlist = []
			for mbutton in mousebuttonlist:
				self.mbuttonlist.append(mbutton)


	def set_timeout(self, timeout=None):

		"""Set a timeout (in milliseconds)
		
		arguments
		None
		
		keyword arguments
		timeout	-- time in milliseconds after which None is returned
				   on a call to get_clicked method when no click is
				   registered (default = None)
		
		returns
		Nothing	-- sets timeout property
		"""

		self.timeout = timeout


	def set_visible(self, visible=True):

		"""Sets the visibility of the cursor
		
		arguments
		None
		
		keyword arguments
		visible	-- Boolean indicating if mouse should be visible or not
				   (default = False)
		
		returns
		Nothing	-- sets visible property
		"""

		self.visible = visible
		self.mouse.setVisible(self.visible)


	def set_pos(self, pos=(0,0)):

		"""Set the mouse position
		
		arguments
		None
		
		keyword arguments
		pos		-- an (x,y) position tuple, assuming top left is (0,0)
				   (default = (0,0))
		
		returns
		Nothing	-- sets the mouse position
		"""

		self.mouse.setPos(newPos=pos2psychopos(pos))


	def get_pos(self):

		"""Returns mouse position
		
		arguments
		None
		
		returns
		mpos		-- an (x,y) position tuple, assuming top left is (0,0)
		"""

		return psychopos2pos(self.mouse.getPos())


	def get_clicked(self, mousebuttonlist='default', timeout='default'):

		"""Waits for mouse clicks
		
		arguments
		None
		
		keyword arguments
		mousebuttonlist	-- list of mouse buttons that are allowed (e.g.
					   [1,3] for left and right button); None to
					   allow all buttons or 'default' to use the
					   mbuttonlist property (default = 'default')
		timeout	-- time in milliseconds after which None is returned
				   when no click is registered; None for no timeout or
				   'default' to use the timeout property (default =
				   'default')
		
		returns
		mousebutton, clickpos, clicktime	-- mousebutton is an integer,
								   indicating which button has
								   been pressed or None when no
								   button has been pressed;
								   clickpos is an (x,y) position
								   tuple or None when no click
								   was registered;
								   clicktime is the time
								   (measured from expbegintime) a
								   buttonpress or a timeout
								   occured
		"""

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

		"""Returns the current state of the mouse buttons
		
		arguments
		None
		
		returns
		statelist	-- a list of Booleans indicating which mousebutton is
				   down (e.g. [1,0,0] when only button 1 is pressed on
				   a three-button-mouse)
		"""

		return self.mouse.getPressed()


class Keyboard:

	"""A keyboard for collecting responses"""

	def __init__(self, disptype=DISPTYPE, keylist=KEYLIST, timeout=KEYTIMEOUT):

		"""Initializes the Keyboard object
		
		arguments
		None
		
		keyword arguments
		disptype	-- display type, either 'psychopy' or 'pygame' (default
				   = DISPTYPE)
		keylist	-- list of keys that are allowed, e.g. ['1','a','enter']
				   for the 1, A and Enter keys (default =
				   KEYLIST)
		timeout	-- time in milliseconds after which None is returned
				   on a call to the get_key method when no keypress is
				   registered (default = KEYTIMEOUT)
		"""

		if disptype in ['pygame','psychopy']:
			self.disptype = disptype
		else:
			self.disptype = 'pygame'
			print("WARNING! libinput.Keyboard.__init__: disptype not recognized; set to default ('pygame')")

		if self.disptype == 'pygame':
			self.__class__ = PyGameKeyboard
		elif self.disptype == 'psychopy':
			self.__class__ = PsychoPyKeyboard
		else:
			self.__class__ = PyGameKeyboard
			print("WARNING! libscreen.Keyboard.__init__: self.disptype was not recognized, which is very unexpected and should not happen! PyGameKeyboard is used")

		# create keyboard
		self.__init__(keylist=keylist, timeout=timeout)


class PyGameKeyboard:

	"""A keyboard for collecting responses"""

	import pygame.key

	def __init__(self, keylist=KEYLIST, timeout=KEYTIMEOUT):

		"""Initializes the Keyboard object
		
		arguments
		None
		
		keyword arguments
		keylist	-- list of keys that are allowed, e.g. ['1','a','enter']
				   for the 1, A and Enter keys (default =
				   KEYLIST)
		timeout	-- time in milliseconds after which None is returned
				   on a call to the get_key method when no keypress is
				   registered (default = KEYTIMEOUT)
		"""

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

		"""Set a list of accepted keys
		
		arguments
		None
		
		keyword arguments
		keylist	-- list of keys that are allowed (e.g.
				   ['1','a','enter']) or None to allow all keys
				   (default = None)
		
		returns
		Nothing	-- sets klist property
		"""
		
		if keylist == None or keylist == []:
			self.klist = None
		else:
			self.klist = []
			for key in keylist:
				self.klist.append(key)


	def set_timeout(self, timeout=None):

		"""Set a timeout (in milliseconds)
		
		arguments
		None
		
		keyword arguments
		timeout	-- time in milliseconds after which None is returned
				   on a call to get_key method when no keypress is
				   registered (default = None)
		
		returns
		Nothing	-- sets timeout property
		"""

		self.timeout = timeout


	def get_key(self, keylist='default', timeout='default', flush=False):

		"""Wait for keyboard input
		
		arguments
		None
		
		keyword arguments
		keylist	-- list of keys that are allowed (e.g.
				   ['1','a','enter']), None to allow all keys or
				   'default' to use klist property (default = 'default')
		timeout	-- time in milliseconds after which None is returned
				   when no keypress is registered (default = None);
				   None for no timeout or 'default' to use the timeout
				   property (default = 'default')
		flush		--	Boolean indicating if all input from before
					calling get_key should be ignored, if set to
					False keypresses from before calling this
					function will be registered, otherwise every
					keyboard input from before calling this function
					will be flushed (default = False)
		
		returns
		key, presstime	-- key is a string, indicating which button has
					   been pressed or None when no key has been
					   pressed
					   presstime is the time (measured from
					   expbegintime) a keypress or a timeout occured
		"""
		
		# set keylist and timeout
		if keylist == 'default':
			keylist = self.klist
		if timeout == 'default':
			timeout = self.timeout
		
		# flush if necessary
		if flush:
			pygame.event.get(pygame.KEYDOWN)
			
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

	def __init__(self, keylist=KEYLIST, timeout=KEYTIMEOUT):

		"""Initializes the Keyboard object
		
		arguments
		None
		
		keyword arguments
		keylist	-- list of keys that are allowed, e.g. ['1','a','enter']
				   for the 1, A and Enter keys (default =
				   KEYLIST)
		timeout	-- time in milliseconds after which None is returned
				   on a call to the get_key method when no keypress is
				   registered (default = KEYTIMEOUT)
		"""

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

		"""Set a list of accepted keys
		
		arguments
		None
		
		keyword arguments
		keylist	-- list of keys that are allowed (e.g.
				   ['1','a','enter']) or None to allow all keys
				   (default = None)
		
		returns
		Nothing	-- sets klist property
		"""
		
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

		"""Set a timeout (in milliseconds)
		
		arguments
		None
		
		keyword arguments
		timeout	-- time in milliseconds after which None is returned
				   on a call to get_key method when no keypress is
				   registered (default = None)
		
		returns
		Nothing	-- sets timeout property
		"""

		self.timeout = timeout


	def get_key(self, keylist='default', timeout='default', flush=False):

		"""Wait for keyboard input
		
		arguments
		None
		
		keyword arguments
		keylist	-- list of keys that are allowed (e.g.
				   ['1','a','enter']), None to allow all keys or
				   'default' to use klist property (default = 'default')
		timeout	-- time in milliseconds after which None is returned
				   when no keypress is registered (default = None);
				   None for no timeout or 'default' to use the timeout
				   property (default = 'default')
		flush		--	Boolean indicating if all input from before
					calling get_key should be ignored, if set to
					False keypresses from before calling this
					function will be registered, otherwise every
					keyboard input from before calling this function
					will be flushed (default = False)
		
		returns
		key, presstime	-- key is a string, indicating which button has
					   been pressed or None when no key has been
					   pressed
					   presstime is the time (measured from
					   expbegintime) a keypress or a timeout occured
		"""
		
		# set keylist and timeout
		if keylist == 'default':
			keylist = self.klist
		if timeout == 'default':
			timeout = self.timeout

		# flush if necessary
		if flush:
			psychopy.event.clearEvents(eventType='keyboard')

		# starttime
		starttime = libtime.get_time()
		time = libtime.get_time()

		# wait for input
		while timeout == None or time - starttime <= timeout:
			keys = psychopy.event.getKeys(keyList=keylist,timeStamped=False)
			for key in keys:
				if keylist == None or key in keylist:
					return key, libtime.get_time()
			time = libtime.get_time()

		return None, time


class Joystick:

	"""A joystick for collecting responses"""

	def __init__(self, joybuttonlist=JOYBUTTONLIST, timeout=JOYTIMEOUT):

		"""Initializes joystick object (joybuttonlist: list of buttons; timeout: timeout in ms)
		
		arguments
		None
		
		keyword arguments
		joybuttonlist	-- list of joystick buttons that are allowed (e.g.
					   [0,2,4]) or None to allow all buttons
					   (default = JOYBUTTONLIST)
		timeout	-- time in milliseconds after which None is returned
				   on a call to a get_* method when no input is
				   registered (default = JOYTIMEOUT)
		"""

		import pygame
		from pygame.joystick import Joystick

		# initialize joystick
		pygame.init()
		self.js = Joystick(0)

		# set joystick characteristics
		self.set_joybuttonlist(joybuttonlist)
		self.set_timeout(timeout)


	def set_joybuttonlist(self, joybuttonlist=None):

		"""Set a list of accepted joystick buttons
		
		arguments
		None
		
		keyword arguments
		joybuttonlist	-- list of joystick buttons that are allowed (e.g.
					   [0,2,4]) or None to allow all buttons
					   (default = None)
		returns
		Nothing	-- sets the jbuttonlist property
		"""

		if joybuttonlist == None or joybuttonlist == []:
			self.jbuttonlist = None
		else:
			self.jbuttonlist = []
			for joybutton in joybuttonlist:
				self.jbuttonlist.append(joybutton)


	def set_timeout(self, timeout=None):

		"""Set a timeout (in milliseconds)
		
		arguments
		None
		
		keyword arguments
		timeout	-- time in milliseconds after which None is returned
				   on a call to get_clicked method when no click is
				   registered (default = None)
		
		returns
		Nothing	-- sets timeout property
		"""

		self.timeout = timeout


	def get_joybutton(self, joybuttonlist='default', timeout='default'):

		"""Waits for joystick buttonpress
		
		arguments
		None
		
		keyword arguments
		joybuttonlist	-- list of buttons that are allowed (e.g.
					   [0,2,4]), None to allow all buttons or
					   'default' to use jbuttonlist property
					   (default = 'default')
		timeout	-- time in milliseconds after which None is returned
				   when no buttonpress is registered; None for no
				   timeout or 'default' to use the timeout property
				   (default = 'default')
		
		returns
		button, presstime	-- button is an integer, indicating which button
					   has been pressed or None when no button has
					   been pressed
					   presstime is the time (measured from
					   expbegintime) a buttonpress or a timeout
					   occured
		"""

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
				if event.type == pygame.JOYBUTTONDOWN:
					time = libtime.get_time()
					if joybuttonlist == None or event.button in joybuttonlist:
						pressed = event.button
						return pressed, time
		# in case of timeout
		return None, time


	def get_joyaxes(self, timeout='default'):

		"""Waits for joystick axis movement
		
		arguments
		None
		
		keyword arguments
		timeout	-- time in milliseconds after which None is returned
				   when no buttonpress is registered; None for no
				   timeout or 'default' to use the timeout property
				   (default = 'default')
		
		returns
		axespos, time	-- axespos is a [x,y,z] position list for the
					   positions of the joystick axes (usually [x,y,z]
					   for the main stick); x, y and z are floats
					   time is the time (measured from expbegintime)
					   an axismovement or a timeout occured
		"""

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
				if event.type == pygame.JOYAXISMOTION:
					time = libtime.get_time()
					for axis in range(self.js.get_numaxes()):
						pos.append(self.js.get_axis(axis))
					return pos, time
		# in case of timeout
		return None, time


	def get_joyballs(self, timeout='default'):

		"""Waits for joystick trackball movement
		
		arguments
		None
		
		keyword arguments
		timeout	-- time in milliseconds after which None is returned
				   when no buttonpress is registered; None for no
				   timeout or 'default' to use the timeout property
				   (default = 'default')
		
		returns
		ballpos, time	-- ballpos is a [ball1,ball2,...,ballN] position
					   list for the positions of the joystick balls;
					   each ball position is a (x,y) tuple
					   time is the time (measured from expbegintime) a
					   ballmovement or a timeout occured
		"""

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
				if event.type == pygame.JOYBALLMOTION:
					time = libtime.get_time()
					for ball in range(self.js.get_numballs()):
						ballpos.append(self.js.get_ball(ball))
					return ballpos, time
		# in case of timeout
		return None, time


	def get_joyhats(self, timeout='default'):

		"""Waits for joystick hat movement
		
		arguments
		None
		
		keyword arguments
		timeout	-- time in milliseconds after which None is returned
				   when no buttonpress is registered; None for no
				   timeout or 'default' to use the timeout property
				   (default = 'default')
		
		returns
		hatpos, time	-- hatpos is a [hat1,hat2,...,hatN] position list
					   for the positions of the joystick hats; each
					   hat position is a (x,y) tuple
					   time is the time (measured from expbegintime) a
					   hatmovement or a timeout occured
		"""
		
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
				if event.type == pygame.JOYHATMOTION:
					time = libtime.get_time()
					for hat in range(self.js.get_numhats()):
						hatpos.append(self.js.get_hat(hat))
					return hatpos, time
		# in case of timeout
		return None, time


	def get_joyinput(self, joybuttonlist='default', timeout='default'):

		"""Waits for any kind of joystick input
		
		arguments
		None
		
		keyword arguments
		joybuttonlist	-- list of buttons that are allowed (e.g.
					   [0,2,4]), None to allow all buttons or
					   'default' to use jbuttonlist property
					   (default = 'default')
		timeout	-- time in milliseconds after which None is returned
				   when no buttonpress is registered; None for no
				   timeout or 'default' to use the timeout property
				   (default = 'default')
		
		returns
		event, input, time	-- event is a string or None on a timeout,
						   indicating what kind of input was given:
						   'joybuttonpress', input is an integer
						   button number
						   'joyaxismotion', input is a [x,y,z]
						   position list for the positions of the
						   joystick axes (usually [x,y,z] for the
						   main stick); x, y and z are floats
						   'joyballmotion', input is a
						   [ball1,ball2,...,ballN] position list for
						   the positions of the joystick balls; each
						   ball position is a (x,y) tuple
						   'joyhatmotion', input is a
						   [hat1,hat2,...,hatN] position list for
						   the positions of the joystick hats; each
						   hat position is a (x,y) tuple
						   time is the time (measured from
						   expbegintime) any input or a timeout
						   occured
		"""

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
				if event.type == pygame.JOYBUTTONDOWN:
					time = libtime.get_time()
					if joybuttonlist == None or event.button in joybuttonlist:
						eventtype = 'joybuttonpress'
						pressed = event.button
						return eventtype, pressed, time
				if event.type == pygame.JOYAXISMOTION:
					time = libtime.get_time()
					eventtype = 'joyaxismotion'
					for axis in range(self.js.get_numaxes()):
						pos.append(self.js.get_axis(axis))
					return eventtype, pos, time
				if event.type == pygame.JOYBALLMOTION:
					time = libtime.get_time()
					eventtype = 'joyballmotion'
					for ball in range(self.js.get_numballs()):
						ballpos.append(self.js.get_ball(ball))
					return eventtype, ballpos, time
				if event.type == pygame.JOYHATMOTION:
					time = libtime.get_time()
					eventtype = 'joyhatmotion'
					for hat in range(self.js.get_numhats()):
						hatpos.append(self.js.get_hat(hat))
					return eventtype, hatpos, time
		# in case of timeout
		return eventtype, None, time
	

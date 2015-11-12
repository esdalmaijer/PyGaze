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

from pygaze.libtime import clock
from pygaze import settings
from pygaze._joystick.basejoystick import BaseJoystick
# we try importing the copy_docstr function, but as we do not really need it
# for a proper functioning of the code, we simply ignore it when it fails to
# be imported correctly
try:
	from pygaze._misc.misc import copy_docstr
except:
	pass

import pygaze
import pygame
from pygame.joystick import Joystick


class PyGameJoystick(BaseJoystick):

	"""A joystick for collecting responses"""

	def __init__(self, joybuttonlist=settings.JOYBUTTONLIST,
		timeout=settings.JOYTIMEOUT):

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

		# try to import copy docstring (but ignore it if it fails, as we do
		# not need it for actual functioning of the code)
		try:
			copy_docstr(BaseJoystick, PyGameJoystick)
		except:
			# we're not even going to show a warning, since the copied
			# docstring is useful for code editors; these load the docs
			# in a non-verbose manner, so warning messages would be lost
			pass

		# initialize joystick
		pygame.init()
		pygame.joystick.init()
		self.js = Joystick(0)
		self.js.init()

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
		starttime = clock.get_time()
		time = starttime
		# wait for button press
		while timeout == None or time - starttime <= timeout:
			time = clock.get_time()
			for event in pygame.event.get():
				if event.type == pygame.JOYBUTTONDOWN:
					time = clock.get_time()
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
		starttime = clock.get_time()
		time = starttime
		# wait for axis movement
		while timeout == None or time - starttime <= timeout:
			time = clock.get_time()
			for event in pygame.event.get():
				if event.type == pygame.JOYAXISMOTION:
					time = clock.get_time()
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
		starttime = clock.get_time()
		time = starttime
		# wait for axis movement
		while timeout == None or time - starttime <= timeout:
			time = clock.get_time()
			for event in pygame.event.get():
				if event.type == pygame.JOYBALLMOTION:
					time = clock.get_time()
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
		starttime = clock.get_time()
		time = starttime
		# wait for axis movement
		while timeout == None or time - starttime <= timeout:
			time = clock.get_time()
			for event in pygame.event.get():
				if event.type == pygame.JOYHATMOTION:
					time = clock.get_time()
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
		starttime = clock.get_time()
		time = starttime
		# wait for input
		while timeout == None or time - starttime <= timeout:
			time = clock.get_time()
			for event in pygame.event.get():
				if event.type == pygame.JOYBUTTONDOWN:
					time = clock.get_time()
					if joybuttonlist == None or event.button in joybuttonlist:
						eventtype = 'joybuttonpress'
						pressed = event.button
						return eventtype, pressed, time
				if event.type == pygame.JOYAXISMOTION:
					time = clock.get_time()
					eventtype = 'joyaxismotion'
					for axis in range(self.js.get_numaxes()):
						pos.append(self.js.get_axis(axis))
					return eventtype, pos, time
				if event.type == pygame.JOYBALLMOTION:
					time = clock.get_time()
					eventtype = 'joyballmotion'
					for ball in range(self.js.get_numballs()):
						ballpos.append(self.js.get_ball(ball))
					return eventtype, ballpos, time
				if event.type == pygame.JOYHATMOTION:
					time = clock.get_time()
					eventtype = 'joyhatmotion'
					for hat in range(self.js.get_numhats()):
						hatpos.append(self.js.get_hat(hat))
					return eventtype, hatpos, time
		# in case of timeout
		return eventtype, None, time
	

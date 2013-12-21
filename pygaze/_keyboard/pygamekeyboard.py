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

from pygaze.defaults import *
try:
	from constants import *
except:
	pass
	
import pygaze
import pygame

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
		starttime = pygaze.clock.get_time()
		time = pygaze.clock.get_time()

		# wait for input
		while timeout == None or time - starttime <= timeout:
			time = pygaze.clock.get_time()
			for event in pygame.event.get():
				if event.type == pygame.KEYDOWN:
					time = pygaze.clock.get_time()
					key = pygame.key.name(event.key)
					if keylist == None or key in keylist:
						return key, time
					
		# in case of timeout
		return None, time

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

from libopensesame.exceptions import osexception
from openexp.keyboard import keyboard
from pygaze.defaults import *
try:
	from constants import *
except:
	pass

class OSKeyboard:

	"""See _keyboard.pygamekeyboard.PyGameKeyboard"""

	def __init__(self, keylist=KEYLIST, timeout=KEYTIMEOUT):

		"""See _keyboard.pygamekeyboard.PyGameKeyboard"""

		self.experiment = osexperiment
		self.keyboard = keyboard(self.experiment, keylist=keylist, timeout= \
			timeout)
	
	def set_keylist(self, keylist=None):

		"""See _keyboard.pygamekeyboard.PyGameKeyboard"""
		
		self.keyboard.set_keylist(keylist)

	def set_timeout(self, timeout=None):

		"""See _keyboard.pygamekeyboard.PyGameKeyboard"""
		
		self.keyboard.set_timeout(timeout)

	def get_key(self, keylist='default', timeout='default', flush=False):
		
		"""See _keyboard.pygamekeyboard.PyGameKeyboard"""

		# set keylist and timeout
		if keylist == 'default':
			keylist = None
		if timeout == 'default':
			timeout = None
		# flush if necessary
		if flush:
			self.keyboard.flush()
		return self.keyboard.get_key(keylist=keylist, timeout=timeout)

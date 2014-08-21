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

from pygaze._keyboard.basekeyboard import BaseKeyboard
# we try importing the copy_docstr function, but as we do not really need it
# for a proper functioning of the code, we simply ignore it when it fails to
# be imported correctly
try:
	from pygaze._misc.misc import copy_docstr
except:
	pass

class OSKeyboard(BaseKeyboard):

	# See _keyboard.basekeyboard.BaseKeyboard

	def __init__(self, keylist=KEYLIST, timeout=KEYTIMEOUT):

		# See _keyboard.basekeyboard.BaseKeyboard

		# try to copy docstring (but ignore it if it fails, as we do
		# not need it for actual functioning of the code)
		try:
			copy_docstr(BaseKeyboard, OSKeyboard)
		except:
			# we're not even going to show a warning, since the copied
			# docstring is useful for code editors; these load the docs
			# in a non-verbose manner, so warning messages would be lost
			pass

		self.experiment = osexperiment
		self.keyboard = keyboard(self.experiment, keylist=keylist, timeout= \
			timeout)

	def set_keylist(self, keylist=None):

		# See _keyboard.basekeyboard.BaseKeyboard

		self.keyboard.set_keylist(keylist)

	def set_timeout(self, timeout=None):

		# See _keyboard.basekeyboard.BaseKeyboard

		self.keyboard.set_timeout(timeout)

	def get_key(self, keylist='default', timeout='default', flush=False):

		# See _keyboard.basekeyboard.BaseKeyboard

		if keylist != 'default':
			self.set_keylist(keylist)
		if timeout != 'default':
			self.set_timeout(timeout)
		# flush if necessary
		if flush:
			self.keyboard.flush()
		return self.keyboard.get_key()

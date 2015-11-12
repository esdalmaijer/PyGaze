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

from pygaze.py3compat import *
from pygaze import settings
from pygaze._misc.misc import copy_docstr
from pygaze._keyboard.basekeyboard import BaseKeyboard


class Keyboard(BaseKeyboard):

	# see BaseKeyboard

	def __init__(self, disptype=settings.DISPTYPE, **args):

		# see BaseKeyboard

		if disptype == u'pygame':
			from pygaze._keyboard.pygamekeyboard import PyGameKeyboard as \
				Keyboard
		elif disptype == u'psychopy':
			from pygaze._keyboard.psychopykeyboard import PsychoPyKeyboard as \
				Keyboard
		elif disptype == u'opensesame':
			from pygaze._keyboard.oskeyboard import OSKeyboard as \
				Keyboard
		else:
			raise Exception(u'Unexpected disptype : %s' % disptype)
		self.__class__ = Keyboard
		self.__class__.__init__(self, **args)
		copy_docstr(BaseKeyboard, Keyboard)

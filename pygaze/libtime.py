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
if settings.DISPTYPE == u'psychopy':
	from pygaze._time.psychopytime import PsychoPyTime as Time
elif settings.DISPTYPE == u'pygame':
	from pygaze._time.pygametime import PyGameTime as Time
elif settings.DISPTYPE == u'opensesame':
	from pygaze._time.ostime import OSTime as Time
else:
	raise Exception(u'Unexpected disptype : %s' % disptype)

# # # # #
# functions

# the following function definitions are for backwards compatibility

import pygaze

def expstart():
	
	"""Time is set to 0 upon calling this"""
	
	clock.expstart()

	
def get_time():
	
	"""Returns the current time in milliseconds
	
	arguments
	None
	
	keyword arguments
	None
	
	returns
	time		--	current time in milliseconds, as measured from
				expbegintime
	"""
	
	return clock.get_time()


def pause(pausetime):
	
	"""Pauses the experiment for the given number of milliseconds
	
	arguments
	pausetime	--	time to pause in milliseconds
	
	keyword arguments
	None
	
	returns
	pausetime	--	the actual duration of the pause in milliseconds
	"""
	
	return clock.pause(pausetime)


def expend():
	
	"""Completely ends the experiment (only call this at the very end!)
	
	arguments
	None
	
	keyword arguments
	None
	
	returns
	endtime		--	experiment ending time in milliseconds, as measured
				from expbegintime
	"""
	
	return clock.expend()

# Create a singleton clock 
clock = Time()
clock.expstart()

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

import psychopy.core

def expstart():

	"""Time is set to 0 when calling this
	
	arguments
	None

	returns
	Nothing
	"""

	global expbegintime

	expbegintime = psychopy.core.getTime() * 1000

def get_time():

	"""Returns current time in milliseconds
	
	arguments
	None
	
	returns
	time		-- current time in milliseconds, as measured since
				expbegintime
	"""

	return psychopy.core.getTime() * 1000 - expbegintime


def pause(pausetime):

	"""Pauses the experiment for given number of milliseconds
	
	arguments
	pausetime	-- time to pause in milliseconds
	
	returns
	pausetime	-- actual time the system paused (in milliseconds)
	"""

	t0 = psychopy.core.getTime()
	psychopy.core.wait(pausetime/1000.0)
	t1 = psychopy.core.getTime()

	return t1-t0

def expend():

	"""Completely ends the experiment (only call this at the end!)
	
	arguments
	None
	
	returns
	endtime	-- ending time of the experiment (in milliseconds since
				expbegintime
	"""

	endtime = get_time() * 1000

	psychopy.core.quit()

	return endtime 

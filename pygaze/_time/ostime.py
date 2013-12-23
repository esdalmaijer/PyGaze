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

from pygaze.defaults import osexperiment
try:
	from constants import osexperiment
except:
	pass

from pygaze._time.basetime import BaseTime
# we try importing the copy_docstr function, but as we do not really need it
# for a proper functioning of the code, we simply ignore it when it fails to
# be imported correctly
try:
	from pygaze._misc.misc import copy_docstr
except:
	pass


class OSTime(BaseTime):
	
	# see pygaze._time.basetime.BaseTime
	
	def __init__(self):
		
		# see pygaze._time.basetime.BaseTime

		# try to copy docstring (but ignore it if it fails, as we do
		# not need it for actual functioning of the code)
		try:
			copy_docstr(BaseTime, OSTime)
		except:
			# we're not even going to show a warning, since the copied
			# docstring is useful for code editors; these load the docs
			# in a non-verbose manner, so warning messages would be lost
			pass
		
		pass


	def expstart(self):
		
		# see pygaze._time.basetime.BaseTime

		global expbegintime
		
		expbegintime = 0


	def get_time(self):

		# see pygaze._time.basetime.BaseTime

		return osexperiment.time()


	def pause(self, pausetime):

		# see pygaze._time.basetime.BaseTime

		return osexperiment.sleep(pausetime)


	def expend(self):

		# see pygaze._time.basetime.BaseTime

		return osexperiment.time()
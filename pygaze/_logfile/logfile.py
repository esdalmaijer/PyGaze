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

import os
from pygaze.defaults import *
try:
	from constants import *
except:
	pass


class Logfile:

	"""Logfile object for saving data"""

	def __init__(self, filename=LOGFILE):

		"""Initiates logfile object
		
		arguments
		None
		
		keyword arguments
		filename	-- name (possibly including path) for the logfile;
				   WITHOUT extension! (default = LOGFILE)
		
		returns
		Nothing	-- sets filename and logfile properties
		"""

		self.filename = filename + ".txt"
		self.logfile = open(self.filename, "w")


	def write(self, vallist):

		"""Writes given values to logfile (each value separated with a tab)
		
		arguments
		vallist	-- list of values to be written to logfile
		
		returns
		Nothing	-- writes each value to the logfile, adding tabs between
				   the values
		"""

		# empty string
		line = ""

		# all values to string
		vallist = map(str, vallist)
		
		# insert tabs between values, end with newline character
		line = "\t".join(vallist) + "\n"

		# write line to file (on disk)
		self.logfile.write(line) # write to internal buffer
		self.logfile.flush() # internal buffer to RAM
		os.fsync(self.logfile.fileno()) # RAM file cache to disk


	def close(self):

		"""Closes logfile (do this after writing everything to the file!)
		
		arguments
		None
		
		returns
		Nothing	-- closes logfile; calling write method after calling
				   close method will result in an error!
		"""

		self.logfile.close()


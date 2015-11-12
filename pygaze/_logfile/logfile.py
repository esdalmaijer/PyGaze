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
from pygaze import settings
from pygaze._logfile.baselogfile import BaseLogfile
# we try importing the copy_docstr function, but as we do not really need it
# for a proper functioning of the code, we simply ignore it when it fails to
# be imported correctly
try:
	from pygaze._misc.misc import copy_docstr
except:
	pass


class Logfile(BaseLogfile):

	# See _logfile.baselogfile.BaseLogfile

	def __init__(self, filename=settings.LOGFILE):

		# See _logfile.baselogfile.BaseLogfile

		# try to copy docstring (but ignore it if it fails, as we do
		# not need it for actual functioning of the code)
		try:
			copy_docstr(BaseLogfile, Logfile)
		except:
			# we're not even going to show a warning, since the copied
			# docstring is useful for code editors; these load the docs
			# in a non-verbose manner, so warning messages would be lost
			pass

		self.filename = filename + ".txt"
		self.logfile = open(self.filename, "w")


	def write(self, vallist):

		# See _logfile.baselogfile.BaseLogfile

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

		# See _logfile.baselogfile.BaseLogfile

		self.logfile.close()

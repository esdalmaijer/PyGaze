#!/usr/bin/env python3

"""
This file is part of qnotero.

qnotero is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

qnotero is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with qnotero.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
import glob
import pygaze
from distutils.core import setup

def data_files():

	"""
	desc:
		The OpenSesame plug-ins are installed as additional data. Under Windows,
		there is no special folder to put these plug-ins in, so we skip this
		step.

	returns:
		desc:	A list of data files to include.
		type:	list
	"""

	if os.name == 'nt':
		return []
	return [
		("/usr/share/opensesame/plugins/pygaze_init", glob.glob("opensesame_plugins/pygaze_init/*")),
		("/usr/share/opensesame/plugins/pygaze_drift_correct", glob.glob("opensesame_plugins/pygaze_drift_correct/*")),
		("/usr/share/opensesame/plugins/pygaze_log", glob.glob("opensesame_plugins/pygaze_log/*")),
		("/usr/share/opensesame/plugins/pygaze_start_recording", glob.glob("opensesame_plugins/pygaze_start_recording/*")),
		("/usr/share/opensesame/plugins/pygaze_stop_recording", glob.glob("opensesame_plugins/pygaze_stop_recording/*")),
		("/usr/share/opensesame/plugins/pygaze_wait", glob.glob("opensesame_plugins/pygaze_wait/*"))
		]

setup(name="python-pygaze",
	version = pygaze.deb_version,
	description = "A Python library for eye tracking",
	author = "Edwin Dalmaijer",
	author_email = "edwin.dalmaijer@psy.ox.ac.uk",
	url = "http://www.pygaze.org/",
	packages = [
		"pygaze",
		"pygaze._display",
		"pygaze._eyetracker",
		"pygaze._joystick",
		"pygaze._keyboard",
		"pygaze._logfile",
		"pygaze._misc",
		"pygaze._mouse",
		"pygaze._screen",
		"pygaze._sound",
		"pygaze._time",
		"pygaze.plugins",
		],
	data_files=data_files()
	)

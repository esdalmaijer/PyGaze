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
from pygaze.settings import settings
from distutils.version import StrictVersion
import sys
import os

__version__ = version = u'0.6.0a16'
strict_version = StrictVersion(__version__)
# The version without the prerelease (if any): e.g. 3.0.0
main_version = u'.'.join([str(i) for i in strict_version.version])
# The version following the debian convention: e.g. 3.0.0~a1
if strict_version.prerelease is None:
	deb_version = main_version
else:
	deb_version = main_version + u'~%s%d' % strict_version.prerelease

# directory stuff
DIR = safe_decode(os.path.dirname(__file__), enc=sys.getfilesystemencoding())
if os.path.exists(u'resources'):
	RESDIR = u'resources'
elif os.path.exists(os.path.join(DIR, u'resources')):
	RESDIR = os.path.join(DIR, u'resources')
elif os.path.exists(u'/usr/share/pygaze/resources'):
	RESDIR = u'/usr/share/pygaze/resources'
elif py3:
	RESDIR = os.getcwd()
else:
	RESDIR = os.getcwdu()
FONTDIR = os.path.join(RESDIR, u'fonts')
SOUNDDIR = os.path.join(RESDIR, u'sounds')

# fontfiles
FONTFILES = []
if os.path.isdir(FONTDIR):
	for fontfile in os.listdir(FONTDIR):
		FONTFILES.append(os.path.join(FONTDIR, fontfile))

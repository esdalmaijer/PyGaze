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

version = u'0.5.0'

import os

# directory stuff
DIR = os.path.dirname(__file__)
if os.path.exists(u'resources'):
	RESDIR = u'resources'
elif os.path.exists(os.path.join(DIR, u'resources')):
	RESDIR = os.path.join(DIR, u'resources')
elif os.path.exists(u'/usr/share/pygaze/resources'):
	RESDIR = u'/usr/share/pygaze/resources'
else:
	RESDIR = os.getcwd()
FONTDIR = os.path.join(RESDIR, u'fonts')
SOUNDDIR = os.path.join(RESDIR, u'sounds') 

# fontfiles
FONTFILES = []
if os.path.isdir(FONTDIR):
	for fontfile in os.listdir(FONTDIR):
		FONTFILES.append(os.path.join(FONTDIR, fontfile))


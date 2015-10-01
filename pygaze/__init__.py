# -*- coding: utf-8 -*-
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


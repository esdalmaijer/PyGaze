#!/usr/bin/env python
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
        desc:    A list of data files to include.
        type:    list
    """
    if os.name == 'nt':
        return []

    return [('/usr/share/opensesame/plugins/pygaze_drift_correct',
             glob.glob('opensesame_plugins/pygaze_drift_correct/*')),
            ('/usr/share/opensesame/plugins/pygaze_init',
             glob.glob('opensesame_plugins/pygaze_init/*')),
            ('/usr/share/opensesame/plugins/pygaze_log',
             glob.glob('opensesame_plugins/pygaze_log/*')),
            ('/usr/share/opensesame/plugins/pygaze_start_recording',
             glob.glob('opensesame_plugins/pygaze_start_recording/*')),
            ('/usr/share/opensesame/plugins/pygaze_stop_recording',
             glob.glob('opensesame_plugins/pygaze_stop_recording/*')),
            ('/usr/share/opensesame/plugins/pygaze_wait',
             glob.glob('opensesame_plugins/pygaze_wait/*'))]


setup(
    name='python-pygaze',
    version=pygaze.version,
    description='A Python library for eye tracking',
    author='Edwin Dalmaijer',
    author_email='edwin.dalmaijer@psy.ox.ac.uk',
    url='http://www.pygaze.org/',
    packages=[
        'pygaze',
        'pygaze._display',
        'pygaze._eyetracker',
        'pygaze._joystick',
        'pygaze._keyboard',
        'pygaze._logfile',
        'pygaze._misc',
        'pygaze._mouse',
        'pygaze._screen',
        'pygaze._sound',
        'pygaze._time',
        'pygaze.plugins',
    ],
    data_files=data_files()
)

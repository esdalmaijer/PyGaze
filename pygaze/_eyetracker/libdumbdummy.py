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

from pygaze import settings
from pygaze.py3compat import *
from pygaze.libtime import clock
import pygaze
from pygaze.screen import Screen
from pygaze._eyetracker.baseeyetracker import BaseEyeTracker
# we try importing the copy_docstr function, but as we do not really need it
# for a proper functioning of the code, we simply ignore it when it fails to
# be imported correctly
try:
	from pygaze._misc.misc import copy_docstr
except:
	pass


def message(msg):
	
	"""Prints a timestamp and message to the console"""
	
	print(u"%d\t%s" % (int(clock.get_time()), msg))

class DumbDummy(BaseEyeTracker):

	"""A dummy class to run experiments in 'dumb dummy' mode, where nothing happens (NO simulation!)"""
	

	def __init__(self, display):

		"""Initiates a 'dumb dummy' object, that doesn't do a thing
		
		arguments
		display		--	a pygaze display.Display instance
		
		keyword arguments
		None
		"""

		# try to copy docstrings (but ignore it if it fails, as we do
		# not need it for actual functioning of the code)
		try:
			copy_docsafe_decode(BaseEyeTracker, DumbDummy)
		except:
			# we're not even going to show a warning, since the copied
			# docstring is useful for code editors; these load the docs
			# in a non-verbose manner, so warning messages would be lost
			pass

		self.recording = False
		self.blinking = False
		self.bbpos = (settings.DISPSIZE[0]/2, settings.DISPSIZE[1]/2)

		self.display = display
		self.screen = Screen(disptype=settings.DISPTYPE, mousevisible=False)


	def send_command(self, cmd):

		"""Dummy command, messages command instead of sending it to the eyetracker"""

		message(u"The following command would have been given to the eyetracker: " + safe_decode(cmd))


	def log(self, msg):

		"""Dummy log message, messages message instead of sending it to the eyetracker"""

		message(u"The following message would have been logged to the EDF: " + safe_decode(msg))


	def log_var(self, var, val):

		"""Dummy varlog, messages variable and value instead of sending it to the eyetracker"""

		message(u"The following variable would have been logged to the EDF: " + safe_decode(var) + u", value: " + safe_decode(val))


	def status_msg(self, msg):
		
		"""Dummy status message, messages message instead of sending it to the eyetracker"""

		message(u"The following status message would have been visible on the experimentor PC: " + safe_decode(msg))


	def connected(self):

		"""Dummy connection status"""

		message("Dummy mode, eyetracker not connected.")

		return True


	def calibrate(self):

		"""Dummy calibration"""

		message("Calibration would now take place")


	def drift_correction(self, pos=None, fix_triggered=False):

		"""Dummy drift correction"""

		message("Drift correction would now take place")
		
		return True


	def prepare_drift_correction(self, pos):

		"""Dummy drift correction preparation"""

		message("Drift correction preparation would now take place")


	def fix_triggered_drift_correction(self, pos=None, min_samples=30, max_dev=60, reset_threshold=10):

		"""Dummy drift correction (fixation triggered)"""

		message("Drift correction (fixation triggered) would now take place")
		
		return True


	def start_recording(self):

		"""Dummy for starting recording, messages what would have been the recording start"""

		self.recording = True
		
		message("Recording would have started now")


	def stop_recording(self):

		"""Dummy for stopping recording, messages what would have been the recording end"""

		self.recording = False

		message("Recording would have stopped now")


	def close(self):

		"""Dummy for closing connection with eyetracker, messages what would have been connection closing time"""

		if self.recording:
			self.stop_recording()

		message("eyetracker connection would have closed now")


	def set_eye_used(self):

		"""Dummy for setting which eye to track (does nothing)"""
		
		message("Which eye to track would now be set")


	def pupil_size(self):
		
		"""Returns dummy pupil size"""
		
		return 19


	def sample(self):

		"""Returns dummy gaze position"""

		return (19,19)


	def wait_for_event(self, event):

		"""Waits for simulated event (3=STARTBLINK, 4=ENDBLINK, 5=STARTSACC, 6=ENDSACC, 7=STARTFIX, 8=ENDFIX)"""

		if event == 5:
			outcome = self.wait_for_saccade_start()
		elif event == 6:
			outcome = self.wait_for_saccade_end()
		elif event == 7:
			outcome = self.wait_for_fixation_start()
		elif event == 8:
			outcome = self.wait_for_fixation_end()
		elif event == 3:
			outcome = self.wait_for_blink_start()
		elif event == 4:
			outcome = self.wait_for_blink_end()

		return outcome


	def wait_for_saccade_start(self):

		"""Returns starting time and starting position when a simulated saccade is started"""

		return clock.get_time(), (19,19)


	def wait_for_saccade_end(self):

		"""Returns ending time, starting and end position when a simulated saccade is ended"""

		# function assumes that a 'saccade' has ended when 'gaze' position remains reasonably
		# (i.e.: within maxerr) stable for five samples
		# for saccade start algorithm, see wait_for_fixation_start

		stime, spos = self.wait_for_saccade_start()

		return clock.get_time(), spos, (190,190)


	def wait_for_fixation_start(self):

		"""Returns starting time and position when a simulated fixation is started"""

		return clock.get_time(), (19,19)


	def wait_for_fixation_end(self):

		"""Returns time and gaze position when a simulated fixation is ended"""

		stime, spos = self.wait_for_fixation_start()

		return clock.get_time(), spos


	def wait_for_blink_start(self):

		"""Returns starting time and position of a simulated blink"""

		return clock.get_time(), (19,19)


	def wait_for_blink_end(self):

		"""Returns ending time and position of a simulated blink (mousebuttonup)"""
		
		return clock.get_time(), (19,19)

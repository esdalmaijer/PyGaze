# -*- coding: utf-8 -*-
#
# This file is part of PyGaze - the open-source toolbox for eye tracking
#
# PyGaze is a Python module for easily creating gaze contingent experiments
# or other software (as well as non-gaze contingent experiments/software)
# Copyright (C) 2012-2013 Edwin S. Dalmaijer
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>


# TobiiGlassesTracker
import copy
import math
import numpy


from pygaze import settings
from pygaze.libtime import clock
import pygaze
from pygaze.screen import Screen
from pygaze.keyboard import Keyboard
from pygaze.sound import Sound

from pygaze._eyetracker.baseeyetracker import BaseEyeTracker
# we try importing the copy_docstr function, but as we do not really need it
# for a proper functioning of the code, we simply ignore it when it fails to
# be imported correctly
try:
	from pygaze._misc.misc import copy_docstr
except:
	pass


import os
import datetime

import signal
import sys


import urllib2
import json
import time
import threading
import socket
import uuid
import logging as log

import warnings
warnings.filterwarnings("ignore", category=numpy.VisibleDeprecationWarning)


# # # # #
# TobiiGlassesController

from tobiiglasses.tobiiglassescontroller import TobiiGlassesController



# # # # #
# classes

class TobiiGlassesTracker(BaseEyeTracker):

	"""A class for Tobii Pro Glasses 2 EyeTracker objects"""

	def __init__(self, display, address='192.168.71.50', udpport=49152, logfile=settings.LOGFILE,
		eventdetection=settings.EVENTDETECTION, saccade_velocity_threshold=35,
		saccade_acceleration_threshold=9500, blink_threshold=settings.BLINKTHRESH, **args):

		"""Initializes a TobiiProGlassesTracker instance

		arguments
		display	--	a pygaze.display.Display instance

		keyword arguments
		address	-- internal ipv4/ipv6 address for Tobii Pro Glasses 2 (default =
				   '192.168.71.50', for IpV6 address use square brackets [fe80::xxxx:xxxx:xxxx:xxxx])
		udpport	-- UDP port number for Tobii Pro Glasses data streaming (default = 49152)
		"""

		# try to copy docstrings (but ignore it if it fails, as we do
		# not need it for actual functioning of the code)
		try:
			copy_docstr(BaseEyeTracker, TobiiProGlassesTracker)
		except:
			# we're not even going to show a warning, since the copied
			# docstring is useful for code editors; these load the docs
			# in a non-verbose manner, so warning messages would be lost
			pass


		# object properties
		self.disp = display
		self.screen = Screen()
		self.dispsize = settings.DISPSIZE # display size in pixels
		self.screensize = settings.SCREENSIZE # display size in cm
		self.screendist = settings.SCREENDIST # distance between participant and screen in cm
		self.pixpercm = (self.dispsize[0]/float(self.screensize[0]) + self.dispsize[1]/float(self.screensize[1])) / 2.0
		self.kb = Keyboard(keylist=['space', 'escape', 'q'], timeout=1)
		self.errorbeep = Sound(osc='saw',freq=100, length=100)

		# output file properties
		self.outputfile = logfile
		self.description = "experiment" # TODO: EXPERIMENT NAME
		self.participant = "participant" # TODO: PP NAME

		# eye tracker properties
		self.eye_used = 0 # 0=left, 1=right, 2=binocular
		self.left_eye = 0
		self.right_eye = 1
		self.binocular = 2


		self.maxtries = 100 # number of samples obtained before giving up (for obtaining accuracy and tracker distance information, as well as starting or stopping recording)
		self.prevsample = (-1,-1)

		# validation properties
		self.nvalsamples = 1000 # samples for one validation point

		# event detection properties
		self.fixtresh = 1.5 # degrees; maximal distance from fixation start (if gaze wanders beyond this, fixation has stopped)
		self.fixtimetresh = 100 # milliseconds; amount of time gaze has to linger within self.fixtresh to be marked as a fixation
		self.spdtresh = saccade_velocity_threshold # degrees per second; saccade velocity threshold
		self.accthresh = saccade_acceleration_threshold # degrees per second**2; saccade acceleration threshold
		self.blinkthresh = blink_threshold # milliseconds; blink detection threshold used in PyGaze method
		self.eventdetection = eventdetection
		self.set_detection_type(self.eventdetection)
		self.weightdist = 10 # weighted distance, used for determining whether a movement is due to measurement error (1 is ok, higher is more conservative and will result in only larger saccades to be detected)


		self.tobiiglasses = TobiiGlassesController(udpport, address)

		self.triggers_values = {}

		self.logging = False
		self.current_recording_id = None
		self.current_participant_id = None
		self.current_project_id = None


	def __del__(self):

		self.close()

	def __get_log_row__(self, keys, triggers):

		row = ""
		ac = [None, None, None]
		gy = [None, None, None]
		if "mems" in keys:

			try:
				for i in range(0,3):
					ac[i] = self.tobiiglasses.data['mems']['ac']['ac'][i]
			except:
				pass

			try:
				for i in range(0,3):
					gy[i] = self.tobiiglasses.data['mems']['gy']['gy'][i]
			except:
				pass

			row += ("%s; %s; %s; %s; %s; %s; " % (ac[0], ac[1], ac[2], gy[0], gy[1], gy[2]))


		gp = [None, None]
		if "gp" in keys:

			try:
				for i in range(0,2):
					gp[i] = self.tobiiglasses.data['gp']['gp'][i]
			except:
				pass

			row += ("%s; %s; " % (gp[0], gp[1]))


		gp3 = [None, None, None]
		if "gp3" in keys:

			try:
				for i in range(0,3):
					gp3[i] = self.tobiiglasses.data['gp3']['gp3'][i]
			except:
				pass

			row += ("%s; %s; %s; " % (gp3[0], gp3[1], gp3[2]))


		pc = [None, None, None]
		pd = None
		gd = [None, None, None]
		if "left_eye" in keys:

			try:
				for i in range(0,3):
					pc[i] = self.tobiiglasses.data['left_eye']['pc']['pc'][i]
			except:
				pass

			try:
				pd = self.tobiiglasses.data['left_eye']['pd']['pd']
			except:
				pass

			try:
				for i in range(0,3):
					gd[i] = self.tobiiglasses.data['left_eye']['gd']['gd'][i]
			except:
				pass


			row += ("%s; %s; %s; %s; %s; %s; %s; " % (pc[0], pc[1], pc[2], pd, gd[0], gd[1], gd[2]))

		pc = [None, None, None]
		pd = None
		gd = [None, None, None]
		if "right_eye" in keys:

			try:
				for i in range(0,3):
					pc[i] = self.tobiiglasses.data['right_eye']['pc']['pc'][i]
			except:
				pass

			try:
				pd = self.tobiiglasses.data['right_eye']['pd']['pd']
			except:
				pass

			try:
				for i in range(0,3):
					gd[i] = self.tobiiglasses.data['right_eye']['gd']['gd'][i]
			except:
				pass

			row += ("%s; %s; %s; %s; %s; %s; %s; " % (pc[0], pc[1], pc[2], pd, gd[0], gd[1], gd[2]))

		if len(triggers) > 0:
			for trigger in triggers:
				row += ("%s; " % self.triggers_values[trigger])

		row = row[:-2]
		return row

	def __get_log_header__(self, keys, triggers):

		header = "ts; "

		if "mems" in keys:
			header+="ac_x [m/s^2]; ac_y [m/s^2]; ac_z [m/s^2]; gy_x [°/s]; gy_y [°/s]; gy_z [°/s]; "
		if "gp" in keys:
			header+="gp_x; gp_y; "
		if "gp3" in keys:
			header+="gp3_x [mm]; gp3_y [mm]; gp3_z [mm]; "
		if "left_eye" in keys:
			header+="left_pc_x [mm]; left_pc_y [mm]; left_pc_z [mm]; left_pd [mm]; left_gd_x; left_gd_y; left_gd_z; "
		if "left_eye" in keys:
			header+="right_pc_x [mm]; right_pc_y [mm]; right_pc_z [mm]; right_pd [mm]; right_gd_x; right_gd_y; right_gd_z; "

		if len(triggers) > 0:
			for trigger in triggers:
				header+=trigger + "; "
				self.triggers_values[trigger] = None

		header = header[:-2]
		return header



	def __data_logger__(self, logfile, frequency, keys, triggers, time_offset):

		with open(logfile, 'a') as f:

			header = self.__get_log_header__(keys, triggers)
			f.write(header + "\n")

			while self.logging:

				row = self.__get_log_row__(keys, triggers)
				f.write("%s; %s \n" % (time_offset, row))
				time_period = float(1.0/float(frequency))
				time_offset += int(time_period*1000)
				time.sleep(time_period)


	def start_capturing(self):

		if not self.tobiiglasses.is_streaming():
			self.tobiiglasses.start_streaming()
		else:
			log.error("The eye-tracker is already in capturing mode.")

		return self.tobiiglasses.is_streaming()

	def stop_capturing(self):

		if self.tobiiglasses.is_streaming():
			self.tobiiglasses.stop_streaming()
		else:
			log.error("The eye-tracker is not in capturing mode.")

		return not self.tobiiglasses.is_streaming()

	def calibrate(self, calibrate=True, validate=True):

		"""Calibrates the eye tracking system

		arguments
		None

		keyword arguments
		calibrate	--	Boolean indicating if calibration should be
					performed (default = True)
		validate	--	Boolean indicating if validation should be performed
					(default = True)

		returns
		success	--	returns True if calibration succeeded, or False if
					not; in addition a calibration log is added to the
					log file and some properties are updated (i.e. the
					thresholds for detection algorithms)
		"""

		if self.current_project_id is None:
			self.current_project_id = self.set_project()

		if self.current_participant_id is None:
			self.current_participant_id = self.create_participant(self.current_project_id)

		calibration_id = self.__create_calibration__(self.current_project_id, self.current_participant_id)

		self.tobiiglasses.start_calibration(calibration_id)

		res = self.tobiiglasses.wait_until_is_calibrated(calibration_id)

		return res

	def set_current_project(self, project_name = None):

		if project_name is None:
			self.current_project_id = self.tobiiglasses.create_project()
		else:
			self.current_project_id = self.tobiiglasses.create_project(project_name)

	def set_current_participant(self, participant_name = None):

		if self.current_project_id is None:
			log.error("There is no project to assign a participant.")
		else:
			if participant_name is None:
				self.current_participant_id = self.tobiiglasses.create_participant(self.current_project_id)
			else:
				self.current_participant_id = self.tobiiglasses.create_participant(self.current_project_id, participant_name)

	def __create_calibration__(self, project_id, participant_id):

		calibration_id = self.tobiiglasses.create_calibration(project_id, participant_id)
		return calibration_id


	def start_logging(self, logfile, frequency, keys = ["mems", "gp", "gp3", "left_eye", "right_eye"], triggers = [], time_offset=0):

		if not self.logging:
			self.logger = threading.Timer(0, self.__data_logger__, [logfile, frequency, keys, triggers, time_offset])
			self.logging = True
			self.logger.start()
			log.debug("Start logging selected data in file " + logfile + " ...")
		else:
			log.error("The eye-tracker is already in logging mode.")

		return self.logging

	def trigger(self, trigger_key, trigger_value):

		try:
			self.triggers_values[trigger_key] = trigger_value
			log.debug("Trigger received! Key: " + trigger_key + " Value: " + trigger_value)
		except:
			pass


	def stop_logging(self):

		if self.logging:
			self.logging = False
			self.logger.join()
			log.debug("Stop logging!")
		else:
			log.error("The eye-tracker is not in logging mode.")

		return not self.logging

	def close(self):

		"""Neatly close connection to tracker

		arguments
		None

		returns
		None

		"""

		if self.logging:
			self.stop_logging()

		if self.tobiiglasses.is_streaming():
			self.stop_capturing()



	def connected(self):

		"""Checks if the tracker is connected

		arguments
		None

		returns
		connected	--	True if connection is established, False if not

		"""

		res = self.tobiiglasses.wait_until_status_is_ok()

		return res


	def drift_correction(self, pos=None, fix_triggered=False):

		"""Performs a drift check

		arguments
		None

		keyword arguments
		pos			-- (x, y) position of the fixation dot or None for
					   a central fixation (default = None)
		fix_triggered	-- Boolean indicating if drift check should be
					   performed based on gaze position (fix_triggered
					   = True) or on spacepress (fix_triggered =
					   False) (default = False)

		returns
		checked		-- Boolaan indicating if drift check is ok (True)
					   or not (False); or calls self.calibrate if 'q'
					   or 'escape' is pressed


		"""

		"""Not supported for TobiiProGlassesTracker (yet)"""

		print("function not supported yet")



	def fix_triggered_drift_correction(self, pos=None, min_samples=10, max_dev=60, reset_threshold=30):

		"""Performs a fixation triggered drift correction by collecting
		a number of samples and calculating the average distance from the
		fixation position

		arguments
		None

		keyword arguments
		pos			-- (x, y) position of the fixation dot or None for
					   a central fixation (default = None)
		min_samples		-- minimal amount of samples after which an
					   average deviation is calculated (default = 10)
		max_dev		-- maximal deviation from fixation in pixels
					   (default = 60)
		reset_threshold	-- if the horizontal or vertical distance in
					   pixels between two consecutive samples is
					   larger than this threshold, the sample
					   collection is reset (default = 30)

		returns
		checked		-- Boolaan indicating if drift check is ok (True)
					   or not (False); or calls self.calibrate if 'q'
					   or 'escape' is pressed

		"""

		"""Not supported for TobiiProGlassesTracker (yet)"""

		print("function not supported yet")


	def get_eyetracker_clock_async(self):

		"""Retrieve difference between tracker time and experiment time

		arguments
		None

		keyword arguments
		None

		returns
		timediff	--	tracker time minus experiment time


		return self.controller.syncmanager.convert_from_local_to_remote(self.controller.clock.get_time()) - clock.get_time()
		"""

		"""Not supported for TobiiProGlassesTracker (yet)"""

		print("function not supported yet")


	def log(self, msg):

		"""Writes a message to the log file

		arguments
		msg		-- a string to include in the log file

		returns
		Nothing	-- uses native log function of iViewX to include a line
				   in the log file

		"""

		"""Not supported for TobiiProGlassesTracker (yet)"""

		print("function not supported yet")





	def log_var(self, var, val):

		"""Writes a variable to the log file

		arguments
		var		-- variable name
		val		-- variable value

		returns
		Nothing	-- uses native log function of iViewX to include a line
				   in the log file in a "var NAME VALUE" layout

		"""

		"""Not supported for TobiiProGlassesTracker (yet)"""

		print("function not supported yet")


	def prepare_backdrop(self):

		"""Not supported for TobiiProGlassesTracker (yet)"""

		print("function not supported yet")


	def prepare_drift_correction(self, pos):

		"""Not supported for TobiiProGlassesTracker (yet)"""

		print("function not supported yet")


	def pupil_size(self):

		"""Returns newest available pupil size

		arguments
		None

		returns
		pupilsize	--	a float or -1 on an error


		"""

		"""Not supported for TobiiProGlassesTracker (yet)"""

		print("function not supported yet")


	def sample(self):

		"""Returns newest available gaze position

		arguments
		None

		returns
		sample	-- an (x,y) tuple or a (-1,-1) on an error

		"""

		"""Not supported for TobiiProGlassesTracker (yet)"""

		print("function not supported yet")


	def send_command(self, cmd):

		"""Not supported for TobiiProGlassesTracker (yet)"""

		print("function not supported yet")


	def set_backdrop(self):

		"""Not supported for TobiiProGlassesTracker (yet)"""

		print("function not supported yet")


	def set_eye_used(self):

		"""Logs the eye_used variable, based on which eye was specified
		(if both eyes are being tracked, the left eye is used)

		arguments
		None

		returns
		Nothing	-- logs which eye is used by calling self.log_var, e.g.
				   self.log_var("eye_used", "right")

		"""

		"""Not supported for TobiiProGlassesTracker (yet)"""

		print("function not supported yet")


	def start_recording(self):

		"""Starts recording eye position

		arguments
		recording_id

		returns
		None		-- sets self.recording to True when recording is
				   successfully started
		"""

		if self.current_recording_id is None:

			self.current_recording_id = self.tobiiglasses.create_recording(self.current_participant_id)
			try:
				self.tobiiglasses.start_recording(self.current_recording_id)
				log.debug("Recording " + self.current_recording_id + " started!")
			except:
				raise Exception("Error in libtobiiproglasses.TobiiProGlassesController.start_recording: failed to start recording")
		else:
			log.error("The Tobii Pro Glasses is already recording!")


	def status_msg(self, msg):

		"""Not supported for TobiiProGlassesTracker (yet)"""

		print("function not supported yet")


	def stop_recording(self):

		"""Stop recording eye position

		arguments
		None

		returns
		Nothing	-- sets self.recording to False when recording is
				   successfully started

		"""

		if self.current_recording_id is None:
			log.error("There is no recordings started!")

		else:
			self.tobiiglasses.stop_recording(self.current_recording_id)
			res = self.tobiiglasses.wait_until_recording_is_done(self.current_recording_id)					
			self.current_recording_id = None


	def set_detection_type(self, eventdetection):

		"""Set the event detection type to either PyGaze algorithms, or
		native algorithms as provided by the manufacturer (only if
		available: detection type will default to PyGaze if no native
		functions are available)

		arguments
		eventdetection	--	a string indicating which detection type
						should be employed: either 'pygaze' for
						PyGaze event detection algorithms or
						'native' for manufacturers algorithms (only
						if available; will default to 'pygaze' if no
						native event detection is available)
		returns		--	detection type for saccades, fixations and
						blinks in a tuple, e.g.
						('pygaze','native','native') when 'native'
						was passed, but native detection was not
						available for saccade detection


		"""

		"""Not supported for TobiiProGlassesTracker (yet)"""

		print("function not supported yet")


	def wait_for_event(self, event):

		"""Waits for event

		arguments
		event		-- an integer event code, one of the following:
					3 = STARTBLINK
					4 = ENDBLINK
					5 = STARTSACC
					6 = ENDSACC
					7 = STARTFIX
					8 = ENDFIX

		returns
		outcome	-- a self.wait_for_* method is called, depending on the
				   specified event; the return values of corresponding
				   method are returned
		"""

		"""Not supported for TobiiProGlassesTracker (yet)"""

		print("function not supported yet")


	def wait_for_blink_end(self):

		"""Waits for a blink end and returns the blink ending time

		arguments
		None

		returns
		timestamp		--	blink ending time in milliseconds, as
						measured from experiment begin time
		"""

		"""Not supported for TobiiProGlassesTracker (yet)"""

		print("function not supported yet")

	def wait_for_blink_start(self):

		"""Waits for a blink start and returns the blink starting time

		arguments
		None

		returns
		timestamp		--	blink starting time in milliseconds, as
						measured from experiment begin time

		"""

		"""Not supported for TobiiProGlassesTracker (yet)"""

		print("function not supported yet")


	def wait_for_fixation_end(self):

		"""Returns time and gaze position when a fixation has ended;
		function assumes that a 'fixation' has ended when a deviation of
		more than self.pxfixtresh from the initial fixation position has
		been detected (self.pxfixtresh is created in self.calibration,
		based on self.fixtresh, a property defined in self.__init__)

		arguments
		None

		returns
		time, gazepos	-- time is the starting time in milliseconds (from
					   expstart), gazepos is a (x,y) gaze position
					   tuple of the position from which the fixation
					   was initiated


		"""

		"""Not supported for TobiiProGlassesTracker (yet)"""

		print("function not supported yet")

	def wait_for_fixation_start(self):

		"""Returns starting time and position when a fixation is started;
		function assumes a 'fixation' has started when gaze position
		remains reasonably stable (i.e. when most deviant samples are
		within self.pxfixtresh) for five samples in a row (self.pxfixtresh
		is created in self.calibration, based on self.fixtresh, a property
		defined in self.__init__)

		arguments
		None

		returns
		time, gazepos	-- time is the starting time in milliseconds (from
					   expstart), gazepos is a (x,y) gaze position
					   tuple of the position from which the fixation
					   was initiated

		"""

		"""Not supported for TobiiProGlassesTracker (yet)"""

		print("function not supported yet")


	def wait_for_saccade_end(self):

		"""Returns ending time, starting and end position when a saccade is
		ended; based on Dalmaijer et al. (2013) online saccade detection
		algorithm

		arguments
		None

		returns
		endtime, startpos, endpos	-- endtime in milliseconds (from
							   expbegintime); startpos and endpos
							   are (x,y) gaze position tuples

		"""

		"""Not supported for TobiiProGlassesTracker (yet)"""

		print("function not supported yet")

	def wait_for_saccade_start(self):

		"""Returns starting time and starting position when a saccade is
		started; based on Dalmaijer et al. (2013) online saccade detection
		algorithm

		arguments
		None

		returns
		endtime, startpos	-- endtime in milliseconds (from expbegintime);
					   startpos is an (x,y) gaze position tuple

		"""

		"""Not supported for TobiiProGlassesTracker (yet)"""

		print("function not supported yet")


	def is_valid_sample(self, gazepos):

		"""Checks if the sample provided is valid, based on Tobii specific
		criteria (for internal use)

		arguments
		gazepos		--	a (x,y) gaze position tuple, as returned by
						self.sample()

		returns
		valid			--	a Boolean: True on a valid sample, False on
						an invalid sample

		"""

		"""Not supported for TobiiProGlassesTracker (yet)"""

		print("function not supported yet")

	def get_data(self):

		return self.tobiiglasses.data

	def get_mems(self):

		return self.tobiiglasses.data['mems']

	def get_gp(self):

		return self.tobiiglasses.data['gp']

	def get_gp3(self):

		return self.tobiiglasses.data['gp3']

	def get_lefteyedata(self):

		return self.tobiiglasses.data['left_eye']

	def get_righteyedata(self):

		return self.tobiiglasses.data['right_eye']

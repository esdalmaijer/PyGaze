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

# The BaseClasses are meant to store the documentation on all methods of a
# class, but not to contain any functionality whatsoever. BaseClass is
# inherited by all of the subclasses, and the documentation is copied using
# pygaze.copy_docstr. If you intend to make your own subclass for the current
# baseclass, be sure to inherit BaseClass, copy the documentation, and
# redefine the methods as you see fit, e.g.:
#
#import pygaze
#from pygaze._display.basedisplay import BaseDisplay
#
#class DummyDisplay(BaseDisplay):
#
#	"""An example child of BaseDisplay"""
#
#	def __init__(self, *args, **kwargs):
#
#		"""Initializes a DummyDisplay instance"""
#
#		pygaze.copy_docstring(BaseDisplay,DummyDisplay)
#
#	def show(self):
#
#		# note that here no docstring is provided, as it is copied from
#		# the parent class
#
#		print("Display.show call at %d" % int(clock.get_time()))
#

from pygaze.py3compat import *

class BaseEyeTracker:

	"""
	desc: |
		A generic Python library for eye tracking.
	"""

	def __init__(self):

		"""
		strict:
			False

		desc: |
			Initializes the EyeTracker object.

		arguments:
			display:
				desc:	A pygaze.display.Display instance.
				type:	Display

		keywords:
			logfile:
				desc: |
					A logfile name (string value); path may be included in the
					file name for SMI and for Tobii; SMI will create a `.idf`
					and a `.txt`, Tobii will make a `.tsv`; for EyeLink PLEASE
					DO NOT USE THIS: use `data_file` instead, see below for
					explanation.
				type:	[unicode, str]
			eventdetection:
				desc: |
					A string specifying the type of event detection, either
					'native' for system default functions (not always
					available!), of 'pygaze' for Dalmaijer et al. (2013)
					algorithms; NOTE: will fall back to 'pygaze' if 'native' is
					not available on your system!
				type:	[unicode, str]
			saccade_velocity_threshold:
				desc:	A saccade velocity threshold in degrees per second.
				type:	[float, int]
			saccade_acceleration_threshold:
				desc:	A saccade acceleration threshold in degrees per square
						second.
				type:	[float, int]
			data_file:
				desc: |
					__EyeLink only!__ IMPORTANT: use data_file in stead of
					logfile keyword for EyeLink, as it does not
					support filenames longer than 8 characters (so no
					path assignment in the logfile name, as is possible
					for SMI and Tobii).
				type:	[str, unicode]
			force_drift_correct:
				desc: |
					__EyeLink only!__ Indicates whether an active drift
					correction should be used. This option is relevant for
					EyeLink 1000 devices, on which drift correction is by
					default only a check, and not an actual single-point
					recalibration.
				type:	bool
			pupil_size_mode:
				desc: |
					__EyeLink only!__ Indicates whether pupil size is recorded
					in area or diameter values.
				type:	bool
			resolution:
				desc: |
					__EyeLink only!__ Specify the display resolution using
					a (w,h) tuple.
				type:	tuple
			fg_color: |
				desc: |
					__EyeLink only!__ Specify the foreground colour using
					an (R,G,B) tuple.
				type:	tuple
			bg_color:
				desc: |
					__EyeLink only!__ Specify the background colour using
					an (R,G,B) tuple.
				type:	tuple
			ip:
				desc: __SMI only!__ The ip address for iViewX.
				type:	[str, unicode]
					(default = '127.0.0.1')
			sendport:
				desc:	__SMI only!__ port number for iViewX sending.
				type:	int
			receiveport:
				desc:	__SMI only!__ port number for iViewX receiving.
				type:	int
		"""

		pass


	def calibrate(self):

		"""
		desc: |
			Calibrates the eye tracking system. The actual behavior of this
			function depends on the type of eye tracker and is described below.

			__EyeLink:__

			This function will activate the camera-setup screen, which allows
			you to adjust the camera, and peform a calibration/ validation
			procedure. Pressing 'q' will exit the setup routine. Pressing
			'escape' will first trigger a confirmation dialog and then, upon
			confirmation, raises an Exception.

			__EyeTribe:__

			Activates a simple calibration routine.

		returns:
			desc: |
				Returns True if calibration succeeded, or False if not; in
				addition a calibration log is added to the log file and some
				properties are updated (i.e. the thresholds for detection
				algorithms).
			type:	bool
		"""

		pass

	def close(self):

		"""
		desc: |
			Neatly closes connection to tracker. Saves data and sets
			`self.connected` to False.
		"""

		pass


	def connected(self):

		"""
		desc:
			Checks if the tracker is connected.

		returns:
			desc: |
				True if connection is established, False if not; sets
				`self.connected` to the same value.
			type:	bool
		"""

		pass


	def drift_correction(self, pos=None, fix_triggered=False):

		"""
		desc: |
			Performs a drift-correction procedure. The exact behavior of this
			function on the type of eye tracker and is described below. Because
			drift correction may fail, you will generally call this function in
			a loop.

			__EyeLink:__

			Pressing 'q' during drift-correction will activate the camera-setup
			screen. From there, pressing 'q' again will cause drift correction
			to fail immediately. Pressing 'escape' will give the option to abort
			the experiment, in which case an Exception is raised.

		keywords:
			pos:
				desc:	(x, y) position of the fixation dot or None for a
						central fixation.
				type:	[tuple, NoneType]
			fix_triggered:
				desc:	Boolean indicating if drift check should be performed
						based on gaze position (True) or on spacepress (False).
				type:	bool

		returns:
			desc:	A boolean indicating if drift check is ok (True) or not
					(False).
			type:	bool
		"""

		pass


	def fix_triggered_drift_correction(self, pos=None, min_samples=30,
		max_dev=60, reset_threshold=10):

		"""
		desc: |
			Performs a fixation triggered drift correction by collecting
			a number of samples and calculating the average distance from the
			fixation position

		keywords:
			pos:
				desc:	(x, y) position of the fixation dot or None for a
						central fixation.
				type:	[tuple, NoneType]
			min_samples:
				desc:	The minimal amount of samples after which an
						average deviation is calculated.
				type:	int
			max_dev:
				desc:	The maximal deviation from fixation in pixels.
				type:	int
			reset_threshold:
				desc:	If the horizontal or vertical distance in pixels between
						two consecutive samples is larger than this threshold,
						the sample collection is reset.
				type:	int

		returns:
			desc:	A boolean indicating if drift check is ok (True) or not
					(False).
			type:	bool
		"""

		pass


	def get_eyetracker_clock_async(self):

		"""
		desc:
			Returns the difference between tracker time and PyGaze time, which
			can be used to synchronize timing

		returns:
			desc:	The difference between eyetracker time and PyGaze time.
			type:	[int, float]
		"""

		pass

	def log(self, msg):

		"""
		desc:
			Writes a message to the log file.

		arguments:
			msg:
				desc:	A message.
				type:	[str, unicode]
		"""

		pass


	def log_var(self, var, val):

		"""
		desc:
			Writes a variable's name and value to the log file

		arguments:
			var:
				desc:	A variable name.
				type:	[str, unicode]
			val:
				desc:	A variable value
		"""

		self.log(u"var %s %s" % (safe_decode(var), safe_decode(val)))

	def pupil_size(self):

		"""
		desc:
			Returns the newest pupil size sample; size may be measured as the
			diameter or the area of the pupil, depending on your setup (note
			that pupil size mostly is given in an arbitrary units).

		returns:
			desc:	Returns pupil size for the eye that is currently
					being tracked (as specified by self.eye_used) or -1
					when no data is obtainable.
			type:	[int, float]
		"""

		pass

	def sample(self):

		"""
		desc:
			Returns newest available gaze position.

		returns:
			desc: 	An (x,y) tuple or a (-1,-1) on an error.
			type:	tuple
		"""

		pass

	def send_command(self, cmd):

		"""
		desc:
			Directly sends a command to the eye tracker (not supported for all
			brands; might produce a warning message if your setup does not
			support direct commands).

		arguments:
			cmd:
				desc:	The command to be sent to the eye tracker.
				type:	[str, unicode]
		"""

		pass

	def set_eye_used(self):

		"""
		desc:
			Logs the `eye_used` variable, based on which eye was specified
			(if both eyes are being tracked, the left eye is used). Does not
			return anything.
		"""

		pass

	def draw_drift_correction_target(self, x, y):

		"""
		desc:
			Draws a drift-correction target.

		arguments:
			x:
				desc:	The X coordinate
				type:	int
			y:
				desc:	The Y coordinate
				type:	int
		"""

		pass

	def draw_calibration_target(self, x, y):

		"""
		desc:
			Draws a calibration target.

		arguments:
			x:
				desc:	The X coordinate
				type:	int
			y:
				desc:	The Y coordinate
				type:	int
		"""

		pass

	def set_draw_calibration_target_func(self, func):

		"""
		desc:
			Specifies a custom function to draw the calibration target. This
			will function will override the default [draw_calibration_target].

		arguments:
			func:
				desc:	The function to draw a calibration target. This function
						should accept two parameters, for the x and y coordinate
						of the target.
				type:	function
		"""

		self.draw_calibration_target = func

	def set_draw_drift_correction_target_func(self, func):

		"""
		desc:
			Specifies a custom function to draw the drift-correction target.
			This function will override the default
			[draw_drift_correction_target].

		arguments:
			func:
				desc:	The function to draw a drift-correction target. This
						function should accept two parameters, for the x and y
						coordinate of the target.
				type:	function
		"""

		self.draw_drift_correction_target = func

	def start_recording(self):

		"""
		desc:
			Starts recording. Sets `self.recording` to `True` when recording
			is successfully started.
		"""

		pass

	def status_msg(self, msg):

		"""
		desc:
			Sends a status message to the eye tracker, which is displayed in
			the tracker's GUI (only available for EyeLink setups).

		arguments:
			msg:
				desc: |
						A string that is to be displayed on the experimenter PC,
						e.g.: "current trial: %d" % trialnr.
				type:	[str, unicode]
		"""

		pass


	def stop_recording(self):

		"""
		desc:
			Stops recording. Sets `self.recording` to `False` when recording is
			successfully stopped.
		"""

		pass


	def set_detection_type(self, eventdetection):

		"""
		desc: |
			Set the event detection type to either PyGaze algorithms, or
			native algorithms as provided by the manufacturer (only if
			available: detection type will default to PyGaze if no native
			functions are available)

		arguments:
			eventdetection:
				desc: |
						A string indicating which detection type
						should be employed: either 'pygaze' for
						PyGaze event detection algorithms or
						'native' for manufacturers algorithms (only
						if available; will default to 'pygaze' if no
						native event detection is available)
				type:	[str, unicode]

		returns:
			desc:		Detection type for saccades, fixations and
						blinks in a tuple, e.g.
						('pygaze','native','native') when 'native'
						was passed, but native detection was not
						available for saccade detection.
			type:		tuple
		"""

		pass

	def wait_for_event(self, event):

		"""
		desc:
			Waits for an event.

		arguments:
			event:
				desc: |
					An integer event code, one of the following:

					- 3 = STARTBLINK
					- 4 = ENDBLINK
					- 5 = STARTSACC
					- 6 = ENDSACC
					- 7 = STARTFIX
					- 8 = ENDFIX

				type:	int

		returns:
			desc:	A `self.wait_for_*` method is called, depending on the
					specified event; the return value of corresponding
					method is returned.
		"""

		pass


	def wait_for_blink_end(self):

		"""
		desc: |
			Waits for a blink end and returns the blink ending time.
			Detection based on Dalmaijer et al. (2013) if EVENTDETECTION is set
			to 'pygaze', or using native detection functions if EVENTDETECTION
			is set to 'native' (NOTE: not every system has native functionality;
			will fall back to ;pygaze' if 'native' is not available!)

		returns:
			desc:	Blink ending time in milliseconds, as measured from
					experiment begin time.
			type:	[int, float]
		"""

		pass

	def wait_for_blink_start(self):

		"""
		desc: |
			Waits for a blink start and returns the blink starting time.
			Detection based on Dalmaijer et al. (2013) if EVENTDETECTION is set
			to 'pygaze', or using native detection functions if EVENTDETECTION
			is set to 'native' (NOTE: not every system has native functionality;
			will fall back to ;pygaze' if 'native' is not available!)

		returns:
			desc: 	Blink starting time in milliseconds, as measured from
					experiment begin time
			type:	[int, float]
		"""

		pass


	def wait_for_fixation_end(self):

		"""
		desc: |
			Returns time and gaze position when a fixation has ended;
			function assumes that a 'fixation' has ended when a deviation of
			more than self.pxfixtresh from the initial fixation position has
			been detected (self.pxfixtresh is created in self.calibration,
			based on self.fixtresh, a property defined in self.__init__).
			Detection based on Dalmaijer et al. (2013) if EVENTDETECTION is set
			to 'pygaze', or using native detection functions if EVENTDETECTION
			is set to 'native' (NOTE: not every system has native functionality;
			will fall back to ;pygaze' if 'native' is not available!)

		returns:
			desc: 	A `time, gazepos` tuple. Time is the end time in
					milliseconds (from expstart), gazepos is a (x,y) gaze
					position tuple of the position from which the fixation was
					initiated.
			type:	tuple
		"""

		pass


	def wait_for_fixation_start(self):

		"""
		desc: |
			Returns starting time and position when a fixation is started;
			function assumes a 'fixation' has started when gaze position
			remains reasonably stable (i.e. when most deviant samples are
			within self.pxfixtresh) for five samples in a row (self.pxfixtresh
			is created in self.calibration, based on self.fixtresh, a property
			defined in self.__init__).
			Detection based on Dalmaijer et al. (2013) if EVENTDETECTION is set
			to 'pygaze', or using native detection functions if EVENTDETECTION
			is set to 'native' (NOTE: not every system has native functionality;
			will fall back to ;pygaze' if 'native' is not available!)

		returns:
			desc: 	A `time, gazepos` tuple. Time is the starting time in
					milliseconds (from expstart), gazepos is a (x,y) gaze
					position tuple of the position from which the fixation was
					initiated.
			type:	tuple
		"""

		pass


	def wait_for_saccade_end(self):

		"""
		desc: |
			Returns ending time, starting and end position when a saccade is
			ended; based on Dalmaijer et al. (2013) online saccade detection
			algorithm if EVENTDETECTION is set to 'pygaze', or using native
			detection functions if EVENTDETECTION is set to 'native' (NOTE: not
			every system has native functionality; will fall back to ;pygaze'
			if 'native' is not available!)

		returns:
			desc:	An `endtime, startpos, endpos` tuple. Endtime in
					milliseconds (from expbegintime); startpos and endpos
					are (x,y) gaze position tuples.
			type:	tuple
		"""

		pass

	def wait_for_saccade_start(self):

		"""
		desc: |
			Returns starting time and starting position when a saccade is
			started; based on Dalmaijer et al. (2013) online saccade detection
			algorithm if EVENTDETECTION is set to 'pygaze', or using native
			detection functions if EVENTDETECTION is set to 'native' (NOTE: not
			every system has native functionality; will fall back to ;pygaze'
			if 'native' is not available!)

		returns:
			desc:	An `endtime, startpos` tuple. Endtime in milliseconds (from
					expbegintime); startpos is an (x,y) gaze position tuple.
			type:	tuple
		"""

		pass

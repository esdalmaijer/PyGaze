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

class BaseEyeTracker:

	"""A class for Display objects, to present Screen objects on a monitor"""

	def __init__(self):

		"""
		Initializes the EyeTracker object
		
		arguments
		
		display	--	a pygaze.display.Display instance
		
		keyword arguments (general)
		
		logfile		--	logfile name (string value); path may be
						inlcuded in the file name for SMI and for
						Tobii; SMI will create a .idf and a .txt,
						Tobii will make a .tsv; for EyeLink PLEASE DO
						NOT USE THIS: use data_file instead, see below
						for explanation (default = LOGFILE)
		eventdetection	--	string specifying the type of event detection,
						either 'native' for system default functions
						(not always available!), of 'pygaze' for
						Dalmaijer et al. (2013) algorithms; NOTE:
						will fall back to 'pygaze' if 'native' is not
						available on your system!
						(default = EVENTDETECTION)
		saccade_velocity_threshold	--	saccade velocity threshold in
								degrees per second
		saccade_acceleration_threshold	--	saccade acceleration threshold
									in degrees per square second

		keyword arguments (platform specific)
		
		data_file	--	EyeLink only! IMPORTANT: use data_file in stead of
					logfile keyword for EyeLink, as it does not
					support filenames longer than 8 characters (so no
					path assignment in the logfile name, as is possible
					for SMI and Tobii) (default = LOGFILENAME)
		force_drift_correct		--	EyeLink only! Indicates whether an
					active drift correction should be used. This option is
					relevant for EyeLink 1000 devices, on which drift correction
					is by default only a check, and not an actual single-point
					recalibration.
		pupil_size_mode	--	EyeLink only! Indicates whether pupil-size is
					recorded in area or diameter values. (default='area')
		resolution	--	EyeLink only! Specify the display resolution using
					a (w,h) tuple (default = DISPSIZE)
		fg_color	--	EyeLink only! Specify the foreground colour using
					a (R,G,B) tuple (default = FGC)
		bg_color	--	EyeLink only! Specify the background colour using
					a (R,G,B) tuple (default = BGC)
		
		ip		--	SMI only! ip address for iViewX
					(default = '127.0.0.1')
		sendport	--	SMI only! port number for iViewX sending
					(default = 4444)
		receiveport	--	SMI only! port number for iViewX receiving
					(default = 5555)
		"""

		pass


	def calibrate(self):

		"""
		Calibrates the eye tracking system. The actual behavior of this function
		depends on the type of eye tracker and is described below.

		EyeLink:

		This function will activate the camera-setup screen, which allows you
		to adjust the camera, and peform a calibration/ validation procedure.
		Pressing 'q' will exit the setup routine. Pressing 'escape' will first
		trigger a confirmation dialog and then, upon confirmation, raises an
		Exception.
		
		arguments
		
		None
		
		keyword arguments

		None
		
		returns
		success	--	returns True if calibration succeeded, or False if
					not; in addition a calibration log is added to the
					log file and some properties are updated (i.e. the
					thresholds for detection algorithms)
		"""

		pass


	def close(self):

		"""
		Neatly close connection to tracker
		
		arguments

		None
		
		keyword arguments
		
		None
		
		returns
		
		None		--	saves data and sets self.connected to False
		"""

		pass
		

	def connected(self):

		"""
		Checks if the tracker is connected
		
		arguments

		None

		keyword arguments
		
		None
		
		returns

		connected	--	True if connection is established, False if not;
					sets self.connected to the same value
		"""

		pass


	def drift_correction(self, pos=None, fix_triggered=False):

		"""
		Performs a drift-correction procedure. The exact behavior of this
		function on the type of eye tracker and is described below. Because
		drift correction may fail, you will generally call this function in a
		loop.

		EyeLink:

		Pressing 'q' during drift-correction will activate the camera-setup
		screen. From there, pressing 'q' again will cause drift correction to
		fail immediately. Pressing 'escape' will give the option to abort the
		experiment, in which case an Exception is raised.
		
		arguments
		
		None
		
		keyword arguments

		pos			--	(x, y) position of the fixation dot or None for
						a central fixation (default = None)
		fix_triggered	--	Boolean indicating if drift check should be
						performed based on gaze position (fix_triggered
						= True) or on spacepress (fix_triggered = 
						False) (default = False)
		
		returns
		
		checked		--	Boolaan indicating if drift check is ok (True)
						or not (False); or calls self.calibrate if 'q'
						or 'escape' is pressed
		"""

		pass
		

	def fix_triggered_drift_correction(self):

		"""
		Performs a fixation triggered drift correction by collecting
		a number of samples and calculating the average distance from the
		fixation position
		
		arguments

		None
		
		keyword arguments

		pos			--	(x, y) position of the fixation dot or None for
						a central fixation (default = None)
		min_samples		--	minimal amount of samples after which an
						average deviation is calculated (default = 10)
		max_dev		--	maximal deviation from fixation in pixels
						(default = 60)
		reset_threshold	--	if the horizontal or vertical distance in
						pixels between two consecutive samples is
						larger than this threshold, the sample
						collection is reset (default = 30)
		
		returns
		
		checked		--	Boolaan indicating if drift check is ok (True)
						or not (False); or calls self.calibrate if 'q'
						or 'escape' is pressed
		"""

		pass


	def get_eyetracker_clock_async(self):

		"""
		Returns the difference between tracker time and PyGaze time, which
		can be used to synchronize timing
		
		arguments
		
		None
		
		keyword arguments
		
		None
		
		returns
		
		timediff	--	difference between eyetracker time and PyGaze
					time
		"""


	def log(self):

		"""
		Writes a message to the log file
		
		arguments

		msg		--	a string to include in the tracker log file
		
		keyword arguments
		
		None
		
		returns
		
		None		--	writes a line in the tracker's log file
		"""

		pass


	def log_var(self):

		"""
		Writes a variable's name and value to the log file
		
		arguments

		var		--	variable name
		val		--	variable value
		
		keyword arguments
		
		None
		
		returns
		
		None		--	uses native self.log method to include a line
					in the log file in a "var NAME VALUE" layout
		"""

		pass

	def pupil_size(self):

		"""
		Returns the newest pupil size sample; size may be measured as the
		diameter or the area of the pupil, depending on your setup (note
		that pupil size mostly is given in an arbitrary units)
		
		arguments
		
		None
		
		keyword arguments
		
		None
		
		returns
		
		pupilsize	--	returns pupil size for the eye that is currently
					being tracked (as specified by self.eye_used) or -1
					when no data is obtainable
		"""

		pass


	def sample(self):

		"""
		Returns newest available gaze position
		
		arguments

		None
		
		keyword arguments
		
		None
		
		returns
		
		sample	--	an (x,y) tuple or a (-1,-1) on an error
		"""

		pass


	def send_command(self):

		"""
		Directly sends a command to the eye tracker (not supported for all
		brands; might produce a warning message if your setup does not
		support direct commands)
		
		arguments

		cmd		--	the command (a string value) to be sent to the
					eye tracker
		
		keyword arguments
		
		None
		
		returns

		None
		"""

		pass


#	def set_backdrop(self):
#
#		"""
#		Sets a background image to the experimenter PC (EyeLink only!)
#		"""
#
#		pass


	def set_eye_used(self):

		"""
		Logs the eye_used variable, based on which eye was specified
		(if both eyes are being tracked, the left eye is used)
		
		arguments
		
		None
		
		keyword arguments
		
		None
		
		returns
		
		None		--	logs which eye is used by calling self.log_var, e.g.
					self.log_var("eye_used", "right")
		"""

		pass

	def set_draw_calibration_target_func(self, func):
		
		"""
		Specifies a custom function to draw the calibration target.
		
		arguments
		
		func		--	The function to draw a calibration target. This function
					should accept two parameters, for the x and y coordinate of
					the target.
		"""
		
		pass
	
	def set_draw_drift_correction_target_func(self, func):
		
		"""
		Specifies a custom function to draw the drift-correction target.
		
		arguments
		
		func		--	The function to draw a drift-correction target. This
					function should accept two parameters, for the x and y
					coordinate of the target.
		"""
		
		pass

	def start_recording(self):

		"""
		Starts recording
		
		arguments
		
		None
		
		keyword arguments
		
		None
		
		returns
		
		None		--	sets self.recording to True when recording is
					successfully started
		"""

		pass


	def status_msg(self):

		"""
		Sends a status message to the eye tracker, which is displayed in
		the tracker's GUI (only available for EyeLink setups)
		
		arguments
		
		msg		--	a string that is to be displayed on the
					experimenter PC, e.g.:
					"current trial: %d" % trialnr
					
		keyword arguments
		
		None
		
		returns
		
		None
		"""

		pass


	def stop_recording(self):

		"""
		Stop recording eye position
		
		arguments

		None

		keyword arguments

		None
		
		returns

		None		--	sets self.recording to False when recording is
					successfully stopped
		"""

		pass
	
	
	def set_detection_type(self):
		
		"""
		Set the event detection type to either PyGaze algorithms, or
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
		
		keyword arguments
		
		None

		returns
		
		detectiontype	--	detection type for saccades, fixations and
						blinks in a tuple, e.g. 
						('pygaze','native','native') when 'native'
						was passed, but native detection was not
						available for saccade detection
		"""
		
		pass


	def wait_for_event(self):

		"""
		Waits for event
		
		arguments
		
		event		--	an integer event code, one of the following:
						3 = STARTBLINK
						4 = ENDBLINK
						5 = STARTSACC
						6 = ENDSACC
						7 = STARTFIX
						8 = ENDFIX
		
		keyword arguments
		
		None
		
		returns

		outcome	--	a self.wait_for_* method is called, depending on the
					specified event; the return values of corresponding
					method are returned
		"""

		pass


	def wait_for_blink_end(self):

		"""
		Waits for a blink end and returns the blink ending time.
		Detection based on Dalmaijer et al. (2013) if EVENTDETECTION is set
		to 'pygaze', or using native detection functions if EVENTDETECTION
		is set to 'native' (NOTE: not every system has native functionality;
		will fall back to ;pygaze' if 'native' is not available!)
		
		arguments
		
		None
		
		keyword arguments
		
		None
		
		returns
		
		timestamp		--	blink ending time in milliseconds, as
						measured from experiment begin time
		"""

		
		pass	
		

	def wait_for_blink_start(self):

		"""
		Waits for a blink start and returns the blink starting time.
		Detection based on Dalmaijer et al. (2013) if EVENTDETECTION is set
		to 'pygaze', or using native detection functions if EVENTDETECTION
		is set to 'native' (NOTE: not every system has native functionality;
		will fall back to ;pygaze' if 'native' is not available!)
		
		arguments

		None
		
		keyword arguments
		
		None
		
		returns
		
		timestamp		--	blink starting time in milliseconds, as
						measured from experiment begin time
		"""
		
		pass
		

	def wait_for_fixation_end(self):

		"""
		Returns time and gaze position when a fixation has ended;
		function assumes that a 'fixation' has ended when a deviation of
		more than self.pxfixtresh from the initial fixation position has
		been detected (self.pxfixtresh is created in self.calibration,
		based on self.fixtresh, a property defined in self.__init__).
		Detection based on Dalmaijer et al. (2013) if EVENTDETECTION is set
		to 'pygaze', or using native detection functions if EVENTDETECTION
		is set to 'native' (NOTE: not every system has native functionality;
		will fall back to ;pygaze' if 'native' is not available!)
		
		arguments
		
		None
		
		keyword arguments
		
		None
		
		returns
		
		time, gazepos	--	time is the starting time in milliseconds (from
						expstart), gazepos is a (x,y) gaze position
						tuple of the position from which the fixation
						was initiated
		"""

		pass


	def wait_for_fixation_start(self):

		"""
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
		
		arguments
		
		None
		
		keyword arguments
		
		None
		
		returns
		
		time, gazepos	--	time is the starting time in milliseconds (from
						expstart), gazepos is a (x,y) gaze position
						tuple of the position from which the fixation
						was initiated
		"""
		
		pass


	def wait_for_saccade_end(self):

		"""
		Returns ending time, starting and end position when a saccade is
		ended; based on Dalmaijer et al. (2013) online saccade detection
		algorithm if EVENTDETECTION is set to 'pygaze', or using native
		detection functions if EVENTDETECTION is set to 'native' (NOTE: not
		every system has native functionality; will fall back to ;pygaze'
		if 'native' is not available!)
		
		arguments
		
		None
		
		keyword arguments
		
		None
		
		returns
		
		endtime, startpos, endpos	--	endtime in milliseconds (from 
								expbegintime); startpos and endpos
								are (x,y) gaze position tuples
		"""

		pass

	def wait_for_saccade_start(self):

		"""
		Returns starting time and starting position when a saccade is
		started; based on Dalmaijer et al. (2013) online saccade detection
		algorithm if EVENTDETECTION is set to 'pygaze', or using native
		detection functions if EVENTDETECTION is set to 'native' (NOTE: not
		every system has native functionality; will fall back to ;pygaze'
		if 'native' is not available!)
		
		arguments

		None
		
		keyword arguments
		
		None
		
		returns
		
		endtime, startpos	--	endtime in milliseconds (from expbegintime);
							startpos is an (x,y) gaze position tuple
		"""

		pass
	


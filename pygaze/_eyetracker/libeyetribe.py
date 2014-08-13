# -*- coding: utf-8 -*-
#
# This file is part of PyGaze - the open-source toolbox for eye tracking
#
# PyGaze is a Python module for easily creating gaze contingent experiments
# or other software (as well as non-gaze contingent experiments/software)
# Copyright (C) 2012-2014 Edwin S. Dalmaijer
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


# PyGaze imports
from pygaze.defaults import *
from pygaze.libtime import clock
try:
	from constants import *
except:
	pass

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

# native imports
import copy
import math
import random

# external imports
from pytribe import EyeTribe


def deg2pix(cmdist, angle, pixpercm):

	"""Returns the value in pixels for given values (internal use)
	
	arguments
	cmdist	-- distance to display in centimeters
	angle		-- size of stimulus in visual angle
	pixpercm	-- amount of pixels per centimeter for display
	
	returns
	pixelsize	-- stimulus size in pixels (calculation based on size in
			   visual angle on display with given properties)
	"""

	cmsize = math.tan(math.radians(angle)) * float(cmdist)
	return cmsize * pixpercm


# class
class EyeTribeTracker(BaseEyeTracker):

	"""A class for EyeTribeTracker objects"""

	def __init__(self, display, logfile=LOGFILE, eventdetection=EVENTDETECTION, \
		saccade_velocity_threshold=35, saccade_acceleration_threshold=9500, \
		**args):

		"""Initializes the EyeTribeTracker object
		
		arguments
		display	-- a pygaze.display.Display instance
		
		keyword arguments
		logfile	-- logfile name (string value); note that this is the
				   name for the eye data log file (default = LOGFILE)
		"""

		# try to copy docstrings (but ignore it if it fails, as we do
		# not need it for actual functioning of the code)
		try:
			copy_docstr(BaseEyeTracker, EyeTribeTracker)
		except:
			# we're not even going to show a warning, since the copied
			# docstring is useful for code editors; these load the docs
			# in a non-verbose manner, so warning messages would be lost
			pass

		# object properties
		self.disp = display
		self.screen = Screen()
		self.dispsize = DISPSIZE # display size in pixels
		self.screensize = SCREENSIZE # display size in cm
		self.kb = Keyboard(keylist=['space', 'escape', 'q'], timeout=1)
		self.errorbeep = Sound(osc='saw',freq=100, length=100)
		
		# output file properties
		self.outputfile = logfile
		
		# eye tracker properties
		self.connected = False
		self.recording = False
		self.errdist = 2 # degrees; maximal error for drift correction
		self.maxtries = 100 # number of samples obtained before giving up (for obtaining accuracy and tracker distance information, as well as starting or stopping recording)
		self.prevsample = (-1,-1)
		self.prevps = -1
		
		# event detection properties
		self.fixtresh = 1.5 # degrees; maximal distance from fixation start (if gaze wanders beyond this, fixation has stopped)
		self.fixtimetresh = 100 # milliseconds; amount of time gaze has to linger within self.fixtresh to be marked as a fixation
		self.spdtresh = saccade_velocity_threshold # degrees per second; saccade velocity threshold
		self.accthresh = saccade_acceleration_threshold # degrees per second**2; saccade acceleration threshold
		self.eventdetection = eventdetection
		self.set_detection_type(self.eventdetection)
		self.weightdist = 10 # weighted distance, used for determining whether a movement is due to measurement error (1 is ok, higher is more conservative and will result in only larger saccades to be detected)

		# connect to the tracker
		self.eyetribe = EyeTribe(logfilename=logfile)

		# get info on the sample rate
		self.samplerate = self.eyetribe._samplefreq
		self.sampletime = 1000.0 * self.eyetribe._intsampletime

		# initiation report
		self.log("pygaze initiation report start")
		self.log("display resolution: %sx%s" % (self.dispsize[0],self.dispsize[1]))
		self.log("display size in cm: %sx%s" % (self.screensize[0],self.screensize[1]))
		self.log("samplerate: %.2f Hz" % self.samplerate)
		self.log("sampletime: %.2f ms" % self.sampletime)
		self.log("fixation threshold: %s degrees" % self.fixtresh)
		self.log("speed threshold: %s degrees/second" % self.spdtresh)
		self.log("acceleration threshold: %s degrees/second**2" % self.accthresh)
		self.log("pygaze initiation report end")


	def calibrate(self):

		"""Calibrates the eye tracking system
		
		arguments
		None
		
		keyword arguments
		None

		returns
		success	-- returns True if calibration succeeded, or False if
				   not; in addition a calibration log is added to the
				   log file and some properties are updated (i.e. the
				   thresholds for detection algorithms)
		"""
		
		# CALIBRATION
		# determine the calibration points
		calibpoints = []
		for x in [0.1,0.5,0.9]:
			for y in [0.1,0.5,0.9]:
				calibpoints.append((int(x*self.dispsize[0]),int(y*self.dispsize[1])))
		random.shuffle(calibpoints)
		
		# show a message
		self.screen.clear()
		self.screen.draw_text(text="Press Space to start the calibration.")
		self.disp.fill(self.screen)
		self.disp.show()
		
		# wait for keyboard input
		key, keytime = self.kb.get_key(keylist=['q','space'], timeout=None, flush=True)
		if key == 'q':
			quited = True
		else:
			quited = False
		
		# run until the user is statisfied, or quits
		calibrated = False
		calibresult = None
		while not quited and not calibrated:
			# start a new calibration
			self.eyetribe.calibration.start(pointcount=len(calibpoints))
			
			# loop through calibration points
			for cpos in calibpoints:
				# show a new calibration point
				self.screen.clear()
				self.screen.draw_fixation(fixtype='dot', pos=cpos)
				self.disp.fill(self.screen)
				self.disp.show()
				# wait for a bit to allow participant to start looking at
				# the calibration point (#TODO: space press?)
				clock.pause(1000)
				# start calibration of point
				self.eyetribe.calibration.pointstart(cpos[0],cpos[1])
				# wait for a second
				clock.pause(1000)
				# stop calibration of this point
				result = self.eyetribe.calibration.pointend()
				# the final calibration point returns a dict (does it?)
				if type(result) == dict:
					calibresult = copy.deepcopy(result)
				# check if the Q key has been pressed
				if self.kb.get_key(keylist=['q'],timeout=10,flush=False)[0] == 'q':
					# abort calibration
					self.eyetribe.calibration.abort()
					# set quited variable and break this for loop
					quited = True
					break
			
			# retry option if the calibration was aborted			
			if quited:
				# show retry message
				self.screen.clear()
				self.screen.draw_text("Calibration aborted. Press Space to restart, or 'Q' to quit.")
				self.disp.fill(self.screen)
				self.disp.show()
				# get input
				key, keytime = self.kb.get_key(keylist=['q','space'], timeout=None, flush=True)
				if key == 'space':
					# unset quited Boolean
					quited = False
				# skip further processing
				continue

			# get the calibration result if it was not obtained yet
			if type(calibresult) != dict:
				# empty display
				self.disp.fill()
				self.disp.show()
				# allow for a bit of calculation time
				clock.pause(2000)
				# get the result
				calibresult = self.eyetribe._tracker.get_calibresult()

			# results
			# clear the screen
			self.screen.clear()
			# draw results for each point
			if type(calibresult) == dict:
				for p in calibresult['calibpoints']:
					# only draw the point if data was obtained
					if p['state'] > 0:
						# draw the mean error
						self.screen.draw_circle(colour=(252,233,79), pos=(p['cpx'],p['cpy']), r=p['mepix'], pw=0, fill=True)
						# draw the point
						self.screen.draw_fixation(fixtype='dot', colour=(115,210,22), pos=(p['cpx'],p['cpy']))
						# draw the estimated point
						self.screen.draw_fixation(fixtype='dot', colour=(32,74,135), pos=(p['mecpx'],p['mecpy']))
						# annotate accuracy
						self.screen.draw_text(text=str(p['acd']), pos=(p['cpx']+10,p['cpy']+10), fontsize=12)
					# if no data was obtained, draw the point in red
					else:
						self.screen.draw_fixation(fixtype='dot', colour=(204,0,0), pos=(p['cpx'],p['cpy']))
				# draw box for averages
				self.screen.draw_rect(colour=(238,238,236), x=int(self.dispsize[0]*0.15), y=int(self.dispsize[1]*0.2), w=400, h=200, pw=0, fill=True)
				# draw result
				if calibresult['result']:
					self.screen.draw_text(text="calibration is successful", colour=(115,210,22), pos=(int(self.dispsize[0]*0.25),int(self.dispsize[1]*0.25)), fontsize=12)
				else:
					self.screen.draw_text(text="calibration failed", colour=(204,0,0), pos=(int(self.dispsize[0]*0.25),int(self.dispsize[1]*0.25)), fontsize=12)
				# draw average accuracy
				self.screen.draw_text(text="average error = %.2f degrees" % (calibresult['deg']), colour=(211,215,207), pos=(int(self.dispsize[0]*0.25),int(self.dispsize[1]*0.25+20)), fontsize=12)
				# draw input options
				self.screen.draw_text(text="Press Space to continue, or 'R' to restart.", colour=(211,215,207), pos=(int(self.dispsize[0]*0.25),int(self.dispsize[1]*0.25+40)), fontsize=12)
			else:
				self.screen.draw_text(text="Calibration failed, press 'R' to try again.")
			# show the results
			self.disp.fill(self.screen)
			self.disp.show()
			# wait for input
			key, keytime = self.kb.get_key(keylist=['space','r'], timeout=None, flush=True)
			# process input
			if key == 'space':
				calibrated = True

		# calibration failed if the user quited
		if quited:
			return False

		# NOISE CALIBRATION
		# get all error estimates (pixels)
		var = []
		for p in calibresult['calibpoints']:
			# only draw the point if data was obtained
			if p['state'] > 0:
				var.append(p['mepix'])
		noise = sum(var) / float(len(var))
		self.pxdsttresh = (noise, noise)
				
		# AFTERMATH
		# store some variables
		pixpercm = (self.dispsize[0]/float(self.screensize[0]) + self.dispsize[1]/float(self.screensize[1])) / 2
		screendist = SCREENDIST
		# calculate thresholds based on tracker settings
		self.accuracy = ((calibresult['Ldeg'],calibresult['Ldeg']), (calibresult['Rdeg'],calibresult['Rdeg'])) 
		self.pxerrdist = deg2pix(screendist, self.errdist, pixpercm)
		self.pxfixtresh = deg2pix(screendist, self.fixtresh, pixpercm)
		self.pxaccuracy = ((deg2pix(screendist, self.accuracy[0][0], pixpercm),deg2pix(screendist, self.accuracy[0][1], pixpercm)), (deg2pix(screendist, self.accuracy[1][0], pixpercm),deg2pix(screendist, self.accuracy[1][1], pixpercm)))
		self.pxspdtresh = deg2pix(screendist, self.spdtresh/1000.0, pixpercm) # in pixels per millisecond
		self.pxacctresh = deg2pix(screendist, self.accthresh/1000.0, pixpercm) # in pixels per millisecond**2

		# calibration report
		self.log("pygaze calibration report start")
		self.log("accuracy (degrees): LX=%s, LY=%s, RX=%s, RY=%s" % (self.accuracy[0][0],self.accuracy[0][1],self.accuracy[1][0],self.accuracy[1][1]))
		self.log("accuracy (in pixels): LX=%s, LY=%s, RX=%s, RY=%s" % (self.pxaccuracy[0][0],self.pxaccuracy[0][1],self.pxaccuracy[1][0],self.pxaccuracy[1][1]))
		self.log("precision (RMS noise in pixels): X=%s, Y=%s" % (self.pxdsttresh[0],self.pxdsttresh[1]))
		self.log("distance between participant and display: %s cm" % screendist)
		self.log("fixation threshold: %s pixels" % self.pxfixtresh)
		self.log("speed threshold: %s pixels/ms" % self.pxspdtresh)
		self.log("acceleration threshold: %s pixels/ms**2" % self.pxacctresh)
		self.log("pygaze calibration report end")

		return True


	def close(self):

		"""Neatly close connection to tracker
		
		arguments
		None
		
		returns
		Nothing	-- saves data and sets self.connected to False
		"""

		# close connection
		self.eyetribe.close()
		self.connected = False		


	def connected(self):

		"""Checks if the tracker is connected
		
		arguments
		None
		
		returns
		connected	-- True if connection is established, False if not;
				   sets self.connected to the same value
		"""

		res = self.eyetribe._tracker.get_trackerstate()

		if res == 0:
			self.connected = True
		else:
			self.connected = False

		return self.connected


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

		if fix_triggered:
			return self.fix_triggered_drift_correction(pos)
		self.draw_drift_correction_target(pos[0], pos[1])
		if pos == None:
			pos = self.dispsize[0] / 2, self.dispsize[1] / 2

		pressed = False
		while not pressed:
			pressed, presstime = self.kb.get_key()
			if pressed:
				if pressed == 'escape' or pressed == 'q':
					print("libeyetribe.EyeTribeTracker.drift_correction: 'q' or 'escape' pressed")
					return self.calibrate()
				gazepos = self.sample()
				if ((gazepos[0]-pos[0])**2  + (gazepos[1]-pos[1])**2)**0.5 < self.pxerrdist:
					return True
				else:
					self.errorbeep.play()
		return False
		

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

		self.draw_drift_correction_target(pos[0], pos[1])
		if pos == None:
			pos = self.dispsize[0] / 2, self.dispsize[1] / 2

		# loop until we have sufficient samples
		lx = []
		ly = []
		while len(lx) < min_samples:

			# pressing escape enters the calibration screen
			if self.kb.get_key()[0] in ['escape','q']:
				print("libeyetribe.EyeTribeTracker.fix_triggered_drift_correction: 'q' or 'escape' pressed")
				return self.calibrate()

			# collect a sample
			x, y = self.sample()

			if len(lx) == 0 or x != lx[-1] or y != ly[-1]:

				# if present sample deviates too much from previous sample, reset counting
				if len(lx) > 0 and (abs(x - lx[-1]) > reset_threshold or abs(y - ly[-1]) > reset_threshold):
					lx = []
					ly = []

				# collect samples
				else:
					lx.append(x)
					ly.append(y)

			if len(lx) == min_samples:

				avg_x = sum(lx) / len(lx)
				avg_y = sum(ly) / len(ly)
				d = ((avg_x - pos[0]) ** 2 + (avg_y - pos[1]) ** 2)**0.5

				if d < max_dev:
					return True
				else:
					lx = []
					ly = []
					
	def set_draw_drift_correction_target_func(self, func):
		
		"""See pygaze._eyetracker.baseeyetracker.BaseEyeTracker"""
		
		self.draw_drift_correction_target = func					

	def get_eyetracker_clock_async(self):

		"""Not supported for EyeTribeTracker (yet)"""

		print("function not supported yet")


	def log(self, msg):

		"""Writes a message to the log file
		
		arguments
		ms		-- a string to include in the log file
		
		returns
		Nothing	-- uses native log function of iViewX to include a line
				   in the log file
		"""

		self.eyetribe.log_message(msg)


	def log_var(self, var, val):

		"""Writes a variable to the log file
		
		arguments
		var		-- variable name
		val		-- variable value
		
		returns
		Nothing	-- uses native log function of iViewX to include a line
				   in the log file in a "var NAME VALUE" layout
		"""

		msg = "var %s %s" % (var, val)

		self.log(msg)


	def prepare_drift_correction(self, pos):

		"""Not supported for EyeTribeTracker (yet)"""

		print("function not supported yet")


	def pupil_size(self):

		"""Return pupil size
		
		arguments
		None
		
		returns
		pupil size	-- returns pupil diameter for the eye that is currently
				   being tracked (as specified by self.eye_used) or -1
				   when no data is obtainable
		"""
		
		# get newest pupil size
		ps = self.eyetribe.pupil_size()
		
		# invalid data
		if ps == None:
			return -1
		
		# check if the new pupil size is the same as the previous
		if ps != self.prevps:
			# update the pupil size
			self.prevps = copy.copy(ps)
		
		return self.prevps


	def sample(self):

		"""Returns newest available gaze position
		
		arguments
		None
		
		returns
		sample	-- an (x,y) tuple or a (-1,-1) on an error
		"""

		# get newest sample
		s = self.eyetribe.sample()
		
		# invalid data
		if s == (None,None):
			return (-1,-1)
		
		# check if the new sample is the same as the previous
		if s != self.prevsample:
			# update the current sample
			self.prevsample = copy.copy(s)
		
		return self.prevsample


	def send_command(self, cmd):

		"""Sends a command to the eye tracker
		
		arguments
		cmd		--	the command to be sent to the EyeTribe, which should
					be a list with the following information:
						[category, request, values]
		
		returns
		Nothing
		"""

		self.eyetribe._connection.request(cmd)


	def start_recording(self):

		"""Starts recording eye position
		
		arguments
		None
		
		returns
		Nothing	-- sets self.recording to True when recording is
				   successfully started
		"""

		self.eyetribe.start_recording()
		self.recording = True


	def status_msg(self, msg):

		"""Not supported for EyeTribeTracker (yet)"""

		print("function not supported yet")


	def stop_recording(self):

		"""Stop recording eye position
		
		arguments
		None
		
		returns
		Nothing	-- sets self.recording to False when recording is
				   successfully started
		"""

		self.eyetribe.stop_recording()
		self.recording = False
	
	
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
		
		if eventdetection in ['pygaze','native']:
			self.eventdetection = eventdetection
		
		return ('pygaze','pygaze','pygaze')


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
		else:
			raise Exception("Error in libsmi.SMItracker.wait_for_event: eventcode %s is not supported" % event)

		return outcome


	def wait_for_blink_end(self):

		"""Waits for a blink end and returns the blink ending time
		
		arguments
		None
		
		returns
		timestamp		--	blink ending time in milliseconds, as
						measured from experiment begin time
		"""

		
		# # # # #
		# EyeTribe method

		if self.eventdetection == 'native':
			
			# print warning, since EyeTribe does not have a blink detection
			# built into their API
			
			print("WARNING! 'native' event detection has been selected, \
				but EyeTribe does not offer blink detection; PyGaze algorithm \
				will be used")

		# # # # #
		# PyGaze method
		
		blinking = True
		
		# loop while there is a blink
		while blinking:
			# get newest sample
			gazepos = self.sample()
			# check if it's valid
			if self.is_valid_sample(gazepos):
				# if it is a valid sample, blinking has stopped
				blinking = False
		
		# return timestamp of blink end
		return clock.get_time()		
		

	def wait_for_blink_start(self):

		"""Waits for a blink start and returns the blink starting time
		
		arguments
		None
		
		returns
		timestamp		--	blink starting time in milliseconds, as
						measured from experiment begin time
		"""
		
		# # # # #
		# EyeTribe method

		if self.eventdetection == 'native':
			
			# print warning, since EyeTribe does not have a blink detection
			# built into their API
			
			print("WARNING! 'native' event detection has been selected, \
				but EyeTribe does not offer blink detection; PyGaze algorithm \
				will be used")

		# # # # #
		# PyGaze method
		
		blinking = False
		
		# loop until there is a blink
		while not blinking:
			# get newest sample
			gazepos = self.sample()
			# check if it's a valid sample
			if not self.is_valid_sample(gazepos):
				# get timestamp for possible blink start
				t0 = clock.get_time()
				# loop until a blink is determined, or a valid sample occurs
				while not self.is_valid_sample(self.sample()):
					# check if time has surpassed 150 ms
					if clock.get_time()-t0 >= 150:
						# return timestamp of blink start
						return t0
		

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

		# # # # #
		# EyeTribe method

		if self.eventdetection == 'native':
			
			# print warning, since EyeTribe does not have a blink detection
			# built into their API
			
			print("WARNING! 'native' event detection has been selected, \
				but EyeTribe does not offer fixation detection; \
				PyGaze algorithm will be used")

		# # # # #
		# PyGaze method
			
		# function assumes that a 'fixation' has ended when a deviation of more than fixtresh
		# from the initial 'fixation' position has been detected
		
		# get starting time and position
		stime, spos = self.wait_for_fixation_start()
		
		# loop until fixation has ended
		while True:
			# get new sample
			npos = self.sample() # get newest sample
			# check if sample is valid
			if self.is_valid_sample(npos):
				# check if sample deviates to much from starting position
				if (npos[0]-spos[0])**2 + (npos[1]-spos[1])**2 > self.pxfixtresh**2: # Pythagoras
					# break loop if deviation is too high
					break

		return clock.get_time(), spos


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
		
		# # # # #
		# EyeTribe method

		if self.eventdetection == 'native':
			
			# print warning, since EyeTribe does not have a fixation start
			# detection built into their API (only ending)
			
			print("WARNING! 'native' event detection has been selected, \
				but EyeTribe does not offer fixation detection; \
				PyGaze algorithm will be used")
			
			
		# # # # #
		# PyGaze method
		
		# function assumes a 'fixation' has started when gaze position
		# remains reasonably stable for self.fixtimetresh
		
		# get starting position
		spos = self.sample()
		while not self.is_valid_sample(spos):
			spos = self.sample()
		
		# get starting time
		t0 = clock.get_time()

		# wait for reasonably stable position
		moving = True
		while moving:
			# get new sample
			npos = self.sample()
			# check if sample is valid
			if self.is_valid_sample(npos):
				# check if new sample is too far from starting position
				if (npos[0]-spos[0])**2 + (npos[1]-spos[1])**2 > self.pxfixtresh**2: # Pythagoras
					# if not, reset starting position and time
					spos = copy.copy(npos)
					t0 = clock.get_time()
				# if new sample is close to starting sample
				else:
					# get timestamp
					t1 = clock.get_time()
					# check if fixation time threshold has been surpassed
					if t1 - t0 >= self.fixtimetresh:
						# return time and starting position
						return t1, spos


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

		# # # # #
		# EyeTribe method

		if self.eventdetection == 'native':
			
			# print warning, since EyeTribe does not have a blink detection
			# built into their API
			
			print("WARNING! 'native' event detection has been selected, \
				but EyeTribe does not offer saccade detection; PyGaze \
				algorithm will be used")

		# # # # #
		# PyGaze method
		
		# get starting position (no blinks)
		t0, spos = self.wait_for_saccade_start()
		# get valid sample
		prevpos = self.sample()
		while not self.is_valid_sample(prevpos):
			prevpos = self.sample()
		# get starting time, intersample distance, and velocity
		t1 = clock.get_time()
		s = ((prevpos[0]-spos[0])**2 + (prevpos[1]-spos[1])**2)**0.5 # = intersample distance = speed in px/sample
		v0 = s / (t1-t0)

		# run until velocity and acceleration go below threshold
		saccadic = True
		while saccadic:
			# get new sample
			newpos = self.sample()
			t1 = clock.get_time()
			if self.is_valid_sample(newpos) and newpos != prevpos:
				# calculate distance
				s = ((newpos[0]-prevpos[0])**2 + (newpos[1]-prevpos[1])**2)**0.5 # = speed in pixels/sample
				# calculate velocity
				v1 = s / (t1-t0)
				# calculate acceleration
				a = (v1-v0) / (t1-t0) # acceleration in pixels/sample**2 (actually is v1-v0 / t1-t0; but t1-t0 = 1 sample)
				# check if velocity and acceleration are below threshold
				if v1 < self.pxspdtresh and (a > -1*self.pxacctresh and a < 0):
					saccadic = False
					epos = newpos[:]
					etime = clock.get_time()
				# update previous values
				t0 = copy.copy(t1)
				v0 = copy.copy(v1)
			# udate previous sample
			prevpos = newpos[:]

		return etime, spos, epos


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

		# # # # #
		# EyeTribe method

		if self.eventdetection == 'native':
			
			# print warning, since EyeTribe does not have a blink detection
			# built into their API
			
			print("WARNING! 'native' event detection has been selected, \
				but EyeTribe does not offer saccade detection; PyGaze \
				algorithm will be used")

		# # # # #
		# PyGaze method
		
		# get starting position (no blinks)
		newpos = self.sample()
		while not self.is_valid_sample(newpos):
			newpos = self.sample()
		# get starting time, position, intersampledistance, and velocity
		t0 = clock.get_time()
		prevpos = newpos[:]
		s = 0
		v0 = 0

		# get samples
		saccadic = False
		while not saccadic:
			# get new sample
			newpos = self.sample()
			t1 = clock.get_time()
			if self.is_valid_sample(newpos) and newpos != prevpos:
				# check if distance is larger than precision error
				sx = newpos[0]-prevpos[0]; sy = newpos[1]-prevpos[1]
				if (sx/self.pxdsttresh[0])**2 + (sy/self.pxdsttresh[1])**2 > self.weightdist: # weigthed distance: (sx/tx)**2 + (sy/ty)**2 > 1 means movement larger than RMS noise
					# calculate distance
					s = ((sx)**2 + (sy)**2)**0.5 # intersampledistance = speed in pixels/ms
					# calculate velocity
					v1 = s / (t1-t0)
					# calculate acceleration
					a = (v1-v0) / (t1-t0) # acceleration in pixels/ms**2
					# check if either velocity or acceleration are above threshold values
					if v1 > self.pxspdtresh or a > self.pxacctresh:
						saccadic = True
						spos = prevpos[:]
						stime = clock.get_time()
					# update previous values
					t0 = copy.copy(t1)
					v0 = copy.copy(v1)

				# udate previous sample
				prevpos = newpos[:]

		return stime, spos
	
	
	def is_valid_sample(self, gazepos):
		
		"""Checks if the sample provided is valid, based on EyeTribe specific
		criteria (for internal use)
		
		arguments
		gazepos		--	a (x,y) gaze position tuple, as returned by
						self.sample()
		
		returns
		valid		--	a Boolean: True on a valid sample, False on
						an invalid sample
		"""
		
		# return False if a sample is invalid
		if gazepos == (None,None) or gazepos == (-1,-1):
			return False
		
		# in any other case, the sample is valid
		return True

# Copyright (C) 2012-2019 Edwin S. Dalmaijer
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
import pygaze
from pygaze.py3compat import *
from pygaze import settings
from pygaze.libtime import clock
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
import ctypes
import math
import random

# external imports
from .alea import AleaTracker as OGAleaTracker


def deg2pix(cmdist, angle, pixpercm):

	"""Returns the value in pixels for given values (internal use)
	
	arguments
	cmdist	-- distance to display in centimeters
	angle		-- size of stimulus in visual angle
	pixpercm	-- amount of pixels per centimeter for display
	
	returns
	pixelsize	-- stimulus size in pixels
	"""

	cmsize = math.tan(math.radians(angle)) * float(cmdist)
	return cmsize * pixpercm

def pix2deg(cmdist, pixelsize, pixpercm):

	"""Converts a distance on the screen in pixels into degrees of visual
	angle (internal use)
	
	arguments
	cmdist	-- distance to display in centimeters
	pixelsize	-- stimulus size in pixels
	pixpercm	-- amount of pixels per centimeter for display
	
	returns
	angle		-- size of stimulus in visual angle
	"""
	
	cmsize = float(pixelsize) / pixpercm
	return 2 * cmdist * math.tan(math.radians(cmsize) / 2.0)


class AleaTracker(BaseEyeTracker):

	"""A class for AleaTracker objects"""

	def __init__(self, display, logfile=settings.LOGFILE, \
		eventdetection=settings.EVENTDETECTION, \
		saccade_velocity_threshold=35, \
		saccade_acceleration_threshold=9500, \
		blink_threshold=settings.BLINKTHRESH, \
		**args):

		"""Initializes the AleaTracker object
		
		arguments
		display	-- a pygaze.display.Display instance
		
		keyword arguments
		logfile	-- logfile name (string value); note that this is the
				   name for the eye data log file (default = LOGFILE)
		"""

		# try to copy docstrings (but ignore it if it fails, as we do
		# not need it for actual functioning of the code)
		try:
			copy_docstr(BaseEyeTracker, AleaTracker)
		except:
			# we're not even going to show a warning, since the copied
			# docstring is useful for code editors; these load the docs
			# in a non-verbose manner, so warning messages would be lost
			pass

		# object properties
		self.disp = display
		self.screen = Screen()
		self.dispsize = self.disp.dispsize # display size in pixels
		self.screensize = settings.SCREENSIZE # display size in cm
		self.kb = Keyboard(keylist=['space', 'escape', 'q'], timeout=1)
		self.errorbeep = Sound(osc='saw', freq=100, length=100)
		
		# show a message
		self.screen.clear()
		self.screen.draw_text(
			text="Initialising the eye tracker, please wait...",
			fontsize=20)
		self.disp.fill(self.screen)
		self.disp.show()
		
		# output file properties
		self.outputfile = logfile + '.tsv'
		
		# eye tracker properties
		self.connected = False
		self.recording = False
		self.errdist = 2 # degrees; maximal error for drift correction
		self.pxerrdist = 30 # initial error in pixels
		self.maxtries = 100 # number of samples obtained before giving up (for obtaining accuracy and tracker distance information, as well as starting or stopping recording)
		self.prevsample = (-1,-1)
		self.prevps = -1
		
		# event detection properties
		self.fixtresh = 1.5 # degrees; maximal distance from fixation start (if gaze wanders beyond this, fixation has stopped)
		self.fixtimetresh = 100 # milliseconds; amount of time gaze has to linger within self.fixtresh to be marked as a fixation
		self.spdtresh = saccade_velocity_threshold # degrees per second; saccade velocity threshold
		self.accthresh = saccade_acceleration_threshold # degrees per second**2; saccade acceleration threshold
		self.blinkthresh = blink_threshold # milliseconds; blink detection threshold used in PyGaze method
		self.eventdetection = eventdetection
		self.set_detection_type(self.eventdetection)
		self.weightdist = 10 # weighted distance, used for determining whether a movement is due to measurement error (1 is ok, higher is more conservative and will result in only larger saccades to be detected)

		# connect to the tracker
		self.alea = OGAleaTracker("pg=12", file_path=self.outputfile)

		# get info on the sample rate
		# TODO: Compute after streaming some samples?
		self.samplerate = 60.0
		self.sampletime = 1000.0 / self.samplerate

		# initiation report
		self.log("pygaze initiation report start")
		self.log("display resolution: %sx%s" % (self.dispsize[0], self.dispsize[1]))
		self.log("display size in cm: %sx%s" % (self.screensize[0], self.screensize[1]))
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
		
		# Show a message.
		self.screen.clear()
		self.screen.draw_text(
			text="Running calibration in the foreground...",
			fontsize=20)
		self.disp.fill(self.screen)
		self.disp.show()
		
		# CALIBRATION
		# Re-run the calibration until it was approved by the user.
		quited = False
		calibration_approved = False
		while not calibration_approved:
			# Wait for the calibration to finish.
			status, improve = self.alea.calibrate()
			# Construct a string message.
			calib_str = "Calibration:\n- status = %s\n- improve=%s\n\n\nPress R to retry, or Space to continue." \
				% (status, improve)
			# Show calibration results.
			self.screen.clear()
			self.screen.draw_text(text=calib_str, fontsize=20)
			self.disp.fill(self.screen)
			self.disp.show()
			# Wait for user input.
			key = None
			while key not in ["r", "Space", "space", "q"]:
				key, keytime = self.kb.get_key(keylist=['q', 'r', 'space'],
					timeout=None, flush=True)
			# Process key press.
			if key in ["q", "Space", "space"]:
				calibration_approved = True
				if key == "q":
					quited = True

		# Calibration failed if the user quited.
		if quited:
			return False

		# NOISE CALIBRATION
		# Present noise calibration instructions.
		self.screen.clear()
		self.screen.draw_text(
			text="Noise calibration. Please look at the dot, and press any key to start.",
			fontsize=20, \
			pos=(int(self.dispsize[0]/2),int(self.dispsize[1]*0.3)))
		self.screen.draw_fixation(fixtype="dot")
		self.disp.fill(self.screen)
		self.disp.show()
		# Wait for a keypress.
		key, keytime = self.kb.get_key(keylist=None, timeout=None, \
			flush=True)
		# Start with empty lists.
		err = {'LX':[], 'LY':[], 'RX':[], 'RY':[]}
		var = {'LX':[], 'LY':[], 'RX':[], 'RY':[]}
		# Start streaming data so that samples can be obtained.
		self.start_recording()
		self.log("noise_calibration_start")
		# Present a central fixation.
		x = int(float(self.dispsize[0]) / 2.0)
		y = int(float(self.dispsize[1]) / 2.0)
		self.screen.clear()
		self.screen.draw_fixation(fixtype="dot", pos=(x,y))
		self.disp.fill(self.screen)
		t0 = self.disp.show()
		# Collect at least 10 samples, and wait for at least 1 second.
		i = 0
		while (i < 10) or (clock.get_time()-t0 < 1000):
			# Get new sample.
			gx, gy = self.sample()
			if (gx > 0) and (gy > 0):
				i += 1
				err["LX"].append(abs(float(x) - float(gx)))
				err["LY"].append(abs(float(y) - float(gy)))
				err["RX"].append(abs(float(x) - float(gx)))
				err["RY"].append(abs(float(y) - float(gy)))
				for k in var.keys():
					var[k].append(err[k][-1]**2)
				clock.pause(self.sampletime)
		# Stop streaming.
		self.log("noise_calibration_stop")
		self.stop_recording()

		# Compute the RMS noise for the calibration points.
		xnoise = (math.sqrt(sum(var['LX']) / float(len(var['LX']))) + \
			math.sqrt(sum(var['RX']) / float(len(var['RX'])))) / 2.0
		ynoise = (math.sqrt(sum(var['LY']) / float(len(var['LY']))) + \
			math.sqrt(sum(var['RY']) / float(len(var['RY'])))) / 2.0
		self.pxdsttresh = (xnoise, ynoise)
				
		# AFTERMATH
		# store some variables
		pixpercm = (self.dispsize[0] / float(self.screensize[0]) + \
			self.dispsize[1]/float(self.screensize[1])) / 2
		screendist = settings.SCREENDIST
		# calculate thresholds based on tracker settings
		self.accuracy = ( \
			(pix2deg(screendist, sum(err['LX']) / float(len(err['LX'])), pixpercm), \
			pix2deg(screendist, sum(err['LY']) / float(len(err['LY'])), pixpercm)), \
			(pix2deg(screendist, sum(err['RX']) / float(len(err['RX'])), pixpercm), \
			pix2deg(screendist, sum(err['RY']) / float(len(err['RY'])), pixpercm)))
		self.pxerrdist = deg2pix(screendist, self.errdist, pixpercm)
		self.pxfixtresh = deg2pix(screendist, self.fixtresh, pixpercm)
		self.pxaccuracy = ( \
			(sum(err['LX']) / float(len(err['LX'])), \
			sum(err['LY']) / float(len(err['LY']))), \
			(sum(err['RX']) / float(len(err['RX'])), \
			sum(err['RY']) / float(len(err['RY']))))
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
		self.alea.close()
		self.connected = False		


	def connected(self):

		"""Checks if the tracker is connected
		
		arguments
		None
		
		returns
		connected	-- True if connection is established, False if not;
				   sets self.connected to the same value
		"""

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
		
		if pos == None:
			pos = (int(self.dispsize[0] / 2), int(self.dispsize[1] / 2))
		if fix_triggered:
			return self.fix_triggered_drift_correction(pos)

		self.draw_drift_correction_target(pos[0], pos[1])

		pressed = False
		while not pressed:
			pressed, presstime = self.kb.get_key()
			if pressed:
				if pressed in ["Escape", "escape", "q"]:
					print("libalea.AleaTracker.drift_correction: 'q' or 'escape' pressed")
					return self.calibrate()
				gazepos = self.sample()
				if ((gazepos[0]-pos[0])**2  + (gazepos[1]-pos[1])**2)**0.5 < self.pxerrdist:
					return True
				else:
					self.errorbeep.play()
		return False
		
	def draw_drift_correction_target(self, x, y):
		
		"""
		Draws the drift-correction target.
		
		arguments
		
		x		--	The X coordinate
		y		--	The Y coordinate
		"""
		
		self.screen.clear()
		self.screen.draw_fixation(fixtype='dot', colour=settings.FGC, pos=(x,y),
			pw=0, diameter=12)
		self.disp.fill(self.screen)
		self.disp.show()			
		
	def draw_calibration_target(self, x, y):
		
		self.draw_drift_correction_target(x, y)

	def fix_triggered_drift_correction(self, pos=None, min_samples=4, max_dev=120, timeout=10000):

		"""Performs a fixation triggered drift correction by collecting
		a number of samples and calculating the average distance from the
		fixation position
		
		arguments
		None
		
		keyword arguments
		pos			-- (x, y) position of the fixation dot or None for
					   a central fixation (default = None)
		min_samples	-- minimal amount of samples after which a
					   fixation is accepted (default = 4)
		max_dev		-- maximal deviation from fixation in pixels
					   (default = 120)
		timeout		-- Time in milliseconds until fixation-triggering is
					   given up on, and calibration is started 
					   (default = 10000)
		
		returns
		checked		-- Boolean indicating if drift check is ok (True)
					   or not (False); or calls self.calibrate if 'q'
					   or 'escape' is pressed
		"""

		if pos == None:
			pos = (int(self.dispsize[0] / 2), int(self.dispsize[1] / 2))

		self.draw_drift_correction_target(pos[0], pos[1])
		
		t0 = clock.get_time()
		consecutive_count = 0
		while consecutive_count < min_samples:

			# Get new sample.
			x, y = self.sample()

			# Ignore empty samples.
			if (x is None) or (y is None):
				continue

			# Measure the distance to the target position.
			d = ((x-pos[0])**2 + (y-pos[1])**2)**0.5
			# Check whether the distance is below the allowed distance.
			if d <= max_dev:
				# Increment count.
				consecutive_count += 1
			else:
				# Reset count.
				consecutive_count = 0
			
			# Check for a timeout.
			if clock.get_time() - t0 > timeout:
				print("libalea.AleaTracker.fix_triggered_drift_correction: timeout during fixation-triggered drift check")
				return self.calibrate()

			# Pressing escape enters the calibration screen.
			if self.kb.get_key()[0] in ["Escape", "escape", "q"]:
				print("libalea.AleaTracker.fix_triggered_drift_correction: 'q' or 'escape' pressed")
				return self.calibrate()
		
		return True


	def get_eyetracker_clock_async(self):

		"""Not supported for AleaTracker (yet)"""

		print("get_eyetracker_clock_async function not supported for AleaTracker")


	def log(self, msg):

		"""Writes a message to the log file
		
		arguments
		ms		-- a string to include in the log file
		
		returns
		Nothing	-- uses native log function of iViewX to include a line
				   in the log file
		"""
		
		self.alea.log(msg)

	def prepare_drift_correction(self, pos):

		"""Not supported for AleaTracker"""

		print("prepare_drift_correction function not supported for AleaTracker")


	def pupil_size(self):

		"""Return pupil size
		
		arguments
		None
		
		returns
		pupil size	-- returns pupil diameter for the eye that is currently
				   being tracked (as specified by self.eye_used) or -1
				   when no data is obtainable
		"""
		
		# Get the latest sample.
		t, x, y, ps = self.alea.sample()
		
		# Invalid data.
		if ps == 0:
			return -1
		
		# Check if the new pupil size is the same as the previous.
		if ps != self.prevps:
			# Update the pupil size.
			self.prevps = copy.copy(ps)
		
		return self.prevps


	def sample(self):

		"""Returns newest available gaze position
		
		arguments
		None
		
		returns
		sample	-- an (x,y) tuple or a (-1,-1) on an error
		"""

		# Get the latest sample.
		t, x, y, ps = self.alea.sample()
		
		# Invalid data.
		if (x == 0) and (y == 0):
			return (-1,-1)
		
		# Combine the x and y coordinates.
		s = (int(x), int(y))
		# Check if the new sample is the same as the previous.
		if s != self.prevsample:
			# Update the current sample.
			self.prevsample = copy.copy(s)
		
		return self.prevsample


	def send_command(self, cmd):

		"""Function not supported.
		"""

		print("send_command function not supported for AleaTracker")


	def start_recording(self):

		"""Starts recording eye position
		
		arguments
		None
		
		returns
		Nothing	-- sets self.recording to True when recording is
				   successfully started
		"""

		self.alea.start_recording()
		self.recording = True


	def status_msg(self, msg):

		"""Not supported for AleaTracker"""

		print("status_msg function not supported for AleaTracker")


	def stop_recording(self):

		"""Stop recording eye position
		
		arguments
		None
		
		returns
		Nothing	-- sets self.recording to False when recording is
				   successfully started
		"""

		self.alea.stop_recording()
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
			raise Exception("Error in libalea.AleaTracker.wait_for_event: eventcode %s is not supported" % event)

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
		# Native method

		if self.eventdetection == 'native':
			
			print("WARNING! 'native' event detection not implemented")

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
		# Native method

		if self.eventdetection == 'native':
			
			print("WARNING! 'native' event detection not implemented")

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
					# check if time has surpassed BLINKTHRESH
					if clock.get_time()-t0 >= self.blinkthresh:
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
		# Native method

		if self.eventdetection == 'native':
			
			print("WARNING! 'native' event detection not implemented")

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
		# Native method

		if self.eventdetection == 'native':
			
			print("WARNING! 'native' event detection not implemented")

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
		# Native method

		if self.eventdetection == 'native':
			
			print("WARNING! 'native' event detection not implemented")

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
		# Native method

		if self.eventdetection == 'native':
			
			print("WARNING! 'native' event detection not implemented")

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
		
		"""Checks if the sample provided is valid (for internal use)
		
		arguments
		gazepos		--	a (x,y) gaze position tuple, as returned by
						self.sample()
		
		returns
		valid		--	a Boolean: True on a valid sample, False on
						an invalid sample
		"""
		
		# return False if a sample is invalid
		if gazepos == (None,None) or gazepos == (-1,-1) or gazepos == (0,0):
			return False
		
		# in any other case, the sample is valid
		return True


## This file is part of PyGaze - the open-source toolbox for eye tracking
##
## PyGaze is a Python module for easily creating gaze contingent experiments
## or other software (as well as non-gaze contingent experiments/software)
## Copyright (C) 2012-2013 Edwin S. Dalmaijer
##
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program. If not, see <http://www.gnu.org/licenses/>
#
# version: 0.4 (25-03-2013)

# TobiiTracker
import math
import numpy

from defaults import *
try:
	from constants import *
except:
	pass

import libtime
import libscreen
from libinput import Keyboard
from libsound import Sound


## letobii 
#from letobii import TobiiController
#

# TobiiController
from tobii.eye_tracking_io.basic import EyetrackerException

import os
import datetime

import tobii.eye_tracking_io.mainloop
import tobii.eye_tracking_io.browsing
import tobii.eye_tracking_io.eyetracker
import tobii.eye_tracking_io.time.clock
import tobii.eye_tracking_io.time.sync

from tobii.eye_tracking_io.types import Point2D, Blob

import psychopy.visual
import psychopy.event

import Image
import ImageDraw


# # # # #
# functions

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


# # # # #
# classes

class TobiiTracker:
	
	"""A class for Tobii EyeTracker objects"""
	
	def __init__(self, display, logfile=LOGFILE):
		
		"""Initializes a TobiiTracker instance
		
		arguments
		display	--	a libscreen.Display instance
		
		keyword arguments
		None
		"""
		
		# event detection properties
		self.errdist = 2 # degrees
		self.fixtresh = 1.5 # degrees
		self.spdtresh = 35 # degrees per second; saccade speed threshold
		self.accthresh = 9500 # degrees per second**2; saccade acceleration threshold
		self.weightdist = 10 # weighted distance, used for determining whether a movement is due to measurement error (1 is ok, higher is more conservative and will result in only larger saccades to be detected)
		self.dispsize = DISPSIZE # display size in pixels
		self.screensize = SCREENSIZE # display size in cm
		self.pixpercm = (self.dispsize[0]/float(self.screensize[0]) + self.dispsize[1]/float(self.screensize)) / 2.0
		self.prevsample = (-1,-1)
		
		# validation properties
		self.nvalsamples = 500 # samples for one validation point

		# basic properties
		self.connected = False
		self.recording = False
		self.eye_used = 0 # 0=left, 1=right, 2=binocular
		self.left_eye = 0
		self.right_eye = 1
		self.binocular = 2
		
		# objects
		self.disp = display
		self.screen = libscreen.Screen()
		self.kb = Keyboard(keylist=['space', 'escape', 'q'], timeout=1)
		self.errorbeep = Sound(osc='saw',freq=100, length=100)
		
		# initialize controller
		self.controller = TobiiController(display.expdisplay)
		self.controller.setDataFile("%s_TOBII_output.tsv" % logfile)

		# initiation report
		self.log("pygaze initiation report start")
		self.log("display resolution: %sx%s" % (self.dispsize[0],self.dispsize[1]))
		self.log("display size in cm: %sx%s" % (self.screensize[0],self.screensize[1]))
		self.log("samplerate: %s Hz" % self.samplerate)
		self.log("sampletime: %s ms" % self.sampletime)
		self.log("fixation threshold: %s degrees" % self.fixtresh)
		self.log("speed threshold: %s degrees/second" % self.spdtresh)
		self.log("accuracy threshold: %s degrees/second**2" % self.accthresh)
		self.log("pygaze initiation report end")


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
		
		# calibration and validation points
		calpos = [(0.1,0.1), (0.9,0.1) , (0.5,0.5), (0.1,0.9), (0.9,0.9)]


		# # # # #
		# calibration
		
		while True:
			
			ret = controller.doCalibration(calpos)
			
			if ret == 'accept':
				calibrated =  True
				break
				
			elif ret == 'abort':
				calibrated =  False
				return calibrated


		# # # # #
		# validation
		
		# start recording
		self.start_recording()
		
		# arrays for data storage
		lxacc = numpy.zeros(len(calpos))
		lyacc = numpy.zeros(len(calpos))
		rxacc = numpy.zeros(len(calpos))
		ryacc = numpy.zeros(len(calpos))
		
		# loop through all calibration positions
		for pos in calpos:
			# show validation point
			self.screen.draw_fixation(fixtype='dot', pos=pos)
			self.disp.fill(self.screen)
			self.disp.show()
			self.screen.clear()
			# collect samples
			lxsamples = numpy.zeros(self.nvalsamples)
			lysamples = numpy.zeros(self.nvalsamples)
			rxsamples = numpy.zeros(self.nvalsamples)
			rysamples = numpy.zeros(self.nvalsamples)
			prevsample = ()
			for i in range(0,self.nvalsamples):
				# add new sample to list
				newsample = self.controller.getCurrentGazePosition()
				if newsample != prevsample and newsample != (None,None,None,None):
					lx, ly, rx, ry = newsample
					lxsamples[i] = lx
					lysamples[i] = ly
					rxsamples[i] = rx
					rysamples[i] = ry
					prevsample = newsample[:]
			# calculate mean deviation
			lxdev = numpy.mean(abs(lxsamples-pos[0]))
			lydev = numpy.mean(abs(lysamples-pos[1]))
			rxdev = numpy.mean(abs(rxsamples-pos[0]))
			rydev = numpy.mean(abs(rysamples-pos[1]))
			lxacc.append(lxdev)
			lyacc.append(lydev)
			rxacc.append(rxdev)
			ryacc.append(rydev)

		# calculate mean accuracy
		self.pxaccuracy = [(numpy.mean(lxacc), numpy.mean(lyacc)), (numpy.mean(rxacc), numpy.mean(ryacc))]
		

		# # # # #
		# RMS noise
		
		# present instructions
		self.screen.draw_text(text="Noise calibration: please look at the dot\n\n(press space to start)", pos=(self.dispsize[0]/2, int(self.dispsize[1]*0.2)), center=True)
		self.screen.draw_fixation(fixtype='dot')
		self.disp.fill(self.screen)
		self.disp.show()
		self.screen.clear()

		# wait for spacepress
		self.kb.get_key(keylist=['space'], timeout=None)

		# show fixation
		self.screen.draw_fixation(fixtype='dot')
		self.disp.fill(self.screen)
		self.disp.show()
		self.screen.clear()
		
		# wait for a bit, to allow participant to fixate
		libtime.pause(500)

		# get samples
		sl = [self.sample()] # samplelist, prefilled with 1 sample to prevent sl[-1] from producing an error; first sample will be ignored for RMS calculation
		t0 = libtime.get_time() # starting time
		while libtime.get_time() - t0 < 1000:
			s = self.sample() # sample
			if s != sl[-1] and s != (-1,-1) and s != (0,0):
				sl.append(s)

		# calculate RMS noise
		Xvar = []
		Yvar = []
		for i in range(2,len(sl)):
			Xvar.append((sl[i][0]-sl[i-1][0])**2)
			Yvar.append((sl[i][1]-sl[i-1][1])**2)
		XRMS = (sum(Xvar) / len(Xvar))**0.5
		YRMS = (sum(Yvar) / len(Yvar))**0.5
		self.pxdsttresh = (XRMS, YRMS)
		
		
		# # # # #
		# sample rate
		
		# calculate intersample times
		t0 = self.controller.gazeData[0].Timestamp
		ist = numpy.zeros(len(self.controller.gazeData)-1)
		for i in range(0,len(self.controller.gazeData)-1):
			ist[i] = (self.controller.gazeData[i+1] - self.controller.gazeData[i]) / 1000.0
		
		# mean intersample time
		self.sampletime = numpy.mean(ist)
		self.samplerate = int(1000.0 / self.sampletime)
		
		# stop recording WITHOUT saving gaze data
		self.controller.eyetracker.StopTracking()
		self.controller.eyetracker.events.OnGazeDataReceived -= self.controller.on_gazedata
		self.controller.gazeData = []
		self.controller.eventData = []


		# # # # #
		# calibration report

		# recalculate thresholds (degrees to pixels)
		self.pxfixtresh = deg2pix(screendist, self.fixtresh, self.pixpercm)
		self.pxspdtresh = deg2pix(screendist, self.spdtresh/float(self.samplerate), self.pixpercm) # in pixels per sample
		self.pxacctresh = deg2pix(screendist, self.accthresh/float(self.samplerate**2), self.pixpercm) # in pixels per sample**2
		
		# write report to log
		self.log("pygaze calibration report start")
		self.log("accuracy (in pixels): LX=%s, LY=%s, RX=%s, RY=%s" % (self.pxaccuracy[0][0],self.pxaccuracy[0][1],self.pxaccuracy[1][0],self.pxaccuracy[1][1]))
		self.log("precision (RMS noise in pixels): X=%s, Y=%s" % (self.pxdsttresh[0],self.pxdsttresh[1]))
		self.log("distance between participant and display: %s cm" % SCREENDIST)
		self.log("fixation threshold: %s pixels" % self.pxfixtresh)
		self.log("speed threshold: %s pixels/sample" % self.pxspdtresh)
		self.log("accuracy threshold: %s pixels/sample**2" % self.pxacctresh)
		self.log("pygaze calibration report end")

		return True


	def close(self):
		
		"""Neatly close connection to tracker
		
		arguments
		None

		returns
		None		--	saves data and sets self.connected to False
		"""

		# stop tracking
		if self.recording:
			self.stop_recording()

		# save data
		controller.closeDataFile()
		
		# close connection
		controller.destroy()
		self.connected = False
	
	
	def connected(self):
		
		"""Checks if the tracker is connected
		
		arguments
		None

		returns
		connected	--	True if connection is established, False if not
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

		if fix_triggered:
			return self.fix_triggered_drift_correction(pos)

		if pos == None:
			pos = self.dispsize[0] / 2, self.dispsize[1] / 2

		pressed = False
		while not pressed:
			pressed, presstime = self.kb.get_key()
			if pressed:
				if pressed == 'escape' or pressed == 'q':
					print("libsmi.SMItracker.drift_correction: 'q' or 'escape' pressed")
					return self.calibrate(calibrate=True, validate=True)
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

		if pos == None:
			pos = self.dispsize[0] / 2, self.dispsize[1] / 2

		# loop until we have sufficient samples
		lx = []
		ly = []
		while len(lx) < min_samples:

			# pressing escape enters the calibration screen
			if self.kb.get_key()[0] in ['escape','q']:
				print("libsmi.SMItracker.fix_triggered_drift_correction: 'q' or 'escape' pressed")
				return self.calibrate(calibrate=True, validate=True)

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

	
	def get_eyetracker_clock_async(self):

		"""Retrieve difference between tracker time and experiment time
		
		arguments
		None
		
		keyword arguments
		None
		
		returns
		timediff	--	tracker time minus experiment time
		"""
		
		return self.controller.syncmanager.convert_from_local_to_remote(self.controller.clock.get_time()) - libtime.get_time()
	
	
	def log(self, msg):

		"""Writes a message to the log file
		
		arguments
		ms		-- a string to include in the log file
		
		returns
		Nothing	-- uses native log function of iViewX to include a line
				   in the log file
		"""
		
		controller.recordEvent(msg)
	
	
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
	
	
	def prepare_backdrop(self):

		"""Not supported for TobiiTracker (yet)"""
		
		print("function not supported yet")
	

	def prepare_drift_correction(self, pos):

		"""Not supported for TobiiTracker (yet)"""
		
		print("function not supported yet")
	
	
	def pupil_size(self):

		"""Not supported for TobiiTracker (yet)"""
		
		print("function not supported yet")
	
	
	def sample(self):

		"""Returns newest available gaze position
		
		arguments
		None
		
		returns
		sample	-- an (x,y) tuple or a (-1,-1) on an error
		"""

		# get new sample		
		gazepos = controller.getCurrentGazePosition()
		
		# if sample is invalid, return missing value
		if None in gazepos:
			return (-1,-1)
		
		# return gaze x,y
		if self.eye_used == self.left_eye or self.eye_used == self.binocular:
			return gazepos[0], gazepos[1]
		else:
			return gazepos[2], gazepos[3]
	
	
	def send_command(self, cmd):

		"""Not supported for TobiiTracker (yet)"""
		
		print("function not supported yet")
	
	
	def set_backdrop(self):

		"""Not supported for TobiiTracker (yet)"""
		
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

		if self.eye_used == self.right_eye:
			self.log_var("eye_used", "right")

		else:
			self.log_var("eye_used", "left")
	
	
	def start_recording(self):

		"""Starts recording eye position
		
		arguments
		None
		
		returns
		None		-- sets self.recording to True when recording is
				   successfully started
		"""

		try:
			self.controller.startTracking()
			self.recording = True
		except:
			print("Error in libsmi.TobiiTracker.start_recording: failed to start recording")
			self.recording = False
	
	
	def status_msg(self, msg):

		"""Not supported for TobiiTracker (yet)"""
		
		print("function not supported yet")
	

	def stop_recording(self):

		"""Stop recording eye position
		
		arguments
		None
		
		returns
		Nothing	-- sets self.recording to False when recording is
				   successfully started
		"""

		try:
			self.controller.stopTracking()
			self.recording = False
		except:
			print("Error in libsmi.TobiiTracker.stop_recording: failed to stop recording")
			self.recording = True
	
	
	def wait_for_blink_end(self):

		"""Not supported for TobiiTracker (yet)"""
		
		print("function not supported yet")
	
	
	def wait_for_blink_start(self):

		"""Not supported for TobiiTracker (yet)"""
		
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

	
	def wait_for_fixation_end(self):

		"""Returns time and gaze position when a fixation is ended;
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

		# function assumes that a 'fixation' has ended when a deviation of more than maxerr
		# from the initial 'fixation' position has been detected (using Pythagoras, ofcourse)

		stime, spos = self.wait_for_fixation_start()
		
		while True:
			npos = self.sample() # get newest sample
			if npos != (0,0):
				if ((spos[0]-npos[0])**2  + (spos[1]-npos[1])**2)**0.5 > self.pxfixtresh: # Pythagoras
					break

		return libtime.get_time(), spos


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

		# function assumes a 'fixation' has started when gaze position remains reasonably
		# stable for five samples in a row
		
		# wait for reasonably stable position
		xl = [] # list for last five samples (x coordinate)
		yl = [] # list for last five samples (y coordinate)
		moving = True
		while moving:
			npos = self.sample()
			if npos != (0,0):
				xl.append(npos[0]) # add newest sample
				yl.append(npos[1]) # add newest sample
				if len(xl) == 5:
					# check if deviation is small enough
					if ((max(xl)-min(xl))**2 + (max(yl)-min(yl))**2)**0.5 < self.pxfixtresh:
						moving = False
					# remove oldest sample
					xl.pop(0); yl.pop(0)

		return libtime.get_time(), (xl[-1],yl[-1])


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

		# NOTE: v in px/sample = s
		# NOTE: a in px/sample**2 = v1 - v0

		# METHOD 2
		# get starting position (no blinks)
		stime, spos = self.wait_for_saccade_start()
		prevpos = self.sample()
		s0 = ((prevpos[0]-spos[0])**2 + (prevpos[1]-spos[1])**2)**0.5 # = intersample distance = speed in px/sample

		# get samples
		saccadic = True
		while saccadic:
			# get new sample
			newpos = self.sample()
			if sum(newpos) > 0 and newpos != prevpos:
				# calculate distance
				s1 = ((newpos[0]-prevpos[0])**2 + (newpos[1]-prevpos[1])**2)**0.5 # = speed in pixels/sample
				# calculate acceleration
				a = s1-s0 # acceleration in pixels/sample**2 (actually is v1-v0 / t1-t0; but t1-t0 = 1 sample)
				if s1 < self.pxspdtresh and (a > -1*self.pxacctresh and a < 0):
					saccadic = False
					epos = newpos[:]
					etime = libtime.get_time()
				s0 = copy.copy(s1)
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

		# get starting position (no blinks)
		newpos = self.sample()
		while sum(newpos) == 0:
			newpos = self.sample()
		prevpos = newpos[:]
		s0 = 0

		# get samples
		saccadic = False
		while not saccadic:
			# get new sample
			newpos = self.sample()
			if sum(newpos) > 0 and newpos != prevpos:
				# check if distance is larger than accuracy error
				sx = newpos[0]-prevpos[0]; sy = newpos[1]-prevpos[1]
				if (sx/self.pxdsttresh[0])**2 + (sy/self.pxdsttresh[1])**2 > self.weightdist: # weigthed distance: (sx/tx)**2 + (sy/ty)**2 > 1 means movement larger than RMS noise
					# calculate distance
					s1 = ((sx)**2 + (sy)**2)**0.5 # intersampledistance = speed in pixels/sample
					# calculate acceleration
					a = s1-s0 # acceleration in pixels/sample**2 (actually is v1-v0 / t1-t0; but t1-t0 = 1 sample)
					if s1 > self.pxspdtresh or a > self.pxacctresh:
						saccadic = True
						spos = prevpos[:]
						stime = libtime.get_time()
					s0 = copy.copy(s1)

				# udate previous sample
				prevpos = newpos[:]

		return stime, spos


# The code below is based on Hiroyuki Sogo's (Ehime University)
# TobiiController for PsychoPy. The code has been modified by Edwin Dalmaijer
# to work in with PyGaze display routines.
#
# more information: http://www.s12600.net/psy/etc/python.html#TobiiController
# original code: http://www.s12600.net/psy/etc/TobiiController/TobiiControllerP.py


class TobiiController:
    def __init__(self, win):
        self.eyetracker = None
        self.eyetrackers = {}
        self.win = win
        self.gazeData = []
        self.eventData = []
        self.datafile = None
        
        tobii.eye_tracking_io.init()
        self.clock = tobii.eye_tracking_io.time.clock.Clock()
        self.mainloop_thread = tobii.eye_tracking_io.mainloop.MainloopThread()
        self.browser = tobii.eye_tracking_io.browsing.EyetrackerBrowser(self.mainloop_thread, lambda t, n, i: self.on_eyetracker_browser_event(t, n, i))
        self.mainloop_thread.start()
        
    def waitForFindEyeTracker(self):
        while len(self.eyetrackers.keys())==0:
            pass
        
    def on_eyetracker_browser_event(self, event_type, event_name, eyetracker_info):
        # When a new eyetracker is found we add it to the treeview and to the 
        # internal list of eyetracker_info objects
        if event_type == tobii.eye_tracking_io.browsing.EyetrackerBrowser.FOUND:
            self.eyetrackers[eyetracker_info.product_id] = eyetracker_info
            return False
        
        # Otherwise we remove the tracker from the treeview and the eyetracker_info list...
        del self.eyetrackers[eyetracker_info.product_id]
        
        # ...and add it again if it is an update message
        if event_type == tobii.eye_tracking_io.browsing.EyetrackerBrowser.UPDATED:
            self.eyetrackers[eyetracker_info.product_id] = eyetracker_info
        return False
        
    def destroy(self):
        self.eyetracker = None
        self.browser.stop()
        self.browser = None
        self.mainloop_thread.stop()
        
    ############################################################################
    # activation methods
    ############################################################################
    def activate(self,eyetracker):
        eyetracker_info = self.eyetrackers[eyetracker]
        print "Connecting to:", eyetracker_info
        tobii.eye_tracking_io.eyetracker.Eyetracker.create_async(self.mainloop_thread,
                                                     eyetracker_info,
                                                     lambda error, eyetracker: self.on_eyetracker_created(error, eyetracker, eyetracker_info))
        
        while self.eyetracker==None:
            pass
        self.syncmanager = tobii.eye_tracking_io.time.sync.SyncManager(self.clock,eyetracker_info,self.mainloop_thread)
        
    def on_eyetracker_created(self, error, eyetracker, eyetracker_info):
        if error:
            print "  Connection to %s failed because of an exception: %s" % (eyetracker_info, error)
            if error == 0x20000402:
                print "The selected unit is too old, a unit which supports protocol version 1.0 is required.\n\n<b>Details:</b> <i>%s</i>" % error
            else:
                print "Could not connect to %s" % (eyetracker_info)
            return False
        
        self.eyetracker = eyetracker
        
    ############################################################################
    # calibration methods
    ############################################################################
    
    def doCalibration(self,calibrationPoints):
        if self.eyetracker is None:
            return
			        
        self.points = calibrationPoints
        self.point_index = -1
        
        img = Image.new('RGB',self.win.size)
        draw = ImageDraw.Draw(img)
        
        self.calin = psychopy.visual.Circle(self.win,radius=2,fillColor=(0.0,0.0,0.0))
        self.calout = psychopy.visual.Circle(self.win,radius=64,lineColor=(0.0,1.0,0.0))
        self.calresult = psychopy.visual.SimpleImageStim(self.win,img)
        self.calresultmsg = psychopy.visual.TextStim(self.win,pos=(0,-win.size[1]/4))
        
        self.initcalibration_completed = False
        print "StartCalibration"
        self.eyetracker.StartCalibration(lambda error, r: self.on_calib_start(error, r))
        while not self.initcalibration_completed:
            pass
			
        waitkey = True
        while waitkey:
            for key in psychopy.event.getKeys():
				if key=='space':
					waitkey = False				
            self.calout.draw()
            self.calin.draw()
            win.flip()
        
        clock = psychopy.core.Clock()
        for self.point_index in range(len(self.points)):
            p = Point2D()
            p.x, p.y = self.points[self.point_index]
            self.calin.setPos(((p.x-0.5)*self.win.size[0],(0.5-p.y)*self.win.size[1]))
            self.calout.setPos(((p.x-0.5)*self.win.size[0],(0.5-p.y)*self.win.size[1]))
            
            clock.reset()
            currentTime = clock.getTime()
            while currentTime < 1.5:
                self.calout.setRadius(40*(1.5-(currentTime))+4)
                psychopy.event.getKeys()
                self.calout.draw()
                self.calin.draw()
                win.flip()
                currentTime = clock.getTime()
            self.add_point_completed = False
            self.eyetracker.AddCalibrationPoint(p, lambda error, r: self.on_add_completed(error, r))
            while not self.add_point_completed:
                psychopy.event.getKeys()
                self.calout.draw()
                self.calin.draw()
                win.flip()
         
        self.computeCalibration_completed = False
        self.computeCalibration_succeeded = False
        self.eyetracker.ComputeCalibration(lambda error, r: self.on_calib_compute(error, r))
        while not self.computeCalibration_completed:
            pass
        self.eyetracker.StopCalibration(None)
        
        win.flip()
        
        self.getcalibration_completed = False
        self.calib = self.eyetracker.GetCalibration(lambda error, calib: self.on_calib_response(error, calib))
        while not self.getcalibration_completed:
            pass
        
        draw.rectangle(((0,0),tuple(self.win.size)),fill=(128,128,128))
        if not self.computeCalibration_succeeded:
            #computeCalibration failed.
            self.calresultmsg.setText('Not enough data was collected (Retry:r/Abort:ESC)')
            
        elif self.calib == None:
            #no calibration data
            self.calresultmsg.setText('No calibration data (Retry:r/Abort:ESC)')
        else:
            points = {}
            for data in self.calib.plot_data:
                points[data.true_point] = {'left':data.left, 'right':data.right}
            
            if len(points) == 0:
                self.calresultmsg.setText('No ture calibration data (Retry:r/Abort:ESC)')
            
            else:
                for p,d in points.iteritems():
                    if d['left'].status == 1:
                        draw.line(((p.x*self.win.size[0],p.y*self.win.size[1]),
                                   (d['left'].map_point.x*self.win.size[0],
                                    d['left'].map_point.y*self.win.size[1])),fill=(255,0,0))
                    if d['right'].status == 1:
                        draw.line(((p.x*self.win.size[0],p.y*self.win.size[1]),
                                   (d['right'].map_point.x*self.win.size[0],
                                    d['right'].map_point.y*self.win.size[1])),fill=(0,255,0))
                    draw.ellipse(((p.x*self.win.size[0]-10,p.y*self.win.size[1]-10),
                                  (p.x*self.win.size[0]+10,p.y*self.win.size[1]+10)),
                                 outline=(0,0,0))
                self.calresultmsg.setText('Accept calibration results (Accept:a/Retry:r/Abort:ESC)')
                
        self.calresult.setImage(img)
        
        waitkey = True
        while waitkey:
            for key in psychopy.event.getKeys():
                if key == 'a':
                    retval = 'accept'
                    waitkey = False
                elif key == 'r':
                    retval = 'retry'
                    waitkey = False
                elif key == 'escape':
                    retval = 'abort'
                    waitkey = False
            self.calresult.draw()
            self.calresultmsg.draw()
            self.win.flip()
        
        return retval

    
    def on_calib_start(self, error, r):
        if error:
            print "Could not start calibration because of error. (0x%0x)" % error
            return False
        self.initcalibration_completed = True
    
    def on_add_completed(self, error, r):
        if error:
            print "Add Calibration Point failed because of error. (0x%0x)" % error
            return False
        
        self.add_point_completed = True
        return False
    
    def on_calib_compute(self, error, r):
        if error == 0x20000502:
            print "CalibCompute failed because not enough data was collected:", error
            print "Not enough data was collected during calibration procedure."
            self.computeCalibration_succeeded = False
        elif error != 0:
            print "CalibCompute failed because of a server error:", error
            print "Could not compute calibration because of a server error.\n\n<b>Details:</b>\n<i>%s</i>" % (error)
            self.computeCalibration_succeeded = False
        else:
            print ""
            self.computeCalibration_succeeded = True
        
        self.computeCalibration_completed = True
        return False
    
    def on_calib_response(self, error, calib):
        if error:
            print "On_calib_response: Error =", error
            self.calib = None
            self.getcalibration_completed = True
            return False
        
        print "On_calib_response: Success"
        self.calib = calib
        self.getcalibration_completed = True
        return False    
    
    
    def on_calib_done(self, status, msg):
        # When the calibration procedure is done we update the calibration plot
        if not status:
            print msg
            
        self.calibration = None
        return False
    
    def startTracking(self):
        self.gazeData = []
        self.eventData = []
        self.eyetracker.events.OnGazeDataReceived += self.on_gazedata
        self.eyetracker.StartTracking()
    
    def stopTracking(self):
        self.eyetracker.StopTracking()
        self.eyetracker.events.OnGazeDataReceived -= self.on_gazedata
        self.flushData()
        self.gazeData = []
        self.eventData = []
    
    def on_gazedata(self,error,gaze):
        self.gazeData.append(gaze)
    
    def getGazePosition(self,gaze):
        return ((gaze.LeftGazePoint2D.x-0.5)*self.win.size[0],
                (0.5-gaze.LeftGazePoint2D.y)*self.win.size[1],
                (gaze.RightGazePoint2D.x-0.5)*self.win.size[0],
                (0.5-gaze.RightGazePoint2D.y)*self.win.size[1])
    
    def getCurrentGazePosition(self):
        if len(self.gazeData)==0:
            return (None,None,None,None)
        else:
            return self.getGazePosition(self.gazeData[-1])
    
    def setDataFile(self,filename):
        print 'set datafile ' + filename
        self.datafile = open(filename,'w')
        self.datafile.write('Recording date:\t'+datetime.datetime.now().strftime('%Y/%m/%d')+'\n')
        self.datafile.write('Recording time:\t'+datetime.datetime.now().strftime('%H:%M:%S')+'\n')
        self.datafile.write('Recording resolution\t%d x %d\n\n' % tuple(self.win.size))
        
    def closeDataFile(self):
        print 'datafile closed'
        if self.datafile != None:
            self.flushData()
            self.datafile.close()
        
        self.datafile = None
    
    def recordEvent(self,event):
        t = self.syncmanager.convert_from_local_to_remote(self.clock.get_time())
        self.eventData.append((t,event))
    
    def flushData(self):
        if self.datafile == None:
            print 'data file is not set.'
            return
        
        if len(self.gazeData)==0:
            return
        
        self.datafile.write('\t'.join(['TimeStamp',
                                       'GazePointXLeft',
                                       'GazePointYLeft',
                                       'ValidityLeft',
                                       'GazePointXRight',
                                       'GazePointYRight',
                                       'ValidityRight',
                                       'GazePointX',
                                       'GazePointY',
                                       'Event'])+'\n')
        timeStampStart = self.gazeData[0].Timestamp
        for g in self.gazeData:
            self.datafile.write('%.1f\t%.4f\t%.4f\t%d\t%.4f\t%.4f\t%d'%(
                                (g.Timestamp-timeStampStart)/1000.0,
                                g.LeftGazePoint2D.x*self.win.size[0] if g.LeftValidity!=4 else -1.0,
                                g.LeftGazePoint2D.y*self.win.size[1] if g.LeftValidity!=4 else -1.0,
                                g.LeftValidity,
                                g.RightGazePoint2D.x*self.win.size[0] if g.RightValidity!=4 else -1.0,
                                g.RightGazePoint2D.y*self.win.size[1] if g.RightValidity!=4 else -1.0,
                                g.RightValidity))
            if g.LeftValidity == 4 and g.RightValidity == 4: #not detected
                ave = (-1.0,-1.0)
            elif g.LeftValidity == 4:
                ave = (g.RightGazePoint2D.x,g.RightGazePoint2D.y)
            elif g.RightValidity == 4:
                ave = (g.LeftGazePoint2D.x,g.LeftGazePoint2D.y)
            else:
                ave = (g.LeftGazePoint2D.x+g.RightGazePoint2D.x,
                       g.LeftGazePoint2D.y+g.RightGazePoint2D.y)
                
            self.datafile.write('\t%.4f\t%.4f\t'%ave)
            self.datafile.write('\n')
        
        formatstr = '%.1f'+'\t'*9+'%s\n'
        for e in self.eventData:
            self.datafile.write(formatstr % ((e[0]-timeStampStart)/1000.0,e[1]))
        
        self.datafile.flush()
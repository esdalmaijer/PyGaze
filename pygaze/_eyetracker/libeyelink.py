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


from pygaze.defaults import *
try:
	from constants import *
except:
	pass
	
from pygaze import libtime
import libscreen
from libinput import Mouse
from libinput import Keyboard
from libsound import Sound

if not DUMMYMODE:
	import pylink
	import Image
	custom_display = pylink.EyeLinkCustomDisplay
else:
	custom_display = object

if DISPTYPE == 'psychopy':
	try:
		import psychopy.visual
	except:
		raise Exception("Error in libeyelink: PsychoPy could not be loaded!")

if DISPTYPE == 'pygame':
	try:
		import pygame
	except:
		raise Exception("Error in libeyelink: PyGame could not be loaded!")

import copy
import math
import os.path
import array
from PIL import Image

_eyelink = None


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


class libeyelink:

	MAX_TRY = 100

	def __init__(self, display, resolution=DISPSIZE, data_file=LOGFILE+".edf", fg_color=FGC, bg_color=BGC, eventdetection=EVENTDETECTION, saccade_velocity_threshold=35, saccade_acceleration_threshold=9500):

		""""Initializes the connection to the Eyelink"""

		global _eyelink

		stem, ext = os.path.splitext(data_file)
		if len(stem) > 8 or len(ext) > 4:
			data_file = "default.edf"
			print("WARNING! The Eyelink cannot handle filenames longer than 8 characters (excluding '.EDF' extension). Filename set to 'default.EDF'.")

		# properties
		self.data_file = data_file
		self.screen = display
		self.scr = libscreen.Screen(mousevisible=False)
		self.kb = Keyboard(keylist=["escape", "q"], timeout=1)
		self.resolution = resolution
		self.recording = False
		self.saccade_velocity_treshold = saccade_velocity_threshold
		self.saccade_acceleration_treshold = saccade_acceleration_threshold
		self.eye_used = None
		self.left_eye = 0
		self.right_eye = 1
		self.binocular = 2
		self.prevsample = (-1,-1)
		self.prevps = -1

		# event detection properties
		self.fixtresh = 1.5 # degrees; maximal distance from fixation start (if gaze wanders beyond this, fixation has stopped)
		self.fixtimetresh = 100 # milliseconds; amount of time gaze has to linger within self.fixtresh to be marked as a fixation
		self.spdtresh = self.saccade_velocity_treshold # degrees per second; saccade velocity threshold
		self.accthresh = self.saccade_acceleration_treshold # degrees per second**2; saccade acceleration threshold
		self.eventdetection = eventdetection
		self.set_detection_type(self.eventdetection)
		self.weightdist = 10 # weighted distance, used for determining whether a movement is due to measurement error (1 is ok, higher is more conservative and will result in only larger saccades to be detected)
		self.screendist = SCREENDIST # distance between participant and screen in cm
		self.screensize = SCREENSIZE # distance between participant and screen in cm
		self.pixpercm = (self.resolution[0]/float(self.screensize[0]) + self.resolution[1]/float(self.screensize[1])) / 2.0


		# only initialize eyelink once
		if _eyelink == None:
			try:
				_eyelink = pylink.EyeLink()
			except:
				raise Exception("Error in libeyelink.libeyelink.__init__(): Failed to connect to the tracker!")

			graphics_env = eyelink_graphics(self.screen, _eyelink)
			pylink.openGraphicsEx(graphics_env)

		pylink.getEYELINK().openDataFile(self.data_file)
		pylink.flushGetkeyQueue()
		pylink.getEYELINK().setOfflineMode()

		# notify eyelink of display resolution
		self.send_command("screen_pixel_coords = 0 0 %d %d" % (self.resolution[0], self.resolution[1]))

		# determine software version of tracker
		self.tracker_software_ver = 0
		self.eyelink_ver = pylink.getEYELINK().getTrackerVersion()
		if self.eyelink_ver == 3:
			tvstr = pylink.getEYELINK().getTrackerVersionString()
			vindex = tvstr.find("EYELINK CL")
			self.tracker_software_ver = int(float(tvstr[(vindex + len("EYELINK CL")):].strip()))

		# get some configuration stuff
		if self.eyelink_ver >= 2:
			self.send_command("select_parser_configuration 0")
			if self.eyelink_ver == 2: # turn off scenelink camera stuff
				self.send_command("scene_camera_gazemap = NO")
		else:
			self.send_command("saccade_velocity_threshold = %d" % self.saccade_velocity_threshold)
			self.send_command("saccade_acceleration_threshold = %s" % self.saccade_acceleration_threshold)

		# set EDF file contents (this specifies which data is written to the EDF file)
		self.send_command("file_event_filter = LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON")
		if self.tracker_software_ver >= 4:
			self.send_command("file_sample_data  = LEFT,RIGHT,GAZE,AREA,GAZERES,STATUS,HTARGET")
		else:
			self.send_command("file_sample_data  = LEFT,RIGHT,GAZE,AREA,GAZERES,STATUS")

		# set link data (this specifies which data is sent through the link and thus can be used in gaze contingent displays)
		self.send_command("link_event_filter = LEFT,RIGHT,FIXATION,SACCADE,BLINK,BUTTON")
		if self.tracker_software_ver >= 4:
			self.send_command("link_sample_data  = LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS,HTARGET")
		else:
			self.send_command("link_sample_data  = LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS")

		# not quite sure what this means (according to Sebastiaan Mathot, it might be the button that is used to end drift correction?)
		self.send_command("button_function 5 'accept_target_fixation'")

		if not self.connected():
			raise Exception("Error in libeyelink.libeyelink.__init__(): Failed to connect to the eyetracker!")


	def send_command(self, cmd):

		"""Sends a command to the eyelink"""

		pylink.getEYELINK().sendCommand(cmd)


	def log(self, msg):

		"""Writes a message to the eyelink data file"""

		pylink.getEYELINK().sendMessage(msg)


	def log_var(self, var, val):

		"""Writes a variable to the eyelink data file"""

		pylink.getEYELINK().sendMessage("var %s %s" % (var, val))


	def status_msg(self, msg):

		"""Sets the eyelink status message (which is displayed on the eyelink experimenter PC)"""

		pylink.getEYELINK().sendCommand("record_status_message '%s'" % msg)


	def connected(self):

		"""Returns the status of the eyelink connection"""

		return pylink.getEYELINK().isConnected()


	def calibrate(self):

		"""Starts eyelink calibration"""

		if self.recording:
			raise Exception("Error in libeyelink.libeyelink.calibrate(): Trying to calibrate after recording has started!")

		# # # # #
		# EyeLink calibration and validation
		
		pylink.getEYELINK().doTrackerSetup()
		
		
		# # # # #
		# RMS calibration
		
		# present instructions
		self.screen.fill() # clear display
		self.scr.draw_text(text="Noise calibration: please look at the dot\n\n(press space to start)", pos=(self.resolution[0]/2, int(self.resolution[1]*0.2)), center=True)
		self.scr.draw_fixation(fixtype='dot')
		self.screen.fill(self.scr)
		self.screen.show()
		self.scr.clear() # clear screen again

		# wait for spacepress
		self.kb.get_key(keylist=['space'], timeout=None)

		# start recording
		self.log("PYGAZE RMS CALIBRATION START")
		self.start_recording()

		# show fixation
		self.screen.fill()
		self.scr.draw_fixation(fixtype='dot')
		self.screen.fill(self.scr)
		self.screen.show()
		self.scr.clear()

		# wait for a bit, to allow participant to fixate
		libtime.pause(500)

		# get samples
		sl = [self.sample()] # samplelist, prefilled with 1 sample to prevent sl[-1] from producing an error; first sample will be ignored for RMS calculation
		t0 = libtime.get_time() # starting time
		while libtime.get_time() - t0 < 1000:
			s = self.sample() # sample
			if s != sl[-1] and s != (-1,-1) and s != (0,0):
				sl.append(s)

		# stop recording
		self.log("PYGAZE RMS CALIBRATION END")
		self.stop_recording()

		# calculate RMS noise
		Xvar = []
		Yvar = []
		for i in range(2,len(sl)):
			Xvar.append((sl[i][0]-sl[i-1][0])**2)
			Yvar.append((sl[i][1]-sl[i-1][1])**2)
		XRMS = (sum(Xvar) / len(Xvar))**0.5
		YRMS = (sum(Yvar) / len(Yvar))**0.5
		self.pxdsttresh = (XRMS, YRMS)

		# recalculate thresholds (degrees to pixels)
		self.pxfixtresh = deg2pix(self.screendist, self.fixtresh, self.pixpercm)
		self.pxspdtresh = deg2pix(self.screendist, self.spdtresh, self.pixpercm)/1000.0 # in pixels per millisecons
		self.pxacctresh = deg2pix(self.screendist, self.accthresh, self.pixpercm)/1000.0 # in pixels per millisecond**2


	def drift_correction(self, pos=None, fix_triggered=False):

		"""Performs drift correction and falls back to calibration screen if necessary"""

		if self.recording:
			raise Exception("Error in libeyelink.libeyelink.drift_correction(): Trying to perform drift correction after recording has started!")

		if fix_triggered:
			return self.fix_triggered_drift_correction(pos)

		if pos == None:
			pos = self.resolution[0] / 2, self.resolution[1] / 2

		# show fixation
		self.scr.draw_fixation(fixtype='dot', colour=FGC, pos=pos, pw=0, diameter=12)
		self.screen.fill(self.scr)
		self.screen.show()
		self.scr.clear()

		# perform drift check
		while True:
			if not self.connected():
				raise Exception("Error in libeyelink.libeyelink.drift_correction(): The eyelink is not connected!")
			try:
				# Params: x, y, draw fix, allow_setup
				error = pylink.getEYELINK().doDriftCorrect(pos[0], pos[1], 0, 1)
				if error != 27:
					print("libeyelink.libeyelink.drift_correction(): success")
					return True
				else:
					print("libeyelink.drift_correction(): escape pressed")
					return False
			except:
				print("libeyelink.drift_correction(): try again")
				return False


	def prepare_drift_correction(self, pos):

		"""Puts the tracker in drift correction mode"""

		# start collecting samples in drift correction mode
		self.send_command("heuristic_filter = ON")
		self.send_command("drift_correction_targets = %d %d" % pos)
		self.send_command("start_drift_correction data = 0 0 1 0")
		pylink.msecDelay(50);

		# wait for a bit until samples start coming in (again, not sure if this is indeed what's going on)
		if not pylink.getEYELINK().waitForBlockStart(100, 1, 0):
			print("WARNING libeyelink.libeyelink.prepare_drift_correction(): Failed to perform drift correction (waitForBlockStart error)")


	def fix_triggered_drift_correction(self, pos=None, min_samples=30, max_dev=60, reset_threshold=10):

		"""Performs fixation triggered drift correction and falls back to the calibration screen if necessary"""

		if self.recording:
			raise Exception("Error in libeyelink.libeyelink.fix_triggered_drift_correction(): Trying to perform drift correction after recording has started!")

		self.recording = True

		if pos == None:
			pos = self.resolution[0] / 2, self.resolution[1] / 2

		self.prepare_drift_correction(pos)

		# show fixation
		self.scr.draw_fixation(fixtype='dot', colour=FGC, pos=pos, pw=0, diameter=12)
		self.screen.fill(self.scr)
		self.screen.show()
		self.scr.clear()

		# loop until we have sufficient samples
		lx = []
		ly = []
		while len(lx) < min_samples:

			# pressing escape enters the calibration screen
			if self.kb.get_key(keylist=["escape", "q"], timeout=1)[0] != None:
				self.recording = False
				print("libeyelink.libeyelink.fix_triggered_drift_correction(): 'q' pressed")
				return False

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

				# emulate spacebar press on succes
				pylink.getEYELINK().sendKeybutton(32, 0, pylink.KB_PRESS)

				# getCalibrationResult() returns 0 on success and an exception or a non-zero value otherwise
				result = -1
				try:
					result = pylink.getEYELINK().getCalibrationResult()
				except:
					lx = []
					ly = []
					print("libeyelink.libeyelink.fix_triggered_drift_correction(): try again")
				if result != 0:
					
					try:
						result = pylink.getEYELINK().getCalibrationResult()
					except:
						lx = []
						ly = []
						print("libeyelink.libeyelink.fix_triggered_drift_correction(): try again")

		# apply drift correction
		pylink.getEYELINK().applyDriftCorrect()
		self.recording = False
		print("libeyelink.libeyelink.fix_triggered_drift_correction(): success")

		return True


	def start_recording(self):

		"""Starts recording of gaze samples"""

		self.recording = True

		i = 0
		while True:
			# params: write samples, write event, send samples, send events
			error = pylink.getEYELINK().startRecording(1, 1, 1, 1)
			
			if not error:
				break
			if i > self.MAX_TRY:
				raise Exception("Error in libeyelink.libeyelink.start_recording(): Failed to start recording!")
				self.close()
				libtime.expend()
			i += 1
			print("WARNING libeyelink.libeyelink.start_recording(): Failed to start recording (attempt %d of %d)" % (i, self.MAX_TRY))
			pylink.msecDelay(100)

		# don't know what this is
		pylink.pylink.beginRealTimeMode(100)

		# wait a bit until samples start coming in
		if not pylink.getEYELINK().waitForBlockStart(100, 1, 0):
			raise Exception("Error in libeyelink.libeyelink.start_recording(): Failed to start recording (waitForBlockStart error)!")


	def stop_recording(self):

		"""Stops recording of gaze samples"""

		self.recording = False

		pylink.endRealTimeMode()
		pylink.getEYELINK().setOfflineMode()
		pylink.msecDelay(500)


	def close(self):

		"""Close the connection with the eyelink"""

		if self.recording:
			self.stop_recording()

		# close data file and transfer it to the experimental PC
		print("libeyelink.libeyelink.close(): Closing data file")
		pylink.getEYELINK().closeDataFile()
		pylink.msecDelay(100)
		print("libeyelink.libeyelink.close(): Transferring data file")
		pylink.getEYELINK().receiveDataFile(self.data_file, self.data_file)
		pylink.msecDelay(100)
		print("libeyelink.libeyelink.close(): Closing eyelink")
		pylink.getEYELINK().close();
		pylink.msecDelay(100)


	def set_eye_used(self):

		"""Sets the eye_used variable, based on the eyelink's report (which specifies which eye is being tracked); if both eyes are being tracked, the left eye is used"""

		self.eye_used = pylink.getEYELINK().eyeAvailable()
		if self.eye_used == self.right_eye:
			self.log_var("eye_used", "right")
		elif self.eye_used == self.left_eye or self.eye_used == self.binocular:
			self.log_var("eye_used", "left")
			self.eye_used = self.left_eye
		else:
			print("WARNING libeyelink.libeyelink.set_eye_used(): Failed to determine which eye is being recorded")
	
	
	def pupil_size(self):

		"""Return pupil size
		
		arguments
		None
		
		returns
		pupil size	-- returns pupil diameter for the eye that is currently
				   being tracked (as specified by self.eye_used) or -1
				   when no data is obtainable
		"""

		if not self.recording:
			raise Exception("Error in libeyelink.libeyelink.pupil_size(): Recording was not started before collecting eyelink data!")

		if self.eye_used == None:
			self.set_eye_used()
		
		# get newest sample
		s = pylink.getEYELINK().getNewestSample()
		
		# check if sample is new
		if s != None:
			# right eye
			if self.eye_used == self.right_eye and s.isRightSample():
				ps = s.getRightEye().getPupilSize()
			# left eye
			elif self.eye_used == self.left_eye and s.isLeftSample():
				ps = s.getLeftEye().getPupilSize()
			# invalid
			else:
				ps = -1
			# set new pupil size as previous pupil size
			self.prevps = ps

		# if no new sample is available, use old data
		else:
			ps = self.prevps

		return ps


	def sample(self):

		"""Returns a (x,y) tuple of the most recent gaze sample from the eyelink"""

		if not self.recording:
			raise Exception("Error in libeyelink.libeyelink.sample(): Recording was not started before collecting eyelink data!")

		if self.eye_used == None:
			self.set_eye_used()

		s = pylink.getEYELINK().getNewestSample()
		if s != None:
			if self.eye_used == self.right_eye and s.isRightSample():
				gaze = s.getRightEye().getGaze()
			elif self.eye_used == self.left_eye and s.isLeftSample():
				gaze = s.getLeftEye().getGaze()
			else:
				gaze = (-1,-1)
			self.prevsample = gaze[:]
		else:
			gaze = self.prevsample[:]

		return gaze
	
	
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
		
		return (self.eventdetection,self.eventdetection,self.eventdetection)


	def wait_for_event(self, event):

		"""Waits until a specified event has occurred"""

		if not self.recording:
			raise Exception("Error in libeyelink.libeyelink.wait_for_event(): Recording was not started before collecting eyelink data!")

		if self.eye_used == None:
			self.set_eye_used()
		
		if self.eventdetection == 'native':
			d = 0
			while d != event:
				d = pylink.getEYELINK().getNextData()
	
			return pylink.getEYELINK().getFloatData()
		
		else:
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
				raise Exception("Error in libeyelink.libeyelink.wait_for_event: eventcode %s is not supported" % event)
	
			return outcome


	def wait_for_saccade_start(self):

		"""Waits for a saccade start  and returns time and start position"""
		
		# # # # #
		# EyeLink method
		
		if self.eventdetection == 'native':
			d = self.wait_for_event(pylink.STARTSACC)
			return d.getTime(), d.getStartGaze()
		
		
		# # # # #
		# PyGaze method
		
		else:
		
			# get starting position (no blinks)
			newpos = self.sample()
			while not self.is_valid_sample(newpos):
				newpos = self.sample()
			# get starting time, position, intersampledistance, and velocity
			t0 = libtime.get_time()
			prevpos = newpos[:]
			s = 0
			v0 = 0
	
			# get samples
			saccadic = False
			while not saccadic:
				# get new sample
				newpos = self.sample()
				t1 = libtime.get_time()
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
							stime = libtime.get_time()
						# update previous values
						t0 = copy.copy(t1)
						v0 = copy.copy(v1)
	
					# udate previous sample
					prevpos = newpos[:]
	
			return stime, spos


	def wait_for_saccade_end(self):

		"""Waits for a saccade end  and returns time, start position and end position"""

		# # # # #
		# EyeLink method
		
		if self.eventdetection == 'native':
			d = self.wait_for_event(pylink.ENDSACC)
			return d.getTime(), d.getStartGaze(), d.getEndGaze()
		
		
		# # # # #
		# PyGaze method
		
		else:
		
			# get starting position (no blinks)
			t0, spos = self.wait_for_saccade_start()
			# get valid sample
			prevpos = self.sample()
			while not self.is_valid_sample(prevpos):
				prevpos = self.sample()
			# get starting time, intersample distance, and velocity
			t1 = libtime.get_time()
			s = ((prevpos[0]-spos[0])**2 + (prevpos[1]-spos[1])**2)**0.5 # = intersample distance = speed in px/sample
			v0 = s / (t1-t0)
	
			# run until velocity and acceleration go below threshold
			saccadic = True
			while saccadic:
				# get new sample
				newpos = self.sample()
				t1 = libtime.get_time()
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
						etime = libtime.get_time()
					# update previous values
					t0 = copy.copy(t1)
					v0 = copy.copy(v1)
				# udate previous sample
				prevpos = newpos[:]
	
			return etime, spos, epos


	def wait_for_fixation_start(self):

		"""Waits for a fixation start and returns time and start position"""

		# # # # #
		# EyeLink method
		
		if self.eventdetection == 'native':
			d = self.wait_for_event(pylink.STARTFIX)
			return d.getTime(), d.getStartGaze()
		
		
		# # # # #
		# PyGaze method
		
		else:
		
			# function assumes a 'fixation' has started when gaze position
			# remains reasonably stable for self.fixtimetresh
			
			# get starting position
			spos = self.sample()
			while not self.is_valid_sample(spos):
				spos = self.sample()
			
			# get starting time
			t0 = libtime.get_time()
	
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
						t0 = libtime.get_time()
					# if new sample is close to starting sample
					else:
						# get timestamp
						t1 = libtime.get_time()
						# check if fixation time threshold has been surpassed
						if t1 - t0 >= self.fixtimetresh:
							# return time and starting position
							return t1, spos


	def wait_for_fixation_end(self):

		"""Waits for a fixation end and returns ending time and position"""

		# # # # #
		# EyeLink method
		
		if self.eventdetection == 'native':
			d = self.wait_for_event(pylink.ENDFIX)
			return d.getTime(), d.getStartGaze()
		
		
		# # # # #
		# PyGaze method
		
		else:
			
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
	
			return libtime.get_time(), spos	


	def wait_for_blink_start(self):

		"""Waits for a blink start and returns time"""

		# # # # #
		# EyeLink method
		
		if self.eventdetection == 'native':
			d = self.wait_for_event(pylink.STARTBLINK)
			return d.getTime()
		
		
		# # # # #
		# PyGaze method
		
		else:
		
			blinking = False
			
			# loop until there is a blink
			while not blinking:
				# get newest sample
				gazepos = self.sample()
				# check if it's a valid sample
				if not self.is_valid_sample(gazepos):
					# get timestamp for possible blink start
					t0 = libtime.get_time()
					# loop until a blink is determined, or a valid sample occurs
					while not self.is_valid_sample(self.sample()):
						# check if time has surpassed 150 ms
						if libtime.get_time()-t0 >= 150:
							# return timestamp of blink start
							return t0


	def wait_for_blink_end(self):

		"""Waits for a blink end and returns time"""

		# # # # #
		# EyeLink method
		
		if self.eventdetection == 'native':
			d = self.wait_for_event(pylink.ENDBLINK)
			return d.getTime()
		
		
		# # # # #
		# PyGaze method
		
		else:
		
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
			return libtime.get_time()	
	
	
	def is_valid_sample(self, gazepos):
		
		"""Checks if the sample provided is valid, based on EyeLink specific
		criteria (for internal use)
		
		arguments
		gazepos		--	a (x,y) gaze position tuple, as returned by
						self.sample()
		
		returns
		valid			--	a Boolean: True on a valid sample, False on
						an invalid sample
		"""
		
		# return False if a sample is invalid
		if gazepos == (-1,-1):
			return False
		
		# in any other case, the sample is valid
		return True


class eyelink_graphics(custom_display):

	"""A custom graphics environment to use PyGame or PsychoPy graphics (see libscreen) for calibration, rather than PyLink built-in functions"""

	def __init__(self, display, tracker):

		pylink.EyeLinkCustomDisplay.__init__(self)

		# objects
		self.display = display
		self.screen = libscreen.Screen(mousevisible=False)
		self.kb = Keyboard(keylist=None, timeout=1)
		if display.disptype == 'pygame':
			self.kb.set_timeout(timeout=0.001)

		# drawing properties
		self.xc = self.display.dispsize[0]/2
		self.yc = self.display.dispsize[1]/2
		self.ld = 40 # line distance

		# menu
		self.menuscreen = libscreen.Screen(mousevisible=False)
		self.menuscreen.draw_text(text="== Eyelink calibration menu ==", pos=(self.xc,self.yc-5*self.ld), center=True, font='mono', fontsize=12, antialias=True)
		self.menuscreen.draw_text(text="Press C to calibrate", pos=(self.xc,self.yc-3*self.ld), center=True, font='mono', fontsize=12, antialias=True)
		self.menuscreen.draw_text(text="Press V to validate", pos=(self.xc,self.yc-2*self.ld), center=True, font='mono', fontsize=12, antialias=True)
		self.menuscreen.draw_text(text="Press A to auto-threshold", pos=(self.xc,self.yc-1*self.ld), center=True, font='mono', fontsize=12, antialias=True)
		self.menuscreen.draw_text(text="Press Enter to show camera image", pos=(self.xc,self.yc+1*self.ld), center=True, font='mono', fontsize=12, antialias=True)
		self.menuscreen.draw_text(text="(then change between images using the arrow keys)", pos=(self.xc,self.yc+2*self.ld), center=True, font='mono', fontsize=12, antialias=True)
		self.menuscreen.draw_text(text="Press Q to exit menu", pos=(self.xc,self.yc+5*self.ld), center=True, font='mono', fontsize=12, antialias=True)

		# beeps
		self.__target_beep__ = Sound(osc='sine', freq=440, length=50, attack=0, decay=0, soundfile=None)
		self.__target_beep__done__ = Sound(osc='sine', freq=880, length=200, attack=0, decay=0, soundfile=None)
		self.__target_beep__error__ = Sound(osc='sine', freq=220, length=200, attack=0, decay=0, soundfile=None)

		# further properties
		self.state = None

		self.imagebuffer = array.array('l')
		self.pal = None
		self.size = (0,0)

		self.set_tracker(tracker)
		self.last_mouse_state = -1


	def set_tracker(self, tracker):

		"""Connect the tracker to the graphics environment"""

		self.tracker = tracker
		self.tracker_version = tracker.getTrackerVersion()
		if(self.tracker_version >=3):
			self.tracker.sendCommand("enable_search_limits=YES")
			self.tracker.sendCommand("track_search_limits=YES")
			self.tracker.sendCommand("autothreshold_click=YES")
			self.tracker.sendCommand("autothreshold_repeat=YES")
			self.tracker.sendCommand("enable_camera_position_detect=YES")


	def setup_cal_display(self):

		"""Setup the calibration display, which contains some instructions"""
		
		# show instructions
		self.display.fill(self.menuscreen)
		self.display.show()


	def exit_cal_display(self):

		"""Clear calibration display"""

		self.display.fill()
		self.display.show()


	def record_abort_hide(self):

		"""No clue what this is supposed to do..."""

		pass


	def clear_cal_display(self):

		"""Clear the calibration display"""

		self.display.fill()
		self.display.show()


	def erase_cal_target(self):

		"""Is done before drawing"""

		pass


	def draw_cal_target(self, x, y):

		"""Draw calibration target at (x,y)"""
		
		# show fixation dot
		self.screen.draw_fixation(fixtype='dot', colour=FGC, pos=(x,y), pw=0, diameter=12)
		self.display.fill(screen=self.screen)
		self.display.show()
		
		# clear screen
		self.screen.clear()


	def play_beep(self, beepid):

		"""Play a sound"""

		if beepid == pylink.CAL_TARG_BEEP:
			self.__target_beep__.play()
		elif beepid == pylink.CAL_ERR_BEEP or beepid == pylink.DC_ERR_BEEP:
			# show a picture
			self.screen.draw_text(text="calibration unsuccesfull, press 'q' to return to menu", pos=(self.xc,self.yc), center=True, font='mono', fontsize=12, antialias=True)
			self.display.fill(self.screen)
			self.display.show()
			self.screen.clear()
			# play beep
			self.__target_beep__error__.play()
		elif beepid == pylink.CAL_GOOD_BEEP:
			if self.state == "calibration":
				self.screen.draw_text(text="calibration succesfull, press 'v' to validate", pos=(self.xc,self.yc), center=True, font='mono', fontsize=12, antialias=True)
				pass
			elif self.state == "validation":
				self.screen.draw_text(text="calibration succesfull, press 'q' to return to menu", pos=(self.xc,self.yc), center=True, font='mono', fontsize=12, antialias=True)
				pass
			else:
				self.screen.draw_text(text="press 'q' to return to menu", pos=(self.xc,self.yc), center=True, font='mono', fontsize=12, antialias=True)
				pass
			# show screen
			self.display.fill(self.screen)
			self.display.show()
			self.screen.clear()
			# play beep
			self.__target_beep__done__.play()
		else: #	DC_GOOD_BEEP	or DC_TARG_BEEP
			pass


	def getColorFromIndex(self,colorindex):

		"""Unused"""

		pass


	def draw_line(self, x1, y1, x2, y2, colorindex):

		"""Unused"""

		pass


	def draw_lozenge(self,x,y,width,height,colorindex):

		"""Unused"""

		pass


	def get_mouse_state(self):

		"""Unused"""

		pass


	def get_input_key(self):

		"""Get an input key"""

		try:
			key, time = self.kb.get_key(keylist=None,timeout='default')
		except:
			return None

		if key == None:
			return None

		if key == "return":
			keycode = pylink.ENTER_KEY
			self.state = None
		elif key == "space":
			keycode = ord(" ")
		elif key == "q":
			keycode = pylink.ESC_KEY
			self.state = None
		elif key == "c":
			keycode = ord("c")
			self.state = "calibration"
		elif key == "v":
			keycode = ord("v")
			self.state = "validation"
		elif key == "a":
			keycode = ord("a")
		elif key == "up":
			keycode = pylink.CURS_UP
		elif key == "down":
			keycode = pylink.CURS_DOWN
		elif key == "left":
			keycode = pylink.CURS_LEFT
		elif key == "right":
			keycode = pylink.CURS_RIGHT
		else:
			keycode = 0

		return [pylink.KeyInput(keycode, 0)] # 0 = pygame.KMOD_NONE


	def exit_image_display(self):

		"""Exit the image display"""

		self.clear_cal_display()


	def alert_printf(self,msg):

		"""Print alert message"""

		print "eyelink_graphics.alert_printf(): %s" % msg


	def setup_image_display(self, width, height):

		"""Setup the image display"""

		self.size = (width,height)
		self.clear_cal_display()
		self.last_mouse_state = -1
		self.imagebuffer = array.array('l')


	def image_title(self, text):

		"""Unused"""

		pass


	def draw_image_line(self, width, line, totlines, buff):

		"""Draw a single eye video frame (keyword arguments: with=width of the video; line=line nr of current line, totlines=total lines in video; buff=frame buffer
		imagesize: 192x160 px"""

		i = 0
		while i < width:
			try:
				self.imagebuffer.append(self.pal[buff[i]])
			except:
				pass
			i = i + 1

		if line == totlines:

			bufferv = self.imagebuffer.tostring()
			img =Image.new("RGBX",self.size)
			imgsz = self.xc, self.yc
			img.fromstring(bufferv)
			img = img.resize(imgsz)

			if DISPTYPE == 'pygame':
				img = pygame.image.fromstring(img.tostring(),imgsz,"RGBX")
				self.display.fill()
				self.display.expdisplay.blit(img,((self.display.expdisplay.get_rect().w-imgsz[0])/2,(self.display.expdisplay.get_rect().h-imgsz[1])/2))
				self.display.show()
			elif DISPTYPE == 'psychopy':
				img = psychopy.visual.SimpleImageStim(self.display.expdisplay, image=img)
				self.display.fill()
				img.draw()
				self.display.show()

			self.imagebuffer = array.array('l')


	def set_image_palette(self, r, g, b):

		"""Set the image palette"""

		self.imagebuffer = array.array('l')
		self.clear_cal_display()
		sz = len(r)
		i = 0
		self.pal = []
		while i < sz:
			rf = int(b[i])
			gf = int(g[i])
			bf = int(r[i])
			self.pal.append((rf<<16) | (gf<<8) | (bf))
			i += 1

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

from pygaze import settings
from pygaze.libtime import clock
import pygaze
from pygaze.screen import Screen
from pygaze.mouse import Mouse
from pygaze.keyboard import Keyboard
from pygaze.sound import Sound
from pygaze._eyetracker.eyelinkgraphics import EyelinkGraphics
from pygaze._eyetracker.baseeyetracker import BaseEyeTracker

# we try importing the copy_docstr function, but as we do not really need it
# for a proper functioning of the code, we simply ignore it when it fails to
# be imported correctly
try:
	from pygaze._misc.misc import copy_docstr
except:
	pass

import pylink
from PIL import Image
import copy
import math
import sys
import os.path

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

class libeyelink(BaseEyeTracker):

	MAX_TRY = 100

	def __init__(self, display, resolution=settings.DISPSIZE,
		data_file=settings.LOGFILENAME+".edf", fg_color=settings.FGC,
		bg_color=settings.BGC, eventdetection=settings.EVENTDETECTION,
		saccade_velocity_threshold=35, saccade_acceleration_threshold=9500,
		blink_threshold=settings.BLINKTHRESH,
		force_drift_correct=True, pupil_size_mode=settings.EYELINKPUPILSIZEMODE,
		**args):

		"""See pygaze._eyetracker.baseeyetracker.BaseEyeTracker"""

		# try to import copy docstring (but ignore it if it fails, as we do
		# not need it for actual functioning of the code)
		try:
			copy_docstr(BaseEyeTracker, libeyelink)
		except:
			# we're not even going to show a warning, since the copied
			# docstring is useful for code editors; these load the docs
			# in a non-verbose manner, so warning messages would be lost
			pass

		global _eyelink

		# Make sure that we have a valid data file. The local_data_file may
		# contain a folder. The eyelink_data_file is only a basename, i.e.
		# without folder. The eyelink_data_file must be at most eight characters
		# and end with a `.edf` extension.
		self.local_data_file = data_file
		self.eyelink_data_file = os.path.basename(data_file)
		stem, ext = os.path.splitext(self.eyelink_data_file)
		if len(stem) > 8 or ext.lower() != '.edf':
			raise Exception(
				"The EyeLink cannot handle filenames longer than eight "
				"characters (excluding '.edf' extension).")

		# properties
		self.display = display
		self.fontsize = 18
		self.scr = Screen(disptype=settings.DISPTYPE, mousevisible=False)
		self.kb = Keyboard(keylist=["escape", "q"], timeout=1)
		self.resolution = resolution
		self.recording = False
		self.saccade_velocity_treshold = saccade_velocity_threshold
		self.saccade_acceleration_treshold = saccade_acceleration_threshold
		self.blink_threshold = blink_threshold
		self.eye_used = None
		self.left_eye = 0
		self.right_eye = 1
		self.binocular = 2
		self.pupil_size_mode = pupil_size_mode
		self.prevsample = (-1,-1)
		self.prevps = -1

		# event detection properties
		# degrees; maximal distance from fixation start (if gaze wanders beyond
		# this, fixation has stopped)
		self.fixtresh = 1.5
		# milliseconds; amount of time gaze has to linger within self.fixtresh
		# to be marked as a fixation
		self.fixtimetresh = 100
		# degrees per second; saccade velocity threshold
		self.spdtresh = self.saccade_velocity_treshold
		# degrees per second**2; saccade acceleration threshold
		self.accthresh = self.saccade_acceleration_treshold
		self.set_detection_type(eventdetection)
		# weighted distance, used for determining whether a movement is due to
		# measurement error (1 is ok, higher is more conservative and will
		# result in only larger saccades to be detected)
		self.weightdist = 10
		# distance between participant and screen in cm
		self.screendist = settings.SCREENDIST
		# distance between participant and screen in cm
		self.screensize = settings.SCREENSIZE
		self.pixpercm = (self.resolution[0]/float(self.screensize[0]) + \
			self.resolution[1]/float(self.screensize[1])) / 2.0
		# only initialize eyelink once
		if _eyelink == None:
			try:
				_eyelink = pylink.EyeLink()
			except:
				raise Exception(
					"Error in libeyelink.libeyelink.__init__(): Failed to "
					"connect to the tracker!")
		# determine software version of tracker
		self.tracker_software_ver = 0
		self.eyelink_ver = pylink.getEYELINK().getTrackerVersion()
		if self.eyelink_ver == 3:
			tvstr = pylink.getEYELINK().getTrackerVersionString()
			vindex = tvstr.find("EYELINK CL")
			self.tracker_software_ver = int(float(tvstr[(vindex + \
				len("EYELINK CL")):].strip()))
		if self.eyelink_ver == 1:
			self.eyelink_model = 'EyeLink I'
		elif self.eyelink_ver == 2:
			self.eyelink_model = 'EyeLink II'
		elif self.eyelink_ver == 3:
			self.eyelink_model = 'EyeLink 1000'
		else:
			self.eyelink_model = 'EyeLink (model unknown)'
		# Open graphics
		self.eyelink_graphics = EyelinkGraphics(self, _eyelink)
		pylink.openGraphicsEx(self.eyelink_graphics)
		# Optionally force drift correction. For some reason this must be done
		# as (one of) the first things, otherwise a segmentation fault occurs.
		if force_drift_correct:
			try:
				self.send_command('driftcorrect_cr_disable = OFF')
			except:
				print('Failed to force drift correction (EyeLink 1000 only)')
		# Set pupil-size mode
		if self.pupil_size_mode == 'area':
			pylink.getEYELINK().setPupilSizeDiameter(False)
		elif self.pupil_size_mode == 'diameter':
			pylink.getEYELINK().setPupilSizeDiameter(True)
		else:
			raise Exception(
				"pupil_size_mode should be 'area' or 'diameter', not %s" \
				% self.pupil_size_mode)
		pylink.getEYELINK().openDataFile(self.eyelink_data_file)
		pylink.flushGetkeyQueue()
		pylink.getEYELINK().setOfflineMode()
		# notify eyelink of display resolution
		self.send_command("screen_pixel_coords = 0 0 %d %d" % \
			(self.resolution[0], self.resolution[1]))
		# get some configuration stuff
		if self.eyelink_ver >= 2:
			self.send_command("select_parser_configuration 0")
			if self.eyelink_ver == 2: # turn off scenelink camera stuff
				self.send_command("scene_camera_gazemap = NO")
		# set EDF file contents (this specifies which data is written to the EDF
		# file)
		self.send_command(
			"file_event_filter = LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON")
		if self.tracker_software_ver >= 4:
			self.send_command(
				"file_sample_data  = LEFT,RIGHT,GAZE,AREA,GAZERES,STATUS,HTARGET")
		else:
			self.send_command(
				"file_sample_data  = LEFT,RIGHT,GAZE,AREA,GAZERES,STATUS")
		# set link data (this specifies which data is sent through the link and
		# thus can be used in gaze contingent displays)
		self.send_command(
			"link_event_filter = LEFT,RIGHT,FIXATION,SACCADE,BLINK,BUTTON")
		if self.tracker_software_ver >= 4:
			self.send_command(
				"link_sample_data  = LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS,HTARGET")
		else:
			self.send_command(

				"link_sample_data  = LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS")
		# not quite sure what this means (according to Sebastiaan Mathot, it
		# might be the button that is used to end drift correction?)
		self.send_command("button_function 5 'accept_target_fixation'")

		if not self.connected():
			raise Exception(
				"Error in libeyelink.libeyelink.__init__(): Failed to connect "
				"to the eyetracker!")

	def send_command(self, cmd):

		"""See pygaze._eyetracker.baseeyetracker.BaseEyeTracker"""

		pylink.getEYELINK().sendCommand(cmd)

	def log(self, msg):

		"""See pygaze._eyetracker.baseeyetracker.BaseEyeTracker"""

		pylink.getEYELINK().sendMessage(msg)

	def status_msg(self, msg):

		"""See pygaze._eyetracker.baseeyetracker.BaseEyeTracker"""

		print('status message: %s' % msg)
		pylink.getEYELINK().sendCommand("record_status_message '%s'" % msg)

	def connected(self):

		"""See pygaze._eyetracker.baseeyetracker.BaseEyeTracker"""

		return pylink.getEYELINK().isConnected()

	def calibrate(self):

		"""See pygaze._eyetracker.baseeyetracker.BaseEyeTracker"""

		while True:
			if self.recording:
				raise Exception(
					"Error in libeyelink.libeyelink.calibrate(): Trying to "
					"calibrate after recording has started!")
	
			# # # # #
			# EyeLink calibration and validation
	
			# attempt calibrate; confirm abort when esc pressed
			while True:
				self.eyelink_graphics.esc_pressed = False
				pylink.getEYELINK().doTrackerSetup()
				if not self.eyelink_graphics.esc_pressed:
					break
				self.confirm_abort_experiment()
	
			# If we are using the built-in EyeLink event detection, we don't need
			# the RMS calibration routine.
			if self.eventdetection == 'native':
				return
	
			# # # # #
			# RMS calibration
			while True:
				# present instructions
				self.display.fill() # clear display
				self.scr.draw_text(text= \
					"Noise calibration: please look at the dot\n\n(press space to start)",
					pos=(self.resolution[0]/2, int(self.resolution[1]*0.2)),
					center=True, fontsize=self.fontsize)
				self.scr.draw_fixation(fixtype='dot')
				self.display.fill(self.scr)
				self.display.show()
				self.scr.clear() # clear screen again
		
				# wait for spacepress
				self.kb.get_key(keylist=['space'], timeout=None)
		
				# start recording
				self.log("PYGAZE RMS CALIBRATION START")
				self.start_recording()
		
				# show fixation
				self.display.fill()
				self.scr.draw_fixation(fixtype='dot')
				self.display.fill(self.scr)
				self.display.show()
				self.scr.clear()
		
				# wait for a bit, to allow participant to fixate
				clock.pause(500)
		
				# get samples
				# samplelist, prefilled with 1 sample to prevent sl[-1] from producing
				# an error; first sample will be ignored for RMS calculation
				sl = [self.sample()]
				t0 = clock.get_time() # starting time
				while clock.get_time() - t0 < 1000:
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
				if Xvar and Yvar: # check if properly recorded to avoid risk of division by zero error
					XRMS = (sum(Xvar) / len(Xvar))**0.5
					YRMS = (sum(Yvar) / len(Yvar))**0.5
					self.pxdsttresh = (XRMS, YRMS)
		
					# recalculate thresholds (degrees to pixels)
					self.pxfixtresh = deg2pix(self.screendist, self.fixtresh, self.pixpercm)
					self.pxspdtresh = deg2pix(self.screendist, self.spdtresh,
						self.pixpercm)/1000.0 # in pixels per millisecons
					self.pxacctresh = deg2pix(self.screendist, self.accthresh,
						self.pixpercm)/1000.0 # in pixels per millisecond**2
					return
				else: # if nothing recorded, display message saying so
					self.display.fill()
					self.scr.draw_text(text = \
						"Noise calibration failed.\n\nPress r to retry,\nor press space to return to calibration screen.", \
						pos=(self.resolution[0]/2, int(self.resolution[1]*0.2)), \
						center=True, fontsize=self.fontsize)
					self.display.fill(self.scr)
					self.display.show()
					self.scr.clear()
					# wait for space or r press, if r restart noise calibration, if space return to calibration menu
					keypressed = self.kb.get_key(keylist=['space','r'], timeout=None)
					if keypressed[0] == 'space':
						break

	def drift_correction(self, pos=None, fix_triggered=False):

		"""See pygaze._eyetracker.baseeyetracker.BaseEyeTracker"""

		if self.recording:
			raise Exception(
				"Error in libeyelink.libeyelink.drift_correction(): Trying to "
				"perform drift correction after recording has started!")
		if not self.connected():
			raise Exception(
				"Error in libeyelink.libeyelink.drift_correction(): The "
				"eyelink is not connected!")
		if pos == None:
			pos = self.resolution[0] / 2, self.resolution[1] / 2
		if fix_triggered:
			return self.fix_triggered_drift_correction(pos)
		return self.manual_drift_correction(pos)

	def manual_drift_correction(self, pos):

		"""
		Performs a manual, i.e. spacebar-triggered drift correction.

		Arguments:
		pos		--	The positionf or the drift-correction target.

		Returns:
		True if drift correction was successfull, False otherwise.
		"""

		self.draw_drift_correction_target(pos[0], pos[1])
		self.eyelink_graphics.esc_pressed = False
		try:
			# The 0 parameters indicate that the display should not be cleared
			# and we should not be allowed to fall back to the set-up screen.
			error = pylink.getEYELINK().doDriftCorrect(pos[0], pos[1], 0, 0)
		except:
			error = -1
		# A 0 exit code means successful drift correction
		if error == 0:
			return True
		# If escape was pressed, we present the confirm abort screen
		if self.eyelink_graphics.esc_pressed:
			self.confirm_abort_experiment()
		# If 'q' was pressed, we drop back to the calibration screen
		else:
			self.calibrate()
		return False

	def prepare_drift_correction(self, pos):

		"""Puts the tracker in drift correction mode"""

		# start collecting samples in drift correction mode
		self.send_command("heuristic_filter = ON")
		self.send_command("drift_correction_targets = %d %d" % pos)
		self.send_command("start_drift_correction data = 0 0 1 0")
		pylink.msecDelay(50);
		# wait for a bit until samples start coming in (again, not sure if this
		# is indeed what's going on)
		if not pylink.getEYELINK().waitForBlockStart(100, 1, 0):
			print(
				"WARNING libeyelink.libeyelink.prepare_drift_correction(): "
				"Failed to perform drift correction (waitForBlockStart error)")

	def fix_triggered_drift_correction(self, pos=None, min_samples=30,
		max_dev=60, reset_threshold=10):

		"""See pygaze._eyetracker.baseeyetracker.BaseEyeTracker"""

		if self.recording:
			raise Exception(
				"Error in libeyelink.libeyelink.fix_triggered_drift_correction(): "
				"Trying to perform drift correction after recording has started!")

		self.recording = True
		if pos == None:
			pos = self.resolution[0] / 2, self.resolution[1] / 2
		self.prepare_drift_correction(pos)
		self.draw_drift_correction_target(pos[0], pos[1])

		# loop until we have enough samples
		lx = []
		ly = []
		while len(lx) < min_samples:

			# Check whether the EyeLink is put into set-up mode on the EyeLink
			# PC and, if so, jump to the calibration menu.
			if pylink.getEYELINK().getCurrentMode() == pylink.IN_SETUP_MODE:
				self.recording = False
				self.calibrate()
				print(
					"libeyelink.libeyelink.fix_triggered_drift_correction(): "
					"'q' pressed")
				return False

			# pressing escape enters the calibration screen
			resp = self.kb.get_key(keylist=["escape", "q"], timeout=1)[0]
			if resp == 'escape':
				self.recording = False
				self.confirm_abort_experiment()
				print(
					"libeyelink.libeyelink.fix_triggered_drift_correction(): "
					"'escape' pressed")
				return False
			elif resp == 'q':
				self.recording = False
				self.calibrate()
				print(
					"libeyelink.libeyelink.fix_triggered_drift_correction(): "
					"'q' pressed")
				return False
			# collect a sample
			x, y = self.sample()
			if len(lx) == 0 or x != lx[-1] or y != ly[-1]:
				# if present sample deviates too much from previous sample,
				# start from scratch.
				if len(lx) > 0 and (abs(x - lx[-1]) > reset_threshold or \
					abs(y - ly[-1]) > reset_threshold):
					lx = []
					ly = []
				# Collect a sample
				else:
					lx.append(x)
					ly.append(y)
			# If we have enough samples to perform a drift correction ...
			if len(lx) == min_samples:
				avg_x = sum(lx) / len(lx)
				avg_y = sum(ly) / len(ly)
				d = ((avg_x - pos[0]) ** 2 + (avg_y - pos[1]) ** 2)**0.5
				# emulate spacebar press on succes
				pylink.getEYELINK().sendKeybutton(32, 0, pylink.KB_PRESS)
				# getCalibrationResult() returns 0 on success and an exception
				# or a non-zero value otherwise
				result = -1
				try:
					result = pylink.getEYELINK().getCalibrationResult()
				except:
					lx = []
					ly = []
					print(
						"libeyelink.libeyelink.fix_triggered_drift_correction(): "
						"try again")
				if result != 0:
					try:
						result = pylink.getEYELINK().getCalibrationResult()
					except:
						lx = []
						ly = []
						print(
							"libeyelink.libeyelink.fix_triggered_drift_correction(): "
							"try again")
		# apply drift correction
		pylink.getEYELINK().applyDriftCorrect()
		self.recording = False
		print("libeyelink.libeyelink.fix_triggered_drift_correction(): success")
		return True

	def start_recording(self):

		"""See pygaze._eyetracker.baseeyetracker.BaseEyeTracker"""

		self.recording = True
		i = 0
		while True:
			# params: write samples, write event, send samples, send events
			print(u'starting recording ...')
			error = pylink.getEYELINK().startRecording(1, 1, 1, 1)
			print(u'returned %s' % error)
			if not error:
				break
			if i > self.MAX_TRY:
				raise Exception(
					"Error in libeyelink.libeyelink.start_recording(): Failed "
					"to start recording!")
				self.close()
				clock.expend()
			i += 1
			print(
				("WARNING libeyelink.libeyelink.start_recording(): Failed to "
				"start recording (attempt %d of %d)") % (i, self.MAX_TRY))
			pylink.msecDelay(100)
		# don't know what this is
		print(u'Start realtime mode ...')
		pylink.msecDelay(100)
		pylink.beginRealTimeMode(100)
		# wait a bit until samples start coming in
		print(u'Wait for block start ...')
		pylink.msecDelay(100)
		if not pylink.getEYELINK().waitForBlockStart(100, 1, 0):
			raise Exception(
				"Error in libeyelink.libeyelink.start_recording(): Failed to "
				"start recording (waitForBlockStart error)!")
		print(u'done ...')

	def stop_recording(self):

		"""See pygaze._eyetracker.baseeyetracker.BaseEyeTracker"""

		print(u'stopping recording ...')
		self.recording = False
		pylink.endRealTimeMode()
		pylink.getEYELINK().setOfflineMode()
		pylink.msecDelay(500)
		print(u'done ...')

	def close(self):

		"""See pygaze._eyetracker.baseeyetracker.BaseEyeTracker"""

		self.eyelink_graphics.close()
		if self.recording:
			self.stop_recording()
		# close data file and transfer it to the experimental PC
		print("libeyelink.libeyelink.close(): Closing data file")
		pylink.getEYELINK().closeDataFile()
		pylink.msecDelay(500)
		print("libeyelink.libeyelink.close(): Transferring %s to %s" \
			% (self.eyelink_data_file, self.local_data_file))
		# During data transfer, suppress output
		_out = sys.stdout
		with open(os.devnull, 'w') as fd:
			sys.stdout = fd
			pylink.getEYELINK().receiveDataFile(self.eyelink_data_file,
				self.local_data_file)
			sys.stdout = _out
		pylink.msecDelay(500)
		print("libeyelink.libeyelink.close(): Closing eyelink")
		pylink.getEYELINK().close();
		pylink.msecDelay(500)

	def set_eye_used(self):

		"""See pygaze._eyetracker.baseeyetracker.BaseEyeTracker"""

		self.eye_used = pylink.getEYELINK().eyeAvailable()
		if self.eye_used == self.right_eye:
			self.log_var("eye_used", "right")
		elif self.eye_used == self.left_eye or self.eye_used == self.binocular:
			self.log_var("eye_used", "left")
			self.eye_used = self.left_eye
		else:
			print(
				"WARNING libeyelink.libeyelink.set_eye_used(): Failed to "
				"determine which eye is being recorded")

	def pupil_size(self):

		"""See pygaze._eyetracker.baseeyetracker.BaseEyeTracker"""

		if not self.recording:
			raise Exception(
				"Error in libeyelink.libeyelink.pupil_size(): Recording was "
				"not started before collecting eyelink data!")
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

		"""See pygaze._eyetracker.baseeyetracker.BaseEyeTracker"""

		if not self.recording:
			raise Exception(
				"Error in libeyelink.libeyelink.sample(): Recording was not "
				"started before collecting eyelink data!")
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

		"""See pygaze._eyetracker.baseeyetracker.BaseEyeTracker"""

		if eventdetection in ['pygaze','native']:
			self.eventdetection = eventdetection

		return (self.eventdetection,self.eventdetection,self.eventdetection)

	def _get_eyelink_clock_async(self):
		"""
		Retrieve time differenece between tracker timestamps and
		current clock time upheld in the pygaze environment.

		Note that this is not guaranteed to be a static time difference, the
		clocks might run at different speeds. Therefore you should consider
		running this function every time you utilize on this time difference.

		Returns:
		The tracker time minus the clock time
		"""
		return pylink.getEYELINK().trackerTime() -  clock.get_time()

	def wait_for_event(self, event):

		"""See pygaze._eyetracker.baseeyetracker.BaseEyeTracker"""

		if not self.recording:
			raise Exception(
				"Error in libeyelink.libeyelink.wait_for_event(): Recording "
				"was not started before collecting eyelink data!")

		if self.eye_used == None:
			self.set_eye_used()
		if self.eventdetection == 'native':
			# since the link buffer was not have been polled, old data has
			# accumulated in the buffer -- so ignore events that are old:
			t0 = clock.get_time() # time of call
			while True:
				d = pylink.getEYELINK().getNextData()
				if d == event:
					float_data  = pylink.getEYELINK().getFloatData()
					# corresponding clock_time
					tc = float_data.getTime() - self._get_eyelink_clock_async()
					if tc > t0:
						return tc, float_data

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
			raise Exception(
				("Error in libeyelink.libeyelink.wait_for_event: eventcode %s "
				"is not supported") % event)
		return outcome

	def wait_for_saccade_start(self):

		"""See pygaze._eyetracker.baseeyetracker.BaseEyeTracker"""

		# # # # #
		# EyeLink method

		if self.eventdetection == 'native':
			t,d = self.wait_for_event(pylink.STARTSACC)
			return t, d.getStartGaze()


		# # # # #
		# PyGaze method

		else:

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
					# weigthed distance: (sx/tx)**2 + (sy/ty)**2 > 1 means
					# movement larger than RMS noise
					if (sx/self.pxdsttresh[0])**2 + (sy/self.pxdsttresh[1])**2 \
						> self.weightdist:
						# calculate distance
						# intersampledistance = speed in pixels/ms
						s = ((sx)**2 + (sy)**2)**0.5
						# calculate velocity
						v1 = s / (t1-t0)
						# calculate acceleration
						a = (v1-v0) / (t1-t0) # acceleration in pixels/ms**2
						# check if either velocity or acceleration are above
						# threshold values
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

	def wait_for_saccade_end(self):

		"""See pygaze._eyetracker.baseeyetracker.BaseEyeTracker"""

		# # # # #
		# EyeLink method

		if self.eventdetection == 'native':
			t,d = self.wait_for_event(pylink.ENDSACC)
			return t, d.getStartGaze(), d.getEndGaze()


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
			t1 = clock.get_time()
			# = intersample distance = speed in px/sample
			s = ((prevpos[0]-spos[0])**2 + (prevpos[1]-spos[1])**2)**0.5
			v0 = s / (t1-t0)
			# run until velocity and acceleration go below threshold
			saccadic = True
			while saccadic:
				# get new sample
				newpos = self.sample()
				t1 = clock.get_time()
				if self.is_valid_sample(newpos) and newpos != prevpos:
					# calculate distance
					# = speed in pixels/sample
					s = ((newpos[0]-prevpos[0])**2 + \
						(newpos[1]-prevpos[1])**2)**0.5
					# calculate velocity
					v1 = s / (t1-t0)
					# calculate acceleration
					# acceleration in pixels/sample**2 (actually is
					# v1-v0 / t1-t0; but t1-t0 = 1 sample)
					a = (v1-v0) / (t1-t0)
					# check if velocity and acceleration are below threshold
					if v1 < self.pxspdtresh and (a > -1*self.pxacctresh and \
						a < 0):
						saccadic = False
						epos = newpos[:]
						etime = clock.get_time()
					# update previous values
					t0 = copy.copy(t1)
					v0 = copy.copy(v1)
				# udate previous sample
				prevpos = newpos[:]

			return etime, spos, epos

	def wait_for_fixation_start(self):

		"""See pygaze._eyetracker.baseeyetracker.BaseEyeTracker"""

		# # # # #
		# EyeLink method

		if self.eventdetection == 'native':
			t,d = self.wait_for_event(pylink.STARTFIX)
			return t, d.getTime(), d.getStartGaze()


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
			t0 = clock.get_time()

			# wait for reasonably stable position
			moving = True
			while moving:
				# get new sample
				npos = self.sample()
				# check if sample is valid
				if self.is_valid_sample(npos):
					# check if new sample is too far from starting position
					if (npos[0]-spos[0])**2 + (npos[1]-spos[1])**2 > \
						self.pxfixtresh**2: # Pythagoras
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

	def wait_for_fixation_end(self):

		"""See pygaze._eyetracker.baseeyetracker.BaseEyeTracker"""

		# # # # #
		# EyeLink method

		if self.eventdetection == 'native':
			t, d = self.wait_for_event(pylink.ENDFIX)
			return t, d.getTime(), d.getStartGaze()


		# # # # #
		# PyGaze method

		else:

			# function assumes that a 'fixation' has ended when a deviation of
			# more than fixtresh from the initial 'fixation' position has been
			# detected

			# get starting time and position
			stime, spos = self.wait_for_fixation_start()

			# loop until fixation has ended
			while True:
				# get new sample
				npos = self.sample() # get newest sample
				# check if sample is valid
				if self.is_valid_sample(npos):
					# check if sample deviates to much from starting position
					if (npos[0]-spos[0])**2 + (npos[1]-spos[1])**2 > \
						self.pxfixtresh**2: # Pythagoras
						# break loop if deviation is too high
						break

			return clock.get_time(), spos

	def wait_for_blink_start(self):

		"""See pygaze._eyetracker.baseeyetracker.BaseEyeTracker"""

		# # # # #
		# EyeLink method

		if self.eventdetection == 'native':
			t, d = self.wait_for_event(pylink.STARTBLINK)
			return t, d.getTime()


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
					t0 = clock.get_time()
					# loop until a blink is determined, or a valid sample occurs
					while not self.is_valid_sample(self.sample()):
						# check if time has surpassed 150 ms
						if clock.get_time()-t0 >= self.blink_threshold:
							# return timestamp of blink start
							return t0

	def wait_for_blink_end(self):

		"""See pygaze._eyetracker.baseeyetracker.BaseEyeTracker"""

		# # # # #
		# EyeLink method

		if self.eventdetection == 'native':
			t,d = self.wait_for_event(pylink.ENDBLINK)
			return t


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
			return clock.get_time()

	def set_draw_calibration_target_func(self, func):

		"""See pygaze._eyetracker.baseeyetracker.BaseEyeTracker"""

		self.eyelink_graphics.draw_cal_target = func

	# ***
	#
	# Internal functions below
	#
	# ***

	def is_valid_sample(self, gazepos):

		"""
		Checks if the sample provided is valid, based on EyeLink specific
		criteria.

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


	def confirm_abort_experiment(self):

		"""
		Asks for confirmation before aborting the experiment. Displays a
		confirmation screen, collects the response, and acts accordingly.

		Exceptions:
		Raises a response_error upon confirmation.

		Returns:
		False if no confirmation was given.
		"""

		# Display the confirmation screen
		scr = Screen(disptype=settings.DISPTYPE)
		kb = Keyboard(timeout=5000)
		yc = settings.DISPSIZE[1]/2
		xc = settings.DISPSIZE[0]/2
		ld = 40 # Line height
		scr.draw_text(u'Really abort experiment?', pos=(xc, yc-3*ld),
			fontsize=self.fontsize)
		scr.draw_text(u'Press \'Y\' to abort', pos=(xc, yc-0.5*ld),
			fontsize=self.fontsize)
		scr.draw_text(u'Press any other key or wait 5s to go to setup',
			pos=(xc, yc+0.5*ld), fontsize=self.fontsize)
		self.display.fill(scr)
		self.display.show()
		# process the response:
		try:
			key, time = kb.get_key()
		except:
			return False
		# if confirmation, close experiment
		if key == u'y':
			raise Exception(u'The experiment was aborted')
		self.eyelink_graphics.esc_pressed = False
		return False

	def draw_drift_correction_target(self, x, y):

		"""
		Draws the drift-correction target.

		arguments

		x		--	The X coordinate
		y		--	The Y coordinate
		"""

		self.scr.clear()
		self.scr.draw_fixation(fixtype='dot', colour=settings.FGC, pos=(x,y),
			pw=0, diameter=12)
		self.display.fill(self.scr)
		self.display.show()

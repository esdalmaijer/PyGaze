## This file is part of PyGaze - the open-source toolbox for eye tracking
##
##	PyGaze is a Python module for easily creating gaze contingent experiments
##	or other software (as well as non-gaze contingent experiments/software)
##	Copyright (C) 2012-2013  Edwin S. Dalmaijer
##
##	This program is free software: you can redistribute it and/or modify
##	it under the terms of the GNU General Public License as published by
##	the Free Software Foundation, either version 3 of the License, or
##	(at your option) any later version.
##
##	This program is distributed in the hope that it will be useful,
##	but WITHOUT ANY WARRANTY; without even the implied warranty of
##	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##	GNU General Public License for more details.
##
##	You should have received a copy of the GNU General Public License
##	along with this program.  If not, see <http://www.gnu.org/licenses/>
#
# version: 0.4 (25-03-2013)

from defaults import *
try:
	from constants import *
except:
	pass

import libtime
import libscreen
from libinput import Keyboard
from libsound import Sound

import copy
import math

if not DUMMYMODE:
	from iViewXAPI import  *

# function for identyfing errors
def errorstring(returncode):

	"""Returns a string with a description of the error associated with given
	return code (for internal use)
	
	arguments
	returncode	-- errorcode from iViewXAPI (an integer number)
	
	returns
	errorstring	-- string describing the error associated with specified code
	"""

	if type(returncode) != int:
		try:
			returncode = int(returncode)
		except:
			return "returncode not recognized as a valid integer"
	
	codes = {
		1:"SUCCES: intended functionality has been fulfilled",
		2:"NO_VALID_DATA: no new data available",
		3:"CALIBRATION_ABORTED: calibration was aborted",
		100:"COULD_NOT_CONNECT: failed to establish connection",
		101:"NOT_CONNECTED: no connection established",
		102:"NOT_CALIBRATED: system is not calibrated",
		103:"NOT_VALIDATED: system is not validated",
		104:"EYETRACKING_APPLICATION_NOT_RUNNING: no SMI eye tracking application running",
		105:"WRONG_COMMUNICATION_PARAMETER: wrong port settings",
		111:"WRONG_DEVICE: eye tracking device required for this function is not connected",
		112:"WRONG_PARAMETER: parameter out of range",
		113:"WRONG_CALIBRATION_METHOD: eye tracking device required for this calibration method is not connected",
		121:"CREATE_SOCKET: failed to create sockets",
		122:"CONNECT_SOCKET: failed to connect sockets",
		123:"BIND_SOCKET: failed to bind sockets",
		124:"DELETE_SOCKET: failed to delete sockets",
		131:"NO_RESPONSE_FROM_IVIEW: no response from iView X; check iView X connection settings (IP addresses, ports) or last command",
		132:"INVALID_IVIEWX_VERSION: iView X version could not be resolved",
		133:"WRONG_IVIEWX_VERSION: wrong version of iView X",
		171:"ACCESS_TO_FILE: failed to access log file",
		181:"SOCKET_CONNECTION: socket error during data transfer",
		191:"EMPTY_DATA_BUFFER: recording buffer is empty",
		192:"RECORDING_DATA_BUFFER: recording is activated",
		193:"FULL_DATA_BUFFER: data buffer is full",
		194:"IVIEWX_IS_NOT_READY: iView X is not ready",
		201:"IVIEWX_NOT_FOUND: no installed SMI eye tracking application detected",
		220:"COULD_NOT_OPEN_PORT: could not open port for TTL output",
		221:"COULD_NOT_CLOSE_PORT: could not close port for TTL output",
		222:"AOI_ACCESS: could not access AOI data",
		223:"AOI_NOT_DEFINED: no defined AOI found",
		'unknown': "unknown error with decimal code %d; please refer to the iViewX SDK Manual" % returncode
		}

	if returncode in codes.keys():
		return codes[returncode]
	else:
		return codes['unknown']


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
class SMItracker:

	"""A class for SMI eye tracker objects"""

	def __init__(self, display, ip='127.0.0.1', sendport=4444, receiveport=5555, logfile=LOGFILE):

		"""Initializes the SMItracker object
		
		arguments
		display	-- a libscreen.Display object
		
		keyword arguments
		ip		-- internal ip address for iViewX (default = 
				   '127.0.0.1')
		sendport	-- port number for iViewX sending (default = 4444)
		receiveport	-- port number for iViewX receiving (default = 5555)
		logfile	-- logfile name (string value); note that this is the
				   name for the SMI logfile, NOT the .idf file
				   (default = LOGFILE)
		"""

		# properties
		self.disp = display
		self.screen = libscreen.Screen()
		self.outputfile = logfile #TODO: EDIT PATH TO DATADIRECTORY
		self.description = "experiment" # TODO: EXPERIMENT NAME
		self.participant = "participant" # TODO: PP NAME
		self.connected = False
		self.recording = False
		self.eye_used = 0 # 0=left, 1=right, 2=binocular
		self.left_eye = 0
		self.right_eye = 1
		self.binocular = 2
		self.kb = Keyboard(keylist=['space', 'escape', 'q'], timeout=1)
		self.errorbeep = Sound(osc='saw',freq=100, length=100)
		self.errdist = 2 # degrees
		self.fixtresh = 1.5 # degrees
		self.spdtresh = 35 # degrees per second; saccade speed threshold
		self.accthresh = 9500 # degrees per second**2; saccade acceleration threshold
		self.weightdist = 10 # weighted distance, used for determining whether a movement is due to measurement error (1 is ok, higher is more conservative and will result in only larger saccades to be detected)
		self.dispsize = DISPSIZE # display size in pixels
		self.screensize = SCREENSIZE # display size in cm
		self.prevsample = (-1,-1)
		self.maxtries = 100 # number of samples obtained before giving up (for obtaining accuracy and tracker distance information, as well as starting or stopping recording)

		# set logger
		res = iViewXAPI.iV_SetLogger(c_int(1), c_char_p(logfile + '_SMILOG.txt'))
		if res != 1:
			err = errorstring(res)
			raise Exception("Error in libsmi.SMItracker.__init__: failed to set logger; %s" % err)
		# first logger argument is for logging type (I'm guessing these are decimal bit codes)
		# LOG status					bitcode
		# 1 = LOG_LEVEL_BUG			 00001
		# 2 = LOG_LEVEL_iV_FCT		  00010
		# 4 = LOG_LEVEL_ETCOM		   00100
		# 8 = LOG_LEVEL_ALL			 01000
		# 16 = LOG_LEVEL_IV_COMMAND	 10000
		# these can be used together, using a bitwise or, e.g.: 1|2|4 (bitcode 00111)

		# connect to iViewX
		res = iViewXAPI.iV_Connect(c_char_p(ip), c_int(sendport), c_char_p(ip), c_int(receiveport))
		if res == 1:
			res = iViewXAPI.iV_GetSystemInfo(byref(systemData))
			self.samplerate = systemData.samplerate
			self.sampletime = 1000.0 / self.samplerate
			if res != 1:
				err = errorstring(res)
				raise Exception("Error in libsmi.SMItracker.__init__: failed to get system information; %s" % err)
		# handle connection errors
		else:
			self.connected = False
			err = errorstring(res)
			raise Exception("Error in libsmi.SMItracker.__init__: establishing connection failed; %s" % err)

		# initiation report
		self.log("pygaze initiation report start")
		self.log("experiment: %s" % self.description)
		self.log("participant: %s" % self.participant)
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
		calibrate	-- Boolean indicating if calibration should be
				   performed (default = True)
		validate	-- Boolean indicating if validation should be performed
				   (default = True)
		
		returns
		success	-- returns True if calibration succeeded, or False if
				   not; in addition a calibration log is added to the
				   log file and some properties are updated (i.e. the
				   thresholds for detection algorithms)
		"""

		# TODO:
		# add feedback for calibration (e.g. with iV_GetAccuracyImage (struct ImageStruct * imageData) for accuracy and iV_GetEyeImage for cool eye pictures)
		# example: res = iViewXAPI.iV_GetEyeImage(byref(imageData))
		# ImageStruct has four data fields:
		# imageHeight	-- int vertical size (px)
		# imageWidth	-- int horizontal size (px)
		# imageSize		-- int image data size (byte)
		# imageBuffer	-- pointer to image data (I have NO idea what format this is in)

		# configure calibration (NOT starting it)
		calibrationData = CCalibration(9, 1, 0, 1, 1, 0, 127, 1, 15, b"") # (method (i.e.: number of points), visualization, display, speed, auto, fg, bg, shape, size, filename)

		# setup calibration
		res = iViewXAPI.iV_SetupCalibration(byref(calibrationData))
		if res != 1:
			err = errorstring(res)
			raise Exception("Error in libsmi.SMItracker.calibrate: failed to setup calibration; %s" % err)

		# calibrate
		cres = iViewXAPI.iV_Calibrate()
			
		# validate if calibration returns succes
		if cres == 1:
			cerr = None
			vres = iViewXAPI.iV_Validate()
			# handle validation errors
			if vres != 1:
				verr = errorstring(vres)
			else:
				verr = None
##				# TEST #
##				res = iViewXAPI.iV_GetAccuracyImage(byref(imageData))
##				self.log("IMAGEBUFFERSTART")
##				self.log(imageData.imageBuffer)
##				self.log("IMAGEBUFFERSTOP")
##				print("Image height: %s, image width: %s, image size: %s" % (imageData.imageHeight,imageData.imageWidth, imageData.imageSize))
##				print imageData.imageBuffer
##				########
		# handle calibration errors
		else:
			cerr = errorstring(cres)

		# return succes
		if cerr == None:
			print("libsmi.SMItracker.calibrate: calibration was succesful")
			if verr == None:
				print("libsmi.SMItracker.calibrate: validation was succesful")

				# present instructions
				self.disp.fill() # clear display
				self.screen.draw_text(text="Noise calibration: please look at the dot\n\n(press space to start)", pos=(self.dispsize[0]/2, int(self.dispsize[1]*0.2)), center=True)
				self.screen.draw_fixation(fixtype='dot')
				self.disp.fill(self.screen)
				self.disp.show()
				self.screen.clear() # clear screen again

				# wait for spacepress
				self.kb.get_key(keylist=['space'], timeout=None)

				# show fixation
				self.disp.fill()
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

				# calculate pixels per cm
				pixpercm = (self.dispsize[0]/float(self.screensize[0]) + self.dispsize[1]/float(self.screensize[1])) / 2
				# get accuracy
				res = 0; i = 0
				while res != 1 and i < self.maxtries: # multiple tries, in case no (valid) sample is available
					res = iViewXAPI.iV_GetAccuracy(byref(accuracyData),0) # 0 is for 'no visualization'
					i += 1
					libtime.pause(int(self.sampletime)) # wait for sampletime
				if res == 1:
					self.accuracy = ((accuracyData.deviationLX,accuracyData.deviationLY), (accuracyData.deviationLX,accuracyData.deviationLY)) # dsttresh = (left tuple, right tuple); tuple = (horizontal deviation, vertical deviation) in degrees of visual angle
				else:
					err = errorstring(res)
					print("WARNING libsmi.SMItracker.calibrate: failed to obtain accuracy data; %s" % err)
					self.accuracy = ((2,2),(2,2))
					print("libsmi.SMItracker.calibrate: As an estimate, the intersample distance threshhold was set to it's default value of 2 degrees")
				# get distance from screen to eyes (information from tracker)
				res = 0; i = 0
				while res != 1 and i < self.maxtries: # multiple tries, in case no (valid) sample is available
					res = iViewXAPI.iV_GetSample(byref(sampleData))
					i += 1
					libtime.pause(int(self.sampletime)) # wait for sampletime
				if res == 1:
					screendist = sampleData.leftEye.eyePositionZ / 10.0 # eyePositionZ is in mm; screendist is in cm
				else:
					err = errorstring(res)
					print("WARNING libsmi.SMItracker.calibrate: failed to obtain screen distance; %s" % err)
					screendist = SCREENDIST
					print("libsmi.SMItracker.calibrate: As an estimate, the screendistance was set to it's default value of 57 cm")
				# calculate thresholds based on tracker settings
				self.pxerrdist = deg2pix(screendist, self.errdist, pixpercm)
				self.pxfixtresh = deg2pix(screendist, self.fixtresh, pixpercm)
				self.pxaccuracy = ((deg2pix(screendist, self.accuracy[0][0], pixpercm),deg2pix(screendist, self.accuracy[0][1], pixpercm)), (deg2pix(screendist, self.accuracy[1][0], pixpercm),deg2pix(screendist, self.accuracy[1][1], pixpercm)))
				self.pxspdtresh = deg2pix(screendist, self.spdtresh/float(self.samplerate), pixpercm) # in pixels per sample
				self.pxacctresh = deg2pix(screendist, self.accthresh/float(self.samplerate**2), pixpercm) # in pixels per sample**2

				# calibration report
				self.log("pygaze calibration report start")
				self.log("accuracy (degrees): LX=%s, LY=%s, RX=%s, RY=%s" % (self.accuracy[0][0],self.accuracy[0][1],self.accuracy[1][0],self.accuracy[1][1]))
				self.log("accuracy (in pixels): LX=%s, LY=%s, RX=%s, RY=%s" % (self.pxaccuracy[0][0],self.pxaccuracy[0][1],self.pxaccuracy[1][0],self.pxaccuracy[1][1]))
				self.log("precision (RMS noise in pixels): X=%s, Y=%s" % (self.pxdsttresh[0],self.pxdsttresh[1]))
				self.log("distance between participant and display: %s cm" % screendist)
				self.log("fixation threshold: %s pixels" % self.pxfixtresh)
				self.log("speed threshold: %s pixels/sample" % self.pxspdtresh)
				self.log("accuracy threshold: %s pixels/sample**2" % self.pxacctresh)
				self.log("pygaze calibration report end")

				return True

			# validation error
			else:
				print("WARNING libsmi.SMItracker.calibrate: validation was unsuccesful %s" % verr)
				return False

		# calibration error
		else:
			print("WARNING libsmi.SMItracker.calibrate: calibration was unsuccesful; %s" % cerr)
			return False


	def close(self):

		"""Neatly close connection to tracker
		
		arguments
		None
		
		returns
		Nothing	-- saves data and sets self.connected to False
		"""

		# save data
		res = iViewXAPI.iV_SaveData(str(self.outputfile), str(self.description), str(self.participant), 1)
		if res != 1:
			err = errorstring(res)
			raise Exception("Error in libsmi.SMItracker.close: failed to save data; %s" % err)

		# close connection
		iViewXAPI.iV_Disconnect()
		self.connected = False
		

	def connected(self):

		"""Checks if the tracker is connected
		
		arguments
		None
		
		returns
		connected	-- True if connection is established, False if not;
				   sets self.connected to the same value
		"""

		res = iViewXAPI.iV_IsConnected()

		if res == 1:
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

		"""Not supported for SMItracker (yet)"""

		print("function not supported yet")

	def log(self, msg):

		"""Writes a message to the log file
		
		arguments
		ms		-- a string to include in the log file
		
		returns
		Nothing	-- uses native log function of iViewX to include a line
				   in the log file
		"""

		res = iViewXAPI.iV_Log(c_char_p(msg))
		if res != 1:
			err = errorstring(res)
			print("WARNING libsmi.SMItracker.log: failed to log message '%s'; %s" % (msg,err))

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

		res = iViewXAPI.iV_Log(c_char_p(msg))
		if res != 1:
			err = errorstring(res)
			print("WARNING libsmi.SMItracker.log_var: failed to log variable '%s' with value '%s'; %s" % (var,val,err))

	def prepare_backdrop(self):

		"""Not supported for SMItracker (yet)"""

		print("function not supported yet")

	def prepare_drift_correction(self, pos):

		"""Not supported for SMItracker (yet)"""

		print("function not supported yet")

	def pupil_size(self):

		"""Return pupil size
		
		arguments
		None
		
		returns
		pupil size	-- returns pupil diameter for the eye that is currently
				   being tracked (as specified by self.eye_used) or None
				   when no data is obtainable
		"""

		res = iViewXAPI.iV_GetSample(byref(sampleData))

		if res == 1:
			if self.eye_used == self.left_eye:
				return sampleData.leftEye.diam
			elif self.eye_used == self.right_eye:
				return sampleData.rightEye.diam
		else:
			err = errorstring(res)
			print("WARNING libsmi.SMItracker.sample: failed to obtain sample; %s" % err)
			return None


	def sample(self):

		"""Returns newest available gaze position
		
		arguments
		None
		
		returns
		sample	-- an (x,y) tuple or a (-1,-1) on an error
		"""

		res = iViewXAPI.iV_GetSample(byref(sampleData))

		if self.eye_used == self.right_eye:
			newsample = sampleData.rightEye.gazeX, sampleData.rightEye.gazeY
		else:
			newsample = sampleData.leftEye.gazeX, sampleData.leftEye.gazeY

		if res == 1:
			self.prevsample = newsample[:]
			return newsample
		elif res == 2:
			return self.prevsample
		else:
			err = errorstring(res)
			print("WARNING libsmi.SMItracker.sample: failed to obtain sample; %s" % err)
			return (-1,-1)


	def send_command(self, cmd):

		"""Sends a command to the eye tracker
		
		arguments
		cmd		-- the command (a string value) to be sent to iViewX
		
		returns
		Nothing
		"""

		try:
			iViewXAPI.iV_SendCommand(c_char_p(cmd))
		except:
			raise Exception("Error in libsmi.SMItracker.send_command: failed to send remote command to iViewX (iV_SendCommand might be deprecated)")

	def set_backdrop(self):

		"""Not supported for SMItracker (yet)"""

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
		Nothing	-- sets self.recording to True when recording is
				   successfully started
		"""

		res = 0; i = 0
		while res != 1 and i < self.maxtries:
			res = iViewXAPI.iV_StartRecording()
			i += 1
		
		if res == 1:
			self.recording = True
		else:
			self.recording = False
			err = errorstring(res)
			raise Exception("Error in libsmi.SMItracker.start_recording: %s" % err)


	def status_msg(self, msg):

		"""Not supported for SMItracker (yet)"""

		print("function not supported yet")


	def stop_recording(self):

		"""Stop recording eye position
		
		arguments
		None
		
		returns
		Nothing	-- sets self.recording to False when recording is
				   successfully started
		"""

		res = 0; i = 0
		while res != 1 and i < self.maxtries:
			res = iViewXAPI.iV_StopRecording()
			i += 1
		
		if res == 1:
			self.recording = False
		else:
			self.recording = False
			err = errorstring(res)
			raise Exception("Error in libsmi.SMItracker.stop_recording: %s" % err)


	def wait_for_blink_end(self):

		"""Not supported for SMItracker (yet)"""

		print("function not supported yet")

	def wait_for_blink_start(self):

		"""Not supported for SMItracker (yet)"""

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
		while sum(newpos) < 1:
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

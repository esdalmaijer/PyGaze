## This file is part of the Gaze Contingent Extension for Python
##
##    PyGACE is a Python module for easily creating gaze contingent experiments
##    or other software (as well as non-gaze contingent experiments/software)
##    Copyright (C) 2012-2013  Edwin S. Dalmaijer
##
##    This program is free software: you can redistribute it and/or modify
##    it under the terms of the GNU General Public License as published by
##    the Free Software Foundation, either version 3 of the License, or
##    (at your option) any later version.
##
##    This program is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.
##
##    You should have received a copy of the GNU General Public License
##    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
# version: 0.3 (20-03-2013), NOT RELEASED FOR USE OUTSIDE OF UTRECHT UNIVERSITY)
#
#
# Many thanks to Sebastiaan Mathot. libsmi is a slightly modified version of
# libsmi.py, an optional plugin for the OpenSesame experiment builder
# (see: www.cogsci.nl/opensesame).
# OpenSesame is free software, redistributable under the terms of the GNU Public
# License as published by the Free Software Foundation.

try:
    import constants
except:
    import defaults as constants

import libtime
import libscreen
from libinput import Mouse
from libinput import Keyboard
from libsound import Sound

import time
import serial
import pygame


class libsmi:

	"""Object for communicating with a SMI eyetracker"""

	def __init__(self, port='COM1', baudrate=115200, sound=True):
	
		"""Initializes the SMI tracker class"""
	
		self.tracker = serial.Serial(port=port, baudrate=baudrate, timeout=0.5)		
		self.my_keyboard = Keyboard()
		self.screen = libscreen.create_display()
		self.streaming = False
		self.sound = sound
		if self.sound:
			self.beep1 = Sound(osc='sine', freq=220, length=100, attack=0, decay=5, soundfile=None)
			self.beep1.set_volume(0.5)
			self.beep2 = Sound(osc='sine', freq=440, length=200, attack=0, decay=5, soundfile=None)
			self.beep2.set_volume(0.5)
		self.stop_recording()
		
		
	def send(self, msg, sleep=10):
	
		"""Send a message (msg) to the tracker, then sleep for a value in milliseconds (to prevent overflowing, default=10)"""
		
		# The message needs to be end with a tab-linefeed
		self.tracker.write('%s\t\n' % msg)
		self.experiment.sleep(sleep)

		
	def recv(self):
	
		"""Returns a message from the tracker (tab-linefeed is stripped of)"""
		
		# Receive a line from the tracker
		s = ''
		while True:
			c = self.tracker.read(size=1)		
			if c == None:
				print("Error in libsmi.libsmi.recv(): The tracker said '%s'" % s)
			if c == '\n':
				if len(s) > 1:
					break
				else:
					s = ''
					continue
			s += c
		return s[:-1] # Strip off the tab and return

				
	def calibrate(self, nr_of_pts=9):
	
		"""Performs calibration with given number of points (default=9)"""
		
		h = constants.SIZE[1]
		w = constants.SIZE[0]
		m = 0.05 * w
		
		# ET_CPA [command] [enable]
		self.send('ET_CPA 0 1') # Enable wait for valid data
		self.send('ET_CPA 1 1') # Enable randomize point order
		self.send('ET_CPA 2 1') # Enable auto accept

		# ET_LEV [calibration level]
		self.send('ET_LEV 2') # Set to medium

		# ET_CSZ [xres] [yres]
		self.send('ET_CSZ %d %d' % (w, h)) # Set the screen resolution

		# Start the calibration with default calibration points
		self.send('ET_DEF')
		self.send('ET_CAL %d' % nr_of_pts)
		
		pts = {}
		while True:

			# Poll the keyboard to capture escape pressed
			self.my_keyboard.get_key(timeout=0)

			# Receive a line from the tracker and split it
			s = self.recv()
			cmd = s.split()

			# Ignore empty commands	
			if len(cmd) == 0:
				continue
	
			# Change thc coordinates of the calibration points
			if cmd[0] == 'ET_PNT':
				pt_nr = int(cmd[1])
				x = int(cmd[2])
				y = int(cmd[3])
				pts[pt_nr-1] = x, y
	
			# Indicates that the calibration point has been changed
			elif cmd[0] == 'ET_CHG':				
				pt_nr = int(cmd[1])
				if pt_nr-1 not in pts:
					print("Error in libsmi.libsmi.calibrate(): Something went wrong during the calibration. Please try again.")
				x, y = pts[pt_nr-1]
				self.screen.fill(constants.BGC)
				pygame.draw.circle(screen, constants.FGC, (x, y), 5, 0)
				libscreen.show_display()
				if self.sound:
					self.beep1.play()
		
			# Indicates that the calibration was successful
			elif cmd[0] == 'ET_FIN':
				break
		
		# Initially recording is off
		self.stop_recording()
		
		if self.sound:
			self.beep2.play()


	def drift_check(self, display, x=constants.SIZE[0]/2, y=constants.SIZE[1]/2, samples=10, maxerror=75):

                """Performs custom drift check at position (x,y), continues after fixation has been kept over given samples (within given maxerror in pixels)"""

                # create drift check surface
                display = libscreen.drift_check(x,y)
                # show drift check surface
                libscreen.show_display()

                # wait until participant fixates
                dcrun = 0
                while dcrun < samples:
                        gazepos = self.sample(clear=True)
                        # when eye is not sampled
                        if gazepos[0] == 0 or gazepos[1] == 0:
                                dcrun = 0
                        # calculate distance from point (x,y)
                        dist = ((gazepos[0]-x)**2 + (gazepos[1]-y)**2) ** 0.5 # Pythagoras
                        # your fixation is bad and you should feel bad!
                        if dist > maxerror:
                                dcrun = 0
                        # fixation is within maxerror
                        else:
                                dcrun += 1

	
	def save_data(self, path=None):
	
		"""Save the SMI datafile to disk with given name (path)"""
		
		if path == None:
			path = constants.LOGFILE + time.strftime('_%m_%d_%Y_%H_%M') + '.idf'
		self.send('ET_SAV "%s"' % path) 

				
	def start_recording(self, stream=True):
	
		"""Start recording (if stream=True, samples are streamed so they can be accessed using the sample() function)"""
		
		# Clear the tracker buffer and start recording
		#self.send('ET_CLR')
		self.send('ET_REC')

		if stream:
			self.streaming = True
			self.send('ET_FRM "%SX %SY"')
			self.send('ET_STR')
		else:
			self.streaming = False


	def stop_recording(self):
	
		"""Stop recording"""
	
		if self.streaming:
			self.send('ET_EST')
		self.send('ET_STP')
		self.streaming = False


	def clear(self):
	
		"""Clear the input buffer"""
		
		self.tracker.flushInput()


	def sample(self, clear=False):
	
		"""Returns an (x,y) tuple of the current gaze position from the tracker (clear determines if the input buffer should be flushed). If binocular recording is enabled, return the left eye."""
		
		if not self.streaming:
			print("Error in libsmi.libsmi.sample(): Please set stream=True in start_recording() before using sample()")
			
		if clear:
			self.tracker.flushInput()
		
		while True:
			s = self.recv()
			l = s.split()
			if len(l) > 0 and l[0] == 'ET_SPL':
				try:
					x = int(l[1])
					if len(l) == 5:
						y = int(l[3]) # Binocular
					else:
						y = int(l[2]) # One eye
					break
				except:
					pass
				
		return x, y


	def log(self, msg):
	
		"""Write message (or remark) to the SMI logfile"""
		
		self.send('ET_REM "%s"' % msg)


	def cleanup(self):
	
		"""Neatly close the tracker"""
	
		self.tracker.close()

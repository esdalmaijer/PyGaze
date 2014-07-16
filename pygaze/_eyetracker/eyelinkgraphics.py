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
	
import pygaze
from pygaze.screen import Screen
from pygaze.mouse import Mouse
from pygaze.keyboard import Keyboard
from pygaze.sound import Sound

import os
import platform
import array
from PIL import Image

import pylink
custom_display = pylink.EyeLinkCustomDisplay

if DISPTYPE == 'pygame':
	import pygame
elif DISPTYPE == 'psychopy':
	import psychopy
import pygame

class EyelinkGraphics(custom_display):

	"""
	Implements the EyeLink graphics that are shown on the experimental PC, such
	as the camera image, and the calibration dots. This class only implements
	the drawing operations, and little to no of the logic behind the set-up,
	which is implemented in PyLink.
	"""

	def __init__(self, display, fontsize, tracker):

		"""
		Constructor.

		Arguments:
		display		--	A PyGaze Display object.
		fontsize	--	The font size for the text messages.
		tracker		--	An tracker object as returned by pylink.EyeLink().
		"""

		pylink.EyeLinkCustomDisplay.__init__(self)

		# objects
		self.display = display
		self.screen = Screen(disptype=DISPTYPE, mousevisible=False)
		self.kb = Keyboard(keylist=None, timeout=1)
		if DISPTYPE == 'pygame':
			self.kb.set_timeout(timeout=0.001)
		# If we are using a DISPTYPE that cannot be used directly, we have to
		# save the camera image to a temporary file on each frame.
		#if DISPTYPE not in ('pygame', 'psychopy'):
		import tempfile
		import os
		self.tmp_file = os.path.join(tempfile.gettempdir(), '__eyelink__.jpg')
		# drawing properties
		self.xc = self.display.dispsize[0]/2
		self.yc = self.display.dispsize[1]/2
		self.extra_info = False
		self.ld = 40 # line distance
		self.fontsize = fontsize
		self.title = ""
		self.display_open = True
		# menu
		self.menuscreen = Screen(disptype=DISPTYPE, mousevisible=False)		
		self.menuscreen.draw_text(text="Eyelink calibration menu",
			pos=(self.xc,self.yc-6*self.ld), center=True, font='mono',
			fontsize=int(2*self.fontsize), antialias=True)
		self.menuscreen.draw_text(text="pygaze %s, pylink %s" % (pygaze.version,
			pylink.__version__), pos=(self.xc,self.yc-5*self.ld), center=True,
			font='mono', fontsize=int(.8*self.fontsize), antialias=True)
		self.menuscreen.draw_text(text="Press C to calibrate", 
			pos=(self.xc, self.yc-3*self.ld), center=True, font='mono',
			fontsize=self.fontsize, antialias=True)
		self.menuscreen.draw_text(text="Press V to validate",
			pos=(self.xc, self.yc-2*self.ld), center=True, font='mono',
			fontsize=self.fontsize, antialias=True)
		self.menuscreen.draw_text(text="Press A to auto-threshold",
			pos=(self.xc,self.yc-1*self.ld), center=True, font='mono',
			fontsize=self.fontsize, antialias=True)
		self.menuscreen.draw_text(text="Press I for extra info in camera image",
			pos=(self.xc,self.yc-0*self.ld), center=True, font='mono',
			fontsize=self.fontsize, antialias=True)
		self.menuscreen.draw_text(text="Press Enter to show camera image",
			pos=(self.xc,self.yc+1*self.ld), center=True, font='mono',
			fontsize=self.fontsize, antialias=True)
		self.menuscreen.draw_text(
			text="(then change between images using the arrow keys)",
			pos=(self.xc, self.yc+2*self.ld), center=True, font='mono',
			fontsize=self.fontsize, antialias=True)
		self.menuscreen.draw_text(text="Press Escape to abort experiment",
			pos=(self.xc, self.yc+4*self.ld), center=True, font='mono',
			fontsize=self.fontsize, antialias=True)			
		self.menuscreen.draw_text(text="Press Q to exit menu",
			pos=(self.xc, self.yc+5*self.ld), center=True, font='mono',
			fontsize=self.fontsize, antialias=True)
		# beeps
		self.__target_beep__ = Sound(osc='sine', freq=440, length=50, 
			attack=0, decay=0, soundfile=None)
		self.__target_beep__done__ = Sound(osc='sine', freq=880, length=200,
			attack=0, decay=0, soundfile=None)
		self.__target_beep__error__ = Sound(osc='sine', freq=220, length=200,
			attack=0, decay=0, soundfile=None)
		# further properties
		self.state = None
		self.pal = None
		self.size = (0,0)
		self.set_tracker(tracker)
		self.last_mouse_state = -1
		self.bit64 = '64bit' in platform.architecture()
		self.imagebuffer = self.new_array()		
		
	def close(self):
	
		"""
		Is called when the connection and display are shutting down.		
		"""
		
		self.display_open = False
		
	def new_array(self):
	
		"""
		Creates a new array with a system-specific format.
		
		Returns:
		An array.
		"""
		
		# On 64 bit Linux, we need to use an unsigned int data format.
		# <https://www.sr-support.com/showthread.php?3215-Visual-glitch-when-/
		# sending-eye-image-to-display-PC&highlight=ubuntu+pylink>
		if os.name == 'posix' and self.bit64:
			return array.array('I')
		return array.array('L')

	def set_tracker(self, tracker):

		"""
		Connects the tracker to the graphics environment.

		Arguments:
		tracker		--	An tracker object as returned by pylink.EyeLink().
		"""

		self.tracker = tracker
		self.tracker_version = tracker.getTrackerVersion()
		if self.tracker_version >= 3:
			self.tracker.sendCommand("enable_search_limits=YES")
			self.tracker.sendCommand("track_search_limits=YES")
			self.tracker.sendCommand("autothreshold_click=YES")
			self.tracker.sendCommand("autothreshold_repeat=YES")
			self.tracker.sendCommand("enable_camera_position_detect=YES")

	def setup_cal_display(self):

		"""
		Sets up the initial calibration display, which contains a menu with
		instructions.
		"""
		
		# show instructions
		self.display.fill(self.menuscreen)
		self.display.show()

	def exit_cal_display(self):

		"""Exits calibration display."""

		self.clear_cal_display()

	def record_abort_hide(self):

		"""TODO: What does this do?"""

		pass

	def clear_cal_display(self):

		"""Clears the calibration display"""

		self.display.fill()
		self.display.show()

	def erase_cal_target(self):

		"""TODO: What does this do?"""

		self.clear_cal_display()

	def draw_cal_target(self, x, y):

		"""
		Draws calibration target.

		Arguments:
		x		--	The X coordinate of the target.
		y		--	The Y coordinate of the target.
		"""

		self.play_beep(pylink.CAL_TARG_BEEP)
		self.screen.clear()		
		self.screen.draw_fixation(fixtype='dot', pos=(x,y))
		self.display.fill(screen=self.screen)
		self.display.show()

	def play_beep(self, beepid):

		"""
		Plays a sound.

		Arguments:
		beepid		--	A number that identifies the sound.
		"""

		if beepid == pylink.CAL_TARG_BEEP:
			# For some reason, playing the beep here doesn't work, so we have
			# to play it when the calibration target is drawn.
			if EYELINKCALBEEP:
				self.__target_beep__.play()			
		elif beepid == pylink.CAL_ERR_BEEP or beepid == pylink.DC_ERR_BEEP:
			# show a picture
			self.screen.clear()
			self.screen.draw_text(
				text="calibration lost, press 'q' to return to menu",
				pos=(self.xc,self.yc), center=True, font='mono',
				fontsize=self.fontsize, antialias=True)
			self.display.fill(self.screen)
			self.display.show()
			# play beep
			self.__target_beep__error__.play()
		elif beepid == pylink.CAL_GOOD_BEEP:
			self.screen.clear()
			if self.state == "calibration":
				self.screen.draw_text(
					text="Calibration succesfull, press 'v' to validate",
					pos=(self.xc,self.yc), center=True, font='mono',
					fontsize=self.fontsize, antialias=True)
			elif self.state == "validation":
				self.screen.draw_text(
					text="Validation succesfull, press 'q' to return to menu",
					pos=(self.xc,self.yc), center=True, font='mono',
					fontsize=self.fontsize, antialias=True)				
			else:
				self.screen.draw_text(text="Press 'q' to return to menu",
					pos=(self.xc,self.yc), center=True, font='mono',
					fontsize=self.fontsize, antialias=True)
			# show screen
			self.display.fill(self.screen)
			self.display.show()
			# play beep
			self.__target_beep__done__.play()
		else: #	DC_GOOD_BEEP	or DC_TARG_BEEP
			pass

	def getColorFromIndex(self, i):

		"""
		Maps a PyLink color code onto a color-name string.

		Arguments:
		i		--	A PyLink color code.

		Returns:
		A color-name string.
		"""

		# Currently unused
		return 0

	def draw_line(self, x1, y1, x2, y2, colorindex):

		"""
		Unlike the function name suggests, this draws a single pixel. I.e.
		the end coordinates are always exactly one pixel away from the start
		coordinates.
		
		Arguments:
		x1			--	The starting x.
		y1			--	The starting y.
		x2			--	The end x.
		y2			--	The end y.
		colorIndex	--	A color index.
		"""
	
		i = y1*self.size[0]+x1
		if i > 0 and i < len(self.imagebuffer):
			# Use green
			self.imagebuffer[i] = 65280
		
	def draw_lozenge(self, x, y, width, height, colorindex):

		"""Unused"""

		# According to the Pylink documentation (pylink.csm), this function
		# is currently unused.
		pass

	def get_mouse_state(self):

		"""Unused"""

		pass

	def get_input_key(self):

		"""
		Gets an input key.

		Returns:
		A list containing a single pylink key identifier.
		"""

		# Don't try to collect key presses when the display is no longer
		# available. This is necessary, because pylink polls key presses during
		# file transfer, which generally occurs after the display has been
		# closed.
		if not self.display_open:
			return None
		try:
			key, time = self.kb.get_key(keylist=None, timeout='default')
		except:
			self.esc_pressed = True
			key = 'q'
		if key == None:
			return None
		# Escape functions as a 'q' with the additional esc_pressed flag
		if key == 'escape':
			key = 'q'
			self.esc_pressed = True
		# Process regular keys
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
		elif key == "i":
			self.extra_info = not self.extra_info
			keycode = 0
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
		# Convert key to PyLink keycode and return
		return [pylink.KeyInput(keycode, 0)] # 0 = pygame.KMOD_NONE

	def exit_image_display(self):

		"""Exits the image display."""

		self.clear_cal_display()

	def alert_printf(self,msg):

		"""
		Prints alert message.

		Arguments:
		msg		--	The message to be played.
		"""

		print "eyelink_graphics.alert_printf(): %s" % msg

	def setup_image_display(self, width, height):

		"""
		Initializes the buffer that will contain the camera image.

		Arguments:
		width		--	The width of the image.
		height		--	The height of the image.
		"""

		self.size = (width,height)
		self.clear_cal_display()
		self.last_mouse_state = -1
		self.imagebuffer = self.new_array()

	def image_title(self, text):

		"""
		Sets the current image title.

		Arguments:
		text	--	An image title.
		"""

		self.title = text
		
	def draw_image_line(self, width, line, totlines, buff):

		"""
		Draws a single eye video frame, line by line.

		Arguments:

		width		--	Width of the video.
		line		--	Line nr of current line.
		totlines	--	Total lines in video.
		buff		--	Frame buffer.
		imagesize	--	The size of the image, which is (usually?) 192x160 px.
		"""

		# If the buffer hasn't been filled yet, add a line.
		for i in range(width):
			try:
				self.imagebuffer.append(self.pal[buff[i]])
			except:
				pass
		# If the buffer is full, push it to the display.
		if line == totlines:
			if self.extra_info:
				self.draw_cross_hair()			
			# Convert the image buffer to a pygame image, save it ...			
			img = pygame.image.fromstring(self.imagebuffer.tostring(),
				self.size, 'RGBX')
			pygame.image.save(img, self.tmp_file)
			# ... and then show the image.
			self.screen.clear()
			self.screen.draw_image(self.tmp_file, scale=2)
			if self.extra_info:
				self.screen.draw_text(text=self.title,
					pos=(self.xc, 2*self.fontsize), fontsize=self.fontsize,
					colour='#729fcf')
			self.display.fill(self.screen)
			self.display.show()			
			# Clear the buffer for the next round!
			self.imagebuffer = self.new_array()

	def set_image_palette(self, r, g, b):

		"""
		Sets the image palette.

		TODO: What this function actually does is highly mysterious. Figure it
		out!

		Arguments:
		r		--	The red channel.
		g		--	The green channel.
		b		--	The blue channel.
		"""

		self.imagebuffer = self.new_array()
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



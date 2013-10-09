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


from pygaze.defaults import *
try:
	from constants import *
except:
	pass

import sys


# on Windows, PyGame's webcam support is a bit shaky, so we use vidcap
# project homepage: http://videocapture.sourceforge.net/
if sys.platform == 'win32':
	import vidcap
# for other platforms, we use PyGame
else:
	try:
		import pygame.image
		import pygame.camera
		pygame.camera.init()
	except:
		raise Exception("Error in libwebcam: could not import and initialize PyGame camera module!")

from PIL import Image


# # # # #
# functions

def available_devices():
	
	"""Returns a list of available devices; these names and/or numbers can
	be passed directly as the dev keyword argument of the Webcam class
	
	arguments
	None
	
	keyword arguments
	None
	
	returns
	devlist		--	a list of available device names and/or numbers,
					than can be used as the dev keyword argument for
					the Webcam class
	"""
	
	# Windows
	if sys.platform == 'win32':
		# loop through 100 numbers (0-99) and see if they work
		devlist = []
		for i in range(100):
			try:
				dev = vidcap.new_Dev(i, 0)
				devlist.append(i)
				del dev
			except:
				pass
		
	# other platforms
	else:
		devlist = pygame.camera.list_cameras()
	
	return devlist


# # # # #
# classes

class Camera:
	
	"""A class for communication with webcams, that uses vidcap on Windows
	and PyGame on all other platforms (even if DISPTYPE is set to
	'psychopy'!)"""
	
	def __init__(self, disptype=DISPTYPE, dev=None, resolution=(640,480), verflip=False, horflip=False):
		
		"""Initializes a Camera instance
		
		arguments
		None
		
		keyword arguments
		disptype		--	string indicating the display type: either
						'pygame' or 'psychopy' (default = DISPTYPE)
		dev			--	number or name of the webcam that should be
						accessed (e.g. 0 or '/dev/video0') or None
						to use the first available (default = None)
		resolution		--	preferred resolution of the webcam images
						(default = (640,480))
		verflip		--	Boolean indicating if images should be
						flipped vertically (default = False)
		horflip		--	Boolean indicating if images should be
						flipped horizontally (default = False)
		"""
		
		# properties
		self.disptype = disptype
		self.devname = dev
		self.camres = resolution
		self.horflip = horflip
		self.verflip = verflip
		self.flipnr = 0
		self.img = Image.new('RGB',self.camres,'black')
		
		# autodetect device
		if self.devname == None:
			try:
				self.devname = available_devices()[0]
			except:
				raise Exception("Error in libwebcam.Camera.__init__: no webcam devices available!")
		
		# check if device is available
		if not self.devname in available_devices():
			# if not, raise Exception
			raise Exception("Error in libwebcam.Camera.__init__: webcam %s is not available!" % self.devname)
		
		# create device
		if sys.platform == 'win32':
			# initialize camera device
			self.dev = vidcap.new_Dev(self.devname, 0) # first argument: devnr; second argument: Boolean indicating if camimages should be displayed on separate window (e.g. for debugging purposes)
			self.dev.setresolution(self.camres[0], self.camres[1])
#			# check if resolution is correct
#			buff, width, height = self.dev.getbuffer()
#			if not self.camres == (width,height):
#				print("WARNING in libwebcam.Camera.__init__: requested resolution %s is not available; device actual resolution of (%d,%d) will be used" % (self.camres,width,height))
#				self.camres = (width,height)
		else:
			self.dev = pygame.camera.Camera(self.devname, self.camres, 'RGB')
			self.dev.start()
		
		# set image flipping
		self.set_imgflip(verflip=self.verflip, horflip=self.horflip)
	
	
	def set_imgflip(self, verflip=False, horflip=False):
		
		"""Sets the vertical and horizontal flipping of webcam images
		(sometimes these come out upside down, or mirrored)
		
		arguments
		None
		
		keyword arguments
		verflip		--	Boolean indicating if images should be
						flipped vertically (default = False)
		horflip		--	Boolean indicating if images should be
						flipped horizontally (default = False)
		
		returns
		None			--	changes flipping, and sets self.verflip and
						self.horflip properties
		"""
		
		# set flipping properties
		self.verflip = verflip
		self.horflip = horflip
		
		# windows		
		if sys.platform == 'win32' or self.disptype == 'psychopy':
			if self.verflip:
				self.flipnr = -1 # or 1?
			if self.horflip:
				print("WARNING in libwebcam.Camera.set_imgflip: horizontal flipping not supported (yet)")
		
		# all other platforms
		else:
			try:
				self.dev.set_controls(self.horflip,self.verflip,self.dev.get_controls()[2])
			except:
				print("WARNING in libwebcam.Camera.set_imgflip: flipping not supported by the device")
	
	
	def get_image(self):
		
		"""Returns the most recent webcam image, which can be passed
		directly to libscreen.Screen.draw_image
		
		arguments
		None
		
		keyword arguments
		None
		
		returns
		image			--	an image that can be passed to a PyGaze
						Screen instance's draw_image metod directly
		"""
		
		# windows
		if sys.platform == 'win32':
			# read buffer
			buff, width, height = self.dev.getbuffer()
			# buffer to PIL Image
			self.img.fromstring(buff, 'raw', 'BGR', 0, self.flipnr) # buffer, decoder, funky image type, horflip?, verflip
			# if the display type is psychopy, we can return the PIL Image
			if self.disptype == 'psychopy':
				return self.img
			# if the disptype is pygame, we need to convert the PIL Image to a PyGame image
			else:
				return pygame.image.fromstring(self.img.tostring(), (width,height), 'RGB', False) # (string, size, format, flipped)
		
		# other platforms
		else:
			# get image
			img = self.dev.get_image()
			# if the display type is pygame, we can return the PyGame image
			if self.disptype == 'pygame':
				return img
			# if the disptype is psychopy, we need to convert the PyGame image to a PIL Image
			else:
				self.img.fromstring(pygame.image.tostring(img, 'RGB', False), 'raw', 'RGB', 0, self.flipnr)
				return self.img


	def close(self):
		
		"""Neatly closes the connection to the webcam
		
		arguments
		None
		
		keyword arguments
		None
		
		returns
		None
		"""
		
		if sys.platform != 'win32':
			self.dev.stop()
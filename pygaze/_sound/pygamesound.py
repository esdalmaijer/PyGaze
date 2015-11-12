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

from pygaze import settings
from pygaze._sound.basesound import BaseSound
# we try importing the copy_docstr function, but as we do not really need it
# for a proper functioning of the code, we simply ignore it when it fails to
# be imported correctly
try:
	from pygaze._misc.misc import copy_docstr
except:
	pass

import math
import numpy
import os.path
import pygame
import random

class PyGameSound(BaseSound):

	# see pygaze._sound.basesound.BaseSound

	def __init__(self, osc=settings.SOUNDOSCILLATOR,
		freq=settings.SOUNDFREQUENCY, length=settings.SOUNDLENGTH,
		attack=settings.SOUNDATTACK, decay=settings.SOUNDDECAY, soundfile=None):
		
		# see pygaze._sound.basesound.BaseSound

		# try to copy docstring (but ignore it if it fails, as we do
		# not need it for actual functioning of the code)
		try:
			copy_docstr(BaseSound, PyGameSound)
		except:
			# we're not even going to show a warning, since the copied
			# docstring is useful for code editors; these load the docs
			# in a non-verbose manner, so warning messages would be lost
			pass

		pygame.mixer.init(frequency=settings.SOUNDSAMPLINGFREQUENCY,
			size=settings.SOUNDSAMPLESIZE, channels=settings.SOUNDCHANNELS,
			buffer=settings.SOUNDBUFFERSIZE)

		# if a sound file was specified, use soundfile and ignore other keyword arguments
		if soundfile != None:
			if not os.path.exists(soundfile):
				raise Exception("Error in libsound.Player.__init__(): Sound file %s not found!" % soundfile)
			if os.path.splitext(soundfile)[1].lower() not in (".ogg", ".wav"):
				raise Exception("Error in libsound.Player.__init__(): Sound file %s is not in .ogg or .wav format!" % soundfile)

			self.sound = pygame.mixer.Sound(soundfile)

		# if no soundfile was specified, use keyword arguments to create sound
		else:
			if osc == 'sine':
				_func = math.sin
			elif osc == 'saw':
				_func = self.saw
			elif osc == 'square':
				_func = self.square
			elif osc == 'whitenoise':
				_func = self.white_noise
			else:
				raise Exception("Error in libsound.Sound.__init__(): oscillator %s could not be recognized; oscillator is set to 'sine'." % osc)

			l = []

			attack = attack * settings.SOUNDSAMPLINGFREQUENCY / 1000
			decay = decay * settings.SOUNDSAMPLINGFREQUENCY / 1000
			amp = 32767 / 2
			sps = settings.SOUNDSAMPLINGFREQUENCY
			cps = float(sps/freq) # cycles per sample
			slen = settings.SOUNDSAMPLINGFREQUENCY * length / 1000 # number of samples

			for i in range(slen):
				p = float((i % cps)) / cps * 2 * math.pi
				v = int(amp * (_func(p)))
				if i < attack:
					v = int(v * float(i) / attack)
				if i > slen - decay:
					v = int(v * (float(slen) - float(i)) / decay)
				l.append(v)
				l.append(v)

			b = numpy.array(l, dtype="int16").reshape(len(l) / 2, 2)

			self.sound = pygame.mixer.Sound(b)


	def saw(self, phase):

		"""
		Returns a point in a saw wave (for internal use)
		
		arguments
		
		phase		--	phase of the wave
		
		keyword arguments
		
		None
		
		returns
		
		p		--	point in a saw wave
		"""

		phase = phase % math.pi

		return float(phase) / (0.5 * math.pi) - 1.0


	def square(self, phase):

		"""
		Returns a point in a square wave (for internal use)
		
		arguments
		
		phase		--	phase of the wave
		
		keyword arguments
		
		None
		
		returns
		p		--	point in a square wave
		"""

		if phase < math.pi:
			return 1
		return -1


	def white_noise(self, phase):

		"""
		Returns a point in random noise (for internal use)
		
		arguments
		
		phase		--	phase of the sound (ignored, but necessary for
					internal reasons; see __init__)
		
		keyword arguments
		
		None
		
		returns
		
		p		--	random number (i.e. a point in white noise sound)
		"""

		return random.random()


	def pan(self, panning):

		# see pygaze._sound.basesound.BaseSound

		# raise exception on wrong input
		if type(panning) not in (int, float) and panning not in ['left','right']:
			raise Exception("Error in libsound.Sound.pan(): panning must be a value between -1.0 and 1.0 or either 'left' or 'right'.")

		# correct wrong inputs
		if panning < -1:
			panning = -1
		elif panning > 1:
			panning = 1
		
		# round off, to prevent too long numbers
		panning = numpy.round(panning, decimals=8)
		

		buf = pygame.sndarray.array(self.sound)

		for i in range(len(buf)):

			l = buf[i][0]
			r = buf[i][1]

			if panning == 'left':
				r = 0
			elif panning == 'right':
				l = 0
			elif panning < 0:
				r = int(float(r) / abs(panning))
			elif panning > 0:
				l = int(float(l) / abs(panning))

			buf[i][0] = l
			buf[i][1] = r

		self.sound = pygame.sndarray.make_sound(numpy.array(buf))


	def play(self, repeats=0):

		# see pygaze._sound.basesound.BaseSound

		self.sound.play(loops=repeats)


	def stop(self):

		# see pygaze._sound.basesound.BaseSound

		self.sound.stop()


	def set_volume(self, volume):

		# see pygaze._sound.basesound.BaseSound

		if volume <= 1.0 and volume >= 0.0:
			self.sound.set_volume(volume)
		else:
			raise Exception("Error in libsound.Sound.set_volume(): Volume must be a value between 0.0 and 1.0.")

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
#
#
# Many thanks to Sebastiaan Mathot. libsound is a slightly modified version of
# the synth item, from the openexp part of the OpenSesame experiment builder
# (see: www.cogsci.nl/opensesame).
# OpenSesame is free software, redistributable under the terms of the GNU Public
# License as published by the Free Software Foundation.

from defaults import *
try:
	from constants import *
except:
	pass

import math
import numpy
import os.path
import pygame
import random

class Sound:

	"""Sound object"""

	def __init__(self, osc=SOUNDOSCILLATOR, freq=SOUNDFREQUENCY, length=SOUNDLENGTH, attack=SOUNDATTACK, decay=SOUNDDECAY, soundfile=None):
		
		"""Initializes a sound object
		
		arguments
		None
		
		keyword arguments
		osc		-- type of oscillator; allowed: 'sine', 'saw', 'square',
				   'whitenoise' (default = SOUNDOSCILLATOR)
		freq		-- sound frequency in Herz, either float or integer
				   (default = SOUNDFREQUENCY)
		length	-- sound length in milliseconds (default = 
				   SOUNDLENGTH)
		attack	-- sound attack ('fade in') in milliseconds (default = 
				   SOUNDATTACK)
		decay		-- sound decay ('fade out') in milliseconds (default =
				   SOUNDDECAY)
		soundfile	-- full path to soundfile with .ogg or .wav extension
				   or None for no file; if a file is specified, all
				   other keyword arguments will be ignored (default =
				   None)
		"""

		pygame.mixer.init(frequency=SOUNDSAMPLINGFREQUENCY, size=SOUNDSAMPLESIZE, channels=SOUNDCHANNELS, buffer=SOUNDBUFFERSIZE)

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

			attack = attack * SOUNDSAMPLINGFREQUENCY / 1000
			decay = decay * SOUNDSAMPLINGFREQUENCY / 1000
			amp = 32767 / 2
			sps = SOUNDSAMPLINGFREQUENCY
			cps = float(sps/freq) # cycles per sample
			slen = SOUNDSAMPLINGFREQUENCY * length / 1000 # number of samples

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

		"""Returns a point in a saw wave (for internal use)
		
		arguments
		phase		-- phase of the wave
		
		returns
		p		-- point in a saw wave
		"""

		phase = phase % math.pi

		return float(phase) / (0.5 * math.pi) - 1.0


	def square(self, phase):

		"""Returns a point in a square wave (for internal use)
		
		arguments
		phase		-- phase of the wave
		
		returns
		p		-- point in a square wave
		"""

		if phase < math.pi:
			return 1
		return -1


	def white_noise(self, phase):

		"""Returns a point in random noise (for internal use)
		
		arguments
		phase		-- phase of the sound (ignored, but necessary for
				   internal reasons; see __init__)
		
		returns
		p		-- random number (i.e. a point in white noise sound)
		"""

		return random.random()


	def pan(self, panning):

		"""Sets the panning of a sound (the volume of the 'unpanned'
		channel decreases, while the other channel remaines the same)
		
		arguments
		panning	-- either a float between -1 and 1, 'left' or 'right':
				   'left':	full panning to left (same as -1)
				   < 0: 	panning to left
				   0:		no panning
				   > 0:	panning to right
				   'right':	full panning to left (same as 1)
		
		returns
		None		-- self.sound is panned
		"""

		if type(panning) not in (int, float) and panning not in ['left','right']:
			raise Exception("Error in libsound.Sound.pan(): panning must be a value between 0.0 and 1.0 or either 'left' or 'right'.")

		if panning == 0:
			return

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

		"""Plays specified sound (keyword argument loops specifies how many
		repeats after being played once, -1 is infinite); function does not
		wait for playback end, but returns immediately
		
		arguments
		None
		
		keyword arguments
		repeats	-- specifies the amount of repeats after being played
				   once (-1 is infinite) (default = 0)
		
		returns
		None		-- self.sound is played"""

		self.sound.play(loops=repeats)


	def stop(self):

		"""Stops sound playback
		
		arguments
		None
		
		returns
		None		-- self.sound stops playing"""

		self.sound.stop()


	def set_volume(self, volume):

		"""Set the playback volume (loudness) to specified value
		
		arguments
		volume	-- float between 0 and 1
		
		returns
		None		-- sets self.sound volume to specified value
		"""

		if volume <= 1.0 and volume >= 0.0:
			self.sound.set_volume(volume)
		else:
			raise Exception("Error in libsound.Sound.set_volume(): Volume must be a value between 0.0 and 1.0.")

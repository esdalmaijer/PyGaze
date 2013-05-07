## This file is part of PyGaze - the open-source toolbox for eye tracking
##
##    PyGaze is a Python module for easily creating gaze contingent experiments
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
# version: 0.4 (25-03-2013)
#
#
# Many thanks to Sebastiaan Mathot. libsound is a slightly modified version of
# the synth item, from the openexp part of the OpenSesame experiment builder
# (see: www.cogsci.nl/opensesame).
# OpenSesame is free software, redistributable under the terms of the GNU Public
# License as published by the Free Software Foundation.

try:
    import constants
except:
    import defaults as constants

import math
import numpy
import os.path
import pygame
import random

class Sound:

    """Sound object"""

    def __init__(self, osc=constants.SOUNDOSCILLATOR, freq=constants.SOUNDFREQUENCY, length=constants.SOUNDLENGTH, attack=constants.SOUNDATTACK, decay=constants.SOUNDDECAY, soundfile=None):

        pygame.mixer.init(frequency=constants.SOUNDSAMPLINGFREQUENCY, size=constants.SOUNDSAMPLESIZE, channels=constants.SOUNDCHANNELS, buffer=constants.SOUNDBUFFERSIZE)

        # if a sound file was specified, use soundfile and ignore other keyword arguments
        if soundfile != None:
            if not os.path.exists(soundfile):
                print("Error in libsound.Player.__init__(): Sound file not found!")
            if os.path.splitext(soundfile)[1].lower() not in (".ogg", ".wav"):
                print("Error in libsound.Player.__init__(): Sound file is not in .ogg or .wav format!")

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
                _func = math.sin
                print("Error in libsound.Sound.__init__(): Oscillator could not be recognized; oscillator is set to 'sine'.")

            l = []

            attack = attack * constants.SOUNDSAMPLINGFREQUENCY / 1000
            decay = decay * constants.SOUNDSAMPLINGFREQUENCY / 1000
            amp = 32767 / 2
            sps = constants.SOUNDSAMPLINGFREQUENCY
            cps = float(sps/freq) # cycles per sample
            slen = constants.SOUNDSAMPLINGFREQUENCY * length / 1000 # number of samples

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

        """For internal use!"""

        phase = phase % math.pi

        return float(phase) / (0.5 * math.pi) - 1.0


    def square(self, phase):

        """For internal use!"""

        if phase < math.pi:
            return 1
        return -1


    def white_noise(self, phase):

        """For internal use!"""

        return random.random()


    def pan(self, panning):

        """Sets the panning of a sound: panning < 0 or 'left' = to left; panning > 0 or 'right' = to right (the volume of the 'unpanned' channel decreases, while the other channel remaines the same)"""

        if type(panning) not in (int, float) and panning not in ['left','right']:
            print("Error in libsound.Sound.pan(): panning must be a value between 0.0 and 1.0 or either 'left' or 'right'.")
            return

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

        """Plays specified sound (keyword argument loops specifies how many repeats after being played once, -1 is infinite)"""

        self.sound.play(loops=repeats)


    def stop(self):

        """Stops sound playback"""

        self.sound.stop()


    def set_volume(self, volume):

        """Set the playback volume (loudness) to a value between 0.0 and 1.0"""

        if volume <= 1.0 and volume >= 0.0:
            self.sound.set_volume(volume)
        else:
            print("Error in libsound.Sound.set_volume(): Volume must be a value between 0.0 and 1.0.")

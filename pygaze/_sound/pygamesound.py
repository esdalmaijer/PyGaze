# -*- coding: utf-8 -*-
from pygaze.defaults import *
try:
    from constants import *
except Exception:
    pass

from pygaze._sound.basesound import BaseSound
# we try importing the copy_docstr function, but as we do not really need it
# for a proper functioning of the code, we simply ignore it when it fails to
# be imported correctly
try:
    from pygaze._misc.misc import copy_docstr
except Exception:
    pass

import math
import numpy
import os.path
import pygame
import random

class PyGameSound(BaseSound):

    # see pygaze._sound.basesound.BaseSound

    def __init__(self, osc=SOUNDOSCILLATOR, freq=SOUNDFREQUENCY, length=SOUNDLENGTH, attack=SOUNDATTACK, decay=SOUNDDECAY, soundfile=None):

        # see pygaze._sound.basesound.BaseSound

        # try to copy docstring (but ignore it if it fails, as we do
        # not need it for actual functioning of the code)
        try:
            copy_docstr(BaseSound, PyGameSound)
        except Exception:
            # we're not even going to show a warning, since the copied
            # docstring is useful for code editors; these load the docs
            # in a non-verbose manner, so warning messages would be lost
            pass

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

        """
        Returns a point in a saw wave (for internal use)

        arguments

        phase        --    phase of the wave

        keyword arguments

        None

        returns

        p        --    point in a saw wave
        """

        phase = phase % math.pi

        return float(phase) / (0.5 * math.pi) - 1.0


    def square(self, phase):

        """
        Returns a point in a square wave (for internal use)

        arguments

        phase        --    phase of the wave

        keyword arguments

        None

        returns
        p        --    point in a square wave
        """

        if phase < math.pi:
            return 1
        return -1


    def white_noise(self, phase):

        """
        Returns a point in random noise (for internal use)

        arguments

        phase        --    phase of the sound (ignored, but necessary for
                    internal reasons; see __init__)

        keyword arguments

        None

        returns

        p        --    random number (i.e. a point in white noise sound)
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

# -*- coding: utf-8 -*-
# The BaseClasses are meant to store the documentation on all methods of a
# class, but not to contain any functionality whatsoever. BaseClass is
# inherited by all of the subclasses, and the documentation is copied using
# pygaze.copy_docstr. If you intend to make your own subclass for the current
# baseclass, be sure to inherit BaseClass, copy the documentation, and
# redefine the methods as you see fit, e.g.:
#
#import pygaze
#from pygaze._display.basedisplay import BaseDisplay
#
#class DummyDisplay(BaseDisplay):
#
#    """An example child of BaseDisplay"""
#
#    def __init__(self, *args, **kwargs):
#
#        """Initializes a DummyDisplay instance"""
#
#        pygaze.copy_docstring(BaseDisplay,DummyDisplay)
#
#    def show(self):
#
#        # note that here no docstring is provided, as it is copied from
#        # the parent class
#
#        print("Display.show call at %d" % int(pygaze.clock.get_time()))
#


class BaseSound:

    """A Sound class for creating and playing sounds"""

    def __init__(self):

        """
        Initializes a Sound Instance

        arguments

        None

        keyword arguments

        osc        --    type of oscillator; allowed: 'sine', 'saw', 'square',
                    'whitenoise' (default = SOUNDOSCILLATOR)
        freq        --    sound frequency in Herz, either float or integer
                    (default = SOUNDFREQUENCY)
        length    --    sound length in milliseconds (default =
                    SOUNDLENGTH)
        attack    --    sound attack ('fade in') in milliseconds (default =
                    SOUNDATTACK)
        decay        --    sound decay ('fade out') in milliseconds (default =
                    SOUNDDECAY)
        soundfile    --    full path to soundfile with .ogg or .wav extension
                    or None for no file; if a file is specified, all
                    other keyword arguments will be ignored (default =
                    None)
        """

        pass


    def pan(self):

        """
        Sets the panning of a sound (the volume of the 'unpanned'
        channel decreases, while the other channel remaines the same)

        arguments

        panning    --    either a float between -1 and 1, 'left' or 'right':
                    'left':    full panning to left (same as -1)
                    < 0:     panning to left
                    0:        no panning
                    > 0:    panning to right
                    'right':    full panning to left (same as 1)

        keyword arguments

        None

        returns

        None        -- self.sound is panned
        """

        pass


    def play(self):

        """
        Plays specified sound (keyword argument loops specifies how many
        repeats after being played once, -1 is infinite); function does not
        wait for playback end, but returns immediately

        arguments

        None

        keyword arguments

        repeats    --    specifies the amount of repeats after being played
                    once (-1 is infinite) (default = 0)

        returns

        None        --    self.sound is played
        """

        pass


    def stop(self):

        """
        Stops sound playback

        arguments

        None

        keyword arguments

        None

        returns

        None        --    self.sound stops playing
        """

        pass


    def set_volume(self):

        """
        Set the playback volume (loudness) to specified value

        arguments

        volume    --    float between 0 and 1

        keyword arguments

        None

        returns

        None        --    sets self.sound volume to specified value
        """

        pass

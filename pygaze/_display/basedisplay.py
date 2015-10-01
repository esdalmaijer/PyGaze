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

class BaseDisplay(object):

    """A class for Display objects, to present Screen objects on a monitor"""

    def __init__(self):

        """
        Initializes a Display object.

        arguments

        None

        keyword arguments

        dispsize    --    size of the display in pixels: a (width, height)
                    tuple (default = DISPSIZE)
        fgc        --    the foreground colour: a RGB tuple, e.g. (255,0,0)
                    for red or (0,0,0) for black (default = FGC)
        bgc        --    the background colour: a RGB tuple, e.g. (0,0,255)
                    for blue or (255,255,255) for white (default = BGC)
        screen    --    a screen.Screen instance to be presented on the new
                    Display (default=None)
        """

        pass

    def show(self):

        """
        Updates ('flips') the display.

        arguments

        None

        keyword arguments

        None

        returns
        time        --    the exact refresh time when disptype is PsychoPy,
                    or an estimate when disptype is PyGame
        """

        pass

    def show_part(self, rect, screen=None):

        """
        Fills AND shows part(s) of the screen to given specified screen
        (only works when disptype is PyGame; when this is set to PsychoPy
        the entire display is filled and updated)

        arguments

        rect        --    a single or a list of rects; a rect is a (x,y,w,h)
                    tuple or list

        keyword arguments

        screen    --    the screen of which the specified rects should be
                    updated to the display (default = None)

        returns

        time        --    the exact refresh time when disptype is PsychoPy,
                    or an estimate when disptype is PyGame
        """

        pass

    def fill(self, screen=None):

        """
        Fills the screen with the background colour of the Screen, NOT
        updating it (call Display.show() to actually show the new contents)

        arguments

        None

        keyword arguments

        screen    --    the screen that should be drawn to the display or
                    None to fill the display with its background colour

        returns

        None
        """

        pass

    def close(self):

        """
        Closes the display

        arguments

        None

        keyword arguments

        None

        returns

        None
        """

        pass

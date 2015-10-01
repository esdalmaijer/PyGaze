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


class BaseTime:

    """Class for keeping track of time"""

    def __init__(self):

        """
        Initializes a Time instance

        arguments

        None

        keyword arguments

        None
        """

        pass


    def expstart(self):

        """
        Time is set to 0 when calling this

        arguments

        None

        keyword arguments

        None

        returns

        Nothing
        """

        pass


    def get_time(self):

        """
        Returns current time in milliseconds

        arguments

        None

        keyword arguments

        None

        returns

        time        --    current time in milliseconds, as measured since
                    expbegintime
        """

        pass


    def pause(self):

        """
        Pauses the experiment for given number of milliseconds

        arguments

        pausetime    --    time to pause in milliseconds

        keyword arguments

        None

        returns

        pausetime    --    actual time the system paused (in milliseconds)
        """

        pass


    def expend(self):

        """
        Completely ends the experiment (only call this at the end!)

        arguments

        None

        keyword arguments

        None

        returns

        endtime    --    ending time of the experiment (in milliseconds since
                    expbegintime
        """

        pass

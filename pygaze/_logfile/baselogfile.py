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
#        print("Display.show call at %d" % int(clock.get_time()))
#


class BaseLogfile:

    """Logfile object for saving data"""

    def __init__(self):

        """Initiates logfile object

        arguments

        None

        keyword arguments

        filename    --    name (possibly including path) for the logfile;
                    WITHOUT extension! (default = LOGFILE)

        returns

        None        --    sets filename and logfile properties
        """

        pass


    def write(self):

        """
        Writes given values to logfile (each value separated with a tab)

        arguments

        vallist    --    list of values to be written to logfile

        keyword arguments

        None

        returns

        None        --    writes each value to the logfile, adding tabs between
                    the values
        """

        pass


    def close(self):

        """
        Closes logfile (do this after writing everything to the file!)

        arguments

        None

        keyword arguments

        None

        returns

        None        --    closes logfile; calling write method after calling
                    close method will result in an error!
        """

        pass

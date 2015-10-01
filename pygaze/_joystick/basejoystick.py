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


class BaseJoystick:

    """A joystick for collecting responses"""

    def __init__(self):

        """
        Initializes a Joystick instance

        arguments

        None

        keyword arguments

        joybuttonlist    --    list of joystick buttons that are allowed (e.g.
                        [0,2,4]) or None to allow all buttons
                        (default = JOYBUTTONLIST)
        timeout        --    time in milliseconds after which None is returned
                        on a call to a get_* method when no input is
                        registered (default = JOYTIMEOUT)
        """

        pass


    def set_joybuttonlist(self):

        """
        Set a list of accepted joystick buttons

        arguments

        None

        keyword arguments

        joybuttonlist    --    list of joystick buttons that are allowed (e.g.
                        [0,2,4]) or None to allow all buttons
                        (default = None)
        returns

        None            --    sets the jbuttonlist property
        """

        pass


    def set_timeout(self):

        """
        Set a timeout (in milliseconds)

        arguments

        None

        keyword arguments

        timeout    --    time in milliseconds after which None is returned
                    on a call to get_clicked method when no click is
                    registered (default = None)

        returns

        None        --    sets timeout property
        """

        pass


    def get_joybutton(self):

        """
        Waits for joystick buttonpress

        arguments

        None

        keyword arguments

        joybuttonlist    --    list of buttons that are allowed (e.g.
                        [0,2,4]), None to allow all buttons or
                        'default' to use jbuttonlist property
                        (default = 'default')
        timeout        --    time in milliseconds after which None is returned
                        when no buttonpress is registered; None for no
                        timeout or 'default' to use the timeout property
                        (default = 'default')

        returns

        button, presstime    --    button is an integer, indicating which button
                            has been pressed or None when no button has
                            been pressed
                            presstime is the time (measured from
                            expbegintime) a buttonpress or a timeout
                            occured
        """

        pass


    def get_joyaxes(self):

        """
        Waits for joystick axis movement

        arguments

        None

        keyword arguments

        timeout    --    time in milliseconds after which None is returned
                    when no buttonpress is registered; None for no
                    timeout or 'default' to use the timeout property
                    (default = 'default')

        returns

        axespos, time    --    axespos is a [x,y,z] position list for the
                        positions of the joystick axes (usually [x,y,z]
                        for the main stick); x, y and z are floats
                        time is the time (measured from expbegintime)
                        an axismovement or a timeout occured
        """

        pass


    def get_joyballs(self):

        """
        Waits for joystick trackball movement

        arguments

        None

        keyword arguments

        timeout    --    time in milliseconds after which None is returned
                    when no buttonpress is registered; None for no
                    timeout or 'default' to use the timeout property
                    (default = 'default')

        returns

        ballpos, time    --    ballpos is a [ball1,ball2,...,ballN] position
                        list for the positions of the joystick balls;
                        each ball position is a (x,y) tuple
                        time is the time (measured from expbegintime) a
                        ballmovement or a timeout occured
        """

        pass


    def get_joyhats(self):

        """
        Waits for joystick hat movement

        arguments

        None

        keyword arguments

        timeout    --    time in milliseconds after which None is returned
                    when no buttonpress is registered; None for no
                    timeout or 'default' to use the timeout property
                    (default = 'default')

        returns

        hatpos, time    --    hatpos is a [hat1,hat2,...,hatN] position list
                        for the positions of the joystick hats; each
                        hat position is a (x,y) tuple
                        time is the time (measured from expbegintime) a
                        hatmovement or a timeout occured
        """

        pass


    def get_joyinput(self):

        """
        Waits for any kind of joystick input

        arguments

        None

        keyword arguments

        joybuttonlist    --    list of buttons that are allowed (e.g.
                        [0,2,4]), None to allow all buttons or
                        'default' to use jbuttonlist property
                        (default = 'default')
        timeout        --    time in milliseconds after which None is returned
                        when no buttonpress is registered; None for no
                        timeout or 'default' to use the timeout property
                        (default = 'default')

        returns

        event, input, time    --    event is a string or None on a timeout,
                            indicating what kind of input was given:
                            'joybuttonpress', input is an integer
                            button number
                            'joyaxismotion', input is a [x,y,z]
                            position list for the positions of the
                            joystick axes (usually [x,y,z] for the
                            main stick); x, y and z are floats
                            'joyballmotion', input is a
                            [ball1,ball2,...,ballN] position list for
                            the positions of the joystick balls; each
                            ball position is a (x,y) tuple
                            'joyhatmotion', input is a
                            [hat1,hat2,...,hatN] position list for
                            the positions of the joystick hats; each
                            hat position is a (x,y) tuple
                            time is the time (measured from
                            expbegintime) any input or a timeout
                            occured
        """

        pass

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
# Many thanks to Sebastiaan Mathot. libeyetracker is a slightly modified version of
# libeyetracker.py, part of the eyetracker plugins for the OpenSesame experiment builder
# (see: www.cogsci.nl/opensesame).
# OpenSesame is free software, redistributable under the terms of the GNU Public
# License as published by the Free Software Foundation.

try:
    import constants
except:
    import defaults as constants
    
import libtime
import libscreen # TODO: make sure dummy eyetracker DOES IN FACT SHOW STUFF!
from libinput import Mouse
from libinput import Keyboard
from libsound import Sound

class Dummy:

    """A dummy class to run experiments in dummy mode, where eye movements are simulated by the mouse"""
    

    def __init__(self, simulator='mouse'):

        """Initiates the eyetracker dummy object (keyword argument: simulator='mouse' (default))"""

        self.recording = False

        self.simulator = Mouse()
        self.simulator.set_timeout(timeout=2)

        self.blinking = False
        self.bbpos = (constants.DISPSIZE[0]/2, constants.DISPSIZE[1]/2)


    def send_command(self, cmd):

        """Dummy command, prints command instead of sending it to the eyetracker"""

        print("The following command would have been given to the eyetracker: " + str(cmd))


    def log(self, msg):

        """Dummy log message, prints message instead of sending it to the eyetracker"""

        print("The following message would have been logged to the EDF: " + str(msg))


    def log_var(self, var, val):

        """Dummy varlog, prints variable and value instead of sending it to the eyetracker"""

        print("The following variable would have been logged to the EDF: " + str(var) + ", value: " + str(val))


    def status_msg(self, msg):
        
        """Dummy status message, prints message instead of sending it to the eyetracker"""

        print("The following status message would have been visible on the experimentor PC: " + str(msg))


    def connected(self):

        """Dummy connection status"""

        print("Dummy mode, eyetracker not connected.")

        return True


    def calibrate(self):

        """Dummy calibration"""

        print("Calibration would now take place")

        libtime.pause(1000)


    def drift_correction(self, pos=None, fix_triggered=False):

        """Dummy drift correction"""

        print("Drift correction would now take place")

        # show mouse
        self.simulator.set_visible(visible=True)
        
        if fix_triggered:
            return self.fix_triggered_drift_correction(pos)

        my_keyboard = Keyboard(keylist=["space"], timeout=1)
        angrybeep = Sound(osc='saw',freq=100, length=100)

        if pos == None:
            pos = constants.DISPSIZE[0] / 2, constants.DISPSIZE[1] / 2

        errdist = 60 # pixels (on a 1024x768px and 39.9x29.9cm monitor at 67 cm, this is about 2 degrees of visual angle)
        pressed = None
        while not pressed:
            pressed, presstime = my_keyboard.get_key()
            if pressed:
                gazepos = self.sample()
                if ((gazepos[0]-pos[0])**2  + (gazepos[1]-pos[1])**2)**0.5 < errdist:
                    # hide mouse
                    self.simulator.set_visible(visible=False)
                    return True
        # hide mouse
        self.simulator.set_visible(visible=False)
        # show discontent
        angrybeep.play()
        return False


    def prepare_drift_correction(self, pos):

        """Dummy drift correction preparation"""

        pass


    def fix_triggered_drift_correction(self, pos=None, min_samples=30, max_dev=60, reset_threshold=10):

        """Dummy drift correction (fixation triggered)"""

        print("Drift correction (fixation triggered) would now take place")

        if pos == None:
            pos = constants.DISPSIZE[0] / 2, constants.DISPSIZE[1] / 2

        self.prepare_drift_correction(pos)
        my_keyboard = Keyboard(keylist=["escape", "q"], timeout=0)

        # loop until we have sufficient samples
        lx = []
        ly = []
        while len(lx) < min_samples:

            # pressing escape enters the calibration screen
            if my_keyboard.get_key()[0] != None:
                self.recording = False
                print("libeyetracker.libeyetracker.fix_triggered_drift_correction(): 'q' pressed")
                return False

            # collect a sample
            x, y = self.sample()

            if len(lx) == 0 or x != lx[-1] or y != ly[-1]:

                # if present sample deviates too much from previous sample, reset counting
                if len(lx) > 0 and (abs(x - lx[-1]) > reset_threshold or abs(y - ly[-1]) > reset_threshold):
                    lx = []
                    ly = []

                # collect samples
                else:
                    lx.append(x)
                    ly.append(y)

            if len(lx) == min_samples:

                avg_x = sum(lx) / len(lx)
                avg_y = sum(ly) / len(ly)
                d = ((avg_x - pos[0]) ** 2 + (avg_y - pos[1]) ** 2)**0.5

                if d < max_dev:
                    return True
                else:
                    lx = []
                    ly = []
                        

    def start_recording(self):

        """Dummy for starting recording, prints what would have been the recording start"""

        self.simulator.set_visible(visible=True)
        dumrectime = libtime.get_time()

        self.recording = True
        
        print("Recording would have started at: " + str(dumrectime))


    def stop_recording(self):

        """Dummy for stopping recording, prints what would have been the recording end"""

        self.simulator.set_visible(visible=False)
        dumrectime = libtime.get_time()

        self.recording = False

        print("Recording would have stopped at: " + str(dumrectime))


    def close(self):

        """Dummy for closing connection with eyetracker, prints what would have been connection closing time"""

        if self.recording:
            self.stop_recording()
        
        closetime = libtime.get_time()

        print("eyetracker connection would have closed at: " + str(closetime))


    def set_eye_used(self):

        """Dummy for setting which eye to track (does nothing)"""
        
        pass


    def sample(self):

        """Returns simulated gaze position (=mouse position)"""

        if self.blinking:
            if self.simulator.get_pressed()[2]: # buttondown
                self.simulator.set_pos(pos=(self.bbpos[0],self.resolution[1])) # set position to blinking position
            elif not self.simulator.get_pressed()[2]: # buttonup
                self.simulator.set_pos(pos=self.bbpos) # set position to position before blinking
                self.blinking = False # 'blink' stopped

        elif not self.blinking:
            if self.simulator.get_pressed()[2]: # buttondown
                self.blinking = True # 'blink' started
                self.bbpos =  self.simulator.get_pos()[0] # position before blinking
                self.simulator.set_pos(pos=(self.bbpos[0],self.resolution[1])) # set position to blinking position

        return self.simulator.get_pos()


    def wait_for_event(self, event):

        """Waits for simulated event (3=STARTBLINK, 4=ENDBLINK, 5=STARTSACC, 6=ENDSACC, 7=STARTFIX, 8=ENDFIX)"""

        if event == 5:
            outcome = self.wait_for_saccade_start()
        elif event == 6:
            outcome = self.wait_for_saccade_end()
        elif event == 7:
            outcome = self.wait_for_fixation_start()
        elif event == 8:
            outcome = self.wait_for_fixation_end()
        elif event == 3:
            outcome = self.wait_for_blink_start()
        elif event == 4:
            outcome = self.wait_for_blink_end()

        return outcome


    def wait_for_saccade_start(self):

        """Returns starting time and starting position when a simulated saccade is started"""

        # function assumes that a 'saccade' has been started when a deviation of more than
        # maxerr from the initial 'gaze' position has been detected (using Pythagoras, ofcourse)

        spos = self.sample() # starting position
        maxerr = 3 # pixels
        while True:
            npos = self.sample() # get newest sample
            if ((spos[0]-npos[0])**2  + (spos[1]-npos[1])**2)**0.5 > maxerr: # Pythagoras
                break

        return libtime.get_time(), spos


    def wait_for_saccade_end(self):

        """Returns ending time, starting and end position when a simulated saccade is ended"""

        # function assumes that a 'saccade' has ended when 'gaze' position remains reasonably
        # (i.e.: within maxerr) stable for five samples
        # for saccade start algorithm, see wait_for_fixation_start

        stime, spos = self.wait_for_saccade_start()
        maxerr = 3 # pixels
        
        # wait for reasonably stable position
        xl = [] # list for last five samples (x coordinate)
        yl = [] # list for last five samples (y coordinate)
        moving = True
        while moving:
            # check positions
            npos = self.sample()
            xl.append(npos[0]) # add newest sample
            yl.append(npos[1]) # add newest sample
            if len(xl) == 5:
                # check if deviation is small enough
                if max(xl)-min(xl) < maxerr and max(yl)-min(yl) < maxerr:
                    moving = False
                # remove oldest sample
                xl.pop(0); yl.pop(0)
            # wait for a bit, to avoid immediately returning (runs go faster than mouse moves)
            libtime.pause(10)

        return libtime.get_time(), spos, (xl[len(xl)-1],yl[len(yl)-1])


    def wait_for_fixation_start(self):

        """Returns starting time and position when a simulated fixation is started"""

        # function assumes a 'fixation' has started when 'gaze' position remains reasonably
        # stable for five samples in a row (same as saccade end)

        maxerr = 3 # pixels
        
        # wait for reasonably stable position
        xl = [] # list for last five samples (x coordinate)
        yl = [] # list for last five samples (y coordinate)
        moving = True
        while moving:
            npos = self.sample()
            xl.append(npos[0]) # add newest sample
            yl.append(npos[1]) # add newest sample
            if len(xl) == 5:
                # check if deviation is small enough
                if max(xl)-min(xl) < maxerr and max(yl)-min(yl) < maxerr:
                    moving = False
                # remove oldest sample
                xl.pop(0); yl.pop(0)
            # wait for a bit, to avoid immediately returning (runs go faster than mouse moves)
            libtime.pause(10)

        return libtime.get_time(), (xl[len(xl)-1],yl[len(yl)-1])


    def wait_for_fixation_end(self):

        """Returns time and gaze position when a simulated fixation is ended"""

        # function assumes that a 'fixation' has ended when a deviation of more than maxerr
        # from the initial 'fixation' position has been detected (using Pythagoras, ofcourse)

        stime, spos = self.wait_for_fixation_start()
        maxerr = 3 # pixels
        
        while True:
            npos = self.sample() # get newest sample
            if ((spos[0]-npos[0])**2  + (spos[1]-npos[1])**2)**0.5 > maxerr: # Pythagoras
                break

        return libtime.get_time(), spos


    def wait_for_blink_start(self):

        """Returns starting time and position of a simulated blink (mousebuttondown)"""

        # blinks are simulated with mouseclicks: a right mouseclick simulates the closing
        # of the eyes, a mousebuttonup the opening.

        while not self.blinking:
            pos = self.sample()

        return libtime.get_time(), pos


    def wait_for_blink_end(self):

        """Returns ending time and position of a simulated blink (mousebuttonup)"""
		
        # blinks are simulated with mouseclicks: a right mouseclick simulates the closing
        # of the eyes, a mousebuttonup the opening.

        # wait for blink start
        while not self.blinking:
            spos = self.sample()
        # wait for blink end
        while self.blinking:
            epos = self.sample()

        return libtime.get_time(), epos

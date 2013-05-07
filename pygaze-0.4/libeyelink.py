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
# version: 0.4 (25-03-2013), NOT RELEASED FOR USE OUTSIDE OF UTRECHT UNIVERSITY)
#
#
# Many thanks to Sebastiaan Mathot. libeyelink is a slightly modified version of
# libeyelink.py, part of the eyelink plugins for the OpenSesame experiment builder
# (see: www.cogsci.nl/opensesame).
# OpenSesame is free software, redistributable under the terms of the GNU Public
# License as published by the Free Software Foundation.

try:
    import constants
except:
    import defaults as constants
    
import libtime
import libscreen
from libinput import Mouse
from libinput import Keyboard
from libsound import Sound

if not constants.DUMMYMODE:
    import pylink
    import Image
    custom_display = pylink.EyeLinkCustomDisplay
else:
    custom_display = object

try:
    import psychopy.visual
except:
    if constants.DISPYPE == 'psychopy':
        print("Error in libeyelink: PsychoPy could not be loaded!")

try:
    import pygame
except:
    if constants.DISPTYPE == 'pygame':
        print("Error in libeyelink: PyGame could not be loaded!")

import os.path
import array
from PIL import Image

_eyelink = None


class libeyelink:

    MAX_TRY = 100

    def __init__(self, display, resolution=constants.DISPSIZE, data_file=constants.LOGFILE+".edf", fg_color=constants.FGC, bg_color=constants.BGC, saccade_velocity_threshold=35, saccade_acceleration_threshold=9500):

        """"Initializes the connection to the Eyelink"""

        global _eyelink

        stem, ext = os.path.splitext(data_file)
        if len(stem) > 8 or len(ext) > 4:
            file_name = "default.edf"
            print("The Eyelink cannot handle filenames longer than 8 characters (excluding '.EDF' extension). Filename set to 'default.EDF'.")

        self.data_file = data_file
        self.screen = display
        self.resolution = resolution
        self.recording = False
        self.saccade_velocity_treshold = saccade_velocity_threshold
        self.saccade_acceleration_treshold = saccade_acceleration_threshold
        self.eye_used = None
        self.left_eye = 0
        self.right_eye = 1
        self.binocular = 2

        # only initialize eyelink once
        if _eyelink == None:
            try:
                _eyelink = pylink.EyeLink()
            except:
                print("Error in libeyelink.libeyelink.__init__(): Failed to connect to the tracker!")

            graphics_env = eyelink_graphics(self.screen, _eyelink)
            pylink.openGraphicsEx(graphics_env)

        pylink.getEYELINK().openDataFile(self.data_file)
        pylink.flushGetkeyQueue()
        pylink.getEYELINK().setOfflineMode()

        # notify eyelink of display resolution
        self.send_command("screen_pixel_coords = 0 0 %d %d" % (self.resolution[0], self.resolution[1]))

        # determine software version of tracker
        self.tracker_software_ver = 0
        self.eyelink_ver = pylink.getEYELINK().getTrackerVersion()
        if self.eyelink_ver == 3:
            tvstr = pylink.getEYELINK().getTrackerVersionString()
            vindex = tvstr.find("EYELINK CL")
            self.tracker_software_ver = int(float(tvstr[(vindex + len("EYELINK CL")):].strip()))

        # get some configuration stuff
        if self.eyelink_ver >= 2:
            self.send_command("select_parser_configuration 0")
            if self.eyelink_ver == 2: # turn off scenelink camera stuff
                self.send_command("scene_camera_gazemap = NO")
        else:
            self.send_command("saccade_velocity_threshold = %d" % self.saccade_velocity_threshold)
            self.send_command("saccade_acceleration_threshold = %s" % self.saccade_acceleration_threshold)

        # set EDF file contents (this specifies which data is written to the EDF file)
        self.send_command("file_event_filter = LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON")
        if self.tracker_software_ver >= 4:
            self.send_command("file_sample_data  = LEFT,RIGHT,GAZE,AREA,GAZERES,STATUS,HTARGET")
        else:
            self.send_command("file_sample_data  = LEFT,RIGHT,GAZE,AREA,GAZERES,STATUS")

        # set link data (this specifies which data is sent through the link and thus can be used in gaze contingent displays)
        self.send_command("link_event_filter = LEFT,RIGHT,FIXATION,SACCADE,BLINK,BUTTON")
        if self.tracker_software_ver >= 4:
            self.send_command("link_sample_data  = LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS,HTARGET")
        else:
            self.send_command("link_sample_data  = LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS")

        # not quite sure what this means (according to Sebastiaan Mathot, it might be the button that is used to end drift correction?)
        self.send_command("button_function 5 'accept_target_fixation'")

        if not self.connected():
            print("Error in libeyelink.libeyelink.__init__(): Failed to connect to the eyetracker!")


    def send_command(self, cmd):

        """Sends a command to the eyelink"""

        pylink.getEYELINK().sendCommand(cmd)


    def log(self, msg):

        """Writes a message to the eyelink data file"""

        pylink.getEYELINK().sendMessage(msg)


    def log_var(self, var, val):

        """Writes a variable to the eyelink data file"""

        pylink.getEYELINK().sendMessage("var %s %s" % (var, val))


    def status_msg(self, msg):

        """Sets the eyelink status message (which is displayed on the eyelink experimenter PC)"""

        pylink.getEYELINK().sendCommand("record_status_message '%s'" % msg)


    def connected(self):

        """Returns the status of the eyelink connection"""

        return pylink.getEYELINK().isConnected()


    def calibrate(self):

        """Starts eyelink calibration"""

        if self.recording:
            print("Error in libeyelink.libeyelink.calibrate(): Trying to calibrate after recording has started!")

        pylink.getEYELINK().doTrackerSetup()


    def drift_correction(self, pos=None, fix_triggered=False):

        """Performs drift correction and falls back to calibration screen if necessary"""

        if self.recording:
            print("Error in libeyelink.libeyelink.drift_correction(): Trying to perform drift correction after recording has started!")

        if fix_triggered:
            return self.fix_triggered_drift_correction(pos)

        if pos == None:
            pos = self.resolution[0] / 2, self.resolution[1] / 2

        while True:
            if not self.connected():
                print("Error in libeyelink.libeyelink.drift_correction(): The eyelink is not connected!")
            try:
                # Params: x, y, draw fix, allow_setup
                error = pylink.getEYELINK().doDriftCorrect(pos[0], pos[1], 0, 1)
                if error != 27:
                    print("libeyelink.libeyelink.drift_correction(): success")
                    return True
                else:
                    print("libeyelink.drift_correction(): escape pressed")
                    return False
            except:
                print("libeyelink.drift_correction(): try again")
                return False


    def prepare_drift_correction(self, pos):

        """Puts the tracker in drift correction mode"""

        # start collecting samples in drift correction mode
        self.send_command("heuristic_filter = ON")
        self.send_command("drift_correction_targets = %d %d" % pos)
        self.send_command("start_drift_correction data = 0 0 1 0")
        pylink.msecDelay(50);

        # wait for a bit until samples start coming in (again, not sure if this is indeed what's going on)
        if not pylink.getEYELINK().waitForBlockStart(100, 1, 0):
            print("Error in libeyelink.libeyelink.prepare_drift_correction(): Failed to perform drift correction (waitForBlockStart error)")


    def fix_triggered_drift_correction(self, pos=None, min_samples=30, max_dev=60, reset_threshold=10):

        """Performs fixation triggered drift correction and falls back to the calibration screen if necessary"""

        if self.recording:
            print("Error in libeyelink.libeyelink.fix_triggered_drift_correction(): Trying to perform drift correction after recording has started!")

        self.recording = True

        if pos == None:
            pos = self.resolution[0] / 2, self.resolution[1] / 2

        self.prepare_drift_correction(pos)
        my_keyboard = Keyboard(keylist=["escape", "q"], timeout=0)

        # loop until we have sufficient samples
        lx = []
        ly = []
        while len(lx) < min_samples:

            # pressing escape enters the calibration screen
            if my_keyboard.get_key()[0] != None:
                self.recording = False
                print("libeyelink.libeyelink.fix_triggered_drift_correction(): 'q' pressed")
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

                # emulate spacebar press on succes
                pylink.getEYELINK().sendKeybutton(32, 0, pylink.KB_PRESS)

                # getCalibrationResult() returns 0 on success and an exception or a non-zero value otherwise
                result = -1
                try:
                    result = pylink.getEYELINK().getCalibrationResult()
                except:
                    lx = []
                    ly = []
                    print("libeyelink.libeyelink.fix_triggered_drift_correction(): try again")
                if result != 0:
                    
                    try:
                        result = pylink.getEYELINK().getCalibrationResult()
                    except:
                        lx = []
                        ly = []
                        print("libeyelink.libeyelink.fix_triggered_drift_correction(): try again")

        # apply drift correction
        pylink.getEYELINK().applyDriftCorrect()
        self.recording = False
        print("libeyelink.libeyelink.fix_triggered_drift_correction(): success")

        return True


    def start_recording(self):

        """Starts recording of gaze samples"""

        self.recording = True

        i = 0
        while True:
            # params: write samples, write event, send samples, send events
            error = pylink.getEYELINK().startRecording(1, 1, 1, 1)
            
            if not error:
                break
            if i > self.MAX_TRY:
                print("Error in libeyelink.libeyelink.start_recording(): Failed to start recording!")
                self.close()
                libtime.expend()
            i += 1
            print("libeyelink.libeyelink.start_recording(): Failed to start recording (attempt %d of %d)" % (i, self.MAX_TRY))
            pylink.msecDelay(100)

        # don't know what this is
        pylink.pylink.beginRealTimeMode(100)

        # wait a bit until samples start coming in
        if not pylink.getEYELINK().waitForBlockStart(100, 1, 0):
            print("Error in libeyelink.libeyelink.start_recording(): Failed to start recording (waitForBlockStart error)!")


    def stop_recording(self):

        """Stops recording of gaze samples"""

        self.recording = False

        pylink.endRealTimeMode()
        pylink.getEYELINK().setOfflineMode()
        pylink.msecDelay(500)


    def close(self):

        """Close the connection with the eyelink"""

        if self.recording:
            self.stop_recording()

        # close data file and transfer it to the experimental PC
        print("libeyelink.libeyelink.close(): Closing data file")
        pylink.getEYELINK().closeDataFile()
        pylink.msecDelay(100)
        print("libeyelink.libeyelink.close(): Transferring data file")
        pylink.getEYELINK().receiveDataFile(self.data_file, self.data_file)
        pylink.msecDelay(100)
        print("libeyelink.libeyelink.close(): Closing eyelink")
        pylink.getEYELINK().close();
        pylink.msecDelay(100)


    def set_eye_used(self):

        """Sets the eye_used variable, based on the eyelink's report (which specifies which eye is being tracked); if both eyes are being tracked, the left eye is used"""

        self.eye_used = pylink.getEYELINK().eyeAvailable()
        if self.eye_used == self.right_eye:
            self.log_var("eye_used", "right")
        elif self.eye_used == self.left_eye or self.eye_used == self.binocular:
            self.log_var("eye_used", "left")
            self.eye_used = self.left_eye
        else:
            print("Error in libeyelink.libeyelink.set_eye_used(): Failed to determine which eye is being recorded")


    def sample(self):

        """Returns a (x,y) tuple of the most recent gaze sample from the eyelink"""

        if not self.recording:
            print("Error in libeyelink.libeyelink.sample(): Recording was not started before collecting eyelink data!")

        if self.eye_used == None:
            self.set_eye_used()

        s = pylink.getEYELINK().getNewestSample()
        if s != None:
            if self.eye_used == self.right_eye and s.isRightSample():
                gaze = s.getRightEye().getGaze()
            elif self.eye_used == self.left_eye and s.isLeftSample():
                gaze = s.getLeftEye().getGaze()

        return gaze


    def wait_for_event(self, event):

        """Waits until a specified event has occurred"""

        if not self.recording:
            print("Error in libeyelink.libeyelink.wait_for_event(): Recording was not started before collecting eyelink data!")

        if self.eye_used == None:
            self.set_eye_used()

        d = 0
        while d != event:
            d = pylink.getEYELINK().getNextData()

        return pylink.getEYELINK().getFloatData()


    def wait_for_saccade_start(self):

        """Waits for a saccade start  and returns time and start position"""

        d = self.wait_for_event(pylink.STARTSACC)
        return d.getTime(), d.getStartGaze()


    def wait_for_saccade_end(self):

        """Waits for a saccade end  and returns time, start position and end position"""

        d = self.wait_for_event(pylink.ENDSACC)
        return d.getTime(), d.getStartGaze(), d.getEndGaze()


    def wait_for_fixation_start(self):

        """Waits for a fixation start and returns time and start position"""

        d = self.wait_for_event(pylink.STARTFIX)
        return d.getTime(), d.getStartGaze()


    def wait_for_fixation_end(self):

        """Waits for a fixation end and returns time, start position and end position"""

        d = self.wait_for_event(pylink.ENDFIX)
        return d.getTime(), d.getStartGaze(), d.getEndGaze()


    def wait_for_blink_start(self):

        """Waits for a blink start and returns time"""

        d = self.wait_for_event(pylink.STARTBLINK)
        return d.getTime()


    def wait_for_blink_end(self):

        """Waits for a blink end and returns time"""

        d = self.wait_for_event(pylink.ENDBLINK)
        return d.getTime()


##class libeyelink_dummy:
##
##    """A dummy class to run experiments in dummy mode, where eye movements are simulated by the mouse (or a joystick)"""
##    
##
##    def __init__(self, simulator='mouse'):
##
##        """Initiates the eyelink dummy object (keyword argument: simulator='mouse' (default)"""
##
##        self.recording = False
##
##        self.simulator = Mouse()
##        self.simulator.set_timeout(timeout=2)
##
##        self.blinking = False
##        self.bbpos = (constants.DISPSIZE[0]/2, constants.DISPSIZE[1]/2)
##
##
##    def send_command(self, cmd):
##
##        """Dummy command, prints command instead of sending it to the eyelink"""
##
##        print("The following command would have been given to the eyelink: " + str(cmd))
##
##
##    def log(self, msg):
##
##        """Dummy log message, prints message instead of sending it to the eyelink"""
##
##        print("The following message would have been logged to the EDF: " + str(msg))
##
##
##    def log_var(self, var, val):
##
##        """Dummy varlog, prints variable and value instead of sending it to the eyelink"""
##
##        print("The following variable would have been logged to the EDF: " + str(var) + ", value: " + str(val))
##
##
##    def status_msg(self, msg):
##        
##        """Dummy status message, prints message instead of sending it to the eyelink"""
##
##        print("The following status message would have been visible on the experimentor PC: " + str(msg))
##
##
##    def connected(self):
##
##        """Dummy connection status"""
##
##        print("Dummy mode, eyelink not connected.")
##
##        return True
##
##
##    def calibrate(self):
##
##        """Dummy calibration"""
##
##        print("Calibration would now take place")
##
##        libtime.pause(1000)
##
##
##    def drift_correction(self, pos=None, fix_triggered=False):
##
##        """Dummy drift correction"""
##
##        print("Drift correction would now take place")
##
##        # show mouse
##        self.simulator.set_visible(visible=True)
##        
##        if fix_triggered:
##            return self.fix_triggered_drift_correction(pos)
##
##        my_keyboard = Keyboard(keylist=["space"], timeout=1)
##        angrybeep = Sound(osc='saw',freq=100, length=100)
##
##        if pos == None:
##            pos = constants.DISPSIZE[0] / 2, constants.DISPSIZE[1] / 2
##
##        errdist = 60 # pixels (on a 1024x768px and 39.9x29.9cm monitor at 67 cm, this is about 2 degrees of visual angle)
##        pressed = None
##        while not pressed:
##            pressed, presstime = my_keyboard.get_key()
##            if pressed:
##                gazepos = self.sample()
##                if ((gazepos[0]-pos[0])**2  + (gazepos[1]-pos[1])**2)**0.5 < errdist:
##                    # hide mouse
##                    self.simulator.set_visible(visible=False)
##                    return True
##        # hide mouse
##        self.simulator.set_visible(visible=False)
##        # show discontent
##        angrybeep.play()
##        return False
##
##
##    def prepare_drift_correction(self, pos):
##
##        """Dummy drift correction preparation"""
##
##        pass
##
##
##    def fix_triggered_drift_correction(self, pos=None, min_samples=30, max_dev=60, reset_threshold=10):
##
##        """Dummy drift correction (fixation triggered)"""
##
##        print("Drift correction (fixation triggered) would now take place")
##
##        if pos == None:
##            pos = constants.DISPSIZE[0] / 2, constants.DISPSIZE[1] / 2
##
##        self.prepare_drift_correction(pos)
##        my_keyboard = Keyboard(keylist=["escape", "q"], timeout=0)
##
##        # loop until we have sufficient samples
##        lx = []
##        ly = []
##        while len(lx) < min_samples:
##
##            # pressing escape enters the calibration screen
##            if my_keyboard.get_key()[0] != None:
##                self.recording = False
##                print("libeyelink.libeyelink.fix_triggered_drift_correction(): 'q' pressed")
##                return False
##
##            # collect a sample
##            x, y = self.sample()
##
##            if len(lx) == 0 or x != lx[-1] or y != ly[-1]:
##
##                # if present sample deviates too much from previous sample, reset counting
##                if len(lx) > 0 and (abs(x - lx[-1]) > reset_threshold or abs(y - ly[-1]) > reset_threshold):
##                    lx = []
##                    ly = []
##
##                # collect samples
##                else:
##                    lx.append(x)
##                    ly.append(y)
##
##            if len(lx) == min_samples:
##
##                avg_x = sum(lx) / len(lx)
##                avg_y = sum(ly) / len(ly)
##                d = ((avg_x - pos[0]) ** 2 + (avg_y - pos[1]) ** 2)**0.5
##
##                if d < max_dev:
##                    return True
##                else:
##                    lx = []
##                    ly = []
##                        
##
##    def start_recording(self):
##
##        """Dummy for starting recording, prints what would have been the recording start"""
##
##        self.simulator.set_visible(visible=True)
##        dumrectime = libtime.get_time()
##
##        self.recording = True
##        
##        print("Recording would have started at: " + str(dumrectime))
##
##
##    def stop_recording(self):
##
##        """Dummy for stopping recording, prints what would have been the recording end"""
##
##        self.simulator.set_visible(visible=False)
##        dumrectime = libtime.get_time()
##
##        self.recording = False
##
##        print("Recording would have stopped at: " + str(dumrectime))
##
##
##    def close(self):
##
##        """Dummy for closing connection with eyelink, prints what would have been connection closing time"""
##
##        if self.recording:
##            self.stop_recording()
##        
##        closetime = libtime.get_time()
##
##        print("Eyelink connection would have closed at: " + str(closetime))
##
##
##    def set_eye_used(self):
##
##        """Dummy for setting which eye to track (does nothing)"""
##        
##        pass
##
##
##    def sample(self):
##
##        """Returns simulated gaze position (=mouse position)"""
##
##        if self.blinking:
##            if self.simulator.get_pressed()[2]: # buttondown
##                self.simulator.set_pos(pos=(self.bbpos[0],self.resolution[1])) # set position to blinking position
##            elif not self.simulator.get_pressed()[2]: # buttonup
##                self.simulator.set_pos(pos=self.bbpos) # set position to position before blinking
##                self.blinking = False # 'blink' stopped
##
##        elif not self.blinking:
##            if self.simulator.get_pressed()[2]: # buttondown
##                self.blinking = True # 'blink' started
##                self.bbpos =  self.simulator.get_pos()[0] # position before blinking
##                self.simulator.set_pos(pos=(self.bbpos[0],self.resolution[1])) # set position to blinking position
##
##        return self.simulator.get_pos()
##
##
##    def wait_for_event(self, event):
##
##        """Waits for simulated event (3=STARTBLINK, 4=ENDBLINK, 5=STARTSACC, 6=ENDSACC, 7=STARTFIX, 8=ENDFIX)"""
##
##        if event == 5:
##            self.wait_for_saccade_start()
##        elif event == 6:
##            self.wait_for_saccade_end()
##        elif event == 7:
##            self.wait_for_fixation_start()
##        elif event == 8:
##            self.wait_for_fixation_end()
##        elif event == 3:
##            self.wait_for_blink_start()
##        elif event == 4:
##            self.wait_for_blink_end()
##
##        return (libtime.get_time(), ())
##
##
##    def wait_for_saccade_start(self):
##
##        """Returns starting time and starting position when a simulated saccade is started"""
##
##        # function assumes that a 'saccade' has been started when a deviation of more than
##        # maxerr from the initial 'gaze' position has been detected (using Pythagoras, ofcourse)
##
##        spos = self.sample() # starting position
##        maxerr = 3 # pixels
##        while True:
##            npos = self.sample() # get newest sample
##            if ((spos[0]-npos[0])**2  + (spos[1]-npos[1])**2)**0.5 > maxerr: # Pythagoras
##                break
##
##        return libtime.get_time(), spos
##
##
##    def wait_for_saccade_end(self):
##
##        """Returns ending time, starting and end position when a simulated saccade is ended"""
##
##        # function assumes that a 'saccade' has ended when 'gaze' position remains reasonably
##        # (i.e.: within maxerr) stable for five samples
##        # for saccade start algorithm, see wait_for_fixation_start
##
##        stime, spos = self.wait_for_saccade_start()
##        maxerr = 3 # pixels
##        
##        # wait for reasonably stable position
##        xl = [] # list for last five samples (x coordinate)
##        yl = [] # list for last five samples (y coordinate)
##        moving = True
##        while moving:
##            # check positions
##            npos = self.sample()
##            xl.append(npos[0]) # add newest sample
##            yl.append(npos[1]) # add newest sample
##            if len(xl) == 5:
##                # check if deviation is small enough
##                if max(xl)-min(xl) < maxerr and max(yl)-min(yl) < maxerr:
##                    moving = False
##                # remove oldest sample
##                xl.pop(0); yl.pop(0)
##            # wait for a bit, to avoid immediately returning (runs go faster than mouse moves)
##            libtime.pause(10)
##
##        return libtime.get_time(), spos, (xl[len(xl)-1],yl[len(yl)-1])
##
##
##    def wait_for_fixation_start(self):
##
##        """Returns starting time and position when a simulated fixation is started"""
##
##        # function assumes a 'fixation' has started when 'gaze' position remains reasonably
##        # stable for five samples in a row (same as saccade end)
##
##        maxerr = 3 # pixels
##        
##        # wait for reasonably stable position
##        xl = [] # list for last five samples (x coordinate)
##        yl = [] # list for last five samples (y coordinate)
##        moving = True
##        while moving:
##            npos = self.sample()
##            xl.append(npos[0]) # add newest sample
##            yl.append(npos[1]) # add newest sample
##            if len(xl) == 5:
##                # check if deviation is small enough
##                if max(xl)-min(xl) < maxerr and max(yl)-min(yl) < maxerr:
##                    moving = False
##                # remove oldest sample
##                xl.pop(0); yl.pop(0)
##            # wait for a bit, to avoid immediately returning (runs go faster than mouse moves)
##            libtime.pause(10)
##
##        return libtime.get_time(), (xl[len(xl)-1],yl[len(yl)-1])
##
##
##    def wait_for_fixation_end(self):
##
##        """Returns time and gaze position when a simulated fixation is ended"""
##
##        # function assumes that a 'fixation' has ended when a deviation of more than maxerr
##        # from the initial 'fixation' position has been detected (using Pythagoras, ofcourse)
##
##        stime, spos = self.wait_for_fixation_start()
##        maxerr = 3 # pixels
##        
##        while True:
##            npos = self.sample() # get newest sample
##            if ((spos[0]-npos[0])**2  + (spos[1]-npos[1])**2)**0.5 > maxerr: # Pythagoras
##                break
##
##        return libtime.get_time(), spos
##
##
##    def wait_for_blink_start(self):
##
##        """Returns starting time and position of a simulated blink (mousebuttondown)"""
##
##        # blinks are simulated with mouseclicks: a right mouseclick simulates the closing
##        # of the eyes, a mousebuttonup the opening.
##
##        while not self.blinking:
##            pos = self.sample()
##
##        return libtime.get_time(), pos
##
##
##    def wait_for_blink_end(self):
##
##        """Returns ending time and position of a simulated blink (mousebuttonup)"""
##		
##        # blinks are simulated with mouseclicks: a right mouseclick simulates the closing
##        # of the eyes, a mousebuttonup the opening.
##
##        # wait for blink start
##        while not self.blinking:
##            spos = self.sample()
##        # wait for blink end
##        while self.blinking:
##            epos = self.sample()
##
##        return libtime.get_time(), epos


class eyelink_graphics(custom_display):

    """A custom graphics environment to use PyGame or PsychoPy graphics (see libscreen) for calibration, rather than PyLink built-in functions"""

    def __init__(self, display, tracker):

        pylink.EyeLinkCustomDisplay.__init__(self)

        self.display = display
        self.screen = libscreen.Screen()
        self.my_keyboard = Keyboard(timeout=0, keylist=None)
        self.my_mouse = Mouse()

        self.__target_beep__ = Sound(freq=440, length=50)
        self.__target_beep__done__ = Sound(freq=880, length=200)
        self.__target_beep__error__ = Sound(freq=220, length=200)

        self.state = None

        self.imagebuffer = array.array('l')
        self.pal = None
        self.size = (0,0)

        self.set_tracker(tracker)
        self.last_mouse_state = -1


    def set_tracker(self, tracker):

        """Connect the tracker to the graphics environment"""

        self.tracker = tracker
        self.tracker_version = tracker.getTrackerVersion()
        if(self.tracker_version >=3):
            self.tracker.sendCommand("enable_search_limits=YES")
            self.tracker.sendCommand("track_search_limits=YES")
            self.tracker.sendCommand("autothreshold_click=YES")
            self.tracker.sendCommand("autothreshold_repeat=YES")
            self.tracker.sendCommand("enable_camera_position_detect=YES")


    def setup_cal_display(self):

        """Setup the calibration display, which contains some instructions"""

        yc = constants.DISPSIZE[1]/2 # horizontal center
        ld = 40 # line distance
        self.display.fill()
        # show a picture, with calibration instructions?
        self.display.show()


    def exit_cal_display(self):

        """Clear calibration display"""

        self.display.fill()
        self.display.show()


    def record_abort_hide(self):

        """No clue what this is supposed to do..."""

        pass


    def clear_cal_display(self):

        """Clear the calibration display"""

        self.display.fill()
        self.display.show()


    def erase_cal_target(self):

        """Is done before drawing"""

        pass


    def draw_cal_target(self, x, y):

        """Draw calibration target at (x,y)"""

        calscreen = libscreen.Screen()
        calscreen.draw_fixation(fixtype='dot', colour=constants.FGC, pos=(x,y), pw=0, diameter=12)
        self.display.fill(screen=calscreen)
        self.display.show()


    def play_beep(self, beepid):

        """Play a sound"""

        if beepid == pylink.CAL_TARG_BEEP:
            self.__target_beep__.play()
        elif beepid == pylink.CAL_ERR_BEEP or beepid == pylink.DC_ERR_BEEP:
            self.display.fill()
            # show a picture: "calibration unsuccesfull, press 'q' to return to menu"?
            self.display.show()
            self.__target_beep__error__.play()
        elif beepid == pylink.CAL_GOOD_BEEP:
            self.display.fill()
            if self.state == "calibration":
                # show a picture: "calibration succesfull, press 'v' to validate"?
                pass
            elif self.state == "validation":
                # show a picture: "calibration succesfull, press 'q' to return to menu"?
                pass
            else:
                # show a picture: "press 'q' to return to menu"?
                pass
            self.display.show()
            self.__target_beep__done__.play()
        else: #	DC_GOOD_BEEP	or DC_TARG_BEEP
            pass


    def getColorFromIndex(self,colorindex):

        """Unused"""

        pass


    def draw_line(self, x1, y1, x2, y2, colorindex):

        """Unused"""

        pass


    def draw_lozenge(self,x,y,width,height,colorindex):

        """Unused"""

        pass


    def get_mouse_state(self):

        """Unused"""

        pass


    def get_input_key(self):

        """Get an input key"""

        print "get_input_key"

        try:
            key, time = self.my_keyboard.get_key(keylist=None,timeout=1)
        except:
            return None

        if key == None:
            return None

        ky = []
##        key = self.my_keyboard.to_chr(_key)

        if key == "return":
            keycode = pylink.ENTER_KEY
            self.state = None
        elif key == "space":
            keycode = ord(" ")
        elif key == "q":
            keycode = pylink.ESC_KEY
            self.state = None
        elif key == "c":
            keycode = ord("c")
            self.state = "calibration"
        elif key == "v":
            keycode = ord("v")
            self.state = "validation"
        elif key == "a":
            keycode = ord("a")
        elif key == "up":
            keycode = pylink.CURS_UP
        elif key == "down":
            keycode = pylink.CURS_DOWN
        elif key == "left":
            keycode = pylink.CURS_LEFT
        elif key == "right":
            keycode = pylink.CURS_RIGHT
        else:
            keycode = 0

        #print("key=%s, keycode=%s, state=%s" % (key,keycode,self.state))

        return [pylink.KeyInput(keycode, 0)] # 0 = pygame.KMOD_NONE


    def exit_image_display(self):

        """Exit the image display"""

        self.clear_cal_display()


    def alert_printf(self,msg):

        """Print alert message"""

        print "eyelink_graphics.alert_printf(): %s" % msg


    def setup_image_display(self, width, height):

        """Setup the image display"""

        self.size = (width,height)
        self.clear_cal_display()
        self.last_mouse_state = -1
        self.imagebuffer = array.array('l')


    def image_title(self, text):

        """Unused"""

        pass


    def draw_image_line(self, width, line, totlines, buff):

        """Draw a single eye video frame (keyword arguments: with=width of the video; line=line nr of current line, totlines=total lines in video; buff=frame buffer"""

        i = 0
        while i < width:
            try:
                self.imagebuffer.append(self.pal[buff[i]])
            except:
                pass
            i = i + 1

        if line == totlines:

            bufferv = self.imagebuffer.tostring()
            img =Image.new("RGBX",self.size)
            imgsz = constants.DISPSIZE[0]/2, constants.DISPSIZE[1]/2
            img.fromstring(bufferv)
            img = img.resize(imgsz)

            if constants.DISPTYPE == 'pygame':
                img = pygame.image.fromstring(img.tostring(),imgsz,"RGBX")
                self.display.fill()
                self.display.expdisplay.blit(img,((self.display.expdisplay.get_rect().w-imgsz[0])/2,(self.display.expdisplay.get_rect().h-imgsz[1])/2))
                self.display.show()
            elif constants.DISPTYPE == 'psychopy':
                img = psychopy.visual.SimpleImageStim(self.display.expdisplay, image=img)
                self.display.fill()
                img.draw()
                self.display.show()

            self.imagebuffer = array.array('l')


    def set_image_palette(self, r, g, b):

        """Set the image palette"""

        self.imagebuffer = array.array('l')
        self.clear_cal_display()
        sz = len(r)
        i = 0
        self.pal = []
        while i < sz:
            rf = int(b[i])
            gf = int(g[i])
            bf = int(r[i])
            self.pal.append((rf<<16) | (gf<<8) | (bf))
            i += 1

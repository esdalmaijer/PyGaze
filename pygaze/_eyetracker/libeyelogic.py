# -*- coding = utf-8 -*-
#
# This file is part of PyGaze - the open-source toolbox for eye tracking
#
# PyGaze is a Python module for easily creating gaze contingent experiments
# or other software (as well as non-gaze contingent experiments/software)
# Copyright (C) 2012-2013 Edwin S. Dalmaijer
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>
#

import pygaze
from pygaze import settings
from pygaze.libtime import clock
from pygaze.screen import Screen
from pygaze.keyboard import Keyboard
from pygaze.sound import Sound
from pygaze._eyetracker.baseeyetracker import BaseEyeTracker
from threading import Event, Lock, Thread
from multiprocessing import Queue
import copy
import math

try:
    from pygaze._eyetracker.eyelogic.ELApi import *
except:
    print("Failed to import pygaze._eyetracker.eyelogic.ELApi")
    try:
        from eyelogic.ELApi import *
    except:
        print("Failed to import eyelogic.ELApi")
        raise Exception("Could not import EyeLogicTracker")

## converts an error code of connect( ) to a string
def errorstringConnect(returncode):
    if type(returncode) != ELApi.ReturnConnect:
        return "returncode is not of type ELApi.ReturnConnect"

    codes = {
        ELApi.ReturnConnect.SUCCESS: "no error, successfully connected to server",
        ELApi.ReturnConnect.NOT_INITED: "library not correctly initialized",
        ELApi.ReturnConnect.VERSION_MISMATCH: "version mismatch, please upgrade your EyeLogicServer to the newest version",
        ELApi.ReturnConnect.TIMEOUT: "cannot connect to server, is the server running?",
    }

    if returncode in codes.keys():
        return codes[returncode]
    else:
        return "unknown connection error"

## converts an error code of calibrate( ) to a string
def errorstringCalibrate(returncode):
    if type(returncode) != ELApi.ReturnCalibrate:
        return "returncode is not of type ELApi.ReturnCalibrate"

    codes = {
        ELApi.ReturnCalibrate.SUCCESS: "no error, calibration successful",
        ELApi.ReturnCalibrate.NOT_CONNECTED: "not connected to server",
        ELApi.ReturnCalibrate.NOT_TRACKING: "tracking not started",
        ELApi.ReturnCalibrate.INVALID_CALIBRATION_MODE: "calibration mode is invalid or not supported",
        ELApi.ReturnCalibrate.ALREADY_CALIBRATING: "calibration is already in progress",
        ELApi.ReturnCalibrate.FAILURE: "calibration was not successful or aborted",
    }

    if returncode in codes.keys():
        return codes[returncode]
    else:
        return "unknown calibration error"

def deg2pix(cmdist, angle, pixpercm):
    """Returns the value in pixels for given values (internal use)

    arguments
    cmdist    -- distance to display in centimeters
    angle        -- size of stimulus in visual angle
    pixpercm    -- amount of pixels per centimeter for display

    returns
    pixelsize    -- stimulus size in pixels (calculation based on size in
               visual angle on display with given properties)
    """

    cmsize = math.tan(math.radians(angle)) * float(cmdist)
    return cmsize * pixpercm

def pix2deg(cmdist, pixelsize, pixpercm):
    """Converts a distance on the screen in pixels into degrees of visual
    angle (internal use)
    
    arguments
    cmdist    -- distance to display in centimeters
    pixelsize    -- stimulus size in pixels
    pixpercm    -- amount of pixels per centimeter for display
    
    returns
    angle        -- size of stimulus in visual angle
    """
    
    cmsize = float(pixelsize) / pixpercm
    return 2 * cmdist * math.tan(math.radians(cmsize) / 2.)

g_api = None

@GazeSampleCallback
def gazeSampleCallback(sample = POINTER(ELGazeSample)):
    if g_api is None:
        return
    g_api.sampleLock.acquire()
    scaleX = g_api.dispsize[0] / g_api.rawResolution[0]
    scaleY = g_api.dispsize[1] / g_api.rawResolution[1]

    g_api.lastSample = ELGazeSample()
    g_api.lastSample.timestampMicroSec = sample.contents.timestampMicroSec
    g_api.lastSample.index = sample.contents.index
    if (sample.contents.porRawX == ELInvalidValue):
        g_api.lastSample.porRawX = ELInvalidValue
        g_api.lastSample.porRawY = ELInvalidValue
    else:
        g_api.lastSample.porRawX = sample.contents.porRawX * scaleX
        g_api.lastSample.porRawY = sample.contents.porRawY * scaleY
    if (sample.contents.porFilteredX == ELInvalidValue):
        g_api.lastSample.porFilteredX = ELInvalidValue
        g_api.lastSample.porFilteredY = ELInvalidValue
    else:
        g_api.lastSample.porFilteredX = sample.contents.porFilteredX * scaleX
        g_api.lastSample.porFilteredY = sample.contents.porFilteredY * scaleY
    if (sample.contents.porLeftX == ELInvalidValue):
        g_api.lastSample.porLeftX = ELInvalidValue
        g_api.lastSample.porLeftY = ELInvalidValue
    else:
        g_api.lastSample.porLeftX = sample.contents.porLeftX * scaleX
        g_api.lastSample.porLeftY = sample.contents.porLeftY * scaleY
    g_api.lastSample.eyePositionLeftX = sample.contents.eyePositionLeftX
    g_api.lastSample.eyePositionLeftY = sample.contents.eyePositionLeftY
    g_api.lastSample.eyePositionLeftZ = sample.contents.eyePositionLeftZ
    g_api.lastSample.pupilRadiusLeft = sample.contents.pupilRadiusLeft
    if (sample.contents.porRightX == ELInvalidValue):
        g_api.lastSample.porRightX = ELInvalidValue
        g_api.lastSample.porRightY = ELInvalidValue
    else:
        g_api.lastSample.porRightX = sample.contents.porRightX * scaleX
        g_api.lastSample.porRightY = sample.contents.porRightY * scaleY
    g_api.lastSample.eyePositionRightX = sample.contents.eyePositionRightX
    g_api.lastSample.eyePositionRightY = sample.contents.eyePositionRightY
    g_api.lastSample.eyePositionRightZ = sample.contents.eyePositionRightZ
    g_api.lastSample.pupilRadiusRight = sample.contents.pupilRadiusRight
    gs = copy.copy(g_api.lastSample)
    g_api.sampleLock.release()
    if g_api._recording.is_set():
        g_api._logging_queue.put(gs)

@EventCallback
def eventCallback(eventId):
    if (g_api is None):
        return

    e = ELEvent(eventId)
    if (e == ELEvent.SCREEN_CHANGED):
        screenConfig = self.api.getScreenConfig()
        self.rawResolution = (screenConfig.resolutionX, screenConfig.resolutionY)
        pass
    elif (e == ELEvent.CONNECTION_CLOSED):
        self.api.registerGazeSampleCallback( None )
        g_api._connected.clear()
        g_api._recording.clear()
        g_api._calibrated.clear()
    elif (e == ELEvent.DEVICE_CONNECTED):
        pass
    elif (e == ELEvent.DEVICE_DISCONNECTED):
        g_api._recording.clear()
        g_api._calibrated.clear()
    elif (e == ELEvent.TRACKING_STOPPED):
        g_api._recording.clear()
        g_api._calibrated.clear()

## A class for EyeLogic eye tracker objects.
class EyeLogicTracker(BaseEyeTracker):

## Initializes the EyeTracker object.
    def __init__(self, display,
        logfile=settings.LOGFILE, \
        eventdetection=settings.EVENTDETECTION, \
        saccade_velocity_threshold=35, \
        saccade_acceleration_threshold=9500, \
        blink_threshold=settings.BLINKTHRESH, \
        **args):

        # try to copy docstrings (but ignore it if it fails, as we do
        # not need it for actual functioning of the code)
        try:
            copy_docstr(BaseEyeTracker, EyeLogicTracker)
        except:
            # we're not even going to show a warning, since the copied
            # docstring is useful for code editors; these load the docs
            # in a non-verbose manner, so warning messages would be lost
            pass

        self.disp = display
        self.screen = Screen()
        self.dispsize = self.disp.dispsize # display size in pixels
        self.screensize = settings.SCREENSIZE # display size in cm
        self.kb = Keyboard(keylist=['space', 'escape', 'q'], timeout=1)
        self.errorbeep = Sound(osc='saw', freq=100, length=100)

        # show a message
        self.screen.clear()
        self.screen.draw_text(
            text="Initialising the eye tracker, please wait...",
            fontsize=20)
        self.disp.fill(self.screen)
        self.disp.show()

        # output file properties
        self.logfile = logfile

        # eye tracker properties
        self._recording = Event()
        self._recording.clear()
        self._calibrated = Event()
        self._calibrated.clear()
        self.eye_used = 2 # 0=left, 1=right, 2=binocular
        self.sampleLock = Lock()
        self.lastSample = None
        self.maxtries = 100 # number of samples obtained before giving up (for obtaining accuracy and tracker distance information, as well as starting or stopping recording)

        # event detection properties
        self.pxfixtresh = 50;
        self.fixtresh = 1.5 # degrees; maximal distance from fixation start (if gaze wanders beyond this, fixation has stopped)
        self.fixtimetresh = 100 # milliseconds; amount of time gaze has to linger within self.fixtresh to be marked as a fixation

        self.spdtresh = saccade_velocity_threshold # degrees per second; saccade velocity threshold
        self.accthresh = saccade_acceleration_threshold # degrees per second**2; saccade acceleration threshold
        self.blinkthresh = blink_threshold # milliseconds; blink detection threshold used in PyGaze method
        self.eventdetection = eventdetection

        self._log_vars = [ \
            "timestampMicroSec", \
            "index", \
            "porFilteredX", \
            "porFilteredY", \
            "porLeftX", \
            "porLeftY", \
            "pupilRadiusLeft", \
            "porRightX", \
            "porRightY", \
            "pupilRadiusRight", \
            ]
        # Open a new log file.
        dir_name = os.path.dirname(logfile)
        file_name = os.path.basename(logfile)
        name, ext = os.path.splitext(file_name)
        self._data_file_path = os.path.join(dir_name, name+".eyelogic.csv")
        self._log_file = open(self._data_file_path, "w")
        # Write a header to the log.
        header = ["TYPE"]
        header.extend(self._log_vars)
        self._sep = ";"
        self._log_file.write("Sep="+self._sep+"\n")
        self._log_file.write(self._sep.join(map(str, header)))
        # Create a lock to prevent simultaneous access to the log file.
        self._logging_queue = Queue()
        self._logging_queue_empty = Event()
        self._logging_queue_empty.set()
        self._connected = Event()
        self._connected.set()
        self._log_counter = 0
        self._log_consolidation_freq = 60
        
        self._logging_thread = Thread( target=self.loggingThread, \
                name='PyGaze_EyeLogic_Logging', args=[])

        global g_api
        g_api = self

        # log
        self.log("pygaze initiation")
        #self.log("experiment = {}".format(self.description))
        #self.log("participant = {}".format(self.participant))
        self.log("display resolution = {}x{}".format(self.dispsize[0], \
            self.dispsize[1]))
        self.log("display size in cm = {}x{}".format(self.screensize[0], \
            self.screensize[1]))
        self.log("fixation threshold = {} degrees".format(self.fixtresh))
        self.log("speed threshold = {} degrees/second".format(self.spdtresh))
        self.log("acceleration threshold = {} degrees/second**2".format( \
            self.accthresh))

        # connect
        self.api = ELApi( "PyGaze" )
        self.api.registerGazeSampleCallback( gazeSampleCallback )
        self.api.registerEventCallback( eventCallback )

        resultConnect = self.api.connect()
        if (resultConnect != ELApi.ReturnConnect.SUCCESS):
            self._connected.clear()
            raise Exception("Cannot connect to EyeLogic server = {}".format(errorstringConnect(resultConnect)))
        self._connected.set()

        screenConfig = self.api.getScreenConfig()
        self.log("eye tracker is mounted on screen {}".format(screenConfig.id))
        self.rawResolution = (screenConfig.resolutionX, screenConfig.resolutionY)
        self.log("raw screen resolution = {}x{}".format(
            self.rawResolution[0], self.rawResolution[1]))
        self.log("end pygaze initiation")

        deviceConfig = self.api.getDeviceConfig()
        if (deviceConfig.deviceSerial == 0):
            raise Exception("no eye tracking device connected")
        if (len(deviceConfig.frameRates) == 0):
            raise Exception("failed to read out device configuration")
        g_api.sampleRate = deviceConfig.frameRates[0]
        g_api.sampleTime = 1000.0 / g_api.sampleRate
        g_api.log("samplerate = {} Hz".format(g_api.sampleRate))
        g_api.log("sampletime = {} ms".format(g_api.sampleTime))
        self._logging_thread.start()

        self.screen.clear()
        self.disp.fill(self.screen)
        self.disp.show()


    def loggingThread(self):
        while self._connected.is_set():
            
            # Check if the sample Queue is empty.
            if self._logging_queue.empty():
                # Signal to other Threads that the logging Queue is empty.
                if not self._logging_queue_empty.is_set():
                    self._logging_queue_empty.set()
            
            # Process data from the Queue.
            else:
                # Signal to other Threads that the Queue isn't empty.
                if self._logging_queue_empty.is_set():
                    self._logging_queue_empty.clear()
                # Get the next object from the Queue.
                sample = self._logging_queue.get()
                # Log the message string and/or the sample.
                if type(sample) in [tuple, list]:
                    self._write_tuple(sample)
                elif type(sample) == ELGazeSample:
                    self._write_sample(sample)
                else:
                    print("WARNING = Unrecognised object in log queue = '{}'".format( \
                        sample))
                # Increment the log counter.
                self._log_counter += 1
                # Check if the log file needs to be consolidated.
                if self._log_counter % self._log_consolidation_freq == 0:
                    # Internal buffer to RAM.
                    self._log_file.flush()
                    # RAM to disk.
                    os.fsync(self._log_file.fileno())
                    # Release the log file lock.
    
    def _write_sample(self, sample):
        # Construct a list with the sample data.
        line = ["DAT"]
        for var in self._log_vars:
            line.append(sample.__getattribute__(var))
        # Log the sample to the log file.
        self._log_file.write("\n" + self._sep.join(map(str, line)))

    def _write_tuple(self, tup):

        # Construct a list values that need to be logged.
        line = []
        # Add the values that need to be logged. Usually this will be ("MSG",
        # timestamp, message).
        line.extend(tup)
        # Pad the list so that it will be of equal length to the sample
        # lines, which makes it easier to be read into a spreadsheet editor
        # and by some read_csv functions.
        line.extend([""] * (len(self._log_vars) - len(line) - 1))

        # Log the line to the log file.
        self._log_file.write("\n" + self._sep.join(map(str, line)))

## Calibrates the eye tracking system.
    def calibrate(self):
        #self.screen.clear()
        #self.screen.draw_text(
        #    text="Calibrate EyeTracker",
        #    fontsize=20)
        #self.disp.fill(self.screen)
        #self.disp.show()

        if (not self._recording.is_set()):
            resultTracking = self.api.requestTracking(0)
            if (resultTracking != ELApi.ReturnStart.SUCCESS):
                raise Exception("unable to start eye tracker")

        resultCalibrate = self.api.calibrate(0)
        if (resultCalibrate != ELApi.ReturnCalibrate.SUCCESS):
            self.api.unrequestTracking()
            self.errorbeep.play()
            raise Exception("Calibration failed = {}".format(errorstringCalibrate(resultCalibrate)))
        self._calibrated.set()

        # NOISE CALIBRATION
        self.screen.clear()
        self.screen.draw_text(
            text="Noise calibration. Please look at the dot, and press any key to start.",
            fontsize=20, \
            pos=(int(self.dispsize[0]/2),int(self.dispsize[1]*0.3)))
        x = int(float(self.dispsize[0]) / 2.0)
        y = int(float(self.dispsize[1]) / 2.0)
        self.screen.draw_fixation(fixtype="dot", pos=(x,y))
        self.disp.fill(self.screen)
        self.disp.show()
        self.kb.get_key(keylist=None, timeout=None, flush=True)

        # wait for a bit, to allow participant to fixate
        clock.pause(500)

        # get distance to screen
        screendist = 0
        i = 0
        while screendist == 0 and i < self.maxtries:
            i = i+1
            self.sampleLock.acquire()
            if (self.lastSample is not None):
                if self.eye_used != 1 and self.lastSample.eyePositionLeftZ != ELInvalidValue:
                    screendist = self.lastSample.eyePositionLeftZ / 10.0 # eyePositionZ is in mm; screendist is in cm
                elif self.eye_used != 0 and self.lastSample.eyePositionRightZ != ELInvalidValue:
                    screendist = self.lastSample.eyePositionRightZ / 10.0
            self.sampleLock.release()
            clock.pause(int(self.sampleTime))
        if i >= self.maxtries:
            self.api.unrequestTracking()
            self.errorbeep.play()
            raise Exception("unable to receive gaze data for noise calibration")

        # get samples
        sl = [self.sample()] # samplelist, prefilled with 1 sample to prevent sl[-1] from producing an error; first sample will be ignored for RMS calculation
        t0 = clock.get_time() # starting time
        while clock.get_time() - t0 < 1000:
            s = self.sample() # sample
            if s[0] != -1 and s[1] != -1 and s[0] != ELInvalidValue and s[1] != ELInvalidValue:
                sl.append(s)
            clock.pause(int(self.sampleTime))
        if (len(sl) < 2):
            if (not self._recording.is_set()):
                self.api.unrequestTracking()
            return False

        # calculate RMS noise
        Xvar = []
        Yvar = []
        Xmean = 0.
        Ymean = 0.
        for i in range(2,len(sl)):
            Xvar.append((sl[i][0]-sl[i-1][0])**2)
            Yvar.append((sl[i][1]-sl[i-1][1])**2)
            Xmean += sl[i][0]
            Ymean += sl[i][1]
        XRMS = (sum(Xvar) / len(Xvar))**0.5
        YRMS = (sum(Yvar) / len(Yvar))**0.5
        Xmean = Xmean / (len(sl)-2)
        Ymean = Ymean / (len(sl)-2)
        self.pxdsttresh = (XRMS, YRMS)

        # calculate pixels per cm
        pixpercm = (self.dispsize[0]/float(self.screensize[0]) + self.dispsize[1]/float(self.screensize[1])) / 2

        # get accuracy
        accuracyPxX = abs( Xmean - x )
        accuracyPxY = abs( Ymean - y )
        self.accuracy = ( pix2deg(screendist, accuracyPxX, pixpercm), \
                          pix2deg(screendist, accuracyPxY, pixpercm) )

        # calculate thresholds based on tracker settings
        self.pxfixtresh = deg2pix(screendist, self.fixtresh, pixpercm)
        self.pxaccuracy = (accuracyPxX, accuracyPxY )
        self.pxspdtresh = deg2pix(screendist, self.spdtresh/1000.0, pixpercm) # in pixels per millisecond
        self.pxacctresh = deg2pix(screendist, self.accthresh/1000.0, pixpercm) # in pixels per millisecond**2

        ## log
        self.log("pygaze calibration")
        self.log("accuracy (degrees) = X={}, Y={}".format( \
            self.accuracy[0], self.accuracy[1] ))
        self.log("accuracy (in pixels) = X={}, Y={}".format( \
            self.pxaccuracy[0], self.pxaccuracy[1]))
        self.log("precision (RMS noise in pixels) = X={}, Y={}".format( \
            self.pxdsttresh[0], self.pxdsttresh[1]))
        self.log("distance between participant and display = {} cm".format(screendist))
        self.log("fixation threshold = {} pixels".format(self.pxfixtresh))
        self.log("speed threshold = {} pixels/ms".format(self.pxspdtresh))
        self.log("acceleration threshold = {} pixels/ms**2".format(self.pxacctresh))
        
        if (not self._recording.is_set()):
            self.api.unrequestTracking()
        return True

## Neatly closes connection to tracker.
    def close(self):
        if self._recording.is_set():
            self.stop_recording()
            
        # Wait until the Queue is empty, or until 60 seconds have passed.
        queue_empty = self._logging_queue_empty.wait(timeout=15.0)
        if not queue_empty:
            print("WARNING = Logging Thread timeout occurred; something might have gone wrong!")
        
        # Signal to the Threads to stop.
        self._connected.clear()
        
        # Close the log file.
        self._log_file.close()
        
        # Close the connection.
        self.api.disconnect()
        self._connected = False

## Checks if the tracker is connected.
    def connected(self):
        isConnected = self.api.isConnected()
        if isConnected:
            self._connected.set()
        else:
            self._connected.clear()
        return isConnected

## Performs a drift check
    def drift_correction(self, pos=None, fix_triggered=False):
        return True

## Performs a fixation triggered drift correction by collecting
#  a number of samples and calculating the average distance from the
#  fixation position.
    def fix_triggered_drift_correction(self, pos=None, min_samples=10, max_dev=60, reset_threshold=30):
        pass

## Returns the difference between tracker time and PyGaze time,
#  which can be used to synchronize timing
    def get_eyetracker_clock_async(self):
        return 0

## Writes a message to the log file.
    def log(self, msg):
        # Get current timestamp.
        self.sampleLock.acquire()
        if self.lastSample is None:
            t = 0
        else:
            t = self.lastSample.timestampMicroSec
        self.sampleLock.release()

        # Construct a tuple, and add it to the queue.
        self._logging_queue.put(("MSG", t, msg))

## Writes a variable's name and value to the log file
    def log_var(self, var, val):
        pass

## Returns the newest pupil size sample
    def pupil_size(self):
        self.sampleLock.acquire()
        pupilSize = -1
        if (self.lastSample is not None):
            if self.eye_used == 0:
                pupilSize = 2.*self.lastSample.pupilRadiusLeft;
            elif self.eye_used == 1:
                pupilSize = 2.*self.lastSample.pupilRadiusRight;
            elif self.eye_used == 2:
                pupilSize = self.lastSample.pupilRadiusLeft + self.lastSample.pupilRadiusRight;
        self.sampleLock.release()
        return pupilSize

## Returns newest available gaze position.
    def sample(self):
        self.sampleLock.acquire()
        por = (-1, -1)
        if (self.lastSample is not None):
            if self.eye_used == 0:
                por = (self.lastSample.porLeftX, self.lastSample.porLeftY)
            elif self.eye_used == 1:
                por = (self.lastSample.porRightX, self.lastSample.porRightY)
            elif self.eye_used == 2:
                por = (self.lastSample.porFilteredX, self.lastSample.porFilteredY)
        self.sampleLock.release()
        return por

# Directly sends a command to the eye tracker.
    def send_command(self, cmd):
        pass

## Set the event detection type to either PyGaze algorithms, or
#  native algorithms.
    def set_detection_type(self, eventdetection):
        # detection type for saccades, fixations, blinks (pygaze or native)
        return ('pygaze','pygaze','pygaze')

## Specifies a custom function to draw the calibration target.
    def set_draw_calibration_target_func(self, func):
        pass

## Specifies a custom function to draw the drift-correction target.
    def set_draw_drift_correction_target_func(self, func):
        pass

## Logs the eye_used variable, based on which eye was specified
#  (if both eyes are being tracked, the left eye is used)
    def set_eye_used(self):
        pass

## Starts recording.
    def start_recording(self):
        resultTracking = self.api.requestTracking(0)
        if (resultTracking != ELApi.ReturnStart.SUCCESS):
            raise Exception("unable to start eye tracker")
        self._recording.set()

## Sends a status message to the eye tracker, which is displayed in the tracker's GUI
    def status_msg(self, msg):
        pass

## Stops recording.
    def stop_recording(self):
        self.api.unrequestTracking()
        self._recording.clear()

## Waits for an event.
    def wait_for_event(self, event):
        print("waitforevent", flush=True)

        if event == 3: # STARTBLINK
            return self.wait_for_blink_start()
        elif event == 4: # ENDBLINK
            return self.wait_for_blink_end()
        elif event == 5: # STARTSACC
            return self.wait_for_saccade_start()
        elif event == 6: # ENDSACC
            return self.wait_for_saccade_end()
        elif event == 7: # STARTFIX
            return self.wait_for_fixation_start()
        elif event == 8: # ENDFIX
            return self.wait_for_fixation_end()
        else:
           raise Exception("wait_for_event({}) is not supported".format(event))

## Waits for a blink end and returns the blink ending time.
    def wait_for_blink_end(self):
        blinking = True

        # loop while there is a blink
        while blinking:
            # get newest sample
            gazepos = self.sample()
            # check if it's valid
            if self.is_valid_sample(gazepos):
                # if it is a valid sample, blinking has stopped
                blinking = False

        # return timestamp of blink end
        return clock.get_time()

## Waits for a blink start and returns the blink starting time.
    def wait_for_blink_start(self):
        blinking = False

        # loop until there is a blink
        while not blinking:
            # get newest sample
            gazepos = self.sample()
            # check if it's a valid sample
            if not self.is_valid_sample(gazepos):
                # get timestamp for possible blink start
                t0 = clock.get_time()
                # loop until a blink is determined, or a valid sample occurs
                while not self.is_valid_sample(self.sample()):
                    # check if time has surpassed BLINKTHRESH
                    if clock.get_time()-t0 >= self.blinkthresh:
                        # return timestamp of blink start
                        return t0

## Returns time and gaze position when a fixation has ended.
    def wait_for_fixation_end(self):
        print("wait_for_fixation_end", flush=True)
        # function assumes that a 'fixation' has ended when a deviation of more than fixtresh
        # from the initial 'fixation' position has been detected

        # get starting time and position
        stime, spos = self.wait_for_fixation_start()

        # loop until fixation has ended
        while True:
            # get new sample
            npos = self.sample() # get newest sample
            # check if sample is valid
            if self.is_valid_sample(npos):
                # check if sample deviates to much from starting position
                if (npos[0]-spos[0])**2 + (npos[1]-spos[1])**2 > self.pxfixtresh**2: # Pythagoras
                    # break loop if deviation is too high
                    break

        return clock.get_time(), spos

## Returns starting time and position when a fixation is started.
    def wait_for_fixation_start(self):
        print("wait_for_fixation_start", flush=True)

        # function assumes a 'fixation' has started when gaze position
        # remains reasonably stable for self.fixtimetresh

        # get starting position
        spos = self.sample()
        while not self.is_valid_sample(spos):
            spos = self.sample()

        # get starting time
        t0 = clock.get_time()

        # wait for reasonably stable position
        moving = True
        while moving:
            # get new sample
            npos = self.sample()
            # check if sample is valid
            if self.is_valid_sample(npos):
                # check if new sample is too far from starting position
                if (npos[0]-spos[0])**2 + (npos[1]-spos[1])**2 > self.pxfixtresh**2: # Pythagoras
                    # if not, reset starting position and time
                    spos = copy.copy(npos)
                    t0 = clock.get_time()
                # if new sample is close to starting sample
                else:
                    # get timestamp
                    t1 = clock.get_time()
                    # check if fixation time threshold has been surpassed
                    if t1 - t0 >= self.fixtimetresh:
                        # return time and starting position
                        return t1, spos

## Returns ending time, starting and end position when a saccade is
#  ended.
    def wait_for_saccade_end(self):
        # get starting position (no blinks)
        t0, spos = self.wait_for_saccade_start()
        # get valid sample
        prevpos = self.sample()
        while not self.is_valid_sample(prevpos):
            prevpos = self.sample()
        # get starting time, intersample distance, and velocity
        t1 = clock.get_time()
        s = ((prevpos[0]-spos[0])**2 + (prevpos[1]-spos[1])**2)**0.5 # = intersample distance = speed in px/sample
        v0 = s / (t1-t0)

        # run until velocity and acceleration go below threshold
        saccadic = True
        while saccadic:
            # get new sample
            newpos = self.sample()
            t1 = clock.get_time()
            if self.is_valid_sample(newpos) and newpos != prevpos:
                # calculate distance
                s = ((newpos[0]-prevpos[0])**2 + (newpos[1]-prevpos[1])**2)**0.5 # = speed in pixels/sample
                # calculate velocity
                v1 = s / (t1-t0)
                # calculate acceleration
                a = (v1-v0) / (t1-t0) # acceleration in pixels/sample**2 (actually is v1-v0 / t1-t0; but t1-t0 = 1 sample)
                # check if velocity and acceleration are below threshold
                if v1 < self.pxspdtresh and (a > -1*self.pxacctresh and a < 0):
                    saccadic = False
                    epos = newpos[:]
                    etime = clock.get_time()
                # update previous values
                t0 = copy.copy(t1)
                v0 = copy.copy(v1)
            # udate previous sample
            prevpos = newpos[:]

        return etime, spos, epos

## Returns starting time and starting position when a saccade is started.
    def wait_for_saccade_start(self):
        # get starting position (no blinks)
        newpos = self.sample()
        while not self.is_valid_sample(newpos):
            newpos = self.sample()
        # get starting time, position, intersampledistance, and velocity
        t0 = clock.get_time()
        prevpos = newpos[:]
        s = 0
        v0 = 0

        # get samples
        saccadic = False
        while not saccadic:
            # get new sample
            newpos = self.sample()
            t1 = clock.get_time()
            if self.is_valid_sample(newpos) and newpos != prevpos:
                # check if distance is larger than precision error
                sx = newpos[0]-prevpos[0]; sy = newpos[1]-prevpos[1]
                if (sx/self.pxdsttresh[0])**2 + (sy/self.pxdsttresh[1])**2 > self.weightdist: # weigthed distance = (sx/tx)**2 + (sy/ty)**2 > 1 means movement larger than RMS noise
                    # calculate distance
                    s = ((sx)**2 + (sy)**2)**0.5 # intersampledistance = speed in pixels/ms
                    # calculate velocity
                    v1 = s / (t1-t0)
                    # calculate acceleration
                    a = (v1-v0) / (t1-t0) # acceleration in pixels/ms**2
                    # check if either velocity or acceleration are above threshold values
                    if v1 > self.pxspdtresh or a > self.pxacctresh:
                        saccadic = True
                        spos = prevpos[:]
                        stime = clock.get_time()
                    # update previous values
                    t0 = copy.copy(t1)
                    v0 = copy.copy(v1)

                # udate previous sample
                prevpos = newpos[:]

        return stime, spos

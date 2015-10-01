# -*- coding: utf-8 -*-
from pygaze.defaults import *
from pygaze.libtime import clock
try:
    from constants import *
except Exception:
    pass

import pygaze
from pygaze.screen import Screen
from pygaze._eyetracker.baseeyetracker import BaseEyeTracker
# we try importing the copy_docstr function, but as we do not really need it
# for a proper functioning of the code, we simply ignore it when it fails to
# be imported correctly
try:
    from pygaze._misc.misc import copy_docstr
except Exception:
    pass


def message(msg):

    """Prints a timestamp and message to the console"""

    print("%d\t%s" % (int(clock.get_time()), msg))


class DumbDummy(BaseEyeTracker):

    """A dummy class to run experiments in 'dumb dummy' mode, where nothing happens (NO simulation!)"""


    def __init__(self, display):

        """Initiates a 'dumb dummy' object, that doesn't do a thing

        arguments
        display        --    a pygaze display.Display instance

        keyword arguments
        None
        """

        # try to copy docstrings (but ignore it if it fails, as we do
        # not need it for actual functioning of the code)
        try:
            copy_docstr(BaseEyeTracker, DumbDummy)
        except Exception:
            # we're not even going to show a warning, since the copied
            # docstring is useful for code editors; these load the docs
            # in a non-verbose manner, so warning messages would be lost
            pass

        self.recording = False
        self.blinking = False
        self.bbpos = (DISPSIZE[0]/2, DISPSIZE[1]/2)

        self.display = display
        self.screen = Screen(disptype=DISPTYPE, mousevisible=False)


    def send_command(self, cmd):

        """Dummy command, messages command instead of sending it to the eyetracker"""

        message("The following command would have been given to the eyetracker: " + str(cmd))


    def log(self, msg):

        """Dummy log message, messages message instead of sending it to the eyetracker"""

        message("The following message would have been logged to the EDF: " + str(msg))


    def log_var(self, var, val):

        """Dummy varlog, messages variable and value instead of sending it to the eyetracker"""

        message("The following variable would have been logged to the EDF: " + str(var) + ", value: " + str(val))


    def status_msg(self, msg):

        """Dummy status message, messages message instead of sending it to the eyetracker"""

        message("The following status message would have been visible on the experimentor PC: " + str(msg))


    def connected(self):

        """Dummy connection status"""

        message("Dummy mode, eyetracker not connected.")

        return True


    def calibrate(self):

        """Dummy calibration"""

        message("Calibration would now take place")


    def drift_correction(self, pos=None, fix_triggered=False):

        """Dummy drift correction"""

        message("Drift correction would now take place")

        return True


    def prepare_drift_correction(self, pos):

        """Dummy drift correction preparation"""

        message("Drift correction preparation would now take place")


    def fix_triggered_drift_correction(self, pos=None, min_samples=30, max_dev=60, reset_threshold=10):

        """Dummy drift correction (fixation triggered)"""

        message("Drift correction (fixation triggered) would now take place")

        return True


    def start_recording(self):

        """Dummy for starting recording, messages what would have been the recording start"""

        self.recording = True

        message("Recording would have started now")


    def stop_recording(self):

        """Dummy for stopping recording, messages what would have been the recording end"""

        self.recording = False

        message("Recording would have stopped now")


    def close(self):

        """Dummy for closing connection with eyetracker, messages what would have been connection closing time"""

        if self.recording:
            self.stop_recording()

        message("eyetracker connection would have closed now")


    def set_eye_used(self):

        """Dummy for setting which eye to track (does nothing)"""

        message("Which eye to track would now be set")


    def pupil_size(self):

        """Returns dummy pupil size"""

        return 19


    def sample(self):

        """Returns dummy gaze position"""

        return (19,19)


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

        return clock.get_time(), (19,19)


    def wait_for_saccade_end(self):

        """Returns ending time, starting and end position when a simulated saccade is ended"""

        # function assumes that a 'saccade' has ended when 'gaze' position remains reasonably
        # (i.e.: within maxerr) stable for five samples
        # for saccade start algorithm, see wait_for_fixation_start

        stime, spos = self.wait_for_saccade_start()

        return clock.get_time(), spos, (190,190)


    def wait_for_fixation_start(self):

        """Returns starting time and position when a simulated fixation is started"""

        return clock.get_time(), (19,19)


    def wait_for_fixation_end(self):

        """Returns time and gaze position when a simulated fixation is ended"""

        stime, spos = self.wait_for_fixation_start()

        return clock.get_time(), spos


    def wait_for_blink_start(self):

        """Returns starting time and position of a simulated blink"""

        return clock.get_time(), (19,19)


    def wait_for_blink_end(self):

        """Returns ending time and position of a simulated blink (mousebuttonup)"""

        return clock.get_time(), (19,19)

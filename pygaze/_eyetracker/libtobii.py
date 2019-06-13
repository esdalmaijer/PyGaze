# This code is meant to be part of PyGaze,
# https://github.com/esdalmaijer/PyGaze/
# Changes here should be added to PyGaze repo, as a pull request.

import time
import os
import math
import copy
import tobii_research as tr

from pygaze import settings
from pygaze.screen import Screen
from pygaze.keyboard import Keyboard
from pygaze._eyetracker.baseeyetracker import BaseEyeTracker
from pygaze.libtime import clock


class TobiiProTracker(BaseEyeTracker):
    """A class for Tobii Pro EyeTracker objects"""

    def __init__(self, display, logfile=settings.LOGFILE,
                 eventdetection=settings.EVENTDETECTION,
                 saccade_velocity_threshold=35,
                 saccade_acceleration_threshold=9500,
                 blink_threshold=settings.BLINKTHRESH, **args):
        """Initializes a TobiiProTracker instance

        arguments
        display	--	a pygaze.display.Display instance

        keyword arguments
        None
        """

        self.gaze = []

        self.disp = display

        # initialize a screen
        self.screen = Screen()

        # initialize keyboard
        self.kb = Keyboard(keylist=['space', 'escape', 'q'], timeout=1)

        self.recording = False

        self.screendist = settings.SCREENDIST

        if hasattr(settings, 'TRACKERSERIALNUMBER'):
            # Search for a specific eye tracker
            self.eyetrackers = [t for t in tr.find_all_eyetrackers() if t.serial_number == settings.TRACKERSERIALNUMBER]
        else:
            # Search for all eye trackers (The first one found will be selected)
            self.eyetrackers = tr.find_all_eyetrackers()

        if self.eyetrackers:
            self.eyetracker = self.eyetrackers[0]
        else:
            print("WARNING! libtobii.TobiiProTracker.__init__: no eye trackers found!")
            return

        self.LEFT_EYE = 0
        self.RIGHT_EYE = 1
        self.BINOCULAR = 2
        self.eye_used = 0  # 0=left, 1=right, 2=binocular

        # calibration and validation points
        lb = 0.1  # left bound
        xc = 0.5  # horizontal center
        rb = 0.9  # right bound
        ub = 0.1  # upper bound
        yc = 0.5  # vertical center
        bb = 0.9  # bottom bound

        self.points_to_calibrate = [self._norm_2_px(p) for p in [(lb, ub), (rb, ub), (xc, yc), (lb, bb), (rb, bb)]]

        # event detection properties

        # maximal distance from fixation start (if gaze wanders beyond this, fixation has stopped)
        self.fixtresh = 1.5  # degrees
        # amount of time gaze has to linger within self.fixtresh to be marked as a fixation
        self.fixtimetresh = 100  # milliseconds
        # saccade velocity threshold
        self.spdtresh = saccade_velocity_threshold  # degrees per second
        # saccade acceleration threshold
        self.accthresh = saccade_acceleration_threshold  # degrees per second**2
        # blink detection threshold used in PyGaze method
        self.blinkthresh = blink_threshold  # milliseconds

        # weighted distance, used for determining whether a movement is due to measurement error
        # (1 is ok, higher is more conservative and will result in only larger saccades to be detected)
        self.weightdist = 10

        self.eventdetection = eventdetection

        self.screensize = settings.SCREENSIZE  # display size in cm
        self.pixpercm = (self.disp.dispsize[0] / float(self.screensize[0]) +
                         self.disp.dispsize[1] / float(self.screensize[1])) / 2.0
        self.errdist = 2  # degrees; maximal error for drift correction
        self.pxerrdist = self._deg2pix(self.screendist, self.errdist, self.pixpercm)

        self.event_data = []

        self.t0 = None
        self._write_enabled = True

        self.datafile = open("{0}_TOBII_output.tsv".format(logfile), 'w')

        # initiation report
        self.datafile.write("pygaze initiation report start\n")
        self.datafile.write("display resolution: %sx%s\n" % (self.disp.dispsize[0], self.disp.dispsize[1]))
        self.datafile.write("display size in cm: %sx%s\n" % (self.screensize[0], self.screensize[1]))
        self.datafile.write("fixation threshold: %s degrees\n" % self.fixtresh)
        self.datafile.write("speed threshold: %s degrees/second\n" % self.spdtresh)
        self.datafile.write("acceleration threshold: %s degrees/second**2\n" % self.accthresh)
        self.datafile.write("pygaze initiation report end\n")

    def _norm_2_px(self, normalized_point):
        return (round(normalized_point[0] * self.disp.dispsize[0], 0),
                round(normalized_point[1] * self.disp.dispsize[1], 0))

    def _px_2_norm(self, pixelized_point):
        return (pixelized_point[0] / self.disp.dispsize[0], pixelized_point[1] / self.disp.dispsize[1])

    def _mean(self, array):
        if array:
            a = [s for s in array if s is not None]
            return sum(a) / float(len(a))

    def _deg2pix(self, cmdist, angle, pixpercm):
        return pixpercm * math.tan(math.radians(angle)) * float(cmdist)

    def log_var(self, var, val):
        """Writes a variable to the log file

        arguments
        var		-- variable name
        val		-- variable value

        returns
        Nothing	-- uses native log function to include a line
                    in the log file in a "var NAME VALUE" layout
        """
        self.log("var %s %s" % (var, val))

    def set_eye_used(self):
        """Logs the eye_used variable, based on which eye was specified.

        arguments
        None

        returns
        Nothing	-- logs which eye is used by calling self.log_var, e.g.
                   self.log_var("eye_used", "right")
        """
        if self.eye_used == self.BINOCULAR:
            self.log_var("eye_used", "binocular")
        elif self.eye_used == self.RIGHT_EYE:
            self.log_var("eye_used", "right")
        else:
            self.log_var("eye_used", "left")

    def is_valid_sample(self, sample):
        """Checks if the sample provided is valid, based on Tobii specific
        criteria (for internal use)

        arguments
        sample		--	a (x,y) gaze position tuple, as returned by
                        self.sample()

        returns
        valid			--	a Boolean: True on a valid sample, False on
                        an invalid sample
        """
        return sample != (-1, -1)

    def _on_gaze_data(self, gaze_data):
        self.gaze.append(gaze_data)
        if self._write_enabled:
            self._write_sample(gaze_data)

    def start_recording(self):
        """Starts recording eye position

        arguments
        None

        returns
        None		-- sets self.recording to True when recording is
                   successfully started
        """
        if not self.t0 and self._write_enabled:
            self.t0 = tr.get_system_time_stamp()
            self._write_header()

        if self.recording:
            print("WARNING! libtobii.TobiiProTracker.start_recording: Recording already started!")
            self.gaze = []
        else:
            self.gaze = []
            self.eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, self._on_gaze_data, as_dictionary=True)
            time.sleep(1)
            self.recording = True

    def stop_recording(self):
        """Stop recording eye position

        arguments
        None

        returns
        Nothing	-- sets self.recording to False when recording is
                   successfully started
        """
        if self.recording:
            self.eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA)
            self.recording = False
            self.event_data = []
            self._flush_to_file()
        else:
            print("WARNING! libtobii.TobiiProTracker.stop_recording: A recording has not been started!")

    def sample(self):
        """Returns newest available gaze position

        The gaze position is relative to the self.eye_used currently selected.
        If both eyes are selected, the gaze position is averaged from the data of both eyes.

        arguments
        None

        returns
        sample	-- an (x,y) tuple or a (-1,-1) on an error
        """

        if not self.gaze: # If no gaze samples have been collected
            return -1, -1
        gaze_sample = copy.copy(self.gaze[-1])
        if self.eye_used == self.LEFT_EYE and gaze_sample["left_gaze_point_validity"]:
            return self._norm_2_px(gaze_sample["left_gaze_point_on_display_area"])
        if self.eye_used == self.RIGHT_EYE and gaze_sample["right_gaze_point_validity"]:
            return self._norm_2_px(gaze_sample["right_gaze_point_on_display_area"])
        if self.eye_used == self.BINOCULAR:
            if gaze_sample["left_gaze_point_validity"] and gaze_sample["right_gaze_point_validity"]:
                left_sample = self._norm_2_px(gaze_sample["left_gaze_point_on_display_area"])
                right_sample = self._norm_2_px(gaze_sample["right_gaze_point_on_display_area"])
                return (self._mean([left_sample[0], right_sample[0]]), self._mean([left_sample[1], right_sample[1]]))
            if gaze_sample["left_gaze_point_validity"]:
                return self._norm_2_px(gaze_sample["left_gaze_point_on_display_area"])
            if gaze_sample["right_gaze_point_validity"]:
                return self._norm_2_px(gaze_sample["right_gaze_point_on_display_area"])
        return (-1, -1)

    def pupil_size(self):
        """Returns newest available pupil size

        arguments
        None

        returns
        pupilsize	-- a float if only eye is selected or only one eye has valid data.
                    -- a tuple with two floats if both eyes are selected.
                    -- -1 if there is no valid pupil data available.
        """
        if self.gaze:
            gaze_sample = copy.copy(self.gaze[-1])
            if self.eye_used == self.BINOCULAR:
                pupil_data = [-1, -1]
                if gaze_sample["left_pupil_validity"]:
                    pupil_data[0] = gaze_sample["left_pupil_diameter"]
                if gaze_sample["right_pupil_validity"]:
                    pupil_data[1] = gaze_sample["right_pupil_diameter"]
                return tuple(pupil_data)
            if self.eye_used == self.LEFT_EYE and gaze_sample["left_pupil_validity"]:
                return gaze_sample["left_pupil_diameter"]
            if self.eye_used == self.RIGHT_EYE and gaze_sample["right_pupil_validity"]:
                return gaze_sample["right_pupil_diameter"]
        return -1

    def calibrate(self, calibrate=True, validate=True):
        """Calibrates the eye tracker.

        arguments
        None

        keyword arguments
        calibrate	--	Boolean indicating if calibration should be
                    performed (default = True).
        validate	--	Boolean indicating if validation should be performed
                    (default = True).

        returns
        success	--	returns True if calibration succeeded, or False if
                    not; in addition a calibration log is added to the
                    log file and some properties are updated (i.e. the
                    thresholds for detection algorithms)
        """
        self._write_enabled = False
        self.start_recording()
        self.screen.set_background_colour(colour=(0, 0, 0))

        if calibrate:
            origin = (int(self.disp.dispsize[0] / 4), int(self.disp.dispsize[1] / 4))
            size = (int(2 * self.disp.dispsize[0] / 4), int(2 * self.disp.dispsize[1] / 4))

            while not self.kb.get_key(keylist=['space'], flush=False)[0]:
                # TODO: What should we do when there are no gaze samples yet?
                # Should we wait or raise an Exception to indicate that
                # something went wrong.
                if not self.gaze:
                    continue
                gaze_sample = copy.copy(self.gaze[-1])

                self.screen.clear()

                validity_colour = (255, 0, 0)

                if gaze_sample['right_gaze_origin_validity'] and gaze_sample['left_gaze_origin_validity']:
                    left_validity = 0.15 < gaze_sample['left_gaze_origin_in_trackbox_coordinate_system'][2] < 0.85
                    right_validity = 0.15 < gaze_sample['right_gaze_origin_in_trackbox_coordinate_system'][2] < 0.85
                    if left_validity and right_validity:
                        validity_colour = (0, 255, 0)

                self.screen.draw_text(text="When correctly positioned press \'space\' to start the calibration.",
                                      pos=(int(self.disp.dispsize[0] / 2), int(self.disp.dispsize[1] * 0.1)),
                                      colour=(255, 255, 255),
                                      fontsize=20)
                self.screen.draw_line(colour=validity_colour, spos=origin, epos=(origin[0] + size[0], origin[1]), pw=1)
                self.screen.draw_line(colour=validity_colour, spos=origin, epos=(origin[0], origin[1] + size[1]), pw=1)
                self.screen.draw_line(colour=validity_colour,
                                      spos=(origin[0], origin[1] + size[1]),
                                      epos=(origin[0] + size[0], origin[1] + size[1]),
                                      pw=1)
                self.screen.draw_line(colour=validity_colour,
                                      spos=(origin[0] + size[0], origin[1] + size[1]),
                                      epos=(origin[0] + size[0], origin[1]),
                                      pw=1)

                right_eye, left_eye, distance = None, None, []
                if gaze_sample['right_gaze_origin_validity']:
                    distance.append(round(gaze_sample['right_gaze_origin_in_user_coordinate_system'][2] / 10, 1))
                    right_pos = gaze_sample['right_gaze_origin_in_trackbox_coordinate_system']
                    right_eye = ((1 - right_pos[0]) * size[0] + origin[0], right_pos[1] * size[1] + origin[1])
                    self.screen.draw_circle(colour=validity_colour,
                                            pos=right_eye,
                                            r=int(self.disp.dispsize[0] / 100),
                                            pw=5,
                                            fill=True)

                if gaze_sample['left_gaze_origin_validity']:
                    distance.append(round(gaze_sample['left_gaze_origin_in_user_coordinate_system'][2] / 10, 1))
                    left_pos = gaze_sample['left_gaze_origin_in_trackbox_coordinate_system']
                    left_eye = ((1 - left_pos[0]) * size[0] + origin[0], left_pos[1] * size[1] + origin[1])
                    self.screen.draw_circle(colour=validity_colour,
                                            pos=left_eye,
                                            r=int(self.disp.dispsize[0] / 100),
                                            pw=5,
                                            fill=True)

                self.screen.draw_text(text="Current distance to the eye tracker: {0} cm.".format(self._mean(distance)),
                                      pos=(int(self.disp.dispsize[0] / 2), int(self.disp.dispsize[1] * 0.9)),
                                      colour=(255, 255, 255),
                                      fontsize=20)

                self.disp.fill(self.screen)
                self.disp.show()

            # # # # # #
            # # calibration

            if not self.eyetracker:
                print("WARNING! libtobii.TobiiProTracker.calibrate: no eye trackers found for the calibration!")
                self.stop_recording()
                return False

            calibration = tr.ScreenBasedCalibration(self.eyetracker)

            calibrating = True

            while calibrating:
                calibration.enter_calibration_mode()

                for point in self.points_to_calibrate:
                    self.screen.clear()
                    self.screen.draw_circle(colour=(255, 255, 255),
                                            pos=point,
                                            r=int(self.disp.dispsize[0] / 100.0),
                                            pw=5,
                                            fill=True)
                    self.screen.draw_circle(colour=(255, 0, 0),
                                            pos=point,
                                            r=int(self.disp.dispsize[0] / 400.0),
                                            pw=5,
                                            fill=True)
                    self.disp.fill(self.screen)
                    self.disp.show()

                    # Wait a little for user to focus.
                    clock.pause(1000)

                    normalized_point = self._px_2_norm(point)

                    collect_result = calibration.collect_data(normalized_point[0], normalized_point[1])

                    if collect_result != tr.CALIBRATION_STATUS_SUCCESS:
                        # Try again if it didn't go well the first time.
                        # Not all eye tracker models will fail at this point, but instead fail on ComputeAndApply.
                        calibration.collect_data(normalized_point[0], normalized_point[1])

                self.screen.clear()
                self.screen.draw_text("Calculating calibration result....", colour=(255, 255, 255), fontsize=20)
                self.disp.fill(self.screen)
                self.disp.show()

                calibration_result = calibration.compute_and_apply()

                calibration.leave_calibration_mode()

                print("Compute and apply returned {0} and collected at {1} points.".
                      format(calibration_result.status, len(calibration_result.calibration_points)))

                if calibration_result.status != tr.CALIBRATION_STATUS_SUCCESS:
                    self.stop_recording()
                    print("WARNING! libtobii.TobiiProTracker.calibrate: Calibration was unsuccessful!")
                    return False

                self.screen.clear()
                for point in calibration_result.calibration_points:
                    self.screen.draw_circle(colour=(255, 255, 255),
                                            pos=self._norm_2_px(point.position_on_display_area),
                                            r=self.disp.dispsize[0] / 200,
                                            pw=1,
                                            fill=False)
                    for sample in point.calibration_samples:
                        if sample.left_eye.validity == tr.VALIDITY_VALID_AND_USED:
                            self.screen.draw_circle(colour=(255, 0, 0),
                                                    pos=self._norm_2_px(sample.left_eye.position_on_display_area),
                                                    r=self.disp.dispsize[0] / 450,
                                                    pw=self.disp.dispsize[0] / 450,
                                                    fill=False)
                            self.screen.draw_line(colour=(255, 0, 0),
                                                  spos=self._norm_2_px(point.position_on_display_area),
                                                  epos=self._norm_2_px(sample.left_eye.position_on_display_area),
                                                  pw=1)
                        if sample.right_eye.validity == tr.VALIDITY_VALID_AND_USED:
                            self.screen.draw_circle(colour=(0, 0, 255),
                                                    pos=self._norm_2_px(sample.right_eye.position_on_display_area),
                                                    r=self.disp.dispsize[0] / 450,
                                                    pw=self.disp.dispsize[0] / 450,
                                                    fill=False)
                            self.screen.draw_line(colour=(0, 0, 255),
                                                  spos=self._norm_2_px(point.position_on_display_area),
                                                  epos=self._norm_2_px(sample.right_eye.position_on_display_area),
                                                  pw=1)

                self.screen.draw_text("Press the \'R\' key to recalibrate or \'Space\' to continue....",
                                      pos=(0.5 * self.disp.dispsize[0], 0.95 * self.disp.dispsize[1]),
                                      colour=(255, 255, 255), fontsize=20)

                self.screen.draw_text("Left Eye", pos=(0.5 * self.disp.dispsize[0], 0.01 * self.disp.dispsize[1]),
                                      colour=(255, 0, 0), fontsize=20)
                self.screen.draw_text("Right Eye", pos=(0.5 * self.disp.dispsize[0], 0.03 * self.disp.dispsize[1]),
                                      colour=(0, 0, 255), fontsize=20)

                self.disp.fill(self.screen)
                self.disp.show()

                pressed_key = self.kb.get_key(keylist=['space', 'r'], flush=True, timeout=None)

                if pressed_key[0] == 'space':
                    calibrating = False

        if validate:
            # # # show menu
            self.screen.clear()
            self.screen.draw_text(text="Press space to start validation", colour=(255, 255, 255), fontsize=20)
            self.disp.fill(self.screen)
            self.disp.show()

            # # # wait for spacepress
            self.kb.get_key(keylist=['space'], flush=True, timeout=None)

            # # # # # #
            # # validation

            # # # arrays for data storage
            lxacc, lyacc, rxacc, ryacc = [], [], [], []

            # # loop through all calibration positions
            for pos in self.points_to_calibrate:
                # show validation point
                self.screen.clear()
                self.screen.draw_fixation(fixtype='dot', pos=pos, colour=(255, 255, 255))
                self.disp.fill(self.screen)
                self.disp.show()

                # allow user some time to gaze at dot
                clock.pause(1000)

                lxsamples, lysamples, rxsamples, rysamples = [], [], [], []
                for sample in self.gaze:
                    if sample["left_gaze_point_validity"]:
                        gaze_point = self._norm_2_px(sample["left_gaze_point_on_display_area"])
                        lxsamples.append(abs(gaze_point[0] - pos[0]))
                        lysamples.append(abs(gaze_point[1] - pos[1]))
                    if sample["right_gaze_point_validity"]:
                        gaze_point = self._norm_2_px(sample["right_gaze_point_on_display_area"])
                        rxsamples.append(abs(gaze_point[0] - pos[0]))
                        rysamples.append(abs(gaze_point[1] - pos[1]))

                # calculate mean deviation
                lxacc.append(self._mean(lxsamples))
                lyacc.append(self._mean(lysamples))
                rxacc.append(self._mean(rxsamples))
                ryacc.append(self._mean(rysamples))

                # wait for a bit to slow down validation process a bit
                clock.pause(1000)

            # calculate mean accuracy
            self.pxaccuracy = [(self._mean(lxacc), self._mean(lyacc)), (self._mean(rxacc), self._mean(ryacc))]

            # sample rate
            # calculate intersample times
            timestamps = []
            gaze_samples = copy.copy(self.gaze)
            for i in range(0, len(gaze_samples) - 1):
                next_sample = gaze_samples[i + 1]['system_time_stamp']
                current_sample = gaze_samples[i]['system_time_stamp']
                timestamps.append((next_sample - current_sample) / 1000.0)

            # mean intersample time
            self.sampletime = self._mean(timestamps)
            self.samplerate = int(1000.0 / self.sampletime)

            # # # # # #
            # # RMS noise

            # # present instructions
            self.screen.clear()
            self.screen.draw_text(text="Noise calibration: please look at the dot\n\n(press space to start)",
                                  pos=(self.disp.dispsize[0] / 2, int(self.disp.dispsize[1] * 0.2)),
                                  colour=(255, 255, 255), fontsize=20)
            self.screen.draw_fixation(fixtype='dot', colour=(255, 255, 255))
            self.disp.fill(self.screen)
            self.disp.show()

            # # wait for spacepress
            self.kb.get_key(keylist=['space'], flush=True, timeout=None)

            # # show fixation
            self.screen.clear()
            self.screen.draw_fixation(fixtype='dot', colour=(255, 255, 255))
            self.disp.fill(self.screen)
            self.disp.show()
            self.screen.clear()

            # # wait for a bit, to allow participant to fixate
            clock.pause(500)

            # # get samples
            # samplelist, prefilled with 1 sample to prevent sl[-1] from producing an error
            # first sample will be ignored for RMS calculation
            sl = [self.sample()]
            t0 = clock.get_time()  # starting time
            while clock.get_time() - t0 < 1000:
                s = self.sample()  # sample
                if s != sl[-1] and self.is_valid_sample(s) and s != (0, 0):
                    sl.append(s)

            # # calculate RMS noise
            Xvar, Yvar = [], []
            for i in range(2, len(sl)):
                Xvar.append((sl[i][0] - sl[i - 1][0])**2)
                Yvar.append((sl[i][1] - sl[i - 1][1])**2)
            if len(Xvar) == 0:
                XRMS = 60.0
            else:
                XRMS = (self._mean(Xvar))**0.5
            if len(Yvar) == 0:
                YRMS = 90.0
            else:
                YRMS = (self._mean(Yvar))**0.5
            self.pxdsttresh = (XRMS, YRMS)

            # # # # # # #
            # # # calibration report

            # # # # recalculate thresholds (degrees to pixels)
            self.pxfixtresh = self._deg2pix(self.screendist, self.fixtresh, self.pixpercm)
            # in pixels per millisecons
            self.pxspdtresh = self._deg2pix(self.screendist, self.spdtresh / 1000.0, self.pixpercm)
            # in pixels per millisecond**2
            self.pxacctresh = self._deg2pix(self.screendist, self.accthresh / 1000.0, self.pixpercm)

            data_to_write = ''
            data_to_write += "pygaze calibration report start\n"
            data_to_write += "samplerate: %s Hz\n" % self.samplerate
            data_to_write += "sampletime: %s ms\n" % self.sampletime
            data_to_write += "accuracy (in pixels): LX=%s, LY=%s, RX=%s, RY=%s\n" % (self.pxaccuracy[0][0],
                                                                                     self.pxaccuracy[0][1],
                                                                                     self.pxaccuracy[1][0],
                                                                                     self.pxaccuracy[1][1])
            data_to_write += "precision (RMS noise in pixels): X=%s, Y=%s\n" % (self.pxdsttresh[0], self.pxdsttresh[1])
            data_to_write += "distance between participant and display: %s cm\n" % self.screendist
            data_to_write += "fixation threshold: %s pixels\n" % self.pxfixtresh
            data_to_write += "speed threshold: %s pixels/ms\n" % self.pxspdtresh
            data_to_write += "accuracy threshold: %s pixels/ms**2\n" % self.pxacctresh
            data_to_write += "pygaze calibration report end\n"

            # # # # write report to log
            self.datafile.write(data_to_write)

            self.screen.clear()
            self.screen.draw_text(text=data_to_write, pos=(self.disp.dispsize[0] / 2, int(self.disp.dispsize[1] / 2)),
                                  colour=(255, 255, 255), fontsize=20)
            self.disp.fill(self.screen)
            self.disp.show()

            self.kb.get_key(keylist=['space'], flush=True, timeout=None)

        self.stop_recording()
        self._write_enabled = True

        return True

    def fix_triggered_drift_correction(self, pos=None, min_samples=10, max_dev=60, reset_threshold=30):
        """Performs a fixation triggered drift correction by collecting
        a number of samples and calculating the average distance from the
        fixation position

        arguments
        None

        keyword arguments
        pos			-- (x, y) position of the fixation dot or None for
                       a central fixation (default = None)
        min_samples		-- minimal amount of samples after which an
                       average deviation is calculated (default = 10)
        max_dev		-- maximal deviation from fixation in pixels
                       (default = 60)
        reset_threshold	-- if the horizontal or vertical distance in
                       pixels between two consecutive samples is
                       larger than this threshold, the sample
                       collection is reset (default = 30)

        returns
        checked		-- Boolean indicating if drift check is ok (True)
                       or not (False); or calls self.calibrate if 'q'
                       or 'escape' is pressed
        """
        if pos is None:
            pos = self.disp.dispsize[0] / 2, self.disp.dispsize[1] / 2

        # start recording if recording has not yet started
        if not self.recording:
            self.start_recording()
            stoprec = True
        else:
            stoprec = False

        # loop until we have sufficient samples
        lx = []
        ly = []
        while len(lx) < min_samples:

            # pressing escape enters the calibration screen
            if self.kb.get_key()[0] in ['escape', 'q']:
                print("libtobii.TobiiTracker.fix_triggered_drift_correction: 'q' or 'escape' pressed")
                return self.calibrate(calibrate=True, validate=True)

            # collect a sample
            x, y = self.sample()

            if len(lx) == 0 or (x, y) != (lx[-1], ly[-1]):

                # if present sample deviates too much from previous sample, reset counting
                if len(lx) > 0 and (abs(x - lx[-1]) > reset_threshold or abs(y - ly[-1]) > reset_threshold):
                    lx = []
                    ly = []

                # collect samples
                else:
                    lx.append(x)
                    ly.append(y)

            if len(lx) == min_samples:

                avg_x = self._mean(lx)
                avg_y = self._mean(ly)
                d = ((avg_x - pos[0]) ** 2 + (avg_y - pos[1]) ** 2)**0.5

                if d < max_dev:
                    if stoprec:
                        self.stop_recording()
                    return True
                else:
                    lx = []
                    ly = []
        if stoprec:
            self.stop_recording()

    def drift_correction(self, pos=None, fix_triggered=False):
        """Performs a drift check

        arguments
        None

        keyword arguments
        pos			-- (x, y) position of the fixation dot or None for
                       a central fixation (default = None)
        fix_triggered	-- Boolean indicating if drift check should be
                       performed based on gaze position (fix_triggered
                       = True) or on spacepress (fix_triggered =
                       False) (default = False)

        returns
        checked		-- Boolean indicating if drift check is ok (True)
                       or not (False); or calls self.calibrate if 'q'
                       or 'escape' is pressed
        """
        if fix_triggered:
            return self.fix_triggered_drift_correction(pos)

        if pos is None:
            pos = self.disp.dispsize[0] / 2, self.disp.dispsize[1] / 2

        # start recording if recording has not yet started
        if not self.recording:
            self.start_recording()
            stoprec = True
        else:
            stoprec = False

        result = False
        pressed = False
        while not pressed:
            pressed, presstime = self.kb.get_key()
            if pressed:
                if pressed == 'escape' or pressed == 'q':
                    print("libtobii.TobiiProTracker.drift_correction: 'q' or 'escape' pressed")
                    return self.calibrate(calibrate=True, validate=True)
                gazepos = self.sample()
                if ((gazepos[0] - pos[0])**2 + (gazepos[1] - pos[1])**2)**0.5 < self.pxerrdist:
                    result = True

        if stoprec:
            self.stop_recording()

        return result

    def wait_for_fixation_start(self):
        """Returns starting time and position when a fixation is started;
        function assumes a 'fixation' has started when gaze position
        remains reasonably stable (i.e. when most deviant samples are
        within self.pxfixtresh) for five samples in a row (self.pxfixtresh
        is created in self.calibration, based on self.fixtresh, a property
        defined in self.__init__)

        arguments
        None

        returns
        time, gazepos	-- time is the starting time in milliseconds (from
                       expstart), gazepos is a (x,y) gaze position
                       tuple of the position from which the fixation
                       was initiated
        """
        # # # # #
        # Tobii method

        if self.eventdetection == 'native':
            # print warning, since Tobii does not have a fixation start
            # detection built into their API (only ending)
            print("WARNING! 'native' event detection has been selected, \
                but Tobii does not offer fixation detection; PyGaze \
                algorithm will be used")

        # # # # #
        # PyGaze method

        # function assumes a 'fixation' has started when gaze position
        # remains reasonably stable for self.fixtimetresh

        # start recording if recording has not yet started
        if not self.recording:
            self.start_recording()
            stoprec = True
        else:
            stoprec = False

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
                if (npos[0] - spos[0])**2 + (npos[1] - spos[1])**2 > self.pxfixtresh**2:  # Pythagoras
                    # if not, reset starting position and time
                    spos = copy.copy(npos)
                    t0 = clock.get_time()
                # if new sample is close to starting sample
                else:
                    # get timestamp
                    t1 = clock.get_time()
                    # check if fixation time threshold has been surpassed
                    if t1 - t0 >= self.fixtimetresh:
                        if stoprec:
                            self.stop_recording()
                        # return time and starting position
                        return t0, spos

    def wait_for_fixation_end(self):
        """Returns time and gaze position when a fixation has ended;
        function assumes that a 'fixation' has ended when a deviation of
        more than self.pxfixtresh from the initial fixation position has
        been detected (self.pxfixtresh is created in self.calibration,
        based on self.fixtresh, a property defined in self.__init__)

        arguments
        None

        returns
        time, gazepos	-- time is the starting time in milliseconds (from
                       expstart), gazepos is a (x,y) gaze position
                       tuple of the position from which the fixation
                       was initiated
        """
        # # # # #
        # Tobii method

        if self.eventdetection == 'native':
            # print warning, since Tobii does not have a fixation detection
            # built into their API
            print("WARNING! 'native' event detection has been selected, \
                but Tobii does not offer fixation detection; PyGaze algorithm \
                will be used")

        # # # # #
        # PyGaze method

        # function assumes that a 'fixation' has ended when a deviation of more than fixtresh
        # from the initial 'fixation' position has been detected

        # get starting time and position
        stime, spos = self.wait_for_fixation_start()

        # start recording if recording has not yet started
        if not self.recording:
            self.start_recording()
            stoprec = True
        else:
            stoprec = False

        # loop until fixation has ended
        while True:
            # get new sample
            npos = self.sample()  # get newest sample
            # check if sample is valid
            if self.is_valid_sample(npos):
                # check if sample deviates to much from starting position
                if (npos[0] - spos[0])**2 + (npos[1] - spos[1])**2 > self.pxfixtresh**2:
                    # break loop if deviation is too high
                    break

        if stoprec:
            self.stop_recording()

        return clock.get_time(), spos

    def wait_for_saccade_start(self):
        """Returns starting time and starting position when a saccade is
        started; based on Dalmaijer et al. (2013) online saccade detection
        algorithm

        arguments
        None

        returns
        endtime, startpos	-- endtime in milliseconds (from expbegintime);
                       startpos is an (x,y) gaze position tuple
        """
        # # # # #
        # Tobii method

        if self.eventdetection == 'native':
            # print warning, since Tobii does not have a blink detection
            # built into their API
            print("WARNING! 'native' event detection has been selected, \
                but Tobii does not offer saccade detection; PyGaze \
                algorithm will be used")

        # # # # #
        # PyGaze method

        # start recording if recording has not yet started
        if not self.recording:
            self.start_recording()
            stoprec = True
        else:
            stoprec = False

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
                sx = newpos[0] - prevpos[0]
                sy = newpos[1] - prevpos[1]
                # weigthed distance: (sx/tx)**2 + (sy/ty)**2 > 1 means movement larger than RMS noise
                if (sx / self.pxdsttresh[0])**2 + (sy / self.pxdsttresh[1])**2 > self.weightdist:
                    # calculate distance
                    s = ((sx)**2 + (sy)**2)**0.5  # intersampledistance = speed in pixels/ms
                    # calculate velocity
                    v1 = s / (t1 - t0)
                    # calculate acceleration
                    a = (v1 - v0) / (t1 - t0)  # acceleration in pixels/ms**2
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

        if stoprec:
            self.stop_recording()

        return stime, spos

    def wait_for_saccade_end(self):
        """Returns ending time, starting and end position when a saccade is
        ended; based on Dalmaijer et al. (2013) online saccade detection
        algorithm

        arguments
        None

        returns
        endtime, startpos, endpos	-- endtime in milliseconds (from
                               expbegintime); startpos and endpos
                               are (x,y) gaze position tuples
        """
        # # # # #
        # Tobii method

        if self.eventdetection == 'native':
            # print warning, since Tobii does not have a blink detection
            # built into their API
            print("WARNING! 'native' event detection has been selected, \
                but Tobii does not offer saccade detection; PyGaze \
                algorithm will be used")

        # # # # #
        # PyGaze method

        # get starting position (no blinks)
        t0, spos = self.wait_for_saccade_start()

        # start recording if recording has not yet started
        if not self.recording:
            self.start_recording()
            stoprec = True
        else:
            stoprec = False

        # get valid sample
        prevpos = self.sample()
        while not self.is_valid_sample(prevpos):
            prevpos = self.sample()
        # get starting time, intersample distance, and velocity
        t1 = clock.get_time()
        s = ((prevpos[0] - spos[0])**2 + (prevpos[1] - spos[1])**2)**0.5  # = intersample distance = speed in px/sample
        v0 = s / (t1 - t0)

        # run until velocity and acceleration go below threshold
        saccadic = True
        while saccadic:
            # get new sample
            newpos = self.sample()
            t1 = clock.get_time()
            if self.is_valid_sample(newpos) and newpos != prevpos:
                # calculate distance
                s = ((newpos[0] - prevpos[0])**2 + (newpos[1] - prevpos[1])**2)**0.5  # = speed in pixels/sample
                # calculate velocity
                v1 = s / (t1 - t0)
                # calculate acceleration
                # acceleration in pixels/sample**2 (actually is v1-v0 / t1-t0; but t1-t0 = 1 sample)
                a = (v1 - v0) / (t1 - t0)
                # check if velocity and acceleration are below threshold
                if v1 < self.pxspdtresh and (a > -1 * self.pxacctresh and a < 0):
                    saccadic = False
                    epos = newpos[:]
                    etime = clock.get_time()
                # update previous values
                t0 = copy.copy(t1)
                v0 = copy.copy(v1)
            # udate previous sample
            prevpos = newpos[:]

        if stoprec:
            self.stop_recording()

        return etime, spos, epos

    def wait_for_blink_start(self):
        """Waits for a blink start and returns the blink starting time

        arguments
        None

        returns
        timestamp		--	blink starting time in milliseconds, as
                        measured from experiment begin time
        """
        # # # # #
        # Tobii method

        if self.eventdetection == 'native':
            # print warning, since Tobii does not have a blink detection
            # built into their API
            print("WARNING! 'native' event detection has been selected, \
                but Tobii does not offer blink detection; PyGaze algorithm \
                will be used")

        # # # # #
        # PyGaze method

        # start recording if recording has not yet started
        if not self.recording:
            self.start_recording()
            stoprec = True
        else:
            stoprec = False

        blinking = False

        # loop until there is a blink
        while not blinking:
            # get newest sample
            gazepos = self.sample()
            # check if it's a valid sample
            if self.is_valid_sample(gazepos):
                # get timestamp for possible blink start
                t0 = clock.get_time()
                # loop until a blink is determined, or a valid sample occurs
                while not self.is_valid_sample(self.sample()):
                    # check if time has surpassed BLINKTHRESH
                    if clock.get_time() - t0 >= self.blinkthresh:
                        if stoprec:
                            self.stop_recording()
                        # return timestamp of blink start
                        return t0

    def wait_for_blink_end(self):
        """Waits for a blink end and returns the blink ending time

        arguments
        None

        returns
        timestamp		--	blink ending time in milliseconds, as
                        measured from experiment begin time
        """
        # # # # #
        # Tobii method
        if self.eventdetection == 'native':
            # print warning, since Tobii does not have a blink detection
            # built into their API
            print("WARNING! 'native' event detection has been selected, \
                but Tobii does not offer blink detection; PyGaze algorithm \
                will be used")

        # # # # #
        # PyGaze method

        # start recording if recording has not yet started
        if not self.recording:
            self.start_recording()
            stoprec = True
        else:
            stoprec = False

        blinking = True
        # loop while there is a blink
        while blinking:
            # get newest sample
            gazepos = self.sample()
            # check if it's valid
            if self.is_valid_sample(gazepos):
                # if it is a valid sample, blinking has stopped
                blinking = False

        if stoprec:
            self.stop_recording()

        # return timestamp of blink end
        return clock.get_time()

    def log(self, msg):
        """Writes a message to the log file

        arguments
        msg		-- a string to include in the log file

        returns
        Nothing	-- uses native log function to include a line
                   in the log file
        """
        t = tr.get_system_time_stamp()
        if not self.t0:
            self.t0 = t
            self._write_header()

        self.datafile.write('%.4f\t%s\n' % ((t - self.t0) / 1000.0, msg))

    def _flush_to_file(self):
        # write data to disk
        self.datafile.flush()  # internal buffer to RAM
        os.fsync(self.datafile.fileno())  # RAM file cache to disk

    def _write_header(self):
        # write header
        self.datafile.write('\t'.join(['TimeStamp',
                                       'Event',
                                       'GazePointXLeft',
                                       'GazePointYLeft',
                                       'ValidityLeft',
                                       'GazePointXRight',
                                       'GazePointYRight',
                                       'ValidityRight',
                                       'GazePointX',
                                       'GazePointY',
                                       'PupilSizeLeft',
                                       'PupilValidityLeft',
                                       'PupilSizeRight',
                                       'PupilValidityRight']) + '\n')
        self._flush_to_file()

    def _write_sample(self, sample):
        _write_buffer = ""
        # write timestamp and gaze position for both eyes
        left_gaze_point = self._norm_2_px(sample['left_gaze_point_on_display_area']) if sample['left_gaze_point_validity'] else (-1, -1)  # noqa: E501
        right_gaze_point = self._norm_2_px(sample['right_gaze_point_on_display_area']) if sample['right_gaze_point_validity'] else (-1, -1)  # noqa: E501
        _write_buffer += '\t%d\t%d\t%d\t%d\t%d\t%d' % (
            left_gaze_point[0],
            left_gaze_point[1],
            sample['left_gaze_point_validity'],
            right_gaze_point[0],
            right_gaze_point[1],
            sample['right_gaze_point_validity'])

        # if no correct sample is available, data is missing
        if not (sample['left_gaze_point_validity'] or sample['right_gaze_point_validity']):  # not detected
            ave = (-1.0, -1.0)
        # if the right sample is unavailable, use left sample
        elif not sample['right_gaze_point_validity']:
            ave = left_gaze_point
        # if the left sample is unavailable, use right sample
        elif not sample['left_gaze_point_validity']:
            ave = right_gaze_point
        # if we have both samples, use both samples
        else:
            ave = (int(round((left_gaze_point[0] + right_gaze_point[0]) / 2.0, 0)),
                   (int(round(left_gaze_point[1] + right_gaze_point[1]) / 2.0)))

        # write gaze position, based on the selected sample(s)
        _write_buffer += '\t%d\t%d' % ave

        left_pupil = sample['left_pupil_diameter'] if sample['left_pupil_validity'] else -1
        right_pupil = sample['right_pupil_diameter'] if sample['right_pupil_validity'] else -1

        _write_buffer += '\t%.4f\t%d\t%.4f\t%d' % (
            left_pupil,
            sample['left_pupil_validity'],
            right_pupil,
            sample['right_pupil_validity'])

        # Write buffer to the datafile
        self.log(_write_buffer)

    def close(self):
        """Closes the currently used log file.

        arguments
        None

        returns
        None		--	closes the log file.
        """
        self.datafile.close()

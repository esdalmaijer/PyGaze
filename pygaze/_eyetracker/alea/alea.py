import os
import sys
import copy
import time
import datetime
import ctypes
from multiprocessing import Queue
from threading import Event, Lock, Thread

# Auto-detect whether we're running 32 or 64 bit, and decide which DLL to load.
if sys.maxsize > 2**32:
    dll_name = "CEtAPIx64.dll"
    print("Python Alea: detected 64-bit application, loading '{}'".format(dll_name))
else:
    dll_name = "CEtAPI.dll"

# Auto-detect the current directory, and the place where CEtAPI.dll should be.
dir_path = os.path.dirname(os.path.abspath(__file__))
dll_path = os.path.join(dir_path, dll_name)

# Check whether the DLL exists.
if not os.path.isfile(dll_path):
    raise Exception("WARNING: Could not find CEtAPI.dll in its expected location: '{}'".format(dll_path))

# Load the DLL.
# Available functions in C-wrapped API:
#    etapi.Open
#    etapi.Close
#    etapi.Version
#    etapi.IsOpen
#    etapi.SetDataFile
#    etapi.WriteMessageToDataFile
#    etapi.StartRecording
#    etapi.StopRecording
#    etapi.PerformCalibration
#    etapi.WaitForCalibrationResult
#    etapi.ShowStatusWindow
#    etapi.HideStatusWindow
#    etapi.DataStreaming
#    etapi.WaitForData
#    etapi.ClearDataBuffer
#    etapi.ExitServer
etapi = None
try:
    print("Python Alea: loading '{}'".format(dll_name))
    etapi = ctypes.windll.LoadLibrary(dll_path)
except:
    print("WARNING: Failed to load '{}'! Alea functionality not available!".format(dll_name))

# Define what errors mean.
EtApiError = { \
    0: "Function success", \
    -1: "No acknowledge received", \
    -2: "Function argument error", \
    -3: "API was not opened", \
    -4: "No response from eye tracking server", \
    -5: "IP or port failure (could not connect to IP or port)", \
    -6: "Failed to send command to eye tracker", \
    -7: "Server could not successfully process the given command", \
    -10: "Could not create Mutex and Events in Open", \
    -100: "Could not connect to EtAPI", \
    }
def check_result(et_api_error):
    if et_api_error == 0:
        return True
    else:
        return False

# Define general data struct used in the EtAPI.
class CAleaData(ctypes.Structure):
    _fields_ = [ \
        # RAW DATA
        # Timestamp for this data.
        ("rawDataTimeStamp", ctypes.c_long), \
        # Weighted-average of both eyes' coordinates.
        ("intelliGazeX", ctypes.c_double), \
        ("intelliGazeY", ctypes.c_double), \

        # LEFT EYE
        # Gaze position is measured in pixels, and relates to the screen.
        ("gazePositionXLeftEye", ctypes.c_double), \
        ("gazePositionYLeftEye", ctypes.c_double), \
        # Confidence is in the range [0.0, 1.0]
        ("gazePositionConfidenceLeftEye", ctypes.c_double), \
        # Pupil size is measured in pixels, and a circular pupil is assumed.
        ("pupilDiameterLeftEye", ctypes.c_double), \

        # RIGHT EYE
        # Gaze position is measured in pixels, and relates to the screen.
        ("gazePositionXRightEye", ctypes.c_double), \
        ("gazePositionYRightEye", ctypes.c_double), \
        # Confidence is in the range [0.0, 1.0]
        ("gazePositionConfidenceRightEye", ctypes.c_double), \
        # Pupil size is measured in pixels, and a circular pupil is assumed.
        ("pupilDiameterRightEye", ctypes.c_double), \

        # EVENT DATA
        # Event ID.
        ("eventID", ctypes.c_int), \
        # Timestamp for this data.
        ("eventDataTimeStamp", ctypes.c_long), \
        # The duration of the event.
        ("duration", ctypes.c_long), \
        # The position is measured in pixels (screen coordinates).
        ("positionX", ctypes.c_double), \
        ("positionY", ctypes.c_double), \
        # The horizontal and vertical dispersion.
        ("dispersionX", ctypes.c_double), \
        ("dispersionY", ctypes.c_double), \
        # Confidence is in the range [0.0, 1.0]
        ("confidence", ctypes.c_double), \
        ]

# Define C structs.
class CRawEye(ctypes.Structure):
    _fields_ = [ \
        # Position parameters are in millimeters relative to the camera.
        ("eyeballPosX", ctypes.c_double), \
        ("eyeballPosY", ctypes.c_double), \
        ("eyeballPosZ", ctypes.c_double), \
        # Confidence is in the range [0.0, 1.0]
        ("eyeballConfidence", ctypes.c_double), \
        # Gaze vectors are normalised components.
        ("gazeVectorX", ctypes.c_double), \
        ("gazeVectorY", ctypes.c_double), \
        ("gazeVectorZ", ctypes.c_double), \
        # Confidence is in the range [0.0, 1.0]
        ("gazeVectorConfidence", ctypes.c_double), \
        # Pupil size is measured in pixels, and a circular pupil is assumed.
        ("pupilDiameter", ctypes.c_double), \
        # Gaze position is measured in pixels, and relates to the screen.
        ("gazePositionX", ctypes.c_double), \
        ("gazePositionY", ctypes.c_double), \
        # Confidence is in the range [0.0, 1.0]
        ("gazePositionConfidence", ctypes.c_double), \
        ]

class CRawHead(ctypes.Structure):
    _fields_ = [ \
        # Head position is measured in millimeters, relative to the camera.
        ("headPosX", ctypes.c_double), \
        ("headPosY", ctypes.c_double), \
        ("headPosZ", ctypes.c_double), \
        # Head orientation is measured in degrees.
        ("headYaw", ctypes.c_double), \
        ("headPitch", ctypes.c_double), \
        ("headRoll", ctypes.c_double), \
        # Confidence is in the range [0.0, 1.0]
        ("headPoseConfidence", ctypes.c_double), \
        # Head translation speed is measured in millimeter per second.
        ("headTranslationSpeedX", ctypes.c_double), \
        ("headTranslationSpeedY", ctypes.c_double), \
        ("headTranslationSpeedZ", ctypes.c_double), \
        # Head rotation speed is measured in degrees per second.
        ("headRotationSpeedX", ctypes.c_double), \
        ("headRotationSpeedY", ctypes.c_double), \
        ("headRotationSpeedZ", ctypes.c_double), \
        # Confidence is in the range [0.0, 1.0]
        ("headSpeedConfidence", ctypes.c_double), \
        ]

class CRawData(ctypes.Structure):
    _fields_ = [ \
        # Timestamp for this data.
        ("timeStamp", ctypes.c_int), \
        # Independent left and right eye data.
        ("leftEye", CRawEye), \
        ("rightEye", CRawEye), \
        # Head data.
        ("head", CRawHead), \
        # Weighted-average of both eyes' coordinates.
        ("intelliGazeX", ctypes.c_double), \
        ("intelliGazeY", ctypes.c_double), \
        ]

class CFixation(ctypes.Structure):
    _fields_ = [ \
        # The timestamp marks the fixation start.
        ("timeStamp", ctypes.c_int), \
        # The position is measured in pixels (screen coordinates).
        ("positionX", ctypes.c_double), \
        ("positionY", ctypes.c_double), \
        # The duration of the fixation.
        ("duration", ctypes.c_double), \
        # The horizontal and vertical dispersion.
        ("dispersionX", ctypes.c_double), \
        ("dispersionY", ctypes.c_double), \
        # Confidence is in the range [0.0, 1.0]
        ("Confidence", ctypes.c_double), \
        ]

class CSaccade(ctypes.Structure):
    _fields_ = [ \
        # The timestamp marks the saccade start.
        ("timeStamp", ctypes.c_int), \
        # The duration of the saccade.
        ("duration", ctypes.c_double), \
        ]

class CBlink(ctypes.Structure):
    _fields_ = [ \
        # The timestamp marks the blink start.
        ("timeStamp", ctypes.c_int), \
        # The position is measured in pixels (screen coordinates), and
        # reflects the last fixation coordinates.
        ("positionX", ctypes.c_double), \
        ("positionY", ctypes.c_double), \
        # The duration of the blink.
        ("duration", ctypes.c_double), \
        ]

class CBlickfang(ctypes.Structure):
    _fields_ = [ \
        # Unique ID of this blickfang
        ("id", ctypes.c_int), \
        # Coordinates of the upper left of the blickfang
        ("x", ctypes.c_int), \
        ("y", ctypes.c_int), \
        # Width and height of the blickfang.
        ("w", ctypes.c_int), \
        ("h", ctypes.c_int), \
        ]
        
class CEyeGesture(ctypes.Structure):
    _fields_ = [ \
        # c_char_p is used for pointers to multi-character strings.
        ("Action", ctypes.c_char_p), \
        ]

class CServerCalibrationStatus(ctypes.Structure):
    _fields_ = [ \
        # The number of the point that is currently being calibrated (1-16)
        ("currentPoint", ctypes.c_int), \
        # The position on screen (in pixels) of the current point.
        ("posX", ctypes.c_int), \
        ("posY", ctypes.c_int), \
        # If True, the eye tracker is currently detecting a fixation. Usually
        # this means you can start reducing the size of the fixation target,
        # which signals that the point is currently being calibrated and might
        # make the fixation closer to the target's centre.
        ("fixation", ctypes.c_bool), \
        # If True, the eye tracker is about to skip the current point. Usually
        # this is an indication that the target should be made obvious to the
        # particiant, for example by flashing or enlarging it.
        ("acceptWarning", ctypes.c_bool), \
        ]


# Define a class that wraps the API in a user-friendly way.
class AleaTracker:
    
    """Python class for talking to Alea Technologies eye trackers"""
    
    def __init__(self, app_key, file_path="alea_default.csv", target_ip=None, \
        target_port=None, listen_ip=None, listen_port=None, debug=False):
        
        """
        desc:
            Initialises the API, opens the socket connection, establishes a
            link to the hardware. Make sure that no firewall is blocking the
            port. This function will use the default values for IP addresses
            and ports, unless all keyword arguments are specified. This also
            sets a callback function for raw data.
        
        arguments:
            app_key:
                desc:
                    Application-specific key to register the application, ask
                    alea technologies for your specific application key.
                type: str
        
        keywords:
            file_path:
                desc:
                    Full path to where the data should be stored. (Default = 
                    "alea_default.csv")
                type: str
            target_ip:
                desc:
                    IP address of the eye tracker. (Default = "127.0.0.1")
                type: str
            target_port:
                desc:
                    Target port of the server socket link. (Default = 27412)
                type: int
            listen_ip:
                desc:
                    IP address of the client application. (Default = 
                    "127.0.0.1")
                type: str
            listen_port:
                desc:
                    Listen port of the client socket link. (Default = 27413)
                type: int
            debug:
                desc:
                    In DEBUG mode, some info will be written to a text file.
                    (Default = False)
                type: bool
        """
        
        # Open a new debug file if required.
        if debug:
            self._debug = True
            self._debug_file_name = "pygaze_alea_debug_{}.txt".format( \
                time.strftime("%Y-%m-%d_%H-%M-%S"))
            with open(self._debug_file_name, "w") as f:
                f.write("time\tmessage")
            self._debug_file_lock = Lock()
        else:
            self._debug = False
            self._debug_file_name = None
            self._debug_file_lock = None
        
        # Initialise a new Alea API instance.
        if self._debug:
            self._debug_log("Initialising AleaAPI instance")
        self.api = AleaAPI()

        # Open the connection to the API.
        if self._debug:
            self._debug_log("Alea connection: opening with target IP={} port={}, listen IP={} port={}".format( \
                target_ip, target_port, listen_ip, listen_port))
        self.api.Open(app_key, targetIP=target_ip, targetPort=target_port, \
            listenIP=listen_ip, listenPort=listen_port)
        
        # Set an event that signals we are currently connected. This event
        # will be used to signal to Threads that they should stop what they
        # are doing.
        self._connected = Event()
        self._connected.set()
        
        # Get the version and device number, which are formatted
        # "%d.%d.%d.%d" % (major, minor, build, device)
        version = self.api.Version()
        major, minor, build, device = version.split(".")
        self.api_version = "{}.{}.{}".format(major, minor, build)
        self.device = "device_code_{}".format(device)
        if device == "0":
            self.device = "IG30"
        elif device == "1":
            self.device = "IG15"
        
        # Print a message to the terminal.
        print("Successfully connected to Alea API, version={}, device={}".format( \
            self.api_version, self.device))
        if self._debug:
            self._debug_log("Successfully connected to Alea API, version={}, device={}".format( \
                self.api_version, self.device))
        
        # LOGGING
        # Parse the file path to find out what separator to use.
        dir_name = os.path.dirname(file_path)
        file_name = os.path.basename(file_path)
        name, ext = os.path.splitext(file_name)
        # If no file extension was included, default to TSV.
        if ext == "":
            ext = ".tsv"
        # Choose a separator depending on the file extension.
        if ext == ".csv":
            self._sep = ","
        elif ext == ".tsv":
            self._sep = "\t"
        else:
            self._sep = "\t"
        # Construct the data file name.
        self._data_file_path = os.path.join(dir_name, name+ext)
        # Define the log-able variables.
        self._log_vars = [ \
            "rawDataTimeStamp", \
            "intelliGazeX", \
            "intelliGazeY", \
            "gazePositionXLeftEye", \
            "gazePositionYLeftEye", \
            "gazePositionConfidenceLeftEye", \
            "pupilDiameterLeftEye", \
            "gazePositionXRightEye", \
            "gazePositionYRightEye", \
            "gazePositionConfidenceRightEye", \
            "pupilDiameterRightEye", \
            "eventID", \
            "eventDataTimeStamp", \
            "duration", \
            "positionX", \
            "positionY", \
            "dispersionX", \
            "dispersionY", \
            "confidence", \
            ]
        # Open a new log file.
        if self._debug:
            self._debug_log("Opening new log file '{}'".format(self._log_file))
        self._log_file = open(self._data_file_path, "w")
        # Write a header to the log.
        header = ["TYPE"]
        header.extend(self._log_vars)
        self._log_file.write(self._sep.join(map(str, header)))
        # Create a lock to prevent simultaneous access to the log file.
        self._log_file_lock = Lock()
        # Each log will be counted, and every N logs the file will be flushed.
        # (This writes the data from the buffer to RAM and then to drive.)
        self._log_counter = 0
        self._log_consolidation_freq = 60
        # LOGGING THREAD
        # Initialise a new Queue to push samples through.
        self._logging_queue = Queue()
        # Set an event to signal when data SHOULD BE logged. This is set to
        # signal to the logging Thread that it should log or not.
        self._recording = Event()
        self._recording.clear()
        # Set an event that signals when DATA IS BEING logged. This is set by
        # the logging Thread to signal that the Queue is empty.
        self._logging_queue_empty = Event()
        self._logging_queue_empty.set()
        # Initialise the logging Thread.
        self._logging_thread = Thread( \
            target=self._log_samples,
            name='PyGaze_AleaTracker_logging', \
            args=[])

        # STREAMING THREAD
        # Create a placeholder for the most recent sample.
        self._recent_sample = CAleaData()
        # Create a Lock to prevent simultaneous access to the most recent
        # sample by the streaming thread and the sample function.
        self._recent_sample_lock = Lock()
        # Initialise the streaming Thread.
        self._streaming_thread = Thread( \
            target=self._stream_samples,
            name='PyGaze_AleaTracker_streaming', \
            args=[])
        
        # SAMPLE STREAMING
        # Tell the API to start streaming samples from the tracker.
        if self._debug:
            self._debug_log("DataStreaming: starting")
        self.api.DataStreaming(True)
        # Start the logging Thread.
        if self._debug:
            self._debug_log("Logging Thread: starting")
        self._logging_thread.start()
        # Start the streaming Thread.
        if self._debug:
            self._debug_log("Streaming Thread: starting")
        self._streaming_thread.start()
    
    
    def _debug_log(self, message):
        
        if self._debug:
            self._debug_file_lock.acquire()
            with open(self._debug_file_name, "a") as f:
                f.write("\n{}\t{}".format(datetime.datetime.now().strftime( \
                    "%Y-%m-%d_%H:%M:%S.%f")[:-3], message))
            self._debug_file_lock.release()


    def _flush_log_file(self):

        # Wait until the log file lock is released.
        self._log_file_lock.acquire()
        # Internal buffer to RAM.
        self._log_file.flush()
        # RAM to disk.
        os.fsync(self._log_file.fileno())
        # Release the log file lock.
        self._log_file_lock.release()

    
    def _log_samples(self):
        
        while self._connected.is_set():
            
            # Check if the sample Queue is empty.
            if self._logging_queue.empty():
                # Signal to other Threads that the logging Queue is empty.
                if not self._logging_queue_empty.is_set():
                    self._logging_queue_empty.set()
            
            # Process samples from the Queue.
            else:
                # Signal to other Threads that the Queue isn't empty.
                if self._logging_queue_empty.is_set():
                    self._logging_queue_empty.clear()
                # Get the next object from the Queue.
                sample = self._logging_queue.get()
                # Log the message string and/or the sample.
                if type(sample) in [tuple, list]:
                    self._write_tuple(sample)
                elif type(sample) == CAleaData:
                    self._write_sample(sample)
                else:
                    print("WARNING: Unrecognised object in log queue: '{}'".format( \
                        sample))
                # Increment the log counter.
                self._log_counter += 1
                # Check if the log file needs to be consolidated.
                if self._log_counter % self._log_consolidation_freq == 0:
                    # Consolidate the text file on the harddrive.
                    self._flush_log_file()
    
    
    def _stream_samples(self):
        
        while self._connected.is_set():
            
            # Wait for the next sample, or until 100 milliseconds have passed.
            sample = self.api.WaitForData(100)
            
            # Check if there wasn't a timeout.
            if sample is not None:
                if self._debug:
                    self._debug_log("WaitForData: sample obtained with timestamp {}".format( \
                        sample.rawDataTimeStamp))
                # Update the most recent sample.
                self._recent_sample_lock.acquire()
                self._recent_sample = copy.deepcopy(sample)
                self._recent_sample_lock.release()
                # Add the sample to the Queue, but only during recording.
                if self._recording.is_set():
                    self._logging_queue.put(sample)
            else:
                if self._debug:
                    self._debug_log("WaitForData: timeout")

    
    def _write_sample(self, sample):
        
        # Construct a list with the sample data.
        line = ["DAT"]
        for var in self._log_vars:
            line.append(sample.__getattribute__(var))
        # Log the sample to the log file.
        self._log_file_lock.acquire()
        self._log_file.write("\n" + self._sep.join(map(str, line)))
        self._log_file_lock.release()
    
    
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
        self._log_file_lock.acquire()
        self._log_file.write("\n" + self._sep.join(map(str, line)))
        self._log_file_lock.release()
    
    
    def calibrate(self, n_points=9, location=0, randomise=True, \
            randomize=None, slow=False, audio=True, eye=0, \
            skip_bad_points=False, automatic=True, bgc=(127,127,127), \
            fgc=(0,0,0), image=""):
        
        """
        desc:
            Performs an eye-tracker-controlled calibration: the tracker will
            autonomously run through the calibration process, uncluding the
            displaying of calibration points. The CalibrationDoneDelegate and
            ResultCalibrationExCB callbacks will be called when the
            calibration is finished or when an error occurs.
        
        keywords:
            n_points:
                desc:
                    Number of points used in the calibration. Choose from 1, 5,
                    9, or 16. (Default = 9)
                type: int
            location:
                desc:
                    Indication of where the calibration points should be
                    presented. Choose from 0 (Full, outer points are 5% off
                    the monitor edge), 1 (Center, outer points are 20% off
                    the monitor edge), 2 (Bottom, points are in the lower half
                    of the monitor), 3 (Horizontal, points are located in a
                    horizontal line), and 4 (Vertical, points are located in
                    a vertical line). (Default = 0)
                type: int
            randomise:
                desc:
                    Set to True to allow the tracker to randomise the order in
                    which calibration points are shown. Some experienced users
                    have a tendency to anticipate where points will be shown,
                    and to produce a systematic calibration error by moving
                    their eyes to the next point too quickly. Shuffling the
                    points prevents this. (Default = True)
                type: bool
            randomize:
                desc:
                    Same a randomise, but in US spelling. (Default = None)
                type: bool
            slow:
                desc:
                    Set to True to allow the tracker to show big and slow
                    calibration targets. (Default = False)
                type: bool
            audio:
                desc:
                    Set to True to allow the tracker to play a sound when the
                    point jumps to a new position. (Default = True)
                type: bool
            eye:
                desc:
                    Determines what eyes to calibrate and what eyes to track.
                    Choose from 0 (calibrate both eyes), 1 (calibrate the left
                    eye and track both eyes, "right glass eye"), 2 (calibrate
                    the right eye and track both eyes, "left glass eye"), 3
                    (calibrate and track only the left eye, "right pirate
                    eye"), or 4 (calibrate and track only the right eye, "left
                    pirate eye"). (Default = 0)
                type: int
            skip_bad_points:
                desc:
                    When set to True, IntelliGaze will not get stuck at
                    uncalibratable points. It will skip them, and try to
                    complete the calibration without them. (Default = False)
                type: bool
            automatic:
                desc:
                    Set to True to allow the tracker to detect fixations and
                    accept points automatically. (Default = True)
                type: bool
            bgc:
                desc:
                    RGB value of the background colour. This should have a
                    similar brightness to the experiment or application that
                    this calibration will be used with. The format is a tuple
                    with 3 ints in the range 0-255, representing red, green,
                    and blue. For example, (0,0,0) is black, and (255,255,255)
                    is white. (Default = (127,127,127))
                type: int
            fgc:
                desc:
                    RGB value of the calibration point colour. This should
                    have a good contrast to the background. The format is a
                    tuple with 3 ints in the range 0-255, representing red,
                    green, and blue. For example, (255,0,0) is pure red.
                    (Default = (0,0,0) )
                type: tuple
            image:
                desc:
                    Leave empty for the default circle, or provide a path to
                    an image file to use that image as calibration target. Use
                    the string "ANIMATION:PARROT" to calibrate with an
                    animation. (Default = "")
                type: str
            """
        
        # Check inputs.
        if n_points not in [1, 5, 9, 16]:
            # Close the connection and raise an Exception.
            self.api.Close()
            raise Exception("User requested {} points, but only 1, 5, 9, or 16 are allowed.".format( \
                n_points))

        if type(location) == int:
            if location not in [0, 1, 2, 3, 4]:
                # Close the connection and raise an Exception.
                self.api.Close()
                raise Exception("User requested location {}, but only 0, 1, 2, 3 or 4 are allowed.".format( \
                    location))
        elif type(location) == str:
            location = location.lower()
            if location not in ["full", "centre", "center", "bottom", "horizontal", "vertical"]:
                # Close the connection and raise an Exception.
                self.api.Close()
                raise Exception('User requested location {}, but only "full", "centre", "center", "bottom", "horizontal", "vertical" are allowed.'.format( \
                    location))
            if location == "full":
                location = 0
            elif location in ["centre", "center"]:
                location = 1
            elif location == "bottom":
                location = 2
            elif location == "horizontal":
                location = 3
            elif location == "vertical":
                location = 4
        else:
            # Close the connection and raise an Exception.
            self.api.Close()
            raise Exception('User requested location "{}" (type={}), but only "full", "centre", "center", "bottom", "horizontal", "vertical" are allowed.'.format( \
                location, type(location)))
        
        if randomize is not None:
            randomise = randomize

        if eye not in [0, 1, 2, 3, 4]:
            # Close the connection and raise an Exception.
            self.api.Close()
            raise Exception("User requested eye %d, but only 0, 1, 2, 3 or 4 are allowed." \
                % (eye))
        
        # Run the calibration.
        if self._debug:
            self._debug_log("PerformCalibration: n_points={}, location={}, randomise={}, slow={}, audio={}, automatic={}, bgc={}, fgc={}, image={}".format( \
                n_points, location, randomise, slow, audio, automatic, bgc, fgc, image))
        self.api.PerformCalibration(noPoints=n_points, location=location, \
            randomizePoints=randomise, slowMode=slow, audioFeedback=audio, \
            eye=eye, calibrationImprovement=False, \
            skipBadPoints=skip_bad_points, autoCalibration=automatic, \
            backColor=bgc, pointColor=fgc, \
            imageName=image)

        # Wait until the running calibration has finished.
        if self._debug:
            self._debug_log("WaitForCalibrationResult: waiting...")
        status, improve = self.api.WaitForCalibrationResult()
        if self._debug:
            self._debug_log("WaitForCalibrationResult: status={}, improve={}".format( \
                status, improve))
        
        return status, improve

    
    def log(self, message):
        
        """
        desc:
            Logs a message to the data file. The message will be timestamped
            with the most recently streamed sample.

        arguments:
            message:
                desc:
                    The message to be logged to the data file.
                type: string
        """

        # Get current timestamp.
        self._recent_sample_lock.acquire()
        t = self._recent_sample.rawDataTimeStamp
        self._recent_sample_lock.release()

        # Construct a tuple, and add it to the queue.
        self._logging_queue.put(("MSG", t, message))

    
    def start_recording(self):
        
        """
        desc:
            Starts the streaming of data to the log file.
        """
        
        if self._debug:
            self._debug_log("Starting recording")

        # Signal to the sample processing Thread to queue samples for the
        # logging Thread.
        self._recording.set()
    
    
    def stop_recording(self):
        
        """
        desc:
            Pauses the streaming of data to the log file.
        """
        
        if self._debug:
            self._debug_log("Stopping recording")

        # Signal to the sample processing Thread to stop queueing samples
        # for the logging Thread.
        self._recording.clear()
    
    
    def sample(self):
        
        """
        desc:
            Returns the latest sample's timestamp, intelliGaze X and Y
            coordinates, and average pupil size. This function does not block
            and/or wait for a new sample to come in, but instead simply reads
            the stored latest sample. This can be up to the inter-sample time
            old. E.g., it will be up to 33 ms old at a 30 Hz sampling rate.
        
        returns:
            desc:   A typle that contains the timestamp, X, Y, and pupil size.
                    The format is (int, float, float, float).
            type:   tuple
        """
        
        # Copy data from the most recent sample.
        self._recent_sample_lock.acquire()
        t = copy.copy(self._recent_sample.rawDataTimeStamp)
        x = copy.copy(self._recent_sample.intelliGazeX)
        y = copy.copy(self._recent_sample.intelliGazeY)
        l_size = copy.copy(self._recent_sample.pupilDiameterLeftEye)
        r_size = copy.copy(self._recent_sample.pupilDiameterRightEye)
        self._recent_sample_lock.release()

        # Compute the pupil size.
        if (l_size > 0) and (r_size > 0):
            p_size = (l_size + r_size) / 2.0
        elif l_size > 0:
            p_size = l_size
        elif r_size > 0:
            p_size = r_size
        else:
            p_size = 0.0

        return (t, x, y, p_size)
    
    
    def close(self):
        
        """
        desc:
            Closes the connection to the eye tracker. This will also
            automatically stop recording and close the data file. Note that
            this operation will block until all queued data is stored.
        """
        
        # Stop streaming samples from the API.
        if self._debug:
            self._debug_log("DataStreaming: turning off data streaming")
        self.api.DataStreaming(False)
        
        # Stop recording if it is still ongoing.
        if self._recording:
            self.stop_recording()
        
        # Wait until the Queue is empty, or until 60 seconds have passed.
        if self._debug:
            self._debug_log("Waiting for the logging Queue to empty")
        queue_empty = self._logging_queue_empty.wait(timeout=60.0)
        if not queue_empty:
            print("WARNING: Logging Thread timeout occurred; something might have gone wrong!")
            if self._debug:
                self._debug_log("Logging Queue failed to empty within 60 seconds")
        
        # Signal to the Threads to stop.
        if self._debug:
            self._debug_log("Signalling to Threads that the connection is closed")
        self._connected.clear()
        
        # Close the log file.
        if self._debug:
            self._debug_log("Closing the log file")
        self._log_file.close()
        
        # Close the connection.
        if self._debug:
            self._debug_log("Close: closing API connection")
        self.api.Close()


# Define the class that handles API communication.
class AleaAPI:
    
    """Python wrapper for the ET API from Alea Technologies"""
    
    def __init__(self):
        
        """
        desc:
            Initialises an AleaAPI object, but really only checks whether the
            DLL is properly loaded. Make sure to call Open to start the
            connection.
        """

        # Raise an exception if the DLL could not be loaded.
        if etapi is None:
            raise Exception("Could not load the CEtAPi DLL. Has it been installed? Has it been added to the path?")

    
    def _error(self, code):
        
        # Attempt to close the connection to the API.
        try:
            self.Close()
        except:
            print("WARNING: Failed to close the connection to the API!")
        
        # Throw an Exception.
        raise Exception("Alea EtAPI error: {}".format(EtApiError[code]))

    
    def Open(self, appKey, targetIP=None, targetPort=None, listenIP=None, \
        listenPort=None):
        
        """
        desc:
            Initialises the API, opens the socket connection, establishes a
            link to the hardware. Make sure that no firewall is blocking the
            port. This function will use the default values for IP addresses
            and ports, unless all keyword arguments are specified.
        
        arguments:
            appKey:
                desc:
                    Application-specific key to register the application, ask
                    alea technologies for your specific application key.
                type: str
        
        keywords:
            targetIP:
                desc:
                    IP address of the eye tracker. (Default = "127.0.0.1")
                type: str
            targetPort:
                desc:
                    Target port of the server socket link. (Default = 27412)
                type: int
            listenIP:
                desc:
                    IP address of the client application. (Default is 
                    "127.0.0.1")
                type: str
            listenPort:
                desc:
                    Listen port of the client socket link. (Default = 27413)
        """
        
        # Check whether all keyword arguments are None.
        if (targetIP is None) or (targetPort is None) or (listenIP is None) or (listenPort is None):
            # Use the default values as set in the API.
            r = etapi.Open(ctypes.c_char_p(appKey.encode("utf-8")))
        else:
            # Use the user-defined values.
            r = etapi.Open(ctypes.c_char_p(appKey.encode("utf-8")), \
                ctypes.c_char_p(targetIP.encode("utf-8")), ctypes.c_int32(targetPort), \
                ctypes.c_char_p(listenIP.encode("utf-8")), ctypes.c_int32(listenPort))
        # Check the result.
        if not check_result(r):
            self._error(r)
    
    
    def IsOpen(self):
        
        """
        desc:
            Checks whether the API is open (but not whether the server is up
            and running).
        
        returns:
            desc: True if the API is open, and False if not.
            type: bool
        """
        
        # Make a call to the API, and save the result in a variable.
        is_open = ctypes.c_bool()
        r = etapi.IsOpen(ctypes.byref(is_open))
        
        # Check the result.
        if check_result(r):
            return is_open.value
        else:
            self._error(r)
    
    
    def WaitForData(self, timeOutMilliseconds):
        
        """
        desc:
            Blocks until the next sample comes in. It is not recommended to
            use this function for data streaming. Use Sample instead.
        
        arguments:
            timeOutMilliseconds:
                desc:   Timeout in milliseconds. This function will return
                        on obtaining a sample or on timing out.
                type:   int
        
        returns:
            desc:   The latest AleaData when it becomes available. This is a
                    CAleaData struct, or None if a timeout occurred.
            type:   ctypes.Structure
        """

        # Create a sample struct to write incoming data to.
        sample = CAleaData()
        dwMilliseconds = ctypes.c_int32(timeOutMilliseconds)
        # Make a call to the API, and save the result in a variable.
        r = etapi.WaitForData(ctypes.byref(sample), dwMilliseconds)
        
        # Check if the result is a timeout.
        if r == -1:
            # Set the sample to None.
            sample = None

        # Catch any other errors.
        else:
            if not check_result(r):
                self._error(r)
        
        return sample
        

    def Close(self):
        
        """
        desc:
            Closes the API, releases the socket connection, and frees API
            resources. Call close before quiting the client application!
        """
        
        # Make a call to the API, and save the result in a variable.
        r = etapi.Close()
        
        # In the C API wrapper, the Close function doesn't actually return
        # anything. Instead, it raises a warning about a blocking operation
        # being interrupted by a call to WSACancelBlockingCall. Thus, the
        # result is likely to be 1. We'll ignore this locally.
        if r == 1:
            return

        # Check the result.
        if not check_result(r):
            self._error(r)
    
    
    def Version(self):
        
        """
        desc:
            Returns the major.minor.build version and the device type. The
            device type is coded 0 for IG30 systems, and 1 for IG15 systems.
        
        returns:
            desc: The version and device in a single string, formatted 
                  "major.minor.build.device"
            type: str
        """
        
        # Make a call to the API, and save the result in a variable.
        major = ctypes.c_int32()
        minor = ctypes.c_int32()
        build = ctypes.c_int32()
        device = ctypes.c_int32()
        r = etapi.Version(ctypes.byref(major), ctypes.byref(minor), \
            ctypes.byref(build), ctypes.byref(device))
        # DEBUG #
        print(major.value)
        print(minor.value)
        print(build.value)
        print(device.value)
        # # # # #
        # Convert to string.
        version = "{}.{}.{}.{}".format( \
            major.value, minor.value, build.value, device.value)
        
        # Check the result.
        if check_result(r):
            return version
        else:
            self._error(r)
    
    
    def PerformCalibration(self, noPoints=9, location=0, \
        randomizePoints=True, slowMode=False, audioFeedback=True, eye=0, \
        calibrationImprovement=False, skipBadPoints=False, \
        autoCalibration=True, backColor=(127,127,127), pointColor=(0,0,0), \
        imageName=""):
        
        """
        desc:
            Performs an eye-tracker-controlled calibration: the tracker will
            autonomously run through the calibration process, uncluding the
            displaying of calibration points. The CalibrationDoneDelegate and
            ResultCalibrationExCB callbacks will be called when the
            calibration is finished or when an error occurs.
        
        keywords:
            noPoints:
                desc:
                    Number of points used in the calibration. Choose from 1, 5,
                    9, or 16. (Default = 9)
                type: int
            location:
                desc:
                    Indication of where the calibration points should be
                    presented. Choose from 0 (Full, outer points are 5% off
                    the monitor edge), 1 (Center, outer points are 20% off
                    the monitor edge), 2 (Bottom, points are in the lower half
                    of the monitor), 3 (Horizontal, points are located in a
                    horizontal line), and 4 (Vertical, points are located in
                    a vertical line). (Default = 0)
                type: int
            randomizePoints:
                desc:
                    Set to True to allow the tracker to randomise the order in
                    which calibration points are shown. Some experienced users
                    have a tendency to anticipate where points will be shown,
                    and to produce a systematic calibration error by moving
                    their eyes to the next point too quickly. Shuffling the
                    points prevents this. (Default = True)
                type: bool
            slowMode:
                desc:
                    Set to True to allow the tracker to show big and slow
                    calibration targets. (Default = False)
                type: bool
            audioFeedback:
                desc:
                    Set to True to allow the tracker to play a sound when the
                    point jumps to a new position. (Default = True)
                type: bool
            eye:
                desc:
                    Determines what eyes to calibrate and what eyes to track.
                    Choose from 0 (calibrate both eyes), 1 (calibrate the left
                    eye and track both eyes, "right glass eye"), 2 (calibrate
                    the right eye and track both eyes, "left glass eye"), 3
                    (calibrate and track only the left eye, "right pirate
                    eye"), or 4 (calibrate and track only the right eye, "left
                    pirate eye"). (Default = 0)
                type: int
            calibrationImprovement:
                desc:
                    Set to True if outliers or skipped points from a previous
                    calibrations should be re-calibrated. Can only be done
                    when a previous calibration returned with an "Improvement"
                    suggestion! (Default = False)
                type: bool
            skipBadPoints:
                desc:
                    When set to True, IntelliGaze will not get stuck at
                    uncalibratable points. It will skip them, and try to
                    complete the calibration without them. (Default = False)
                type: bool
            autoCalibration:
                desc:
                    Set to True to allow the tracker to detect fixations and
                    accept points automatically. (Default = True)
                type: bool
            backColor:
                desc:
                    RGB value of the background colour. This should have a
                    similar brightness to the experiment or application that
                    this calibration will be used with. The format is a tuple
                    with 3 ints in the range 0-255, representing red, green,
                    and blue. For example, (0,0,0) is black, and (255,255,255)
                    is white. (Default = (127,127,127) )
                type: int
            pointColor:
                desc:
                    RGB value of the calibration point colour. This should
                    have a good contrast to the background. The format is a
                    tuple with 3 ints in the range 0-255, representing red,
                    green, and blue. For example, (255,0,0) is pure red.
                    (Default = (0,0,0) )
                type: tuple
            imageName:
                desc:
                    Leave empty for the default circle, or provide a path to
                    an image file to use that image as calibration target. Use
                    the string "ANIMATION:PARROT" to calibrate with an
                    animation. (Default = "")
                type: str
        """
        
        # Convert the colours from RGB to 32-bit integer ARGB format.
        alpha = 255 * 256 * 256 * 256
        backColor = alpha + backColor[0] * 256 * 256 + backColor[1] * 256 \
            + backColor[2]
        pointColor = alpha + pointColor[0] * 256 * 256 + pointColor[1] * 256 \
            + pointColor[2]
        
        # Make a call to the API, and save the result in a variable.
        r = etapi.PerformCalibration(ctypes.c_int32(noPoints), \
            ctypes.c_int32(location), ctypes.c_bool(randomizePoints), \
            ctypes.c_bool(slowMode), ctypes.c_bool(audioFeedback), \
            ctypes.c_int32(eye), ctypes.c_bool(calibrationImprovement), \
            ctypes.c_bool(skipBadPoints), ctypes.c_bool(autoCalibration), \
            ctypes.c_int32(backColor), ctypes.c_int32(pointColor), \
            ctypes.c_char_p(imageName.encode("utf-8")))
        # Check the result.
        if not check_result(r):
            self._error(r)
    
    
    def WaitForCalibrationResult(self):
        
        """
        desc:
            Waits until the calibration is done, or until an error occurs.
        
        returns:
            desc:   Status and improve values for the current calibration,
                    Boolean values captured in a tuple (status, improve)
            type:   tuple
        """
        
        # Set up variables to pass to the API function.
        status = ctypes.c_int32()
        improve = ctypes.c_bool()
        # Set the wait time to -1, to signal there isn't a fixed timeout.
        dwMilliseconds = ctypes.c_int(-1)
        
        # Wait for it.
        r = etapi.WaitForCalibrationResult(ctypes.byref(status), \
            ctypes.byref(improve), dwMilliseconds)

        # Check the result.
        if not check_result(r):
            self._error(r)
        
        return (status.value, improve.value)
    
    
    def DataStreaming(self, mode):
        
        """
        desc:
            Instructs the eye tracker to stream data, which will cause
            callback functions to be called when new data becomes available.
            When streaming is disabled, the application centre of IntelliGaze
            is active, as is the mouse control. When data streaming is turned
            on, IntelliGaze is operated in "background mode": The application
            centre is invisible, and no IntelliGaze mouse control takes place.
        
        arguments:
            mode:
                desc:
                    Determines the streaming mode. Choose from 0 (disable
                    streaming), 1 (stream raw data at the maximum tracker
                    speed), 2 (stream eye events data, i.e. fixations and
                    saccades), 4 (stream Blickfang activation data), or 8
                    (EyeGesture data).
                type: int
        """

        # Make a call to the API, and save the result in a variable.
        r = etapi.DataStreaming(ctypes.c_int32(mode))
        # Check the result.
        if not check_result(r):
            self._error(r)
    
    
    def ShowStatusWindow(self, posX, posY, size, opacity):
        
        """
        desc:
            Displays the eye tracker status window at the given position. The
            status window informs about the relative position of the head and
            any eye tracking problems.
        
        arguments:
            posX:
                desc:
                    Horizontal position on the screen (in pixels).
                type: int
            posY:
                desc:
                    Vertical position on the screen (in pixels).
                type: int
            size:
                desc:
                    Width of the status window (in pixels). Can range from 100
                    to 768.
                type: int
            opacity:
                desc:
                    Opacity of the status window, expressed as a percentage.
                type: int
        """
        
        # Make a call to the API, and save the result in a variable.
        r = etapi.ShowStatusWindow(ctypes.c_int32(posX), ctypes.c_int32(posY), \
            ctypes.c_int32(size), ctypes.c_int32(opacity))
        # Check the result.
        if not check_result(r):
            self._error(r)
    
    
    def HideStatusWindow(self):
        
        """
        desc:
            Hides the status window. For info on how to show the status window,
            see the ShowStatusWindow function.
        """
        
        # Make a call to the API, and save the result in a variable.
        r = etapi.HideStatusWindow()
        # Check the result.
        if not check_result(r):
            self._error(r)


    def ExitServer(self):
        
        """
        desc:
            Exits the eye tracker server application.
        """
        
        # Make a call to the API, and save the result in a variable.
        r = etapi.ExitServer()
        # Check the result.
        if not check_result(r):
            self._error(r)


    def QuitServer(self):
        
        """
        desc:
            Exits the eye tracker server application.
        """
        
        # NOTE: Not entirely sure which is the correct function: ExitServer is
        # used in the C API, but QuitServer is listed in the documentation.
        
        # Make a call to the API, and save the result in a variable.
        r = etapi.QuitServer()
        # Check the result.
        if not check_result(r):
            self._error(r)


# # # # #
# UNSUPPORTED IN C API

# The following functions appear in the API, but are not supported in the C
# wrapper for the API. They are commented out for now, but retained in the
# code base in case support is supported/required in future releases.


#    def StartCalibration(self, noPoints=9, location=0, randomizePoints=True, \
#        eye=0, calibrationImprovement=False, skipBadPoints=True, 
#        autoCalibration=True):
#        
#        """
#        desc:
#            Starts a client-controlled calibration. This means the client
#            software is responsible for showing and moving the calibration
#            points! The eye tracker will call the CalibrationDoneDelegate
#            callback when it's finished or an error occurred.
#        
#        keywords:
#            noPoints:
#                desc:
#                    Number of points used in the calibration. Choose from 1, 5,
#                    9, or 16. (Default = 9)
#                type: int
#            location:
#                desc:
#                    Indication of where the calibration points should be
#                    presented. Choose from 0 (Full, outer points are 5% off
#                    the monitor edge), 1 (Center, outer points are 20% off
#                    the monitor edge), 2 (Bottom, points are in the lower half
#                    of the monitor), 3 (Horizontal, points are located in a
#                    horizontal line), and 4 (Vertical, points are located in
#                    a vertical line). (Default = 0)
#                type: int
#            randomizePoints:
#                desc:
#                    Set to True to allow the tracker to randomise the order in
#                    which calibration points are shown. Some experienced users
#                    have a tendency to anticipate where points will be shown,
#                    and to produce a systematic calibration error by moving
#                    their eyes to the next point too quickly. Shuffling the
#                    points prevents this. (Default = True)
#                type: bool
#            eye:
#                desc:
#                    Determines what eyes to calibrate and what eyes to track.
#                    Choose from 0 (calibrate both eyes), 1 (calibrate the left
#                    eye and track both eyes, "right glass eye"), 2 (calibrate
#                    the right eye and track both eyes, "left glass eye"), 3
#                    (calibrate and track only the left eye, "right pirate
#                    eye"), or 4 (calibrate and track only the right eye, "left
#                    pirate eye"). (Default = 0)
#                type: int
#            calibrationImprovement:
#                desc:
#                    Set to True if outliers or skipped points from a previous
#                    calibrations should be re-calibrated. Can only be done
#                    when a previous calibration returned with an "Improvement"
#                    suggestion! (Default = False)
#                type: bool
#            skipBadPoints:
#                desc:
#                    When set to True, IntelliGaze will not get stuck at
#                    uncalibratable points. It will skip them, and try to
#                    complete the calibration without them. (Default = True)
#                type: bool
#            autoCalibration:
#                desc:
#                    Set to True to allow the tracker to detect fixations and
#                    accept points automatically. (Default = True)
#                type: bool
#        """
#        
#        # Make a call to the API, and save the result in a variable.
#        r = etapi.StartCalibration(ctypes.c_int32(noPoints), \
#            ctypes.c_int32(location), ctypes.c_bool(randomizePoints), \
#            ctypes.c_int32(eye), ctypes.c_bool(calibrationImprovement), \
#            ctypes.c_bool(skipBadPoints), ctypes.c_bool(autoCalibration))
#        # Check the result.
#        if not check_result(r):
#            self._error(r)
    
    
#    def StopCalibration(self):
#        
#        """
#        desc:
#            Interrupts the calibration procedure, and will cause the eye
#            tracker to notify the client about the calibration result by
#            calling the CalibrationDoneDelegate callback.
#        """
#
#        # Make a call to the API, and save the result in a variable.
#        r = etapi.StopCalibration()
#        # Check the result.
#        if not check_result(r):
#            self._error(r)
    
    
#    def CalibrationStatus(self, isMoving, isHot, acceptPoint):
#        
#        """
#        desc:
#            Informs the eye tracker server about the current status of the
#            calibration procedure. Note that this function allows client
#            software to let the tracker know about the calibration,
#            particularly whether the calibration target is moving, whether
#            it's "hot" (OK to accept fixations for), and whether to the point
#            should be force-accepted. This data is required by the eye tracker
#            to know when to search for fixations during the calibration
#            procedure.
#        
#        arguments:
#            isMoving:
#                desc:
#                    Set this to True while the fixation target is moving.
#                type: bool
#            isHot:
#                desc:
#                    Set this to True to make the eye tracker accept the next
#                    fixation it detects.
#                type: bool
#            acceptPoint:
#                desc:
#                    If set to True, the eye tracker will accept the next 
#                    fixation it detects to accept the calibration point. Use
#                    this parameter when doing a manual (not self-paced)
#                    calibration, i.e. set this to True when the operator hits
#                    a key to confirm fixation. (Not available in
#                    autoCalibration mode.)
#                type: bool
#        """
#
#        # Make a call to the API, and save the result in a variable.
#        r = etapi.StartCalibration(ctypes.c_bool(isMoving), \
#            ctypes.c_bool(isHot), ctypes.c_bool(acceptPoint))
#        # Check the result.
#        if not check_result(r):
#            self._error(r)
    
    
#    def LoadCalibration(self, profileName):
#        
#        """
#        desc:
#            Tries to load a calibration for the passed profile name.
#        
#        arguments:
#            profileName:
#                desc:
#                    Name of the profile to load.
#                type: str
#        
#        returns:
#            desc: True when the function succeeds, and False when it didn't.
#            type: bool
#            
#        """
#
#        # Make a call to the API, and save the result in a variable.
#        r = etapi.LoadCalibration(ctypes.c_char_p(profileName.encode("utf-8")))
#        # Check and return the result.
#        return check_result(r)
    
    
#    def SaveCalibration(self, profileName):
#        
#        """
#        desc:
#            Tries to save the current calibration profile under the passed
#            profile name.
#        
#        arguments:
#            profileName:
#                desc:
#                    Name of the profile to save the current calibration for.
#                type: str
#        
#        returns:
#            desc: True when the function succeeds, and False when it didn't.
#            type: bool
#            
#        """
#
#        # Make a call to the API, and save the result in a variable.
#        r = etapi.SaveCalibration(ctypes.c_char_p(profileName.encode("utf-8")))
#        # Check and return the result.
#        return check_result(r)
    
    
#    def CalibrationSize(self):
#        
#        """
#        desc:
#            Returns the size of the calibration area. Can be used to remap the
#            gaze data if the screen resolution is changed.
#        
#        returns:
#            desc:
#                A (width,height) tuple of integers describing the calibration
#                area's size.
#            type: tuple
#        """
#        
#        # Create two variables to hold the width and height in.
#        width = ctypes.c_int32()
#        height = ctypes.c_int32()
#
#        # Make a call to the API, and save the result in a variable.
#        r = etapi.CalibrationSize(ctypes.byref(width), ctypes.byref(height))
#        # Check the result.
#        if not check_result(r):
#            self._error(r)
#        
#        return (width.value, height.value)


#    def SetCorrectionPoint(self, targetX, targetY):
#        
#        """
#        desc:
#            Improves the calibration accuracy by feeding gaze activations back
#            into the gaze mapping function. Call this function if a participant
#            is looking at a target. This is effectively a drift correction.
#        
#        arguments:
#            targetX:
#                desc:
#                    The horizontal location of the target on the screen
#                    (measured in pixels).
#                type: int
#            targetY:
#                desc:
#                    The vertical location of the target on the screen
#                    (measured in pixels).
#                type: int
#        """
#
#        # Make a call to the API, and save the result in a variable.
#        r = etapi.SetCorrectionPoint(ctypes.c_int32(targetX), \
#            ctypes.c_int32(targetY))
#        # Check the result.
#        if not check_result(r):
#            self._error(r)

#    def StartCalibration(self, noPoints=9, location=0, randomizePoints=True, \
#        eye=0, calibrationImprovement=False, skipBadPoints=True, 
#        autoCalibration=True):
#        
#        """
#        desc:
#            Starts a client-controlled calibration. This means the client
#            software is responsible for showing and moving the calibration
#            points! The eye tracker will call the CalibrationDoneDelegate
#            callback when it's finished or an error occurred.
#        
#        keywords:
#            noPoints:
#                desc:
#                    Number of points used in the calibration. Choose from 1, 5,
#                    9, or 16. (Default = 9)
#                type: int
#            location:
#                desc:
#                    Indication of where the calibration points should be
#                    presented. Choose from 0 (Full, outer points are 5% off
#                    the monitor edge), 1 (Center, outer points are 20% off
#                    the monitor edge), 2 (Bottom, points are in the lower half
#                    of the monitor), 3 (Horizontal, points are located in a
#                    horizontal line), and 4 (Vertical, points are located in
#                    a vertical line). (Default = 0)
#                type: int
#            randomizePoints:
#                desc:
#                    Set to True to allow the tracker to randomise the order in
#                    which calibration points are shown. Some experienced users
#                    have a tendency to anticipate where points will be shown,
#                    and to produce a systematic calibration error by moving
#                    their eyes to the next point too quickly. Shuffling the
#                    points prevents this. (Default = True)
#                type: bool
#            eye:
#                desc:
#                    Determines what eyes to calibrate and what eyes to track.
#                    Choose from 0 (calibrate both eyes), 1 (calibrate the left
#                    eye and track both eyes, "right glass eye"), 2 (calibrate
#                    the right eye and track both eyes, "left glass eye"), 3
#                    (calibrate and track only the left eye, "right pirate
#                    eye"), or 4 (calibrate and track only the right eye, "left
#                    pirate eye"). (Default = 0)
#                type: int
#            calibrationImprovement:
#                desc:
#                    Set to True if outliers or skipped points from a previous
#                    calibrations should be re-calibrated. Can only be done
#                    when a previous calibration returned with an "Improvement"
#                    suggestion! (Default = False)
#                type: bool
#            skipBadPoints:
#                desc:
#                    When set to True, IntelliGaze will not get stuck at
#                    uncalibratable points. It will skip them, and try to
#                    complete the calibration without them. (Default = True)
#                type: bool
#            autoCalibration:
#                desc:
#                    Set to True to allow the tracker to detect fixations and
#                    accept points automatically. (Default = True)
#                type: bool
#        """
#        
#        # Make a call to the API, and save the result in a variable.
#        r = etapi.StartCalibration(ctypes.c_int32(noPoints), \
#            ctypes.c_int32(location), ctypes.c_bool(randomizePoints), \
#            ctypes.c_int32(eye), ctypes.c_bool(calibrationImprovement), \
#            ctypes.c_bool(skipBadPoints), ctypes.c_bool(autoCalibration))
#        # Check the result.
#        if not check_result(r):
#            self._error(r)
    
    
#    def StopCalibration(self):
#        
#        """
#        desc:
#            Interrupts the calibration procedure, and will cause the eye
#            tracker to notify the client about the calibration result by
#            calling the CalibrationDoneDelegate callback.
#        """
#
#        # Make a call to the API, and save the result in a variable.
#        r = etapi.StopCalibration()
#        # Check the result.
#        if not check_result(r):
#            self._error(r)
    
    
#    def CalibrationStatus(self, isMoving, isHot, acceptPoint):
#        
#        """
#        desc:
#            Informs the eye tracker server about the current status of the
#            calibration procedure. Note that this function allows client
#            software to let the tracker know about the calibration,
#            particularly whether the calibration target is moving, whether
#            it's "hot" (OK to accept fixations for), and whether to the point
#            should be force-accepted. This data is required by the eye tracker
#            to know when to search for fixations during the calibration
#            procedure.
#        
#        arguments:
#            isMoving:
#                desc:
#                    Set this to True while the fixation target is moving.
#                type: bool
#            isHot:
#                desc:
#                    Set this to True to make the eye tracker accept the next
#                    fixation it detects.
#                type: bool
#            acceptPoint:
#                desc:
#                    If set to True, the eye tracker will accept the next 
#                    fixation it detects to accept the calibration point. Use
#                    this parameter when doing a manual (not self-paced)
#                    calibration, i.e. set this to True when the operator hits
#                    a key to confirm fixation. (Not available in
#                    autoCalibration mode.)
#                type: bool
#        """
#
#        # Make a call to the API, and save the result in a variable.
#        r = etapi.StartCalibration(ctypes.c_bool(isMoving), \
#            ctypes.c_bool(isHot), ctypes.c_bool(acceptPoint))
#        # Check the result.
#        if not check_result(r):
#            self._error(r)
    
    
#    def LoadCalibration(self, profileName):
#        
#        """
#        desc:
#            Tries to load a calibration for the passed profile name.
#        
#        arguments:
#            profileName:
#                desc:
#                    Name of the profile to load.
#                type: str
#        
#        returns:
#            desc: True when the function succeeds, and False when it didn't.
#            type: bool
#            
#        """
#
#        # Make a call to the API, and save the result in a variable.
#        r = etapi.LoadCalibration(ctypes.c_char_p(profileName.encode("utf-8")))
#        # Check and return the result.
#        return check_result(r)
    
    
#    def SaveCalibration(self, profileName):
#        
#        """
#        desc:
#            Tries to save the current calibration profile under the passed
#            profile name.
#        
#        arguments:
#            profileName:
#                desc:
#                    Name of the profile to save the current calibration for.
#                type: str
#        
#        returns:
#            desc: True when the function succeeds, and False when it didn't.
#            type: bool
#            
#        """
#
#        # Make a call to the API, and save the result in a variable.
#        r = etapi.SaveCalibration(ctypes.c_char_p(profileName.encode("utf-8")))
#        # Check and return the result.
#        return check_result(r)
    
    
#    def CalibrationSize(self):
#        
#        """
#        desc:
#            Returns the size of the calibration area. Can be used to remap the
#            gaze data if the screen resolution is changed.
#        
#        returns:
#            desc:
#                A (width,height) tuple of integers describing the calibration
#                area's size.
#            type: tuple
#        """
#        
#        # Create two variables to hold the width and height in.
#        width = ctypes.c_int32()
#        height = ctypes.c_int32()
#
#        # Make a call to the API, and save the result in a variable.
#        r = etapi.CalibrationSize(ctypes.byref(width), ctypes.byref(height))
#        # Check the result.
#        if not check_result(r):
#            self._error(r)
#        
#        return (width.value, height.value)


#    def SetCorrectionPoint(self, targetX, targetY):
#        
#        """
#        desc:
#            Improves the calibration accuracy by feeding gaze activations back
#            into the gaze mapping function. Call this function if a participant
#            is looking at a target. This is effectively a drift correction.
#        
#        arguments:
#            targetX:
#                desc:
#                    The horizontal location of the target on the screen
#                    (measured in pixels).
#                type: int
#            targetY:
#                desc:
#                    The vertical location of the target on the screen
#                    (measured in pixels).
#                type: int
#        """
#
#        # Make a call to the API, and save the result in a variable.
#        r = etapi.SetCorrectionPoint(ctypes.c_int32(targetX), \
#            ctypes.c_int32(targetY))
#        # Check the result.
#        if not check_result(r):
#            self._error(r)

# -----------------------------------------------------------------------
# Copyright (C) 2019-2020, EyeLogic GmbH
#
# Permission is hereby granted, free of charge, to any person or
# organization obtaining a copy of the software and accompanying
# documentation covered by this license (the "Software") to use,
# reproduce, display, distribute, execute, and transmit the Software,
# and to prepare derivative works of the Software, and to permit
# third-parties to whom the Software is furnished to do so.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, TITLE AND
# NON-INFRINGEMENT. IN NO EVENT SHALL THE COPYRIGHT HOLDERS OR ANYONE
# DISTRIBUTING THE SOFTWARE BE LIABLE FOR ANY DAMAGES OR OTHER
# LIABILITY, WHETHER IN CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT
# OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# -----------------------------------------------------------------------

## @package ELApi
# This module contains the python prototype declaration for all functions which
# are neccessary to control the EyeLogic software from an API client.

from ctypes import *
from ctypes import wintypes
from enum import Enum
import os
import sys


## contains all information about the state of the eyes at a specific time
class ELGazeSample(Structure):
    _fields_ = [ \
        ("timestampMicroSec",c_int64), \
        ("index",c_int32), \
        ("porRawX",c_double), \
        ("porRawY",c_double), \
        ("porFilteredX",c_double), \
        ("porFilteredY",c_double), \
        ("porLeftX",c_double), \
        ("porLeftY",c_double), \
        ("eyePositionLeftX",c_double), \
        ("eyePositionLeftY",c_double), \
        ("eyePositionLeftZ",c_double), \
        ("pupilRadiusLeft",c_double), \
        ("porRightX",c_double), \
        ("porRightY",c_double), \
        ("eyePositionRightX",c_double), \
        ("eyePositionRightY",c_double), \
        ("eyePositionRightZ",c_double), \
        ("pupilRadiusRight",c_double) \
     ]


## Events coming from the eye tracker
class ELEvent(Enum):
    ## screen or resolution has changed
    SCREEN_CHANGED = 0
    ## connected to server closed
    CONNECTION_CLOSED = 1
    ## a new eye tracker has connected
    DEVICE_CONNECTED = 2
    ## the actual eye tracker has disconnected
    DEVICE_DISCONNECTED = 3
    ## tracking stopped
    TRACKING_STOPPED = 4


## callback function type, new gaze samples
GazeSampleCallback = CFUNCTYPE(None, POINTER(ELGazeSample))
## callback function type, event occurred
EventCallback = CFUNCTYPE(None, c_int32)

if sys.maxsize > 2**32:
    libname = "ELCApi"
else:
    libname = "ELCApi32"
baseDir = os.path.dirname(os.path.abspath(__file__))
libnameGlobal = os.path.join(baseDir, libname + ".dll")
if not os.path.isfile(libnameGlobal):
    raise Exception(
        "WARNING: Could not find EyeLogic dll in its expected location: '{}'".
        format(libnameGlobal))
try:
    kernel32 = WinDLL('kernel32', use_last_error=True)

    def check_bool(result, func, args):
        if not result:
            raise WinError(get_last_error())
        return args

    kernel32.LoadLibraryExW.errcheck = check_bool
    kernel32.LoadLibraryExW.restype = wintypes.HMODULE
    kernel32.LoadLibraryExW.argtypes = (wintypes.LPCWSTR, wintypes.HANDLE,
                                        wintypes.DWORD)
    # 0x00000008 = LOAD_WITH_ALTERED_SEARCH_PATH
    c_libH = kernel32.LoadLibraryExW(libnameGlobal, None, 0x00000008)
    c_lib = WinDLL(libname, handle=c_libH)
except:
    raise Exception("WARNING: Failed to load '{}'".format(libnameGlobal))

## marker for an invalid double value
ELInvalidValue = c_double.in_dll(c_lib, "ELCInvalidValue").value


## main class for communication with the EyeLogic server
class ELApi:

    ## constructor
    #
    # @param   clientName       string identifier of the client (shown in the server tool
    #                           window), may be null
    def __init__(self, clientName: str):

        global c_lib
        clientNameUtf8 = clientName.encode('utf-8')
        c_lib.elInitApi.argtypes = [c_char_p]
        c_lib.elInitApi.restype = c_int
        c_lib.elInitApi(c_char_p(clientNameUtf8))

## destructor

    def __del__(self):
        c_lib.elDestroyApi()

## registers sample callback listener
# @param   sampleCallback   this callback function is called on new gaze samples, may be null

    def registerGazeSampleCallback(self, sampleCallback: GazeSampleCallback):
        c_lib.elRegisterGazeSampleCallback.argtypes = [GazeSampleCallback]
        c_lib.elRegisterGazeSampleCallback.restype = None
        if sampleCallback is None:
            c_lib.elRegisterGazeSampleCallback(cast(None, GazeSampleCallback))
        else:
            c_lib.elRegisterGazeSampleCallback(sampleCallback)

## registers event callback listener
# @param   eventCallback   this callback function is called on eye tracking events, may be null

    def registerEventCallback(self, eventCallback: EventCallback):
        c_lib.elRegisterEventCallback.argtypes = [EventCallback]
        c_lib.elRegisterEventCallback.restype = None
        if eventCallback is None:
            c_lib.elRegisterEventCallback(cast(None, EventCallback))
        else:
            c_lib.elRegisterEventCallback(eventCallback)

## return values of connect( )

    class ReturnConnect(Enum):
        ## connection successully established
        SUCCESS = 0
        ## connection failed: library needs to be initialized first (constructor call missing)
        NOT_INITED = 1
        ## connection failed: API is build on a newer version than the server.
        # Update the EyeLogicServer to the newest version.
        VERSION_MISMATCH = 2
        ## connection failed: the server can not be found or is not responding
        TIMEOUT = 3

## initialize connection to the server (method is blocking until connection
# established)
#
# @return success state

    def connect(self) -> ReturnConnect:
        global c_lib
        c_lib.elConnect.argtypes = []
        c_lib.elConnect.restype = c_int32
        return ELApi.ReturnConnect(c_lib.elConnect())

## closes connection to the server

    def disconnect(self):
        global c_lib
        c_lib.elDisconnect.argtypes = []
        c_lib.elDisconnect.restype = None
        c_lib.elDisconnect()

## whether a connection to the server is established

    def isConnected(self) -> bool:
        global c_lib
        c_lib.elDisconnect.argtypes = []
        c_lib.elDisconnect.restype = c_bool
        return c_lib.elIsConnected()

    ## configuration of the stimulus screen
    class ScreenConfig(Structure):
        _fields_ = [ \
            ("id",c_int32), \
            ("resolutionX",c_int32), \
            ("resolutionY",c_int32), \
            ("physicalSizeX_mm",c_double), \
            ("physicalSizeY_mm",c_double), \
            ("dpiX",c_double), \
            ("dpiY",c_double), \
        ]

    ## get stimulus screen configuration
    # @return    screen configuration
    def getScreenConfig(self) -> ScreenConfig:
        global c_lib
        c_lib.elGetScreenConfig.argtypes = [POINTER(ELApi.ScreenConfig)]
        c_lib.elGetScreenConfig.restype = None
        screenConfig = ELApi.ScreenConfig()
        c_lib.elGetScreenConfig(pointer(screenConfig))
        return screenConfig

    ## configuration of the eye tracker
    class DeviceConfig:
        def __init__(self, deviceSerial):
            self.deviceSerial = deviceSerial
            self.frameRates = []
            self.calibrationMethods = []

    ## get configuration of actual eye tracker device
    # @return    device configuration
    def getDeviceConfig(self) -> DeviceConfig:
        global c_lib

        class DeviceConfigInternal(Structure):
            _fields_ = [ \
                ("deviceSerial",c_int64), \
                ("numFrameRates",c_int32), \
                ("frameRates",c_uint8 * 16), \
                ("numCalibrationMethods",c_int32), \
                ("calibrationMethods",c_uint8 * 16), \
            ]

        c_lib.elGetDeviceConfig.argtypes = [POINTER(DeviceConfigInternal)]
        c_lib.elGetDeviceConfig.restype = None
        deviceConfigInternal = DeviceConfigInternal()
        c_lib.elGetDeviceConfig(deviceConfigInternal)
        deviceConfig = ELApi.DeviceConfig(deviceConfigInternal.deviceSerial)
        for i in range(deviceConfigInternal.numFrameRates):
            deviceConfig.frameRates.append(deviceConfigInternal.frameRates[i])
        for i in range(deviceConfigInternal.numCalibrationMethods):
            deviceConfig.calibrationMethods.append(
                deviceConfigInternal.calibrationMethods[i])
        return deviceConfig

## return values of requestTracking( )

    class ReturnStart(Enum):
        ## start tracking successful
        SUCCESS = 0
        ## not connected to the server
        NOT_CONNECTED = 1
        ## cannot start tracking: no device found
        DEVICE_MISSING = 2
        ## cannot start tracking: framerate mode is invalid or not supported
        INVALID_FRAMERATE_MODE = 3
        ## tracking already ongoing, but frame rate mode is different
        ALREADY_RUNNING_DIFFERENT_FRAMERATE = 4
        ## some general failure occurred
        FAILURE = 5

## request tracking
#
# If tracking is not yet ongoing, tracking is started in the device. If tracking is already
# running (e.g. started from another client) with the same frame-rate as requested, all gaze
# samples are reported to this client as well.
#
# @param   frameRateModeInd    index of the requested frame rate mode (0 .. \#frameRateModes-1)
# @returns success state

    def requestTracking(self, frameRateModeInd: c_int) -> ReturnStart:
        global c_lib
        c_lib.elRequestTracking.argtypes = [c_int]
        c_lib.elRequestTracking.restype = c_int
        return ELApi.ReturnStart(c_lib.elRequestTracking(frameRateModeInd))

## unrequest tracking
#
# Note that the tracking device may continue if other processes still request tracking. Check
# the EyeLogic server window to observe the actual state.

    def unrequestTracking(self):
        global c_lib
        c_lib.elUnrequestTracking.argtypes = []
        c_lib.elUnrequestTracking.restype = None
        c_lib.elUnrequestTracking()

## return values of calibrate( )

    class ReturnCalibrate(Enum):
        ## calibration successful
        SUCCESS = 0
        ## cannot calibrate: not connected to the server
        NOT_CONNECTED = 1
        ## cannot calibrate: no device found or tracking not started
        NOT_TRACKING = 2
        ## cannot start calibration: calibration mode is invalid or not supported
        INVALID_CALIBRATION_MODE = 3
        ## cannot start calibration: calibration is already in progress
        ALREADY_CALIBRATING = 4
        ## calibration was not successful or aborted
        FAILURE = 5


## perform calibration (method is blocking until calibration finished)
#
# @returns success state

    def calibrate(self, calibrationModeInd: c_int):
        global c_lib
        c_lib.elCalibrate.argtypes = [c_int]
        c_lib.elCalibrate.restype = c_int
        return ELApi.ReturnCalibrate(c_lib.elCalibrate(calibrationModeInd))

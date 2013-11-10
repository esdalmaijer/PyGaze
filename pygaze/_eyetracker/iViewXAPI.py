# iViewXAPI.py
#
# Demonstrates features of iView X API 
# Defines structures 
# Loads in iViewXAPI.dll
# This script shows how to set up an experiment with Python 2.7.1 (with ctypes Library) 
#
# Author: SMI GmbH
# Feb. 16, 2011


from ctypes import *


#===========================
#		Struct Definition
#===========================

class CSystem(Structure):
	_fields_ = [("samplerate", c_int),
	("iV_MajorVersion", c_int),
	("iV_MinorVersion", c_int),
	("iV_Buildnumber", c_int),
	("API_MajorVersion", c_int),
	("API_MinorVersion", c_int),
	("API_Buildnumber", c_int),
	("iV_ETDevice", c_int)]

class CCalibration(Structure):
	_fields_ = [("method", c_int),
	("visualization", c_int),
	("displayDevice", c_int),
	("speed", c_int),
	("autoAccept", c_int),
	("foregroundBrightness", c_int),
	("backgroundBrightness", c_int),
	("targetShape", c_int),
	("targetSize", c_int),
	("targetFilename", c_char * 256)]

class CEye(Structure):
	_fields_ = [("gazeX", c_double),
	("gazeY", c_double),
	("diam", c_double),
	("eyePositionX", c_double),
	("eyePositionY", c_double),
	("eyePositionZ", c_double)]

class CSample(Structure):
	_fields_ = [("timestamp", c_longlong),
	("leftEye", CEye),
	("rightEye", CEye),
	("planeNumber", c_int)]

class CEvent(Structure):
	_fields_ = [("eventType", c_char),
	("eye", c_char),
	("startTime", c_longlong),
	("endTime", c_longlong),
	("duration", c_longlong),
	("positionX", c_double),
	("positionY", c_double)]

class CAccuracy(Structure):
	_fields_ = [("deviationLX",c_double),
				("deviationLY",c_double),				
				("deviationRX",c_double),
				("deviationRY",c_double)]
				
#===========================
#		Loading iViewX.dll 
#===========================

iViewXAPI = windll.LoadLibrary("iViewXAPI.dll")


#===========================
#		Initializing Structs
#===========================

systemData = CSystem(0, 0, 0, 0, 0, 0, 0, 0)
calibrationData = CCalibration(5, 1, 0, 0, 1, 20, 239, 1, 15, b"")
leftEye = CEye(0,0,0)
rightEye = CEye(0,0,0)
sampleData = CSample(0,leftEye,rightEye,0)
eventData = CEvent('F', 'L', 0, 0, 0, 0, 0)
accuracyData = CAccuracy(0,0,0,0)



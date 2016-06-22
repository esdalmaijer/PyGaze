# PyTribe: classes to communicate with EyeTribe eye trackers
#
# author: Edwin Dalmaijer
# email: edwin.dalmaijer@psy.ox.ac.uk
#
# version 4 (21-Jun-2016)

import os
import copy
import json
import time
import socket
import codecs
from threading import Lock, Thread
from multiprocessing import Event, Process, Queue
from pygaze.py3compat import *


# # # # #
# EYETRIBE CLASS

# The original EyeTribe class from earlier versions of PyTribe.
class EyeTribe:

	"""class for eye tracking and data collection using an EyeTribe tracker
	"""

	def __init__(self, logfilename='default', host='localhost', port=6555):

		"""Initializes an EyeTribe instance

		keyword arguments

		logfilename	--	string indicating the log file name, including
						a full path to it's location and an extension
						(default = 'default.txt')
		"""
		
		# initialize data collectors
		self._logfile = codecs.open('%s.tsv' % (logfilename), 'w', u'utf-8')
		self._separator = u'\t'
		self._log_header()
		self._queue = Queue()

		# initialize connection
		self._connection = connection(host=host, port=port)
		self._tracker = tracker(self._connection)
		self._heartbeat = heartbeat(self._connection)

		# create a new Lock
		self._lock = Lock()

		# initialize heartbeat thread
		self._beating = True
		self._heartbeatinterval = self._tracker.get_heartbeatinterval() / 1000.0
		self._hbthread = Thread(target=self._heartbeater, args=[self._heartbeatinterval])
		self._hbthread.daemon = True
		self._hbthread.name = 'heartbeater'

		# initialize sample streamer
		self._streaming = True
		self._samplefreq = self._tracker.get_framerate()
		self._intsampletime = 1.0 / self._samplefreq
		self._clockdiff = None
		self._newestframe = self._tracker.get_frame()
		self._ssthread = Thread(target=self._stream_samples, args=[self._queue])
		self._ssthread.daemon = True
		self._ssthread.name = 'samplestreamer'

		# initialize data processer
		self._processing = True
		self._logdata = False
		self._currentsample = copy.deepcopy(self._newestframe)
		self._dpthread = Thread(target=self._process_samples, args=[self._queue])
		self._dpthread.daemon = True
		self._dpthread.name = 'dataprocessor'

		# start all threads
		self._hbthread.start()
		self._ssthread.start()
		self._dpthread.start()

		# initialize calibration
		self.calibration = calibration(self._connection)

	def start_recording(self):

		"""Starts data recording
		"""

		# set self._logdata to True, so the data processing thread starts
		# writing samples to the log file
		if not self._logdata:
			self._logdata = True
			self.log_message("start_recording")

	def stop_recording(self):

		"""Stops data recording
		"""

		# consolidate the data file on the hard drive
		# internal buffer to RAM
		self._logfile.flush()
		# RAM file cache to disk
		os.fsync(self._logfile.fileno())

		# set self._logdata to False, so the data processing thread does not
		# write samples to the log file
		if self._logdata:
			self.log_message("stop_recording")
			self._logdata = False

	def log_message(self, message):

		"""Logs a message to the logfile, time locked to the most recent
		sample
		"""
		
		# Get the current time.
		t = time.time()
		# Make a string in the specific format that the EyeTribe uses:
		# yyyy-mm-dd HH:MM:SS.000
		ts = '%s.%d' % (time.strftime('%Y-%m-%d %H:%M:%S'), round(t % 1, 3)*1000)
		
		# Correct the time to EyeTribe time
		if self._clockdiff != None:
			t = int(t + self._clockdiff)
		else:
			t = ''
		# assemble line
		line = self._separator.join(map(str,[u'MSG', ts, t, safe_decode(message)]))
		# write message
		self._logfile.write(line + u'\n') # to internal buffer

	def sample(self):

		"""Returns the most recent point of regard (=gaze location on screen)
		coordinates (smoothed signal)

		arguments

		None

		returns

		gaze		--	a (x,y) tuple indicating the point of regard
		"""

		if self._newestframe == None:
			return None, None
		else:
			return (self._newestframe['avgx'],self._newestframe['avgy'])

	def pupil_size(self):

		"""Returns the most recent pupil size sample (an average of the size
		of both pupils)

		arguments

		None

		returns

		pupsize	--	a float indicating the pupil size (in arbitrary units)
		"""

		if self._currentsample == None:
			return None
		else:
			return self._newestframe['psize']

	def close(self):

		"""Stops all data streaming, and closes both the connection to the
		tracker and the logfile
		"""

		# if we are currently recording, stop doing so
		if self._logdata:
			self.stop_recording()

		# signal all threads to halt
		self._beating = False
		self._streaming = False
		self._processing = False

		# close the log file
		self._logfile.close()

		# close the connection
		self._connection.close()

	def _wait_while_calibrating(self):

		"""Waits until the tracker is not in the calibration state
		"""

		while self._tracker.get_iscalibrating():
			pass

		return True

	def _heartbeater(self, heartbeatinterval):

		"""Continuously sends heartbeats to the tracker, to let it know the
		connection is still alive (it seems to think we could die any
		moment now, and is very keen on reassurance of our good health;
		almost like my grandparents...)

		arguments

		heartbeatinterval	--	float indicating the heartbeatinterval in
							seconds; note that this is different from
							the value that the EyeTribe tracker reports:
							that value is in milliseconds and should be
							recalculated to seconds here!
		"""

		# keep beating until it is signalled that we should stop
		while self._beating:
			# do not bother the tracker when it is calibrating
			#self._wait_while_calibrating()
			# wait for the Threading Lock to be released, then lock it
			self._lock.acquire(True)
			# send heartbeat
			self._heartbeat.beat()
			# release the Threading Lock
			self._lock.release()
			# wait for a bit
			time.sleep(heartbeatinterval)

	def _stream_samples(self, queue):

		"""Continuously polls the device, and puts all new samples in a
		Queue instance

		arguments

		queue		--	a multithreading.Queue instance, to put samples
						into
		"""

		# keep streaming until it is signalled that we should stop
		while self._streaming:
			# do not bother the tracker when it is calibrating
			#self._wait_while_calibrating()
			# wait for the Threading Lock to be released, then lock it
			self._lock.acquire(True)
			# get a new sample
			sample = self._tracker.get_frame()
			t1 = time.time()
			# put the sample in the Queue
			queue.put(sample)
			# release the Threading Lock
			self._lock.release()
			# Update the newest frame
			self._newestframe = copy.deepcopy(sample)
			# Calculate the clock difference
			self._clockdiff = sample['time'] - t1
			# pause for half the intersample time, to avoid an overflow
			# (but to make sure to not miss any samples)
			time.sleep(self._intsampletime/2)

	def _process_samples(self, queue):

		"""Continuously processes samples, updating the most recent sample
		and writing data to a the log file when self._logdata is set to True

		arguments

		queue		--	a multithreading.Queue instance, to read samples
						from
		"""

		# keep processing until it is signalled that we should stop
		while self._processing:
			# wait for the Threading Lock to be released, then lock it
			self._lock.acquire(True)
			# read new item from the queue
			if not queue.empty():
				sample = queue.get()
			else:
				sample = None
			# release the Threading Lock
			self._lock.release()
			# update newest sample
			if sample != None:
				# check if the new sample is the same as the current sample
				if not self._currentsample['timestamp'] == sample['timestamp']:
					# update current sample
					self._currentsample = copy.deepcopy(sample)
					# write to file if data logging is on
					if self._logdata:
						self._log_sample(sample)

	def _log_sample(self, sample):

		"""Writes a sample to the log file

		arguments

		sample		--	a sample dict, as is returned by
						tracker.get_frame
		"""

		# assemble new line
		line = self._separator.join(map(str,[	sample['timestamp'],
										sample['time'],
										sample['fix'],
										sample['state'],
										sample['rawx'],
										sample['rawy'],
										sample['avgx'],
										sample['avgy'],
										sample['psize'],
										sample['Lrawx'],
										sample['Lrawy'],
										sample['Lavgx'],
										sample['Lavgy'],
										sample['Lpsize'],
										sample['Lpupilx'],
										sample['Lpupily'],
										sample['Rrawx'],
										sample['Rrawy'],
										sample['Ravgx'],
										sample['Ravgy'],
										sample['Rpsize'],
										sample['Rpupilx'],
										sample['Rpupily']
								]))
		# write line to log file
		self._logfile.write(line + '\n') # to internal buffer

	def _log_header(self):

		"""Logs a header to the data file
		"""

		# write a header to the data file
		header = self._separator.join(['timestamp','time','fix','state',
								'rawx','rawy','avgx','avgy','psize',
								'Lrawx','Lrawy','Lavgx','Lavgy','Lpsize','Lpupilx','Lpupily',
								'Rrawx','Rrawy','Ravgx','Ravgy','Rpsize','Rpupilx','Rpupily'
								])
		self._logfile.write(header + '\n') # to internal buffer
		self._logfile.flush() # internal buffer to RAM
		os.fsync(self._logfile.fileno()) # RAM file cache to disk
		self._firstlog = False



# # # # # #
# PARALLEL ClASS


# Ugly, but sod it: A global variable for the most recent sample.
global _current_sample


# Class to communicate with an EyeTribe tracker. The actual communications
# and logging actually run in a separate Process. This class just sends
# commands to that Process.
class ParallelEyeTribe:
	
	def __init__(self, logfilename='default'):
		
		# Set some standard stuff (hard coded now, but can potentially
		# be passed to the __init__ method in the future.)
		host = 'localhost'
		port = 6555
		
		# We need an Event that signals whether the connection to the
		# EyeTribe is supposed to be open.
		self._connection_alive = Event()
		self._connection_alive.set()
		
		# We also need a Queue to send commands through.
		self._command_queue = Queue()
		# And we need a Queue to receive commands through.
		self._to_main_queue = Queue()
		
		# Start a parallel process that will take care of all EyeTribe
		# things. It will provide regular heartbeats to keep the connection
		# alive, it will record gaze data to a file, and it will keep the
		# most recent sample updated. This is all done in a separate
		# Process (rather than in Threads) to so that it can be offloaded
		# to a different CPU core. This prevents the ongoing experiment
		# (or whatever you're doing in the main Thread) from interfering
		# with the processing (and recording) of gaze data.
		self.eyetribe_process = Process(target=_run_eyetribe_process, \
			args=[logfilename, host, port, self._connection_alive, \
			self._command_queue])
		self.eyetribe_process.name = u'pygaze_eyetribe'
		self.eyetribe_process.daemon = True
		self.eyetribe_process.start()

	def start_recording(self):

		"""Starts data recording
		"""
		
		# Send a command to the EyeTribe Process
		self._command_queue.put(('start_recording', ()))

	def stop_recording(self):

		"""Stops data recording
		"""

		# Send a command to the EyeTribe Process
		self._command_queue.put(('stop_recording', ()))

	def log_message(self, message):

		"""Logs a message to the logfile, time locked to the most recent
		sample
		"""

		# Send a command to the EyeTribe Process
		self._command_queue.put(('log_message', (message)))

	def sample(self):

		"""Returns the most recent point of regard (=gaze location on screen)
		coordinates (smoothed signal)

		arguments

		None

		returns

		gaze		--	a (x,y) tuple indicating the point of regard
		"""
		
		global _current_sample
		
		if _current_sample == None:
			return None, None
		else:
			return (_current_sample['avgx'], _current_sample['avgy'])

	def pupil_size(self):

		"""Returns the most recent pupil size sample (an average of the size
		of both pupils)

		arguments

		None

		returns

		pupsize	--	a float indicating the pupil size (in arbitrary units)
		"""

		global _current_sample

		if _current_sample == None:
			return None
		else:
			return _current_sample['psize']

	def close(self):

		"""Stops all data streaming, and closes both the connection to the
		tracker and the logfile
		"""

		# Send a command to the EyeTribe Process
		self._command_queue.put(('close', ()))


# Function that can run in a parallel process, to keep a connection with the
# EyeTribe open, and to log data when appropriate.
def _run_eyetribe_process(logfilename, host, port, connection_alive, command_queue):
		
	"""FOR INTERNAL USE ONLY
	"""
	
	# Ugly, but sod it: A global variable for the most recent sample.
	global _current_sample
	
	# Initialise a new _EyeTribe instance to open the connection to the
	# EyeTribe.
	tracker = EyeTribe(logfilename=logfilename, host=host, port=port)
	
	# Run until the connection is closed.
	while connection_alive.is_set():
		
		# Check the incoming Queue.
		if not command_queue.empty():
			# Get the oldest command in the Queue. This is a tuple that
			# contains a string (the command), and a tuple of values
			# (what they are depends on the specific command).
			cmd, value = command_queue.get()
			
			# Start recording.
			if cmd == 'start_recording':
				tracker.start_recording()

			# Stop recording.
			elif cmd == 'stop_recording':
				tracker.stop_recording()

			# Log a message.
			elif cmd == 'log_message':
				tracker.log_message(value[0])

			# Close the connection to the EyeTribe.
			elif cmd == 'close':
				tracker.close()
				# Unset the Event that signals that the connection is
				# alive.
				connection_alive.clear()
		
		# Update the current sample.
		_current_sample = copy.deepcopy(tracker._currentsample)


# # # # #
# SUPPORTING CLASSES

class connection:

	"""class for connections with the EyeTribe tracker"""

	def __init__(self, host='localhost', port=6555):

		"""Initializes the connection with the EyeTribe tracker

		keyword arguments

		host		--	a string indicating the host IP, NOTE: currently only
					'localhost' is supported (default = 'localhost')
		port		--	an integer indicating the port number, NOTE: currently
					only 6555 is supported (default = 6555)
		"""

		# properties
		self.host = host
		self.port = port
		self.resplist = []
		self.DEBUG = False

		# initialize a connection
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.connect((self.host,self.port))
		# Create lock
		self._request_lock = Lock()

	def request(self, category, request, values):

		"""Send a message over the connection

		arguments

		category	--	string indicating the query category
		request	--	string indicating the actual request of the message
		values	--	dict or list containing parameters of the request
		"""

		# create a JSON formatted string
		msg = self.create_json(category, request, values)
		# send the message over the connection
		self._request_lock.acquire()
		self.sock.send(msg)
		# print request in DEBUG mode
		if self.DEBUG:
			print("REQUEST: '%s'" % msg)

		# give the tracker a wee bit of time to reply
		time.sleep(0.005)

		# get new responses
		success = self.get_response()
		self._request_lock.release()

		# return the appropriate response
		if success:
			for i in range(len(self.resplist)):
				# check if the category matches
				if self.resplist[i]['category'] == category:
					# if this is a heartbeat, return
					if self.resplist[i]['category'] == 'heartbeat':
						return self.resplist.pop(i)
					# if this is another category, check if the request
					# matches
					elif 'request' in self.resplist[i] and \
						self.resplist[i]['request'] == request:
						return self.resplist.pop(i)
		# on a connection error, get_response returns False and a connection
		# error should be returned
		else:
			return self.parse_json('{"statuscode":901,"values":{"statusmessage":"connection error"}}')

	def get_response(self):

		"""Asks for a response, and adds these to the list of all received
		responses (basically a very simple queue)
		"""

		# try to get a new response
		try:
			response = self.sock.recv(32768)
			# print reply in DEBUG mode
			if self.DEBUG:
				print("REPLY: '%s'" % response)
		# if it fails, revive the connection and return a connection error
		except socket.error:
			print("reviving connection")
			self.revive()
			response = '{"statuscode":901,"values":{"statusmessage":"connection error"}}'
			return False
		# split the responses (in case multiple came in)
		response = response.split('\n')
		# add parsed responses to the internal list
		for r in response:
			if r:
				self.resplist.append(self.parse_json(r))

		return True

	def create_json(self, category, request, values):

		"""Creates a new json message, in the format that is required by the
		EyeTribe tracker; these messages consist of a categort, a request and
		a (list of) value(s), which can be thought of as class.method.value
		(for more info, see: http://dev.theeyetribe.com/api/)

		arguments

		category	--	query category (string), e.g. 'tracker',
					'calibration', or 'heartbeat'
		request	--	the request message (string), e.g. 'get' for the
					'tracker' category
		values	--	a dict of parameters and their values, e.g.
					{"push":True, "version":1}
					OR:
					a list of parameters, e.g. ['push','iscalibrated']
					OR:
					None to pass no values at all

		keyword arguments

		None

		returns

		jsonmsg	--	a string in json format, that can be directly sent to
					the EyeTribe tracker
		"""

		# error if the values are anything other than a dict, tuple or list
		if values is not None and type(values) not in [dict, list, tuple]:
			raise Exception("values should be dict, tuple or list, not '%s' (values = %s)" % (type(values),values))

		# create the json message
		if request == None:
			jsondict = {"category":category}
		elif values == None:
			jsondict = {"category":category, "request":request}
		else:
			jsondict = {"category":category, "request":request, "values":values}

		return json.dumps(jsondict)

	def parse_json(self, jsonmsg):

		"""Parses a json message as those that are usually returned by the
		EyeTribe tracker
		(for more info, see: http://dev.theeyetribe.com/api/)

		arguments

		jsonmsg	--	a string in json format

		keyword arguments

		None

		returns

		msg		--	a dict containing the information in the json message;
					this dict has the following content:
						{	"category":	"tracker",
							"request":	"get",
							"statuscode":	200,
							"values":	{	"push":True,
										"iscalibrated":True
										}
							}
		"""

		# parse json message
		parsed = json.loads(jsonmsg)

		return parsed

	def revive(self):

		"""Re-establishes a connection
		"""

		# close old connection
		self.close()
		# initialize a connection
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.connect((self.host,self.port))


	def close(self):

		"""Closes the connection to the EyeTribe tracker
		"""

		# close the socket connection
		self.sock.close()


class tracker:

	"""class for SDK Tracker state and information related requests"""

	def __init__(self, connection):

		"""Initializes a tracker instance

		arguments

		connection	--	a pytribe.connection instance for the currently
						attached EyeTribe tracker
		"""

		self.connection = connection
		self.push = True

	def set_connection(self, connection):

		"""Set a new connection

		arguments

		connection	--	a pytribe.connection instance for the currently
						attached EyeTribe tracker
		"""

		self.connection = connection

	def get_push(self):

		"""Returns a Booleam reflecting the state: True for push mode,
		False for pull mode (Boolean)
		"""

		# send the request
		response = self.connection.request('tracker', 'get', ['push'])
		# return value or error
		if response['statuscode'] == 200:
			return response['values']['push']
		else:
			raise Exception("Error in tracker.get_push: %s (code %d)" % (response['values']['statusmessage'],response['statuscode']))

	def get_heartbeatinterval(self):

		"""Returns the expected heartbeat interval in milliseconds
		(integer)
		"""

		# send the request
		response = self.connection.request('tracker', 'get', ['heartbeatinterval'])
		# check if the tracker is in push mode
		if response['statuscode'] == 200:
			return response['values']['heartbeatinterval']
		else:
			raise Exception("Error in tracker.get_heartbeatinterval: %s (code %d)" % (response['values']['statusmessage'],response['statuscode']))

	def get_version(self):

		"""Returns the version number (integer)
		"""

		# send the request
		response = self.connection.request('tracker', 'get', ['version'])
		# return value or error
		if response['statuscode'] == 200:
			return response['values']['version']
		else:
			raise Exception("Error in tracker.get_version: %s (code %d)" % (response['values']['statusmessage'],response['statuscode']))

	def get_trackerstate(self):

		"""Returns the state of the physcial tracker (integer):
			0:	TRACKER_CONNECTED
				tracker is detected and working
			1:	TRACKER_NOT_CONNECTED
				tracker device is not connected
			2:	TRACKER_CONNECTED_BADFW
				tracker device is connected, but not working due to
				bad firmware
			3:	TRACKER_CONNECTED_NOUSB3
				tracker device is connected, but not working due to
				unsupported USB host
			4:	TRACKER_CONNECTED_NOSTREAM
				tracker device is connected, but no stream could be
				received
		"""

		# send the request
		response = self.connection.request('tracker', 'get', ['trackerstate'])
		# return value of error
		if response['statuscode'] == 200:
			return response['values']['trackerstate']
		else:
			raise Exception("Error in tracker.get_trackerstate: %s (code %d)" % (response['values']['statusmessage'],response['statuscode']))

	def get_framerate(self):

		"""Returns the frame rate that the tracker is running at (integer)
		"""

		# send the request
		response = self.connection.request('tracker', 'get', ['framerate'])
		# return value or error
		if response['statuscode'] == 200:
			return response['values']['framerate']
		else:
			raise Exception("Error in tracker.get_framerate: %s (code %d)" % (response['values']['statusmessage'],response['statuscode']))

	def get_iscalibrated(self):

		"""Indicates whether there is a calibration (Boolean)
		"""

		# send the request
		response = self.connection.request('tracker', 'get', ['iscalibrated'])
		# return value or error
		if response['statuscode'] == 200:
			return response['values']['iscalibrated']
		else:
			raise Exception("Error in tracker.get_iscalibrated: %s (code %d)" % (response['values']['statusmessage'],response['statuscode']))

	def get_iscalibrating(self):

		"""Indicates whether the tracker is in calibration mode (Boolean)
		"""

		# send the request
		response = self.connection.request('tracker', 'get', ['iscalibrating'])
		# return value or error
		if response['statuscode'] == 200:
			return response['values']['iscalibrating']
		else:
			raise Exception("Error in tracker.get_iscalibrating: %s (code %d)" % (response['values']['statusmessage'],response['statuscode']))

	def get_calibresult(self):

		"""Gets the latest valid calibration result

		returns

		WITHOUT CALIBRATION:
		None

		WITH CALIBRATION:
		calibresults	--	a dict containing the calibration results:
						{	'result':	Boolean indicating whether the
									calibration was succesful
							'deg':	float indicating the average error
									in degrees of visual angle
							'Ldeg':	float indicating the left eye
									error in degrees of visual angle
							'Rdeg':	float indicating the right eye
									error in degrees of visual angle
							'calibpoints': list, containing a dict for
										each calibration point:
										{'state':	integer indicating
												the state of the
												calibration point
												(0 means no useful
												data has been
												obtained and the
												point should be
												resampled; 1 means
												the data is of
												questionable
												quality, consider
												resampling; 2 means
												the data is ok)
										'cpx':	x coordinate of the
												calibration point
										'cpy':	y coordinate of the
												calibration point
										'mecpx':	mean estimated x
												coordinate of the
												calibration point
										'mecpy':	mean estimated y
												coordinate of the
												calibration point
										'acd':	float indicating
												the accuracy in
												degrees of visual
												angle
										'Lacd':	float indicating
												the accuracy in
												degrees of visual
												angle (left eye)
										'Racd':	float indicating
												the accuracy in
												degrees of visual
												angle (right eye)
										'mepix':	mean error in
												pixels
										'Lmepix':	mean error in
												pixels (left eye)
										'Rmepix':	mean error in
												pixels (right eye)
										'asdp':	standard deviation
												in pixels
										'Lasdp':	standard deviation
												in pixels (left eye)
										'Rasdp':	standard deviation
												in pixels (right eye)
										}
						}

		"""

		# send the request
		response = self.connection.request('tracker', 'get', ['calibresult'])

		# return value or error
		if response['statuscode'] != 200:
			raise Exception("Error in tracker.get_calibresult: %s (code %d)" % (response['values']['statusmessage'],response['statuscode']))

		# return True if this was not the final calibration point
		if not 'calibpoints' in response['values']:
			return None

		# if this was the final calibration point, return the results
		else:
			# return calibration dict
			returndict =  {	'result':response['values']['calibresult']['result'],
							'deg':response['values']['calibresult']['deg'],
							'Rdeg':response['values']['calibresult']['degl'],
							'Ldeg':response['values']['calibresult']['degr'],
							'calibpoints':[]
							}
			for pointdict in response['values']['calibresult']['calibpoints']:
				returndict['calibpoints'].append({	'state':pointdict['state'],
											'cpx':pointdict['cp']['x'],
											'cpy':pointdict['cp']['y'],
											'mecpx':pointdict['mecp']['x'],
											'mecpy':pointdict['mecp']['y'],
											'acd':pointdict['acd']['ad'],
											'Lacd':pointdict['acd']['adl'],
											'Racd':pointdict['acd']['adr'],
											'mepix':pointdict['mepix']['mep'],
											'Lmepix':pointdict['mepix']['mepl'],
											'Rmepix':pointdict['mepix']['mepr'],
											'asdp':pointdict['asdp']['asd'],
											'Lasdp':pointdict['asdp']['asdl'],
											'Rasdp':pointdict['asdp']['asdr']
											})
			return returndict

	def get_frame(self):

		"""Returns the latest frame data (dict)
			{	'timestamp': string time representation,
				'time': integer timestamp in milliseconds,
				'fix': Boolean indicating whether there is a fixation,
				'state': integer 32bit masked tracker state,
				'rawx': integer raw x gaze coordinate in pixels,
				'rawy': integer raw y gaze coordinate in pixels,
				'avgx': integer smoothed x gaze coordinate in pixels,
				'avgx': integer smoothed y gaze coordinate in pixels,
				'psize': float average pupil size,
				'Lrawx': integer raw x left eye gaze coordinate in pixels,
				'Lrawy': integer raw y left eye gaze coordinate in pixels,
				'Lavgx': integer smoothed x left eye gaze coordinate in pixels,
				'Lavgx': integer smoothed y left eye gaze coordinate in pixels,
				'Lpsize': float left eye pupil size,
				'Lpupilx': integer raw left eye pupil centre x coordinate,
				'Lpupily': integer raw left eye pupil centre y coordinate,
				'Rrawx': integer raw x right eye gaze coordinate in pixels,
				'Rrawy': integer raw y right eye gaze coordinate in pixels,
				'Ravgx': integer smoothed x right eye gaze coordinate in pixels,
				'Ravgx': integer smoothed y right eye gaze coordinate in pixels,
				'Rpsize': float right eye pupil size,
				'Rpupilx': integer raw right eye pupil centre x coordinate,
				'Rpupily': integer raw right eye pupil centre y coordinate
				}
		"""

		# send the request
		response = self.connection.request('tracker', 'get', ['frame'])
		# raise error if needed
		if response['statuscode'] != 200:
			raise Exception("Error in tracker.get_frame: %s (code %d)" % (response['values']['statusmessage'],response['statuscode']))
		# calculate pupil size
		# if both eyes are available, take the average
		if response['values']['frame']['lefteye']['psize'] > 0 and \
			response['values']['frame']['righteye']['psize'] > 0:
			psize = (response['values']['frame']['lefteye']['psize'] + \
				response['values']['frame']['righteye']['psize']) / 2.0
		# if only the right eye is available, then use the right eye
		elif response['values']['frame']['lefteye']['psize'] == 0 and \
			response['values']['frame']['righteye']['psize'] > 0:
			psize = response['values']['frame']['righteye']['psize']
		# if only the left eye is available, then use the left eye
		elif response['values']['frame']['lefteye']['psize'] > 0 and \
			response['values']['frame']['righteye']['psize'] == 0:
			psize = response['values']['frame']['lefteye']['psize']
		# if neither eye is available, then use the EyeTribe's standard
		# missing value (0.0)
		else:
			psize = 0.0
		# return the data in a dict
		return {	'timestamp':	response['values']['frame']['timestamp'],
				'time':		response['values']['frame']['time'],
				'fix':		response['values']['frame']['fix'],
				'state':		response['values']['frame']['state'],
				'rawx':		response['values']['frame']['raw']['x'],
				'rawy':		response['values']['frame']['raw']['y'],
				'avgx':		response['values']['frame']['avg']['x'],
				'avgy':		response['values']['frame']['avg']['y'],
				'psize':		psize,
				'Lrawx':		response['values']['frame']['lefteye']['raw']['x'],
				'Lrawy':		response['values']['frame']['lefteye']['raw']['y'],
				'Lavgx':		response['values']['frame']['lefteye']['avg']['x'],
				'Lavgy':		response['values']['frame']['lefteye']['avg']['y'],
				'Lpsize':		response['values']['frame']['lefteye']['psize'],
				'Lpupilx':		response['values']['frame']['lefteye']['pcenter']['x'],
				'Lpupily':		response['values']['frame']['lefteye']['pcenter']['y'],
				'Rrawx':		response['values']['frame']['righteye']['raw']['x'],
				'Rrawy':		response['values']['frame']['righteye']['raw']['y'],
				'Ravgx':		response['values']['frame']['righteye']['avg']['x'],
				'Ravgy':		response['values']['frame']['righteye']['avg']['y'],
				'Rpsize':		response['values']['frame']['righteye']['psize'],
				'Rpupilx':		response['values']['frame']['righteye']['pcenter']['x'],
				'Rpupily':		response['values']['frame']['righteye']['pcenter']['y']
				}

	def get_screenindex(self):

		"""Returns the screen index number in a multi screen setup (integer)
		"""

		# send the request
		response = self.connection.request('tracker', 'get', ['screenindex'])
		# return value or error
		if response['statuscode'] == 200:
			return response['values']['screenindex']
		else:
			raise Exception("Error in tracker.get_screenindex: %s (code %d)" % (response['values']['statusmessage'],response['statuscode']))

	def get_screenresw(self):

		"""Returns the screen resolution width in pixels (integer)
		"""

		# send the request
		response = self.connection.request('tracker', 'get', ['screenresw'])
		# return value or error
		if response['statuscode'] == 200:
			return response['values']['screenresw']
		else:
			raise Exception("Error in tracker.get_screenresw: %s (code %d)" % (response['values']['statusmessage'],response['statuscode']))

	def get_screenresh(self):

		"""Returns the screen resolution height in pixels (integer)
		"""

		# send the request
		response = self.connection.request('tracker', 'get', ['screenresh'])
		# return value or error
		if response['statuscode'] == 200:
			return response['values']['screenresh']
		else:
			raise Exception("Error in tracker.get_screenresh: %s (code %d)" % (response['values']['statusmessage'],response['statuscode']))

	def get_screenpsyw(self):

		"""Returns the physical screen width in meters (float)
		"""

		# send the request
		response = self.connection.request('tracker', 'get', ['screenpsyw'])
		# return value or error
		if response['statuscode'] == 200:
			return response['values']['screenpsyw']
		else:
			raise Exception("Error in tracker.get_screenpsyw: %s (code %d)" % (response['values']['statusmessage'],response['statuscode']))

	def get_screenpsyh(self):

		"""Returns the physical screen height in meters (float)
		"""

		# send the request
		response = self.connection.request('tracker', 'get', ['screenpsyh'])
		# return value or error
		if response['statuscode'] == 200:
			return response['values']['screenpsyh']
		else:
			raise Exception("Error in tracker.get_screenpsyh: %s (code %d)" % (response['values']['statusmessage'],response['statuscode']))

	def set_push(self, push=None):

		"""Toggles the push state, or sets the state to the passed value

		keyword arguments

		push		--	Boolean indicating the state: True for push,
											False for pull
											None to toggle current
		returns

		state	--	Boolean indicating the push state
		"""

		# check passed value
		if push == None:
			# toggle state
			self.push = self.push != True
		elif type(push) == bool:
			# set state to passed value
			self.push = push
		else:
			# error on anything other than None, True or False
			raise Exception("tracker.set_push: push keyword argument should be a Boolean or None, not '%s'" % push)

		# send the request
		response = self.connection.request('tracker', 'set', {'push':str(self.push).lower()})
		# return value or error
		if response['statuscode'] == 200:
			return self.push
		else:
			raise Exception("Error in tracker.set_push: %s (code %d)" % (response['values']['statusmessage'],response['statuscode']))


	def set_version(self, version):

		"""Set the protocol version

		arguments

		version	--	integer version number
		"""

		# send the request
		response = self.connection.request('tracker', 'set', {'version':version})
		# return value or error
		if response['statuscode'] == 200:
			return version
		else:
			raise Exception("Error in tracker.set_version: %s (code %d)" % (response['values']['statusmessage'],response['statuscode']))

	def set_screenindex(self, index):

		"""Set the screen index

		arguments

		index	--	integer value indicating the index number of the
					screen that is to be used with the tracker
		"""

		# send the request
		response = self.connection.request('tracker', 'set', {'screenindex':index})
		# return value or error
		if response['statuscode'] == 200:
			return index
		else:
			raise Exception("Error in tracker.set_screenindex: %s (code %d)" % (response['values']['statusmessage'],response['statuscode']))

	def set_screenresw(self, width):

		"""Set the screen resolution width

		arguments

		width	--	integer value indicating the screen resolution width
					in pixels
		"""

		# send the request
		response = self.connection.request('tracker', 'set', {'screenresw':width})
		# return value or error
		if response['statuscode'] == 200:
			return width
		else:
			raise Exception("Error in tracker.set_screenresw: %s (code %d)" % (response['values']['statusmessage'],response['statuscode']))

	def set_screenresh(self, height):

		"""Set the screen resolution height

		arguments

		height	--	integer value indicating the screen resolution height
					in pixels
		"""

		# send the request
		response = self.connection.request('tracker', 'set', {'screenresh':height})
		# return value or error
		if response['statuscode'] == 200:
			return height
		else:
			raise Exception("Error in tracker.set_screenresh: %s (code %d)" % (response['values']['statusmessage'],response['statuscode']))

	def set_screenpsyw(self, width):

		"""Set the physical width of the screen

		arguments

		width	--	float value indicating the physical screen width in
					metres
		"""

		# send the request
		response = self.connection.request('tracker', 'set', {'screenpsyw':width})
		# return value or error
		if response['statuscode'] == 200:
			return width
		else:
			raise Exception("Error in tracker.set_screenpsyw: %s (code %d)" % (response['values']['statusmessage'],response['statuscode']))

	def set_screenpsyh(self, height):

		"""Set the physical height of the screen

		arguments

		width	--	float value indicating the physical screen height in
					metres
		"""

		# send the request
		response = self.connection.request('tracker', 'set', {'screenpsyh':height})
		# return value or error
		if response['statuscode'] == 200:
			return height
		else:
			raise Exception("Error in tracker.set_screenpsyh: %s (code %d)" % (response['values']['statusmessage'],response['statuscode']))


class calibration:

	"""class for calibration related requests"""

	def __init__(self, connection):

		"""Initializes a calibration instance

		arguments

		connection	--	a pytribe.connection instance for the currently
						attached EyeTribe tracker
		"""

		self.connection = connection

	def set_connection(self, connection):

		"""Set a new connection

		arguments

		connection	--	a pytribe.connection instance for the currently
						attached EyeTribe tracker
		"""

		self.connection = connection

	def start(self, pointcount=9, max_attempts=5):

		"""Starts the calibration, using the passed number of calibration
		points

		keyword arguments

		pointcount	--	integer value indicating the amount of
						calibration points that should be used, which
						should be at least 7 (default = 9)
		max_attempts --	the number of times that calibration should be restarted
						if starting the calibration fails (default=5)
		"""
		
		for attempt in range(max_attempts):
		    # send the request
		    response = self.connection.request('calibration', 'start',
				{'pointcount':pointcount})
		    # return value or error
		    if response['statuscode'] == 200:
		        return
		    self.abort()
		raise Exception("Error in calibration.start: %s (code %d)" \
			% (response['values']['statusmessage'],response['statuscode']))		

	def pointstart(self, x, y):

		"""Mark the beginning of a new calibration point for the tracker to
		process

		arguments

		x			--	integer indicating the x coordinate of the
						calibration point
		y			--	integer indicating the y coordinate of the
						calibration point

		returns

		success		--	Boolean: True on success, False on a failure
		"""

		# send the request
		response = self.connection.request('calibration', 'pointstart', {'x':x,'y':y})
		# return value or error
		if response['statuscode'] == 200:
			return True
		else:
			raise Exception("Error in calibration.pointstart: %s (code %d)" % (response['values']['statusmessage'],response['statuscode']))

	def pointend(self):

		"""Mark the end of processing a calibration point

		returns

		NORMALLY:
		success		--	Boolean: True on success, False on failure

		AFTER FINAL POINT:
		calibresults	--	a dict containing the calibration results:
						{	'result':	Boolean indicating whether the
									calibration was succesful
							'deg':	float indicating the average error
									in degrees of visual angle
							'Ldeg':	float indicating the left eye
									error in degrees of visual angle
							'Rdeg':	float indicating the right eye
									error in degrees of visual angle
							'calibpoints': list, containing a dict for
										each calibration point:
										{'state':	integer indicating
												the state of the
												calibration point
												(0 means no useful
												data has been
												obtained and the
												point should be
												resampled; 1 means
												the data is of
												questionable
												quality, consider
												resampling; 2 means
												the data is ok)
										'cpx':	x coordinate of the
												calibration point
										'cpy':	y coordinate of the
												calibration point
										'mecpx':	mean estimated x
												coordinate of the
												calibration point
										'mecpy':	mean estimated y
												coordinate of the
												calibration point
										'acd':	float indicating
												the accuracy in
												degrees of visual
												angle
										'Lacd':	float indicating
												the accuracy in
												degrees of visual
												angle (left eye)
										'Racd':	float indicating
												the accuracy in
												degrees of visual
												angle (right eye)
										'mepix':	mean error in
												pixels
										'Lmepix':	mean error in
												pixels (left eye)
										'Rmepix':	mean error in
												pixels (right eye)
										'asdp':	standard deviation
												in pixels
										'Lasdp':	standard deviation
												in pixels (left eye)
										'Rasdp':	standard deviation
												in pixels (right eye)
										}
						}
		"""

		# send the request
		response = self.connection.request('calibration', 'pointend', None)
		# return value or error
		if response['statuscode'] != 200:
			raise Exception("Error in calibration.pointend: %s (code %d)" % (response['values']['statusmessage'],response['statuscode']))

		# return True if this was not the final calibration point
		if not 'calibresult' in response['values']:
			return True

		# if this was the final calibration point, return the results
		else:
			# return calibration dict
			returndict =  {	'result':response['values']['calibresult']['result'],
							'deg':response['values']['calibresult']['deg'],
							'Rdeg':response['values']['calibresult']['degl'],
							'Ldeg':response['values']['calibresult']['degr'],
							'calibpoints':[]
							}
			for pointdict in response['values']['calibresult']['calibpoints']:
				returndict['calibpoints'].append({	'state':pointdict['state'],
											'cpx':pointdict['cp']['x'],
											'cpy':pointdict['cp']['y'],
											'mecpx':pointdict['mecp']['x'],
											'mecpy':pointdict['mecp']['y'],
											'acd':pointdict['acd']['ad'],
											'Lacd':pointdict['acd']['adl'],
											'Racd':pointdict['acd']['adr'],
											'mepix':pointdict['mepix']['mep'],
											'Lmepix':pointdict['mepix']['mepl'],
											'Rmepix':pointdict['mepix']['mepr'],
											'asdp':pointdict['asdp']['asd'],
											'Lasdp':pointdict['asdp']['asdl'],
											'Rasdp':pointdict['asdp']['asdr']
											})
			return returndict

	def abort(self):

		"""Cancels the ongoing sequence and reinstates the previous
		calibration (only if there is one!)

		returns

		success		--	Boolean: True on success, False on failure
		"""

		# send the request
		response = self.connection.request('calibration', 'abort', None)
		# return value or error
		if response['statuscode'] == 200:
			return True
		else:
			raise Exception("Error in calibration.abort: %s (code %d)" % (response['values']['statusmessage'],response['statuscode']))

	def clear(self):

		"""Removes the current calibration from the tracker

		returns

		success		--	Boolean: True on success, False on failure
		"""

		# send the request
		response = self.connection.request('calibration', 'clear', None)
		# return value or error
		if response['statuscode'] == 200:
			return True
		else:
			raise Exception("Error in calibration.clear: %s (code %d)" % (response['values']['statusmessage'],response['statuscode']))


class heartbeat:

	"""class for signalling heartbeats to the server"""

	def __init__(self, connection):

		"""Initializes a heartbeat instance (not implemented in the SDK yet)

		arguments

		connection	--	a pytribe.connection instance for the currently
						attached EyeTribe tracker
		"""

		self.connection = connection

	def set_connection(self, connection):

		"""Set a new connection

		arguments

		connection	--	a pytribe.connection instance for the currently
						attached EyeTribe tracker
		"""

		self.connection = connection

	def beat(self):

		"""Sends a heartbeat to the device
		"""

		# send the request
		response = self.connection.request('heartbeat', None, None)
		# return value or error
		if response['statuscode'] == 200:
			return True
		else:
			raise Exception("Error in heartbeat.beat: %s (code %d)" % (response['values']['statusmessage'],response['statuscode']))


# # # # #
# DEBUG #
if __name__ == "__main__":
	test = EyeTribe()
	test.start_recording()
	time.sleep(10)
	test.stop_recording()
	test.close()
# # # # #

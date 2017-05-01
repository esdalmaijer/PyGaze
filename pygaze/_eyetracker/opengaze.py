# PyOpenGaze: Python wrapper for the OpenGaze API.
#
# author: Edwin Dalmaijer
# email: edwin.dalmaijer@psy.ox.ac.uk
#
# Version 1 (27-Apr-2016)

import os
import copy
import time
import socket
import datetime
import lxml.etree
from multiprocessing import Queue
from threading import Event, Lock, Thread

# TODO: OpenGazeConnection
# Thread that monitors whether the other threads are still alive, and that
#     checks whether the connection is still alive.
# Locks for the log and the DEBUG log.


# # # # #
# OPENGAZE API WRAPPER

# The OpenGazeTracker class communicates to the GazePoint Server through
# a TCP/IP socket.
class OpenGazeTracker:

	def __init__(self, ip='127.0.0.1', port=4242, logfile='default.tsv', \
		debug=False):
		
		"""The OpenGazeConnection class communicates to the GazePoint
		server through a TCP/IP socket. Incoming samples will be written
		to a log at the specified path.
		
		Keyword Arguments
		
		ip	-	The IP address of the computer that is running the
				OpenGaze server. This will usually be the localhost at
				127.0.0.1. Type: str. Default = '127.0.0.1'
		
		port	-	The port number that the OpenGaze server is on; usually
				this will be 4242. Type: int. Default = 4242
		
		logfile	-	The path to the intended log file, including a
					file extension ('.tsv'). Type: str. Default = 
					'default.tsv'

		debug	-	Boolean that determines whether DEBUG mode should be
				active (True) or not (False). In DEBUG mode, all sent
				and received messages are logged to a file. Type: bool.
				Default = False
		"""
		
		# DEBUG
		self._debug = debug
		# Open a new debug file.
		if self._debug:
			dt = time.strftime("%Y-%m-%d_%H-%M-%S")
			self._debuglog = open('debug_%s.txt' % (dt), 'w')
			self._debuglog.write("OPENGAZE PYTHON DEBUG LOG %s\n" % (dt))
			self._debugcounter = 0
			self._debugconsolidatefreq = 100
		
		# CONNECTION
		# Save the ip and port numbers.
		self.host = ip
		self.port = port
		# Start a new TCP/IP socket. It is curcial that it has a timeout,
		# as timeout exceptions will be handled gracefully, and are in fact
		# necessary to prevent the incoming Thread from freezing.
		self._debug_print("Connecting to %s (%s)..." % (self.host, self.port))
		self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self._sock.connect((self.host, self.port))
		self._sock.settimeout(1.0)
		self._debug_print("Successfully connected!")
		self._maxrecvsize = 4096
		# Create a socket Lock to prevent simultaneous access.
		self._socklock = Lock()
		# Create an event that should remain set until the connection is
		# closed. (This is what keeps the Threads running.)
		self._connected = Event()
		self._connected.set()
		# Set the current calibration point.
		self._current_calibration_point = None
		
		# LOGGING
		self._debug_print("Opening new logfile '%s'" % (logfile))
		# Open a new log file.
		self._logfile = open(logfile, 'w')
		# Write the header to the log file.
		self._logheader = ['CNT', 'TIME', 'TIME_TICK', \
			'FPOGX', 'FPOGY', 'FPOGS', 'FPOGD', 'FPOGID', 'FPOGV', \
			'LPOGX', 'LPOGY', 'LPOGV', \
			'RPOGX', 'RPOGY', 'RPOGV', \
			'BPOGX', 'BPOGY', 'BPOGV', \
			'LPCX', 'LPCY', 'LPD', 'LPS', 'LPV', \
			'RPCX', 'RPCY', 'RPD', 'RPS', 'RPV', \
			'LEYEX', 'LEYEY', 'LEYEZ', 'LPUPILD', 'LPUPILV', \
			'REYEX', 'REYEY', 'REYEZ', 'RPUPILD', 'RPUPILV', \
			'CX', 'CY', 'CS', \
			'USER']
		self._n_logvars = len(self._logheader)
		self._logfile.write('\t'.join(self._logheader) + '\n')
		# The log is consolidated (written to the disk) every N samples.
		# This requires an internal counter (because we can't be sure the
		# user turned on the 'CNT' sample counter), and a property that
		# determines the consolidation frequency. This frequency can also
		# be set to None, to never consolidate automatically.
		self._logcounter = 0
		self._log_consolidation_freq = 60
		# Start a Queue for samples that need to be logged.
		self._logqueue = Queue()
		# Set an event that is set while samples should be logged, and
		# unset while they shouldn't.
		self._logging = Event()
		self._logging.set()
		# Set an event that signals is set when the logfile is ready to
		# be closed.
		self._log_ready_for_closing = Event()
		self._log_ready_for_closing.clear()
		# Start a Thread that writes queued samples to the log file.
		self._logthread = Thread( \
			target=self._process_logging,
			name='PyGaze_OpenGazeConnection_logging', \
			args=[])
		
		# INCOMING
		# Start a new dict for the latest incoming messages, and for
		# incoming acknowledgements.
		self._incoming = {}
		self._acknowledgements = {}
		# Create a Lock for the incoming message and acknowledgement dicts.
		self._inlock = Lock()
		self._acklock = Lock()
		# Create an empty string for the current unfinished message. This
		# is to prevent half a message being parsed when it is cut off
		# between two 'self._sock.recv' calls.
		self._unfinished = ''
		# Start a new Thread that processes the incoming messages.
		self._inthread = Thread( \
			target=self._process_incoming, \
			name='PyGaze_OpenGazeConnection_incoming', \
			args=[])
		
		# OUTGOING
		# Start a new outgoing Queue (Thread safe, woop!).
		self._outqueue = Queue()
		# Set an event that is set when all queued outgoing messages have
		# been processed.
		self._sock_ready_for_closing = Event()
		self._sock_ready_for_closing.clear()
		# Create a new Thread that processes the outgoing queue.
		self._outthread = Thread( \
			target=self._process_outgoing, \
			name='PyGaze_OpenGazeConnection_outgoing', \
			args=[])
		# Create a dict that will keep track of at what time which command
		# was sent.
		self._outlatest = {}
		# Create a Lock to prevent simultaneous access to the outlatest
		# dict.
		self._outlock = Lock()
		
		# RUN THREADS
		# Set a signal that will kill all Threads when they receive it.
		self._thread_shutdown_signal = 'KILL_ALL_HUMANS'
		# Start the threads.
		self._debug_print("Starting the logging thread.")
		self._logthread.start()
		self._debug_print("Starting the incoming thread.")
		self._inthread.start()
		self._debug_print("Starting the outgoing thread.")
		self._outthread.start()
		
		# SET UP LOGGING
		# Wait for a bit to allow the Threads to start.
		time.sleep(0.5)
		# Enable the tracker to send ALL the things.
		self.enable_send_counter(True)
		self.enable_send_cursor(True)
		self.enable_send_eye_left(True)
		self.enable_send_eye_right(True)
		self.enable_send_pog_best(True)
		self.enable_send_pog_fix(True)
		self.enable_send_pog_left(True)
		self.enable_send_pog_right(True)
		self.enable_send_pupil_left(True)
		self.enable_send_pupil_right(True)
		self.enable_send_time(True)
		self.enable_send_time_tick(True)
		self.enable_send_user_data(True)
		# Reset the user-defined variable.
		self.user_data("0")

	
	def calibrate(self):
		
		"""Calibrates the eye tracker.
		"""

		# Reset the calibration.
		self.clear_calibration_result()
		# Show the calibration screen.
		self.calibrate_show(True)
		# Start the calibration.
		self.calibrate_start(True)
		# Wait for the calibration result.
		result = None
		while result == None:
			result = self.get_calibration_result()
			time.sleep(0.1)
		# Hide the calibration window.
		self.calibrate_show(False)
		
		return result
	
	def sample(self):

		# If there is no current record yet, return None.
		self._inlock.acquire()
		if 'REC' not in self._incoming.keys():
			x = None
			y = None
		elif 'NO_ID' not in self._incoming['REC'].keys():
			x = None
			y = None
		elif ('BPOGX' not in self._incoming['REC']['NO_ID'].keys()) or \
			('BPOGY' not in self._incoming['REC']['NO_ID'].keys()):
			x = None
			y = None
		else:
			x = float(self._incoming['REC']['NO_ID']['BPOGX'])
			y = float(self._incoming['REC']['NO_ID']['BPOGY'])
		self._inlock.release()

		# Return the (x,y) coordinate.
		return x, y
	
	def pupil_size(self):
		
		"""Return the current pupil size.
		"""

		# If there is no current record yet, return None.
		self._inlock.acquire()
		if 'REC' not in self._incoming.keys():
			psize =  None
		elif 'NO_ID' not in self._incoming['REC'].keys():
			psize = None
		elif ('LPV' not in self._incoming['REC']['NO_ID'].keys()) or \
			('LPS' not in self._incoming['REC']['NO_ID'].keys()) or \
			('RPV' not in self._incoming['REC']['NO_ID'].keys()) or \
			('RPS' not in self._incoming['REC']['NO_ID'].keys()):
			psize = None

		# Compute the pupil size, and return it if there is valid data.
		n = 0
		psize = 0
		if str(self._incoming['REC']['NO_ID']['LPV']) == '1':
			psize += float(self._incoming['REC']['NO_ID']['LPS'])
			n += 1
		if str(self._incoming['REC']['NO_ID']['RPV']) == '1':
			psize += float(self._incoming['REC']['NO_ID']['RPS'])
			n += 1
		self._inlock.release()
		if n == 0:
			psize = None
		else:
			psize = psize / float(n)

		return psize
	
	def log(self, message):
		
		"""Logs a message to the log file. ONLY CALL THIS WHILE RECORDING
		DATA!
		"""

		# Set the user-defined value.
		i = copy.copy(self._logcounter)
		self.user_data(message)
		# Wait until a single sample is logged.
		while self._logcounter <= i:
			time.sleep(0.0001)
		# Reset the user-defined value.
		self.user_data("0")
	
	def start_recording(self):
		
		"""Start writing data to the log file.
		"""
		
		self.enable_send_data(True)
	
	def stop_recording(self):
		
		"""Pause writing data to the log file.
		"""
		
		self.enable_send_data(False)

	
	def _debug_print(self, msg):
		
		if self._debug:
			self._debuglog.write('%s: %s\n' % \
				(datetime.datetime.now().strftime("%H:%M:%S.%f"), msg))
			if self._debugcounter % self._debugconsolidatefreq == 0:
				self._debuglog.flush()
				os.fsync(self._debuglog.fileno())
			self._debugcounter += 1
	
	def _format_msg(self, command, ID, values=None):
		
		# Create the start of the formatted string.
		xml = '<%s ID="%s" ' % (command.upper(), ID.upper())
		# Add the values for each parameter.
		if values:
			for par, val in values:
				xml += '%s="%s" ' % (par.upper(), val)
		# Add the ending.
		xml += '/>\r\n'
		
		return xml
	
	def _log_consolidation(self):
		
		# Internal buffer to RAM.
		self._logfile.flush()
		# RAM to disk.
		os.fsync(self._logfile.fileno())
	
	def _log_sample(self, sample):
		
		# Construct an empty line that has the same length as the log's
		# header (this was computed in __init__).
		line = self._n_logvars * ['']
		# Loop through all keys in the dict.
		for varname in sample.keys():
			# Check if this is a logable variable.
			if varname in self._logheader:
				# Find the appropriate index in the line
				line[self._logheader.index(varname)] = sample[varname]
		self._logfile.write('\t'.join(line) + '\n')

	def _parse_msg(self, xml):
		
		e = lxml.etree.fromstring(xml)
	
		return (e.tag, e.attrib)
	
	def _process_logging(self):
		
		self._debug_print("Logging Thread started.")
		
		while not self._log_ready_for_closing.is_set():

			# Get a new sample from the Queue.
			sample = self._logqueue.get()
			
			# Check if this is the shutdown signal.
			if sample == self._thread_shutdown_signal:
				# Signal that we're done logging all samples.
				self._log_ready_for_closing.set()
				# Break the while loop.
				break
			
			# Log the sample.
			self._log_sample(sample)
			
			# Consolidate the log if necessary.
			if self._logcounter % self._log_consolidation_freq == 0:
				self._log_consolidation()

			# Increment the counter.
			self._logcounter += 1
		
		self._debug_print("Logging Thread ended.")
		return
	
	def _process_incoming(self):
		
		self._debug_print("Incoming Thread started.")
		
		while self._connected.is_set():

			# Lock the socket to prevent other Threads from simultaneously
			# accessing it.
			self._socklock.acquire()
			# Get new messages from the OpenGaze Server.
			timeout = False
			try:
				instring = self._sock.recv(self._maxrecvsize)
			except socket.timeout:
				timeout = True
			# Get a received timestamp.
			t = time.time()
			# Unlock the socket again.
			self._socklock.release()
			
			# Skip further processing if no new message came in.
			if timeout:
				self._debug_print("socket recv timeout")
				continue

			self._debug_print("Raw instring: %r" % (instring))

			# Split the messages (they are separated by '\r\n').
			messages = instring.split('\r\n')

			# Check if there is currently an unfinished message.
			if self._unfinished:
				# Combine the currently unfinished message and the
				# most recent incoming message.
				messages[0] = copy.copy(self._unfinished) + messages[0]
				# Reset the unfinished message.
				self._unfinished = ''
			# Check if the last message was actually complete.
			if not messages[-1][-2:] == '/>':
				self._unfinished = messages.pop(-1)
			
			# Run through all messages.
			for msg in messages:
				self._debug_print("Incoming: %r" % (msg))
				# Parse the message.
				command, msgdict = self._parse_msg(msg)
				# Check if the incoming message is an acknowledgement.
				# Acknowledgements are also stored in a different dict,
				# which is used to monitor whether sent messages are
				# properly received.
				if command == 'ACK':
					self._acklock.acquire()
					self._acknowledgements[msgdict['ID']] = copy.copy(t)
					self._acklock.release()
				# Acquire the Lock for the incoming dict, so that it
				# won't be accessed at the same time.
				self._inlock.acquire()
				# Check if this command is already in the current dict.
				if command not in self._incoming.keys():
					self._incoming[command] = {}
				# Some messages have no ID, for example 'REC' messages.
				# We simply assign 'NO_ID' as the ID.
				if 'ID' not in msgdict.keys():
					msgdict['ID'] = 'NO_ID'
				# Check if this ID is already in the current dict.
				if msgdict['ID'] not in self._incoming[command].keys():
					self._incoming[command][msgdict['ID']] = {}
				# Add receiving time stamp, and the values for each
				# parameter to the current dict.
				self._incoming[command][msgdict['ID']]['t'] = \
					copy.copy(t)
				for par, val in msgdict.items():
					self._incoming[command][msgdict['ID']][par] = \
						copy.copy(val)
				# Log sample if command=='REC' and when the logging
				# event is set.
				if command == 'REC' and self._logging.is_set():
					self._logqueue.put(copy.deepcopy( \
						self._incoming[command][msgdict['ID']]))
				# Unlock the incoming dict again.
				self._inlock.release()
		
		self._debug_print("Incoming Thread ended.")
		return

	def _process_outgoing(self):
		
		self._debug_print("Outgoing Thread started.")
		
		while not self._sock_ready_for_closing.is_set():

			# Get a new command from the Queue.
			msg = self._outqueue.get()
			
			# Check if this is the shutdown signal.
			if msg == self._thread_shutdown_signal:
				# Signal that we're done processing all the outgoing
				# messages.
				self._sock_ready_for_closing.set()
				# Break the while loop.
				break
			
			self._debug_print("Outgoing: %r" % (msg))

			# Lock the socket to prevent other Threads from simultaneously
			# accessing it.
			self._socklock.acquire()
			# Send the command to the OpenGaze Server.
			t = time.time()
			self._sock.send(msg)
			# Unlock the socket again.
			self._socklock.release()
			
			# Store a timestamp for the latest outgoing message.
			self._outlock.acquire()
			self._outlatest[msg] = copy.copy(t)
			self._outlock.release()
		
		self._debug_print("Outgoing Thread ended.")
		return
	
	def _send_message(self, command, ID, values=None, \
		wait_for_acknowledgement=True, resend_timeout=3.0, maxwait=9.0):
		
		# Format a message in an XML format that the Open Gaze API needs.
		msg = self._format_msg(command, ID, values=values)

		# Run until the message is acknowledged or a timeout occurs (or
		# break if we're not supposed to wait for an acknowledgement.)
		timeout = False
		acknowledged = False
		t0 = time.time()
		while (not acknowledged) and (not timeout):

			# Add the command to the outgoing Queue.
			self._debug_print("Outqueue add: %r" % (msg))
			self._outqueue.put(msg)

			# Wait until an acknowledgement comes in.
			if wait_for_acknowledgement:
				sent = False
				t1 = time.time()
				while (time.time() - t1 < resend_timeout) and \
					(not acknowledged):

					# Check the outgoing queue for the sent message to
					# appear.
					if not sent:
						self._outlock.acquire()
						if msg in self._outlatest.keys():
							t = copy.copy(self._outlatest[msg])
							sent = True
							self._debug_print("Outqueue sent: %r" \
								% (msg))
						self._outlock.release()
						time.sleep(0.001)

					# Check the incoming queue for the expected
					# acknowledgement. (NOTE: This does not check
					# whether the values of the incoming acknowlement
					# match the sent message. Ideally, they should.)
					else:
						self._acklock.acquire()
						if ID in self._acknowledgements.keys():
							if self._acknowledgements[ID] >= t:
								acknowledged = True
								self._debug_print("Outqueue acknowledged: %r" \
									% (msg))
						self._acklock.release()
						time.sleep(0.001)

					# Check if there is a timeout.
					if (not acknowledged) and \
						(time.time() - t0 > maxwait):
						timeout = True
						break

			# If we're not supposed to wait for an acknowledgement, break
			# the while loop.
			else:
				break
		
		return acknowledged, timeout
	

	def close(self):
		
		"""Closes the connection to the tracker, closes the log files, and
		ends the Threads that process the incoming and outgoing messages,
		and the logging of samples.
		"""
		
		# Reset the user-defined value.
		self.user_data('0')
		
		# Unset the self._connected event to stop the incoming Thread.
		self._debug_print("Unsetting the connection event")
		self._connected.clear()
		
		# Queue the stop signal to stop the outgoing and logging Threads.
		self._debug_print("Adding stop signal to outgoing Queue")
		self._outqueue.put(self._thread_shutdown_signal)
		self._debug_print("Adding stop signal to logging Queue")
		self._logqueue.put(self._thread_shutdown_signal)
		
		# Wait for the outgoing Queue to be fully processed.
		self._debug_print("Waiting for the socket to close...")
		self._sock_ready_for_closing.wait()
		
		# Close the socket connection to the OpenGaze server.
		self._debug_print("Closing socket connection...")
		self._sock.close()
		self._debug_print("Socket connection closed!")
		
		# Wait for the log Queue to be fully processed.
		self._debug_print("Waiting for the log to close...")
		self._log_ready_for_closing.wait()
		
		# Close the log file.
		self._logfile.close()
		self._debug_print("Log closed!")
		
		# Join the Threads.
		self._debug_print("Waiting for the Threads to join...")
		self._outthread.join()
		self._debug_print("Outgoing Thread joined!")
		self._inthread.join()
		self._debug_print("Incoming Thread joined!")
		self._logthread.join()
		self._debug_print("Logging Thread joined!")

		# Close the DEBUG log.
		if self._debug:
			self._debuglog.write("END OF DEBUG LOG")
			self._debuglog.close()


	def enable_send_data(self, state):
		
		"""Start (state=True) or stop (state=False) the streaming of data
		from the server to the client.
		"""

		# Send the message (returns after the Server acknowledges receipt).
		acknowledged, timeout = self._send_message('SET', \
			'ENABLE_SEND_DATA', \
			values=[('STATE', int(state))], \
			wait_for_acknowledgement=True)
		
		# Return a success Boolean.
		return acknowledged and (timeout==False)

	def enable_send_counter(self, state):
		
		"""Enable (state=True) or disable (state=False) the inclusion of
		the send counter in the data record string.
		"""

		# Send the message (returns after the Server acknowledges receipt).
		acknowledged, timeout = self._send_message('SET', \
			'ENABLE_SEND_COUNTER', \
			values=[('STATE', int(state))], \
			wait_for_acknowledgement=True)
		
		# Return a success Boolean.
		return acknowledged and (timeout==False)

	def enable_send_time(self, state):
		
		"""Enable (state=True) or disable (state=False) the inclusion of
		the send time in the data record string.
		"""

		# Send the message (returns after the Server acknowledges receipt).
		acknowledged, timeout = self._send_message('SET', \
			'ENABLE_SEND_TIME', \
			values=[('STATE', int(state))], \
			wait_for_acknowledgement=True)
		
		# Return a success Boolean.
		return acknowledged and (timeout==False)

	def enable_send_time_tick(self, state):
		
		"""Enable (state=True) or disable (state=False) the inclusion of
		the send time tick in the data record string.
		"""

		# Send the message (returns after the Server acknowledges receipt).
		acknowledged, timeout = self._send_message('SET', \
			'ENABLE_SEND_TIME_TICK', \
			values=[('STATE', int(state))], \
			wait_for_acknowledgement=True)
		
		# Return a success Boolean.
		return acknowledged and (timeout==False)

	def enable_send_pog_fix(self, state):
		
		"""Enable (state=True) or disable (state=False) the inclusion of
		the point of gaze as determined by the tracker's fixation filter in
		the data record string.
		"""

		# Send the message (returns after the Server acknowledges receipt).
		acknowledged, timeout = self._send_message('SET', \
			'ENABLE_SEND_POG_FIX', \
			values=[('STATE', int(state))], \
			wait_for_acknowledgement=True)
		
		# Return a success Boolean.
		return acknowledged and (timeout==False)

	def enable_send_pog_left(self, state):
		
		"""Enable (state=True) or disable (state=False) the inclusion of
		the point of gaze of the left eye in the data record string.
		"""

		# Send the message (returns after the Server acknowledges receipt).
		acknowledged, timeout = self._send_message('SET', \
			'ENABLE_SEND_POG_LEFT', \
			values=[('STATE', int(state))], \
			wait_for_acknowledgement=True)
		
		# Return a success Boolean.
		return acknowledged and (timeout==False)

	def enable_send_pog_right(self, state):
		
		"""Enable (state=True) or disable (state=False) the inclusion of
		the point of gaze of the right eye in the data record string.
		"""

		# Send the message (returns after the Server acknowledges receipt).
		acknowledged, timeout = self._send_message('SET', \
			'ENABLE_SEND_POG_RIGHT', \
			values=[('STATE', int(state))], \
			wait_for_acknowledgement=True)
		
		# Return a success Boolean.
		return acknowledged and (timeout==False)

	def enable_send_pog_best(self, state):
		
		"""Enable (state=True) or disable (state=False) the inclusion of
		the 'best' point of gaze in the data record string. This is based
		on the average of the left and right POG if both eyes are available,
		or on the value of the one available eye.
		"""

		# Send the message (returns after the Server acknowledges receipt).
		acknowledged, timeout = self._send_message('SET', \
			'ENABLE_SEND_POG_BEST', \
			values=[('STATE', int(state))], \
			wait_for_acknowledgement=True)
		
		# Return a success Boolean.
		return acknowledged and (timeout==False)

	def enable_send_pupil_left(self, state):
		
		"""Enable (state=True) or disable (state=False) the inclusion of
		pupil data on the left eye in the data record string. This data
		consists of the following:
		LPCX: The horizontal coordinate of the left eye pupil in the camera
			image, as a fraction of the camera size.
		LPCY: The vertical coordinate of the left eye pupil in the camera
			image, as a fraction of the camera size.
		LPD:  The left eye pupil's diameter in pixels.
		LPS:  The scale factor of the left eye pupil (unitless). Value
			equals 1 at calibration depth, is less than 1 when the user
			is closer to the eye tracker and greater than 1 when the user
			is further away.
		LPV:  The valid flag with a value of 1 if the data is valid, and 0
			if it is not.
		"""

		# Send the message (returns after the Server acknowledges receipt).
		acknowledged, timeout = self._send_message('SET', \
			'ENABLE_SEND_PUPIL_LEFT', \
			values=[('STATE', int(state))], \
			wait_for_acknowledgement=True)
		
		# Return a success Boolean.
		return acknowledged and (timeout==False)

	def enable_send_pupil_right(self, state):
		
		"""Enable (state=True) or disable (state=False) the inclusion of
		pupil data on the right eye in the data record string. This data
		consists of the following:
		RPCX: The horizontal coordinate of the right eye pupil in the camera
			image, as a fraction of the camera size.
		RPCY: The vertical coordinate of the right eye pupil in the camera
			image, as a fraction of the camera size.
		RPD:  The right eye pupil's diameter in pixels.
		RPS:  The scale factor of the right eye pupil (unitless). Value
			equals 1 at calibration depth, is less than 1 when the user
			is closer to the eye tracker and greater than 1 when the user
			is further away.
		RPV:  The valid flag with a value of 1 if the data is valid, and 0
			if it is not.
		"""

		# Send the message (returns after the Server acknowledges receipt).
		acknowledged, timeout = self._send_message('SET', \
			'ENABLE_SEND_PUPIL_RIGHT', \
			values=[('STATE', int(state))], \
			wait_for_acknowledgement=True)
		
		# Return a success Boolean.
		return acknowledged and (timeout==False)

	def enable_send_eye_left(self, state):
		
		"""Enable (state=True) or disable (state=False) the inclusion of
		3D data on left eye in the data record string. This data consists
		of the following:
		LEYEX:   The horizontal coordinate of the left eye in 3D space with
			   respect to the camera focal point, in meters.
		LEYEY:   The vertical coordinate of the left eye in 3D space with
			   respect to the camera focal point, in meters.
		LEYEZ:   The depth coordinate of the left eye in 3D space with
			   respect to the camera focal point, in meters.
		LPUPILD: The diameter of the left eye pupil in meters.
		LPUPILV: The valid flag with a value of 1 if the data is valid, and
			   0 if it is not.
		"""

		# Send the message (returns after the Server acknowledges receipt).
		acknowledged, timeout = self._send_message('SET', \
			'ENABLE_SEND_EYE_LEFT', \
			values=[('STATE', int(state))], \
			wait_for_acknowledgement=True)
		
		# Return a success Boolean.
		return acknowledged and (timeout==False)

	def enable_send_eye_right(self, state):
		
		"""Enable (state=True) or disable (state=False) the inclusion of
		3D data on right eye in the data record string. This data consists
		of the following:
		REYEX:   The horizontal coordinate of the right eye in 3D space with
			   respect to the camera focal point, in meters.
		REYEY:   The vertical coordinate of the right eye in 3D space with
			   respect to the camera focal point, in meters.
		REYEZ:   The depth coordinate of the right eye in 3D space with
			   respect to the camera focal point, in meters.
		RPUPILD: The diameter of the right eye pupil in meters.
		RPUPILV: The valid flag with a value of 1 if the data is valid, and
			   0 if it is not.
		"""

		# Send the message (returns after the Server acknowledges receipt).
		acknowledged, timeout = self._send_message('SET', \
			'ENABLE_SEND_EYE_RIGHT', \
			values=[('STATE', int(state))], \
			wait_for_acknowledgement=True)
		
		# Return a success Boolean.
		return acknowledged and (timeout==False)

	def enable_send_cursor(self, state):
		
		"""Enable (state=True) or disable (state=False) the inclusion of
		data on the mouse cursor in the data record string. This data
		consists of the following:
		CX:   The horizontal coordinate of the mouse cursor, as a percentage
			of the screen resolution.
		CY:   The vertical coordinate of the mouse cursor, as a percentage
			of the screen resolution.
		CS:   The mouse cursor state, 0 for steady state, 1 for left button
			down, 2 for rigght button down.
		"""

		# Send the message (returns after the Server acknowledges receipt).
		acknowledged, timeout = self._send_message('SET', \
			'ENABLE_SEND_CURSOR', \
			values=[('STATE', int(state))], \
			wait_for_acknowledgement=True)
		
		# Return a success Boolean.
		return acknowledged and (timeout==False)

	def enable_send_user_data(self, state):
		
		"""Enable (state=True) or disable (state=False) the inclusion of
		user-defined variables in the data record string. User-defined
		variables can be set with the 'user_data' method.
		"""

		# Send the message (returns after the Server acknowledges receipt).
		acknowledged, timeout = self._send_message('SET', \
			'ENABLE_SEND_USER_DATA', \
			values=[('STATE', int(state))], \
			wait_for_acknowledgement=True)
		
		# Return a success Boolean.
		return acknowledged and (timeout==False)
	
	def calibrate_start(self, state):
		
		"""Starts (state=1) or stops (state=0) the calibration procedure.
		Make sure to call the 'calibrate_show' function beforehand, or to
		implement your own calibration visualisation; otherwise a call to
		this function will make the calibration run in the background.
		"""
		
		# Reset the current calibration point.
		if state:
			self._current_calibration_point = 0
		else:
			self._current_calibration_point = None

		# Send the message (returns after the Server acknowledges receipt).
		acknowledged, timeout = self._send_message('SET', \
			'CALIBRATE_START', \
			values=[('STATE', int(state))], \
			wait_for_acknowledgement=True)
		
		# Return a success Boolean.
		return acknowledged and (timeout==False)
	
	def calibrate_show(self, state):
		
		"""Shows (state=1) or hides (state=0) the calibration window on the
		tracker's display window. While showing the calibration window, you
		can call 'calibrate_start' to run the calibration procedure.
		"""

		# Send the message (returns after the Server acknowledges receipt).
		acknowledged, timeout = self._send_message('SET', \
			'CALIBRATE_SHOW', \
			values=[('STATE', int(state))], \
			wait_for_acknowledgement=True)
		
		# Return a success Boolean.
		return acknowledged and (timeout==False)
	
	def calibrate_timeout(self, value):
		
		"""Set the duration of the calibration point (not including the
		animation time) in seconds. The value can be an int or a float.
		"""

		# Send the message (returns after the Server acknowledges receipt).
		acknowledged, timeout = self._send_message('SET', \
			'CALIBRATE_TIMEOUT', \
			values=[('VALUE', float(value))], \
			wait_for_acknowledgement=True)
		
		# Return a success Boolean.
		return acknowledged and (timeout==False)
	
	def calibrate_delay(self, value):
		
		"""Set the duration of the calibration animation (before
		calibration at a point begins) in seconds. The value can be an int
		or a float.
		"""

		# Send the message (returns after the Server acknowledges receipt).
		acknowledged, timeout = self._send_message('SET', \
			'CALIBRATE_DELAY', \
			values=[('VALUE', float(value))], \
			wait_for_acknowledgement=True)
		
		# Return a success Boolean.
		return acknowledged and (timeout==False)
	
	def calibrate_result_summary(self):
		
		"""Returns a summary of the calibration results, which consists of
		the following values:
		AVE_ERROR:    Average error over all calibrated points.
		VALID_POINTS: Number of successfully calibrated points.
		"""

		# Send the message (returns after the Server acknowledges receipt).
		acknowledged, timeout = self._send_message('GET', \
			'CALIBRATE_RESULT_SUMMARY', \
			values=None, \
			wait_for_acknowledgement=True)
		
		# Return the results.
		ave_error = None
		valid_points = None
		if acknowledged:
			self._inlock.acquire()
			ave_error = copy.copy( \
				self._incoming['ACK']['CALIBRATE_RESULT_SUMMARY']['AVE_ERROR'])
			valid_points = copy.copy( \
				self._incoming['ACK']['CALIBRATE_RESULT_SUMMARY']['VALID_POINTS'])
			self._inlock.release()
		
		return ave_error, valid_points
	
	def calibrate_clear(self):
		
		"""Clear the internal list of calibration points.
		"""

		# Send the message (returns after the Server acknowledges receipt).
		acknowledged, timeout = self._send_message('SET', \
			'CALIBRATE_CLEAR', \
			values=None, \
			wait_for_acknowledgement=True)
		
		# Return a success Boolean.
		return acknowledged and (timeout==False)
	
	def calibrate_reset(self):
		
		"""Reset the internal list of calibration points to the default
		values.
		"""

		# Send the message (returns after the Server acknowledges receipt).
		acknowledged, timeout = self._send_message('SET', \
			'CALIBRATE_RESET', \
			values=None, \
			wait_for_acknowledgement=True)
		
		# Return a success Boolean.
		return acknowledged and (timeout==False)
	
	def calibrate_addpoint(self, x, y):
		
		"""Add a calibration point at the passed horizontal (x) and
		vertical (y) coordinates. These coordinates should be as a
		proportion of the screen resolution, where (0,0) is the top-left,
		(0.5,0.5) is the screen centre, and (1,1) is the bottom-right.
		"""

		# Send the message (returns after the Server acknowledges receipt).
		acknowledged, timeout = self._send_message('SET', \
			'CALIBRATE_ADDPOINT', \
			values=[('X', x), ('Y', y)], \
			wait_for_acknowledgement=True)
		
		# Return a success Boolean.
		return acknowledged and (timeout==False)
	
	def get_calibration_points(self):
		
		"""Returns a list of the current calibration points.
		"""

		# Send the message (returns after the Server acknowledges receipt).
		acknowledged, timeout = self._send_message('GET', \
			'CALIBRATE_ADDPOINT', \
			values=None, \
			wait_for_acknowledgement=True)
		
		# Return the result.
		points = None
		if acknowledged:
			points = []
			self._inlock.acquire()
			for i in range(self._incoming['ACK']['CALIBRATE_ADDPOINT']['PTS']):
				points.append( \
					copy.copy(float( \
						self._incoming['ACK']['CALIBRATE_ADDPOINT']['X%d' % i+1])), \
					copy.copy(float( \
						self._incoming['ACK']['CALIBRATE_ADDPOINT']['Y%d' % i+1])) \
					)
			self._inlock.release()
		
		return points
	
	def clear_calibration_result(self):
		
		"""Clears the internally stored calibration result.
		"""

		# Clear the calibration results.
		self._inlock.acquire()
		if 'CAL' in self._incoming.keys():
			if 'CALIB_RESULT' in self._incoming['CAL'].keys():
				self._incoming['CAL'].pop('CALIB_RESULT')
		self._inlock.release()
	
	def get_calibration_result(self):
		
		"""Returns the latest available calibration results as a list of
		dicts, each with the following keys:
		CALX: Calibration point's horizontal coordinate.
		CALY: Calibration point's vertical coordinate
		LX:   Left eye's recorded horizontal point of gaze.
		LY:   Left eye's recorded vertical point of gaze.
		LV:   Left eye's validity status (1=valid, 0=invalid)
		RX:   Right eye's recorded horizontal point of gaze.
		RY:   Right eye's recorded vertical point of gaze.
		RV:   Right eye's validity status (1=valid, 0=invalid)
		
		Returns None if no calibration results are available.
		"""
		
		# Parameters of the 'CALIB_RESULT' dict.
		params = ['CALX', 'CALY', 'LX', 'LY', 'LV', 'RX', 'RY', 'RV']
		
		# Return the result.
		points = None
		self._inlock.acquire()
		if 'CAL' in self._incoming.keys():
			if 'CALIB_RESULT' in self._incoming['CAL'].keys():
				# Get the latest calibration results.
				cal = copy.deepcopy(self._incoming['CAL']['CALIB_RESULT'])
				# Compute the number of fixation points by dividing the
				# total number of parameters in the 'CALIB_RESULT' dict
				# by 8 (the number of parameters per point). Note that
				# the 'CALIB_RESULT' dict also has an 'ID' parameter,
				# which we should account for by subtracting 1 from the
				# length of the list of keys in the dict.
				n_points = (len(cal.keys()) - 1) // len(params)
				# Put the results in a different format.
				points = []
				for i in range(1, n_points+1):
					p = {}
					for par in params:
						if par in ['LV', 'RV']:
							p['%s' % (par)] = cal['%s%d' % (par, i)] == '1'
						else:
							p['%s' % (par)] = float(cal['%s%d' % (par, i)])
					points.append(copy.deepcopy(p))
		self._inlock.release()
		
		return points
	
	def wait_for_calibration_point_start(self, timeout=10.0):
		
		"""Waits for the next calibration point start, which is defined as
		the first unregistered point after the latest calibration start
		message. This function allows for setting a timeout in seconds
		(default = 10.0). Returns the (x,y) coordinate in relative
		coordinates (proportions of the screen width and height) if the
		point started, and None after a timeout. (Also updates the
		internally stored latest registered calibration point number.)
		"""

		# Get the start time of this function.
		start = time.time()
		
		# Get the most recent calibration start time.
		t0 = None
		while (t0 is None) and (time.time() - start < timeout):
			self._inlock.acquire()
			if 'ACK' in self._incoming.keys():
				if 'CALIBRATE_START' in self._incoming['ACK'].keys():
					t0 = copy.copy( \
						self._incoming['ACK']['CALIBRATE_START']['t'])
			self._inlock.release()
			if t0 == None:
				time.sleep(0.001)

		# Return None if there was no calibration start.
		if t0 is None:
			return None
		
		# Wait for a new calibration point start, or a timeout.
		pos = None
		pt_nr = None
		started = False
		timed_out = False
		while (not started) and (not timed_out):
			# Get the latest calibration point start.
			t1 = 0
			self._inlock.acquire()
			if 'CAL' in self._incoming.keys():
				if 'CALIB_START_PT' in self._incoming['CAL'].keys():
					t1 = copy.copy( \
						self._incoming['CAL']['CALIB_START_PT']['t'])
			self._inlock.release()
			# Check if the point is later than the most recent
			# calibration start.
			if t1 >= t0:
				# Check if the current point is already the latest
				# registered point.
				self._inlock.acquire()
				pt_nr = int(copy.copy(self._incoming['CAL']['CALIB_START_PT']['PT']))
				x = float(copy.copy(self._incoming['CAL']['CALIB_START_PT']['CALX']))
				y = float(copy.copy(self._incoming['CAL']['CALIB_START_PT']['CALY']))
				self._inlock.release()
				if pt_nr != self._current_calibration_point:
					self._current_calibration_point = copy.copy(pt_nr)
					pos = (x, y)
					started = True
			# Check if there is a timeout.
			if time.time() - start > timeout:
				timed_out = True
			# Wait for a short bit to avoid wasting too many resources,
			# and to avoid hogging the incoming messages Lock.
			if not timed_out:
				time.sleep(0.001)
		
		if started:
			return pt_nr, pos
		else:
			return None, None
	
	def user_data(self, value):
		
		"""Set the value of the user data field for embedding custom data
		into the data stream. The user data value should be a string.
		"""

		# Send the message (returns after the Server acknowledges receipt).
		acknowledged, timeout = self._send_message('SET', \
			'USER_DATA', \
			values=[('VALUE', str(value))], \
			wait_for_acknowledgement=True)
		
		# Return a success Boolean.
		return acknowledged and (timeout==False)
	
	def tracker_display(self, state):
		
		"""Shows (state=1) or hides (state=0) the eye tracker display
		window.
		"""

		# Send the message (returns after the Server acknowledges receipt).
		acknowledged, timeout = self._send_message('SET', \
			'TRACKER_DISPLAY', \
			values=[('STATE', int(state))], \
			wait_for_acknowledgement=True)
		
		# Return a success Boolean.
		return acknowledged and (timeout==False)
	
	def time_tick_frequency(self):
		
		"""Returns the time-tick frequency to convert the TIME_TICK
		variable to seconds.
		"""
		
		return self.get_time_tick_frequency()
	
	def get_time_tick_frequency(self):
		
		"""Returns the time-tick frequency to convert the TIME_TICK
		variable to seconds.
		"""

		# Send the message (returns after the Server acknowledges receipt).
		acknowledged, timeout = self._send_message('GET', \
			'TIME_TICK_FREQUENCY', \
			values=None, \
			wait_for_acknowledgement=True)
		
		# Return the result.
		freq = None
		if acknowledged:
			self._inlock.acquire()
			freq = copy.copy(self._incoming['ACK']['TIME_TICK_FREQUENCY']['FREQ'])
			self._inlock.release()
		
		return freq
	
	def screen_size(self, x, y, w, h):
		
		"""Set the gaze tracking screen position (x,y) and size (w, h). You
		can use this to work with multi-monitor systems. All values are in
		pixels.
		"""

		# Send the message (returns after the Server acknowledges receipt).
		acknowledged, timeout = self._send_message('SET', \
			'SCREEN_SIZE', \
			values=[('X', x), ('Y', x), ('WIDTH', w), ('HEIGHT', h)], \
			wait_for_acknowledgement=True)
		
		# Return a success Boolean.
		return acknowledged and (timeout==False)
	
	def get_screen_size(self):
		
		"""Returns the x and y coordinates of the top-left of the screen in
		pixels, as well as the screen width and height in pixels. The
		result is returned as [x, y, w, h].
		"""

		# Send the message (returns after the Server acknowledges receipt).
		acknowledged, timeout = self._send_message('GET', \
			'SCREEN_SIZE', \
			values=None, \
			wait_for_acknowledgement=True)
		
		# Return the result.
		x = None
		y = None
		w = None
		h = None
		if acknowledged:
			self._inlock.acquire()
			x = copy.copy(self._incoming['ACK']['SCREEN_SIZE']['X'])
			y = copy.copy(self._incoming['ACK']['SCREEN_SIZE']['Y'])
			w = copy.copy(self._incoming['ACK']['SCREEN_SIZE']['WIDTH'])
			h = copy.copy(self._incoming['ACK']['SCREEN_SIZE']['HEIGHT'])
			self._inlock.release()
		
		return [x, y, w, h]
	
	def camera_size(self):
		
		"""Returns the size of the camera sensor in pixels, as [w,h].
		"""
		
		return self.get_camera_size()
	
	def get_camera_size(self):
		
		"""Returns the size of the camera sensor in pixels, as [w,h].
		"""

		# Send the message (returns after the Server acknowledges receipt).
		acknowledged, timeout = self._send_message('GET', \
			'CAMERA_SIZE', \
			values=None, \
			wait_for_acknowledgement=True)
		
		# Return the result.
		w = None
		h = None
		if acknowledged:
			self._inlock.acquire()
			w = copy.copy(self._incoming['ACK']['CAMERA_SIZE']['WIDTH'])
			h = copy.copy(self._incoming['ACK']['CAMERA_SIZE']['HEIGHT'])
			self._inlock.release()
		
		return [w, h]
	
	def product_id(self):
		
		"""Returns the identifier of the connected eye-tracker.
		"""
		
		return self.get_product_id()
	
	def get_product_id(self):
		
		"""Returns the identifier of the connected eye-tracker.
		"""

		# Send the message (returns after the Server acknowledges receipt).
		acknowledged, timeout = self._send_message('GET', \
			'PRODUCT_ID', \
			values=None, \
			wait_for_acknowledgement=True)
		
		# Return the result.
		value = None
		if acknowledged:
			self._inlock.acquire()
			value = copy.copy(self._incoming['ACK']['PRODUCT_ID']['VALUE'])
			self._inlock.release()
		
		return value
	
	def serial_id(self):
		
		"""Returns the serial number of the connected eye-tracker.
		"""
		
		return self.get_serial_id()
	
	def get_serial_id(self):
		
		"""Returns the serial number of the connected eye-tracker.
		"""

		# Send the message (returns after the Server acknowledges receipt).
		acknowledged, timeout = self._send_message('GET', \
			'SERIAL_ID', \
			values=None, \
			wait_for_acknowledgement=True)
		
		# Return the result.
		value = None
		if acknowledged:
			self._inlock.acquire()
			value = copy.copy(self._incoming['ACK']['SERIAL_ID']['VALUE'])
			self._inlock.release()
		
		return value
	
	def company_id(self):
		
		"""Returns the identifier of the manufacturer of the connected
		eye-tracker.
		"""
		
		return self.get_company_id()
	
	def get_company_id(self):
		
		"""Returns the identifier of the manufacturer of the connected
		eye-tracker.
		"""

		# Send the message (returns after the Server acknowledges receipt).
		acknowledged, timeout = self._send_message('GET', \
			'COMPANY_ID', \
			values=None, \
			wait_for_acknowledgement=True)
		
		# Return the result.
		value = None
		if acknowledged:
			self._inlock.acquire()
			value = copy.copy(self._incoming['ACK']['COMPANY_ID']['VALUE'])
			self._inlock.release()
		
		return value
	
	def api_id(self):
		
		"""Returns the API version number.
		"""
		
		return self.get_api_id()
	
	def get_api_id(self):
		
		"""Returns the API version number.
		"""

		# Send the message (returns after the Server acknowledges receipt).
		acknowledged, timeout = self._send_message('GET', \
			'API_ID', \
			values=None, \
			wait_for_acknowledgement=True)
		
		# Return the result.
		value = None
		if acknowledged:
			self._inlock.acquire()
			value = copy.copy(self._incoming['ACK']['API_ID']['VALUE'])
			self._inlock.release()
		
		return value

	# TODO: Get sample method.
	# TODO: Write sample method?

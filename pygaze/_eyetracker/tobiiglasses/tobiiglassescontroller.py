# tobiiglassescontroller.py: A Python controller for Tobii Pro Glasses 2
#
# Copyright (C) 2017  Davide De Tommaso
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>

import urllib2
import json
import time
import datetime
import threading
import socket
import uuid
import logging as log

log.basicConfig(format='[%(levelname)s]: %(message)s', level=log.DEBUG)


class TobiiGlassesController():

	def __init__(self, udpport, address =  None):

		self.timeout = 1
		self.streaming = False
		self.connected = False
		self.udpport = udpport
		self.address = address

		self.data = {}
		nd = {'ts': -1}
		self.data['mems'] = { 'ac': nd, 'gy': nd }
		self.data['right_eye'] = { 'pc': nd, 'pd': nd, 'gd': nd}
		self.data['left_eye'] = { 'pc': nd, 'pd': nd, 'gd': nd}
		self.data['gp'] = nd
		self.data['gp3'] = nd

		self.project_id = str(uuid.uuid4())
		self.project_name = "TobiiProGlasses PyController"
		self.project_creation_date = datetime.datetime.now().strftime("%m/%d/%y %H:%M:%S")
		self.recn = 0

		if self.address is None:
			self.__discover_device__()
		else:
			self.__set_address__(self.udpport, self.address)

		# Keep-alive message content used to request live data streams
		self.KA_DATA_MSG = "{\"type\": \"live.data.unicast\", \"key\": \""+ str(uuid.uuid4()) +"\", \"op\": \"start\"}"

	def __set_address__(self, udpport, address):

		self.base_url = 'http://' + address
		self.peer = (address, udpport)


	def __del__(self):

		if self.streaming:
			self.stop_streaming()
		if self.is_connected():
			self.disconnect()


	def __mksock__(self):

		iptype = socket.AF_INET
		if ':' in self.peer[0]:
			iptype = socket.AF_INET6
		return socket.socket(iptype, socket.SOCK_DGRAM)


	def __send_keepalive_msg__(self, socket, msg):

		while self.streaming:
			socket.sendto(msg, self.peer)
			time.sleep(self.timeout)


	def __grab_data__(self, socket):

		time.sleep(1)
		while self.streaming:
			data, address = socket.recvfrom(1024)
			jdata = json.loads(data)
			self.__refresh_data__(jdata)



	def __refresh_data__(self, jsondata):

		try:
			gy = jsondata['gy']
			ts = jsondata['ts']
			if( (self.data['mems']['gy']['ts'] < ts) and (jsondata['s'] == 0) ):
				self.data['mems']['gy'] = jsondata
		except:
			pass

		try:
			ac = jsondata['ac']
			ts = jsondata['ts']
			if( (self.data['mems']['ac']['ts'] < ts) and (jsondata['s'] == 0) ):
				self.data['mems']['ac'] = jsondata
		except:
			pass

		try:
			pc = jsondata['pc']
			ts = jsondata['ts']
			eye = jsondata['eye']
			if( (self.data[eye + '_eye']['pc']['ts'] < ts) and (jsondata['s'] == 0) ):
				self.data[eye + '_eye']['pc'] = jsondata
		except:
			pass

		try:
			pd = jsondata['pd']
			ts = jsondata['ts']
			eye = jsondata['eye']
			if( (self.data[eye + '_eye']['pd']['ts'] < ts) and (jsondata['s'] == 0) ):
				self.data[eye + '_eye']['pd'] = jsondata
		except:
			pass

		try:
			gd = jsondata['gd']
			ts = jsondata['ts']
			eye = jsondata['eye']
			if( (self.data[eye + '_eye']['gd']['ts'] < ts) and (jsondata['s'] == 0) ):
				self.data[eye + '_eye']['gd'] = jsondata
		except:
			pass

		try:
			gp = jsondata['gp']
			ts = jsondata['ts']
			if( (self.data['gp']['ts'] < ts) and (jsondata['s'] == 0) ):
				self.data['gp'] = jsondata

		except:
			pass

		try:
			gp3 = jsondata['gp3']
			ts = jsondata['ts']
			if( (self.data['gp3']['ts'] < ts) and (jsondata['s'] == 0) ):
				self.data['gp3'] = jsondata
		except:
			pass


	def __start_streaming__(self):

		try:
			self.streaming = True
			self.td = threading.Timer(0, self.__send_keepalive_msg__, [self.data_socket, self.KA_DATA_MSG])
			self.tg = threading.Timer(0, self.__grab_data__, [self.data_socket])
			self.td.start()
			self.tg.start()
		except:
			self.streaming = False
			log.error("An error occurs trying to create the threads for receiving data")

	def __post_request__(self, api_action, data=None):

		url = self.base_url + api_action
		req = urllib2.Request(url)
		req.add_header('Content-Type', 'application/json')
		data = json.dumps(data)
		response = urllib2.urlopen(req, data)
		data = response.read()
		json_data = json.loads(data)
		return json_data


	def __discover_device__(self):

		log.debug("Discovering a Tobii Pro Glasses 2 device ...")
		MULTICAST_ADDR = 'ff02::1'  # ipv6: all nodes on the local network segment
		PORT = 13007
		s6 = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
		s6.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		s6.bind(('::', PORT))
		s6.sendto('{"type":"discover"}', (MULTICAST_ADDR, 13006))
		data, address = s6.recvfrom(1024)
		print "[%s]" % address[0]
		self.__set_address__(self.udpport, "[%s]" % address[0].split("%")[0])
		log.debug(" From: " + address[0] + " " + data)


	def connect(self):

		log.debug("Connecting to the Tobii Pro Glasses 2 ...")
		try:
			self.data_socket = self.__mksock__()
			self.connected = True
			log.debug("Tobii Pro Glasses 2 ... successful connected!")
		except:
			log.error("An error occurs trying to connect to the Tobii Pro Glasses")

		return self.connected

	def disconnect(self):
		log.debug("Disconnecting to the Tobii Pro Glasses 2 ...")
		try:
			self.data_socket.close()
			self.connected = False
			log.debug("... Tobii Pro Glasses 2 successful disconnected!")
		except:
			log.error("An error occurs closing the sockets of the Tobii Pro Glasses")

		return not self.connected


	def start_streaming(self):
		log.debug("Start data streaming ...")
		try:
			self.__start_streaming__()
			log.debug("Data streaming successful started!")
		except:
			log.error("An error occurs trying to connect to the Tobii Pro Glasses")

	def stop_streaming(self):
		log.debug("Stop data streaming ...")
		try:
			if self.streaming:
				self.streaming = False
				self.td.join()
				self.tg.join()
			log.debug("Data streaming successful stopped!")
		except:
			log.error("An error occurs trying to stop data streaming")


	def is_connected(self):

		try:
			status = self.wait_for_status('/api/system/status', 'sys_status', ['ok'])

			if status == 'ok' and self.connected:
				res_connection = True
			else:
				res_connection = False
		except:
			res_connection = False


		return res_connection


	def wait_for_status(self, api_action, key, values):

		url = self.base_url + api_action
		self.running = True
		while self.running:
			req = urllib2.Request(url)
			req.add_header('Content-Type', 'application/json')
			response = urllib2.urlopen(req, None)
			data = response.read()
			json_data = json.loads(data)
			if json_data[key] in values:
				self.running = False
			time.sleep(1)

		return json_data[key]

	def is_calibrated(self, calibration_id):

		status = self.wait_for_status('/api/calibrations/' + calibration_id + '/status', 'ca_state', ['failed', 'calibrated'])

		if status == 'failed':
			log.debug("Calibration " + calibration_id + " failed, using default calibration instead")
			res_calibration = False
		else:
			log.debug("Calibration " + calibration_id + " successful")
			res_calibration = True

		return res_calibration


	def create_project(self, projectname = "DefaultProjectName"):

		data = {'pr_info' : {'CreationDate': self.project_creation_date, 'EagleId': self.project_id, 'Name': projectname}}
		json_data = self.__post_request__('/api/projects', data)
		return json_data['pr_id']


	def create_participant(self, project_id, participant_name = "DefaultUser", participant_notes = ""):

		self.participant_name = participant_name
		data = {'pa_project': project_id, 'pa_info': {'EagleId': self.project_id, 'Name': self.participant_name, 'Notes': participant_notes}}
		json_data = self.__post_request__('/api/participants', data)
		return json_data['pa_id']

	def create_calibration(self, project_id, participant_id):

		data = {'ca_project': project_id, 'ca_type': 'default', 'ca_participant': participant_id}
		json_data = self.__post_request__('/api/calibrations', data)
		return json_data['ca_id']

	def start_calibration(self, calibration_id):

		self.__post_request__('/api/calibrations/' + calibration_id + '/start')

	def create_recording(self, participant_id, recording_notes = ""):

		self.recn = self.recn + 1
		recording_name = "Recording" + str(self.recn)
		data = {'rec_participant': participant_id, 'rec_info': {'EagleId': self.project_id, 'Name': recording_name, 'Notes': recording_notes}}
		json_data = self.__post_request__('/api/recordings', data)
		return json_data['rec_id']

	def start_recording(self, recording_id):
		self.__post_request__('/api/recordings/' + recording_id + '/start')

	def stop_recording(self, recording_id):
		self.__post_request__('/api/recordings/' + recording_id + '/stop')

	def get_data(self):
		return self.data

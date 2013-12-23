#-*- coding:utf-8 -*-

"""
This file is part of PyGaze.

PyGaze is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

PyGaze is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with PyGaze.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
from libopensesame.exceptions import osexception
from libopensesame.item import item
from libqtopensesame.items.qtautoplugin import qtautoplugin
from pygaze import EyeTracker, Display

class pygaze_init(item):
	
	"""Plug-in runtime definition."""

	description = u'Initialize and calibrate eye tracker'

	def __init__(self, name, experiment, script=None):

		"""
		Constructor.
		
		Arguments:
		name		--	The name of the plug-in.
		experiment	--	The experiment object.
		
		Keyword arguments:
		script		--	A definition script. (default=None)
		"""

		# Generic settings
		self.tracker_type = u'Simple dummy'
		self.calibrate = u'yes'
		self.sacc_vel_thr = 35
		self.sacc_acc_thr = 9500
		self._logfile = u'automatic'
		# SMI-specific settings
		self.smi_ip = u'127.0.0.1'
		self.smi_send_port = 4444
		self.smi_recv_port = 5555
		item.__init__(self, name, experiment, script)
		self.reload_pygaze()

	def prepare(self):

		"""The preparation phase of the plug-in goes here."""

		item.prepare(self)
		
	def reload_pygaze(self):
		
		"""
		Reloads pygaze modules to get a clean start. This is necessary, because
		otherwise PyGaze will try to use the old experiment instance when the
		experiment is executed twice. Explicitly reloading all
		OpenSesame-related modules will fix this.
		"""
		
		from pygaze import defaults
		defaults.osexperiment = self.experiment
		defaults.DISPTYPE = u'opensesame'
		defaults.DISPSIZE = self.resolution()
		defaults.BGC = self.get(u'background')
		defaults.FGC = self.get(u'foreground')
		from pygaze._screen import osscreen
		from pygaze._display import osdisplay
		from pygaze._keyboard import oskeyboard
		from pygaze._mouse import osmouse
		from pygaze._time import ostime
		reload(osscreen)
		reload(osdisplay)
		reload(oskeyboard)
		reload(osmouse)
		reload(ostime)

	def run(self):

		"""The run phase of the plug-in goes here."""

		self.set_item_onset()
		if self.tracker_type == u'Simple dummy':
			tracker_type = u'dumbdummy'
		elif self.tracker_type == u'Advanced dummy (mouse simulation)':
			tracker_type = u'dummy'
		elif self.tracker_type == u'EyeLink':
			tracker_type = u'eyelink'
		elif self.tracker_type == u'Tobii':
			tracker_type = u'tobii'
		elif self.tracker_type == u'SMI':
			tracker_type = u'smi'
		else:
			raise osexception(u'Unknown tracker type: %s' % self.tracker_type)
		# Determine logfile
		if self.get(u'_logfile') == u'automatic':
			logfile = os.path.splitext(os.path.basename(self.get( \
				u'logfile')))[0]
			if tracker_type == u'eyelink':
				logfile = logfile + u'.edf'
		else:
			logfile = self.get(u'_logfile')
		if tracker_type == u'eyelink' and len(logfile) > 12:
			raise osexception( \
				u'The name for the EyeLink logfile must contain at most eight characters (not counting the .edf extension), not "%s"' \
				% logfile)
		# Determine event detection
		if tracker_type == u'eyelink':
			event_detection = u'native'
		else:
			event_detection = u'pygaze'
		self.experiment.pygaze_display = Display(u'opensesame')
		self.experiment.pygaze_eyetracker = EyeTracker( \
			self.experiment.pygaze_display, trackertype=tracker_type, \
			data_file=logfile, event_detection=event_detection, \
			saccade_velocity_threshold=self.get(u'sacc_vel_thr'), \
			saccade_acceleration_threshold=self.get(u'sacc_acc_thr'), \
			ip=self.get(u'smi_ip'), sendport=self.get(u'smi_send_port'), \
			receiveport=self.get(u'smi_recv_port'), logfile=logfile)
		if self.calibrate == u'yes':
			self.experiment.pygaze_eyetracker.calibrate()

class qtpygaze_init(pygaze_init, qtautoplugin):
	
	"""Plug-in GUI definition."""
	
	def __init__(self, name, experiment, script=None):
		
		"""
		Constructor.
		
		Arguments:
		name		--	The name of the plug-in.
		experiment	--	The experiment object.
		
		Keyword arguments:
		script		--	A definition script. (default=None)
		"""

		pygaze_init.__init__(self, name, experiment, script)
		qtautoplugin.__init__(self, __file__)
		self.custom_interactions()

	def apply_edit_changes(self):

		"""Apply the controls"""

		if not qtautoplugin.apply_edit_changes(self) or self.lock:
			return False
		self.custom_interactions()
		return True
	
	def custom_interactions(self):
		
		"""Activates the relevant controls for each tracker."""
		
		smi = self.get(u'tracker_type') == u'SMI'
		self.line_edit_smi_ip.setEnabled(smi)
		self.spinbox_smi_send_port.setEnabled(smi)
		self.spinbox_smi_recv_port.setEnabled(smi)		
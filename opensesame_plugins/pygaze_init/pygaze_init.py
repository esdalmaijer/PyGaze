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
import inspect
from openexp.canvas import canvas
from libopensesame import debug
from libopensesame.exceptions import osexception
from libopensesame.item import item
from libqtopensesame.items.qtautoplugin import qtautoplugin
from pygaze.eyetracker import EyeTracker
from pygaze.display import Display
import pygaze

class pygaze_init(item):

	"""
	desc:
		Plug-in runtime definition.
	"""

	description = u'Initialize and calibrate eye tracker'

	def __init__(self, name, experiment, string=None):

		item.__init__(self, name, experiment, string)
		self.reload_pygaze()

	def reset(self):

		"""
		desc:
			Resets plug-in settings.
		"""

		# Generic settings
		self.var.tracker_type = u'Simple dummy'
		self.var.calibrate = u'yes'
		self.var.calbeep = u'yes'
		self.var.sacc_vel_thr = 35
		self.var.sacc_acc_thr = 9500
		self.var._logfile = u'automatic'
		# Alea-specific settings
		self.var.alea_api_key = u'Contact Alea for an API key'
		self.var.alea_animated_calibration = u'no'
		# EyeLink-specific settings
		self.var.eyelink_force_drift_correct = u'yes'
		self.var.eyelink_pupil_size_mode = u'area'
		# SMI-specific settings
		self.var.smi_ip = u'127.0.0.1'
		self.var.smi_send_port = 4444
		self.var.smi_recv_port = 5555
		# Tobii Pro Glasses 2 settings
		self.var.tobiiglasses_address = u'192.168.71.50'
		self.var.tobiiglasses_udpport = 49152

	def close(self):

		"""
		desc:
			Closes the connection with the eye tracker when the experiment is
			finished.
		"""

		debug.msg(u'Starting PyGaze deinitialisation')
		self.clock.sleep(1000)
		self.experiment.pygaze_eyetracker.close()
		self.experiment.pygaze_eyetracker = None
		debug.msg(u'Finished PyGaze deinitialisation')
		self.clock.sleep(1000)

	def draw_calibration_canvas(self, x, y):

		"""
		desc:
			A hook to prepare the canvas with the clibration target.

		arguments:
			x:
				desc:	The X coordinate.
				type:	int
			y:
				desc:	The Y coordinate.
				type:	int
		"""

		dc_canvas = canvas(self.experiment)
		# Coordinates are always sent in 0,0=top-left mode, so we need to
		# correct for this if we're using uniform coordinates.
		if self.var.uniform_coordinates == u'yes':
			x -= dc_canvas._xcenter
			y -= dc_canvas._ycenter
		dc_canvas.fixdot(x, y, style=u'large-open')
		if self.var.calbeep == 'yes':
			self.beep.play()
		dc_canvas.show()

	def reload_pygaze(self):

		"""
		desc:
			Reloads pygaze modules to get a clean start. This is necessary,
			because otherwise PyGaze will try to use the old experiment instance
			when the experiment is executed twice. Explicitly reloading all
			OpenSesame-related modules will fix this.
		"""

		from pygaze import settings
		settings.osexperiment = self.experiment
		settings.DISPTYPE = u'opensesame'
		settings.DISPSIZE = self.resolution()
		settings.BGC = self.var.background
		settings.FGC = self.var.foreground
		settings.ALEAKEY = self.var.alea_api_key

		if self.var.calbeep == u'yes':
			settings.EYELINKCALBEEP = True
		else:
			settings.EYELINKCALBEEP = False

		if self.var.alea_animated_calibration == u'yes':
			settings.ALEAANIMATEDCALIBRATION = True
		else:
			settings.ALEAANIMATEDCALIBRATION = False

	def run(self):

		"""
		desc:
			The run phase of the plug-in goes here.
		"""

		if hasattr(self.experiment, u'pygaze_eyetracker'):
			raise osexception(
				u'You should have only one instance of `pygaze_init` in your experiment')
		self.set_item_onset()
		# Determine the tracker type and perform certain tracker-specific
		# operations.
		kwdict = {}
		if self.var.tracker_type == u'Simple dummy':
			tracker_type = u'dumbdummy'
		elif self.var.tracker_type == u'Advanced dummy (mouse simulation)':
			tracker_type = u'dummy'
		elif self.var.tracker_type == u'EyeLink':
			tracker_type = u'eyelink'
			kwdict[u'eyelink_force_drift_correct'] = \
				self.var.eyelink_force_drift_correct == u'yes'
			kwdict[u'pupil_size_mode'] = self.var.eyelink_pupil_size_mode
		elif self.var.tracker_type == u'SMI':
			tracker_type = u'smi'
			kwdict[u'ip'] = self.var.smi_ip
			kwdict[u'sendport'] = self.var.smi_send_port
			kwdict[u'receiveport'] = self.var.smi_recv_port
		elif self.var.tracker_type == u'EyeTribe':
			tracker_type = u'eyetribe'
		elif self.var.tracker_type == u'OpenGaze':
			tracker_type = u'opengaze'
		elif self.var.tracker_type == u'Alea':
			tracker_type = u'alea'
			kwdict[u'alea_key'] = self.var.alea_api_key
			kwdict[u'animated_calibration'] = \
				self.var.alea_animated_calibration == u'yes'
		elif self.var.tracker_type == u'Tobii':
			tracker_type = u'tobii'
		elif self.var.tracker_type == u'Tobii-legacy':
			tracker_type = u'tobii-legacy'
		elif self.var.tracker_type == u'Tobii Pro Glasses 2':
			tracker_type = u'tobiiglasses'
			kwdict[u'address'] = self.var.tobiiglasses_address
			kwdict[u'udpport'] = self.var.tobiiglasses_udpport
		else:
			raise osexception(
				u'Unknown tracker type: %s' % self.var.tracker_type)
		# Determine logfile
		if self.var._logfile == u'automatic':
			logfile = os.path.splitext(self.var.logfile)[0]
			if tracker_type == u'eyelink':
				# Automatically shorten filenames like 'subject-0', because
				# these are too long. This avoids having to rename logfiles
				# all the time.
				basename = os.path.basename(logfile)
				dirname = os.path.dirname(logfile)
				if len(basename) > 8 and basename.startswith(u'subject-'):
					basename = u'sub_' + basename[8:]
					logfile = os.path.join(dirname, basename)
					print(u'Attention: EyeLink logfile renamed to %s.edf' \
						% logfile)
				elif basename == u'defaultlog':
					logfile = u'default'
					print(u'Attention: EyeLink logfile renamed to %s.edf' \
						% logfile)
				logfile = logfile + u'.edf'
				kwdict[u'data_file'] = logfile
		else:
			logfile = self.var._logfile
		# Register the logfile with OpenSesame
		self.experiment.data_files.append(logfile)
		# Determine event detection. Currently, only the EyeLink has native
		# event detection.
		if tracker_type == u'eyelink':
			event_detection = u'native'
		else:
			event_detection = u'pygaze'
		# Initialize pygaze and the eye-tracker object
		self.experiment.pygaze_display = Display(u'opensesame')
		self.experiment.pygaze_eyetracker = EyeTracker(
			self.experiment.pygaze_display,
			trackertype=tracker_type,
			eventdetection=event_detection,
			saccade_velocity_threshold=self.var.sacc_vel_thr,
			saccade_acceleration_threshold=self.var.sacc_acc_thr,
			logfile=logfile,
			**kwdict)
		if self.var.calbeep == u'yes':
			from openexp.synth import synth
			self.beep = synth(self.experiment)
		self.experiment.pygaze_eyetracker.set_draw_calibration_target_func(
			self.draw_calibration_canvas)
		self.experiment.pygaze_eyetracker.set_draw_drift_correction_target_func(
			self.draw_calibration_canvas)
		self.experiment.cleanup_functions.append(self.close)
		if self.var.calibrate == u'yes':
			self.experiment.pygaze_eyetracker.calibrate()
		self.python_workspace[u'eyetracker'] = self.experiment.pygaze_eyetracker

class qtpygaze_init(pygaze_init, qtautoplugin):

	"""
	desc:
		Plug-in GUI definition.
	"""

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

	def init_edit_widget(self):

		qtautoplugin.init_edit_widget(self)
		self.custom_interactions()
		self.text_pygaze_version.setText(
			u'<small>PyGaze version %s</small>' % pygaze.version)

	def apply_edit_changes(self):

		"""
		desc:
			Applies the controls.
		"""

		if not qtautoplugin.apply_edit_changes(self) or self.lock:
			return False
		self.custom_interactions()

	def edit_widget(self):

		"""
		Refreshes the controls.

		Returns:
		The QWidget containing the controls
		"""

		if self.lock:
			return
		self.lock = True
		w = qtautoplugin.edit_widget(self)
		self.custom_interactions()
		self.lock = False
		return w

	def custom_interactions(self):

		"""
		desc:
			Activates the relevant controls for each tracker.
		"""

		alea = self.var.tracker_type == u'Alea'
		self.line_edit_alea_api_key.setEnabled(alea)
		self.checkbox_alea_animated_calibration.setEnabled(alea)
		smi = self.var.tracker_type == u'SMI'
		self.line_edit_smi_ip.setEnabled(smi)
		self.spinbox_smi_send_port.setEnabled(smi)
		self.spinbox_smi_recv_port.setEnabled(smi)
		eyelink = self.var.tracker_type == u'EyeLink'
		self.checkbox_eyelink_force_drift_correct.setEnabled(eyelink)
		self.combobox_eyelink_pupil_size_mode.setEnabled(eyelink)
		self.spinbox_sacc_acc_thr.setDisabled(eyelink)
		self.spinbox_sacc_vel_thr.setDisabled(eyelink)
		tobiiglasses = self.var.tracker_type == u'Tobii Pro Glasses 2'
		self.line_edit_tobiiglasses_address.setEnabled(tobiiglasses)
		self.spinbox_tobiiglasses_udpport.setEnabled(tobiiglasses)
		if eyelink:
			try:
				import pylink
			except:
				pylink = None
			if pylink == None:
				self.text_eyelink_pylink_check.show()
			else:
				self.text_eyelink_pylink_check.hide()
		else:
			self.text_eyelink_pylink_check.hide()

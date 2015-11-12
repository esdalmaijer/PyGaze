# -*- coding: utf-8 -*-
#
# This file is part of PyGaze - the open-source toolbox for eye tracking
#
#	PyGaze is a Python module for easily creating gaze contingent experiments
#	or other software (as well as non-gaze contingent experiments/software)
#	Copyright (C) 2012-2013  Edwin S. Dalmaijer
#
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with this program.  If not, see <http://www.gnu.org/licenses/>

from pygaze import settings
import pygaze
from pygaze._misc.misc import rgb2psychorgb
from pygaze.libtime import clock
#from pygaze._display.basedisplay import BaseDisplay

from psychopy.visual import Window

# we try importing the copy_docstr function, but as we do not really need it
# for a proper functioning of the code, we simply ignore it when it fails to
# be imported correctly
try:
	from pygaze._misc.misc import copy_docstr
except:
	pass


#class PsychoPyDisplay(BaseDisplay):
class PsychoPyDisplay:

	# See _display.basedisplay.BaseDisplay for documentation

	def __init__(self, dispsize=settings.DISPSIZE, fgc=settings.FGC,
		bgc=settings.BGC, screennr=settings.SCREENNR, screen=None, **args):

		# See _display.basedisplay.BaseDisplay for documentation
		
		# try to import copy docstring (but ignore it if it fails, as we do
		# not need it for actual functioning of the code)
		try:
			copy_docstr(BaseDisplay, PsychoPyDisplay)
		except:
			# we're not even going to show a warning, since the copied
			# docstring is useful for code editors; these load the docs
			# in a non-verbose manner, so warning messages would be lost
			pass

		self.dispsize = dispsize
		self.fgc = fgc
		self.bgc = bgc
		self.screennr = screennr
		self.mousevis = False

		# create window
		pygaze.expdisplay = Window(size=self.dispsize, pos=None,
			color=rgb2psychorgb(self.bgc), colorSpace='rgb',
			fullscr=settings.FULLSCREEN, screen=self.screennr, units='pix')
		# set mouse visibility
		pygaze.expdisplay.setMouseVisible(self.mousevis)
		# get screen in window
		if screen:
			for s in screen.screen:
				s.draw()

	def show(self):

		# See _display.basedisplay.BaseDisplay for documentation

		pygaze.expdisplay.flip()
		return clock.get_time()

	def show_part(self, rect, screen=None):

		# See _display.basedisplay.BaseDisplay for documentation

		self.fill(screen)
		self.show()
		print("WARNING! screen.Display.show_part not available for PsychoPy display type; fill() and show() are used instead")
		
		return clock.get_time()


	def fill(self, screen=None):

		# See _display.basedisplay.BaseDisplay for documentation

		pygaze.expdisplay.clearBuffer()
		if screen != None:
			for s in screen.screen:
				s.draw()

	def close(self):

		# See _display.basedisplay.BaseDisplay for documentation

		pygaze.expdisplay.close()

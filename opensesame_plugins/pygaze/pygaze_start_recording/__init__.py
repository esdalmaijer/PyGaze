"""Puts the eye tracker out of recording mode"""

category = 'PyGaze'
priority = 10
help = 'manual/eyetracking/pygaze'
icon = 'os-pygaze_start_recording'
controls = [
  {'type': 'line_edit',
    'var': 'status_msg',
    'label': 'Status message',
    'tooltip': 'A text to use as status message'
   }]

"""Writes information to the eye-tracker logfile"""

category = 'PyGaze'
priority = 10
icon = 'os-pygaze_log'
help = 'manual/eyetracking/pygaze'
controls = [
  {'type': 'spinbox',
   'var': 'throttle',
   'label': 'Pause between messages',
   'min_val': 0,
   'max_val': 1000,
   'suffix': ' ms',
   'tooltip': 'A pause between messages to avoid overloading the eye tracker'},
  {'type': 'checkbox',
   'var': 'auto_log',
   'label': 'Automatically log all variables',
   'tooltip': 'Automatically send all experimental variables to the eye tracker'},
  {'type': 'editor',
   'var': 'msg',
   'label': 'Log message',
   'syntax': False,
   'tooltip': 'The message to write to the eye tracker'}]

"""Performs eye-tracker drift correction"""

category = 'PyGaze'
priority = 10
help = 'manual/eyetracking/pygaze'
icon = 'os-pygaze_drift_correct'
controls = [
  {'type': 'line_edit',
   'var': 'xpos',
   'label': 'X position',
   'tooltip': 'X coordinate for drift correction'},
  {'type': 'line_edit',
   'var': 'ypos',
   'label': 'Y position',
   'tooltip': 'Y position for drift correction'},
  {'type': 'line_edit',
   'var': 'target_color',
   'label': 'Target color',
   'tooltip': 'Color for the drift-correction target',
   'name': 'line_edit_target_color'},
  {'type': 'combobox',
   'var': 'target_style',
   'label': 'Target style (OpenSesame >= 2.8.0)',
   'options': ['default',
    'large-filled',
    'small-filled',
    'large-open',
    'small-open',
    'large-cross',
    'small-cross'],
   'tooltip': 'Style for the drift-correction target',
   'name': 'combobox_target_style'},
  {'type': 'checkbox',
   'var': 'draw_target',
   'label': 'Show display with drift-correction target',
   'tooltip': 'Indicates whether a drift-correction display should be shown'},
  {'type': 'checkbox',
   'var': 'fixation_triggered',
   'label': 'Fixation triggered (no spacebar press required)',
   'tooltip': 'Indicates whether drift correction should be performed as soon as a stable fixation is detected'}]

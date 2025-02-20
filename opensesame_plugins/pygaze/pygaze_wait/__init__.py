category = 'PyGaze'
priority = 10
help = 'manual/eyetracking/pygaze'
icon = 'os-pygaze_wait'
controls = [
    {
        'type': 'combobox',
        'var': 'event',
        'label': 'Event',
        'options': [
            'Saccade start',
            'Saccade end',
            'Fixation start',
            'Fixation end',
            'Blink start',
            'Blink end'
        ],
        'tooltip': 'An eye-tracker event to wait for'
    }
]

import os

# display
DISPTYPE = 'pygame'
DISPSIZE = (1920,1080)

# rumble on/off
RUMBLE = True

# we can only use the rumble function in Windows
if os.name != u'nt':
	RUMBLE = False
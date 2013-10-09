To run this example, you will need to install PyGaze's webcam library. To do so, follow these steps:


OPTION 1 (Windows only)

1) download the PyGaze WinPython mod from http://www.fss.uu.nl/psn/pygaze/downloads/WinPython-PyGaze-0.4.zip

2) unzip to a location of your choice

3) you will find this example in the WinPython-PyGaze-0.4/PyGaze_examples/show_webcam folder

4) doubleclick 'RUNME.bat'


OPTION 2 (all platforms)

1) download 'libwebcam.py' from https://github.com/esdalmaijer/PyGaze/tree/master/additional_libraries

2) copy 'libwebcam.py' to your PyGaze directory:
on Windows this usually is C:\Python27\Lib\site-packages\pygaze
on Linux it usually is /usr/lib/pymodules/python2.7/pygaze/

3) test if it works, by opening a Python Console and typing:
from pygaze import libwebcam

4) run this experiment in the way you would usually run a Python script, e.g.:

Windows: create a text file called 'RUNME.bat' (it now becomes a batch file),
right-click on it and click Edit; now type:
"C:\Python27\python.exe" "camtest.py"
save the file, close your text editor, then double-click RUNME.bat

Linux: open a terminal in this directory, type:
python camtest.py
and press Enter

Spyder (code editor that runs on any platform, see: http://code.google.com/p/spyderlib/)
open webcam.py, press F5 and choose whatever option you prefer (e.g. "Execute in a new dedicated
Python interpreter"), then click Run
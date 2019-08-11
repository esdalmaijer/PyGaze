# PyAlea

Python wrapper for the IntelliGaze API by [Alea Technologies](https://www.intelligaze.com/en/), developed by [Dr Edwin Dalmaijer](https://github.com/esdalmaijer).

PyAlea is covered by the Apache v2.0 license. The original repository can be found on [GitHub](https://github.com/esdalmaijer/PyAlea). This module was copied into PyGaze on 2018-08-11 without modifications.

## C API

Alea offers an API to interact with their eye trackers. This API operates through COM, and is less straightforward to wrap in Python. (While technically possible, it requires external packages, and jumping through several hoops.) An easier solution was to introduce a C++ wrapper for the API, which is then compiled as a DLL. The resulting DLL is more easily accessed through Python's `ctypes`.

The source code for this "C API" wrapper for the original API is included here.

## Download and install

PyAlea is available via the Python Package Index (PyPI), and can be installed through `pip`.

```
pip install python-alea
```

## Usage

After installation, you can import the Alea package into your Python script:

```
import alea
```

### Recording data to file

You can then use the AleaTracker class for quick and easy interfacing with your eye tracker. For example, the following script initialises a connection with the IntelliGaze Server, calibrates the eye tracker, and records 10 seconds of data into a text file.

```python
import time
from alea import AleaTracker

# Initialise the connection to the IntelliGaze Server,
# using the PyGaze alea code.
tracker = AleaTracker("pg=12", file_path="my_data.tsv")

# Calibrate the eye tracker, using the default options.
tracker.calibrate()

# Start recording to file.
tracker.start_recording()
# Log a message to the data file.
tracker.log("recording_started")

# Wait for 10 seconds.
time.sleep(10.0)

# Stop recording.
tracker.stop_recording()

# Close the connection to the eye tracker.
tracker.close()
```

### Streaming samples for gaze-contingent functionality

You can use AleaTracker's `sample` method to obtain the corrent gaze coordinates, as well as the current pupil size. While a connection is open, this will always return the latest available sample.

**NOTE: You do not have to be recording to use the `sample` method, and using the `sample` method does not affect recording. You can do both at the same time, but you don't have to.**

```python
import time
from alea import AleaTracker

# Initialise the connection to the IntelliGaze Server,
# using the PyGaze alea code.
tracker = AleaTracker("pg=12", file_path="my_data.tsv")

# Calibrate the eye tracker, using the default options.
tracker.calibrate()

# Run for 10 seconds.
t0 = time.time()
while time.time() - t0 < 10.0:
    # Get the latest sample
    time_stamp, gaze_x, gaze_y, pupil_size = tracker.sample()
    # Print the current sample to the terminal.
    print("t=%.3f, x=%.2f, y=%.2f, s=%.2f" % (time_stamp, gaze_x, gaze_y, pupil_size))
    # Wait for 33 milliseconds.
    time.sleep(0.033)

# Close the connection to the eye tracker.
tracker.close()
```

## Troubleshooting

* Make sure the IntelliGaze Server is running! Without it, the Python wrapper will have nothing to talk to.
* Make sure you install the IntelliGaze Server! You can download it from the IntelliGaze by [Alea Technologies website](https://www.intelligaze.com/en/support/download).
* Make sure that you are running a Microsoft Windows operating system (tested on Windows 7 and 10). Linux and OS X support is not currently available.


alea_import = True

try:
    from pygaze._eyetracker.alea.alea import *
except:
    try:
        from alea import *
    except:
        alea_import = False

if not alea_import:
    print("pygaze._eyetracker.alea.__init__: Could not import PyGaze or local version of Alea.")

__version__ = "0.0.8"

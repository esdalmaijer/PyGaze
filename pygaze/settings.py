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

from pygaze.py3compat import *

class Settings(object):
    
    def __init__(self):
        
        object.__setattr__(self, u'config', {u'cfg_ver' : 0})
        from pygaze import defaults
        self.read_module(defaults)
        try:
            import constants
            self.read_module(constants)
        except:
            pass
            
    def read_module(self, mod):
        
        for key in dir(mod):
            if key.startswith(u'__') and key.endswith(u'__'):
                continue
            if not hasattr(mod, key):
                continue
            val = getattr(mod, key)
            if val is not None and type(val) not in \
                [tuple, list, int, float, str, bytes, bool]:
                continue
            self.config[key] = val
            
    def __getattr__(self, setting):

        if setting not in self.config:
            raise Exception(u'The setting "%s" does not exist' % setting)
        return self.config[setting]

    def __setattr__(self, setting, value):

        self.config[setting] = value
        self.config[u'cfg_ver'] += 1
            
settings = Settings()
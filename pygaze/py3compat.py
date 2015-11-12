#-*- coding:utf-8 -*-

"""
This file is part of OpenSesame.

OpenSesame is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

OpenSesame is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with OpenSesame.  If not, see <http://www.gnu.org/licenses/>.
"""

import sys

if sys.version_info >= (3,0,0):
	py3 = True
	basestring = str
	universal_newline_mode = u'r'
else:
	bytes = str
	str = unicode
	py3 = False
	universal_newline_mode = u'rU'

def safe_decode(s, enc='utf-8', errors='strict'):
	if isinstance(s, str):
		return s
	if isinstance(s, bytes):
		return s.decode(enc, errors)
	# Numeric values are encoded right away
	if isinstance(s, int) or isinstance(s, float):
		return str(s)
	# Some types need to be converted to unicode, but require the encoding
	# and errors parameters. Notable examples are Exceptions, which have
	# strange characters under some locales, such as French. It even appears
	# that, at least in some cases, they have to be encodeed to str first.
	# Presumably, there is a better way to do this, but for now this at
	# least gives sensible results.
	try:
		return safe_decode(bytes(s), enc=enc, errors=errors)
	except:
		pass
	# For other types, the unicode representation doesn't require a specific
	# encoding. This mostly applies to non-stringy things, such as integers.
	return str(s)

def safe_encode(s, enc='utf-8', errors='strict'):
	if isinstance(s, bytes):
		return s
	return s.encode(enc, errors)

if py3:
	safe_str = safe_decode
else:
	safe_str = safe_encode

__all__ = ['py3', 'safe_decode', 'safe_encode', 'safe_str',
	'universal_newline_mode']
if not py3:
	__all__ += ['str', 'bytes']
else:
	__all__ += ['basestring']

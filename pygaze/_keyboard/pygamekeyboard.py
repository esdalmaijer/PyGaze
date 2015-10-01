# -*- coding: utf-8 -*-
from pygaze.libtime import clock
from pygaze.defaults import *
try:
    from constants import *
except Exception:
    pass

from pygaze._keyboard.basekeyboard import BaseKeyboard
# we try importing the copy_docstr function, but as we do not really need it
# for a proper functioning of the code, we simply ignore it when it fails to
# be imported correctly
try:
    from pygaze._misc.misc import copy_docstr
except Exception:
    pass

import pygaze
import pygame

class PyGameKeyboard(BaseKeyboard):

    # See _keyboard.basekeyboard.BaseKeyboard

    import pygame.key

    def __init__(self, keylist=KEYLIST, timeout=KEYTIMEOUT):

        # See _keyboard.basekeyboard.BaseKeyboard

        # try to copy docstring (but ignore it if it fails, as we do
        # not need it for actual functioning of the code)
        try:
            copy_docstr(BaseKeyboard, PyGameKeyboard)
        except Exception:
            # we're not even going to show a warning, since the copied
            # docstring is useful for code editors; these load the docs
            # in a non-verbose manner, so warning messages would be lost
            pass

        # dictionary for keynames and codes
        self.key_codes = {}
        for i in dir(pygame):
            if i[:2] == "K_":
                code = eval("pygame.%s" % i)
                name1 = pygame.key.name(code).lower()
                name2 = name1.upper()
                name3 = i[2:].lower()
                name4 = name3.upper()
                self.key_codes[name1] = code
                self.key_codes[name2] = code
                self.key_codes[name3] = code
                self.key_codes[name4] = code

        # set keyboard characteristics
        self.set_keylist(keylist)
        self.set_timeout(timeout)

    def set_keylist(self, keylist=None):

        # See _keyboard.basekeyboard.BaseKeyboard

        if keylist == None or keylist == []:
            self.klist = None
        else:
            self.klist = []
            for key in keylist:
                self.klist.append(key)


    def set_timeout(self, timeout=None):

        # See _keyboard.basekeyboard.BaseKeyboard

        self.timeout = timeout


    def get_key(self, keylist='default', timeout='default', flush=False):

        # See _keyboard.basekeyboard.BaseKeyboard

        # set keylist and timeout
        if keylist == 'default':
            keylist = self.klist
        if timeout == 'default':
            timeout = self.timeout

        # flush if necessary
        if flush:
            pygame.event.get(pygame.KEYDOWN)

        # starttime
        starttime = clock.get_time()
        time = clock.get_time()

        # wait for input
        while timeout == None or time - starttime <= timeout:
            time = clock.get_time()
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    time = clock.get_time()
                    key = pygame.key.name(event.key)
                    if keylist == None or key in keylist:
                        return key, time

        # in case of timeout
        return None, time

## This file is part of the Gaze Contingent Extension for Python
##
##    PyGACE is a Python module for easily creating gaze contingent experiments
##    or other software (as well as non-gaze contingent experiments/software)
##    Copyright (C) 2012-2013  Edwin S. Dalmaijer
##
##    This program is free software: you can redistribute it and/or modify
##    it under the terms of the GNU General Public License as published by
##    the Free Software Foundation, either version 3 of the License, or
##    (at your option) any later version.
##
##    This program is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.
##
##    You should have received a copy of the GNU General Public License
##    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
# version: 0.4 (25-03-2013), NOT RELEASED FOR USE OUTSIDE OF UTRECHT UNIVERSITY)


try:
    import constants
except:
    import defaults as constants

import libtime

import copy
import random

try:
    import psychopy
    from psychopy.visual import Window
    from psychopy.visual import GratingStim
    from psychopy.visual import Circle
    from psychopy.visual import Line
    from psychopy.visual import ShapeStim
    from psychopy.visual import TextStim
except:
    if constants.DISPTYPE == 'psychopy':
        print("Error in libscreen: PsychoPy could not be loaded!")

try:
    import pygame
    import pygame.display
    import pygame.draw
except:
    if constants.DISPTYPE == 'pygame':
        print("Error in libscreen: PyGame could not be loaded!")
        
global expdisplay


class Display:

    """A class for Display objects, to present Screen objects on a monitor"""

    def __init__(self, disptype=constants.DISPTYPE, dispsize=constants.DISPSIZE, fgc=constants.FGC, bgc=constants.BGC, screennr=constants.SCREENNR, screen=None):

        """
        Initializes the Display object

        Keyword arguments:
        disptype    -- type of display: either 'pygame' or 'psychopy'
        dispsize    -- size of the display in pixels: a (width, height) tuple
        fgc         -- the foreground colour: a colour name (e.g. 'red') or a RGB(A) tuple (e.g. 255,0,0(,255))
        bgc         -- the background colour: a colour name (e.g. 'red') or a RGB(A) tuple (e.g. 255,0,0(,255))
        screennr    -- the screen number: 0, 1 etc.
        screen      -- a Screen object to be presented on the Display (default=None)
        """

        global expdisplay

        self.dispsize = dispsize
        self.fgc = fgc
        self.bgc = bgc
        self.screennr = screennr
        self.mousevis = False

        if disptype in ['pygame','psychopy']:
            self.disptype = disptype
        else:
            self.disptype = 'pygame'
            print("Error in libscreen.Display.__init__: disptype not recognized; set to default ('pygame')")

        # pygame
        if self.disptype == 'pygame':
            # initialize PyGame display-module
            pygame.display.init()
            # make mouse invisible (should be so per default, but you never know)
            pygame.mouse.set_visible(self.mousevis)
            # create surface for full screen displaying
            expdisplay = pygame.display.set_mode(self.dispsize,pygame.FULLSCREEN|pygame.HWSURFACE|pygame.DOUBLEBUF)

            # blit screen to display surface (if user entered one)
            if screen:
                expdisplay.blit(screen.screen,(0,0))
            else:
                expdisplay.fill(self.bgc)

        # psychopy
        elif self.disptype == 'psychopy':
            # create window
            expdisplay = Window(size=self.dispsize, pos=None, color=rgb2psychorgb(self.bgc), colorSpace='rgb', fullscr=True, screen=self.screennr, units='pix')
            # set mouse visibility
            expdisplay.setMouseVisible(self.mousevis)
            # get screen in window
            if screen:
                for s in screen.screen:
                    s.draw()

        # display
        self.expdisplay = expdisplay
        
        # functions
        if self.disptype == 'pygame':
            self.showfunc = pygame.display.flip
        elif self.disptype == 'psychopy':
            self.showfunc = self.expdisplay.flip


    def show(self):

        """Updates ('flips') the display surface"""

        self.showfunc()
        return libtime.get_time()


    def show_part(self, rect, screen=None):

        """Updates part(s) of the screen to given surface part (rect can be a single rect or a list of rects)"""

        if self.disptype == 'pygame':
            if len(rect) > 1:
                for r in rect:
                    expdisplay.set_clip(r)
                    if screen:
                        self.expdisplay.blit(screen.screen, (0,0))
                    pygame.display.update(r)
                    self.expdisplay.set_clip(None)
                    
            elif len(rect) == 1:
                self.expdisplay.clip(rect)
                if surface:
                    self.expdisplay.blit(screen.screen, (0,0))
                pygame.display.update(rect)
                self.expdisplay.set_clip(None)

            else:
                print("Error in libscreen.Display.show_part: rect should be a single rect (i.e. a (x,y,w,h) tuple) or a list of rects!")

        elif self.disptype == 'psychopy':
            self.show()
            print("Display.show_part not available for psychopy display type; show is used instead")


    def fill(self, screen=None):

        """Fills the screen with the background colour or the specified screen"""

        if self.disptype == 'pygame':
            self.expdisplay.fill(self.bgc)
            if screen != None:
                self.expdisplay.blit(screen.screen,(0,0))

        elif self.disptype == 'psychopy':
            self.expdisplay.clearBuffer()
            if screen != None:
                for s in screen.screen:
                    s.draw()


    def close(self):

        """Closes the display"""

        if self.disptype == 'pygame':
            pygame.display.quit()
            
        elif self.disptype == 'psychopy':
            self.expdisplay.close()


class Screen:

    """A class for Screen objects, for visual stimuli (to be displayed via a Display object)"""

    def __init__(self, disptype=constants.DISPTYPE, dispsize=constants.DISPSIZE, fgc=constants.FGC, bgc=constants.BGC, screennr=constants.SCREENNR, mousevisible=constants.MOUSEVISIBLE, screen=None):

        """Initializes the Screen object"""

        # properties
        self.dispsize = dispsize
        self.fgc = fgc
        self.bgc = bgc
        self.screennr = screennr
        self.mousevis = mousevisible

        if disptype in ['pygame','psychopy']:
            self.disptype = disptype
        else:
            self.disptype = 'pygame'
            print("Error in libscreen.Screen.__init__: disptype not recognized; set to default ('pygame')")

        if self.disptype == 'pygame':
            self.__class__ = PyGameScreen
        elif self.disptype == 'psychopy':
            self.__class__ = PsychoPyScreen
        else:
            self.__class__ = PyGameScreen
            print("Error in libscreen.Screen.__init__: self.disptype was not recognized, which is very unexpected and should not happen! PyGameScreen is used")

        # create screen
        self.create(screen=screen)


class PyGameScreen:

    """A class for PyGame Screen objects, for visual stimuli (to be displayed via a Display object)"""

    def create(self, screen=None):

        """Returns a screen for the display (optionally filled with a screen entered by user)"""

        self.screen = pygame.Surface(self.dispsize)
        self.screen.fill(self.bgc)

        if screen != None:
            self.screen.blit(screen,(0,0))


    def clear(self, colour=None):

        """Clears the screen and fill it with a colour (default=backgroun colour)"""

        if colour == None:
            colour = self.bgc
        
        self.screen.fill(colour)


    def copy(self, screen):

        """Copies a screen to the current screen"""

        self.screen = copy.copy(screen.screen)
            

    def draw_circle(self, colour=None, pos=None, r=50, pw=1, fill=False):

        """Draws a circle on the screen"""

        if colour == None:
            colour = self.fgc
        if pos == None:
            pos = (self.dispsize[0]/2, self.dispsize[1]/2)
        if fill == True:
            pw = 0

        pygame.draw.circle(self.screen, colour, pos, r, pw)
        

    def draw_ellipse(self, colour=None, x=None, y=None, w=50, h=50, pw=1, fill=False):

        """Draws a rectangle on the screen"""

        if colour == None:
            colour = self.fgc
        if x == None:
            x = self.dispsize[0]/2
        if y == None:
            y = self.dispsize[1]/2
        if fill == True:
            pw = 0

        pygame.draw.ellipse(self.screen, colour, [x,y,w,h], pw)

        
    def draw_rect(self, colour=None, x=None, y=None, w=50, h=50, pw=1, fill=False):

        """Draws a rectangle on the screen"""

        if colour == None:
            colour = self.fgc
        if x == None:
            x = self.dispsize[0]/2
        if y == None:
            y = self.dispsize[1]/2
        if fill == True:
            pw = 0

        pygame.draw.rect(self.screen, colour, [x,y,w,h], pw)

    def draw_line(self, colour=None, spos=None, epos=None, pw=1):

        """Draws a line on the screen"""

        if colour == None:
            colour = self.fgc
        if spos == None:
            spos = (int(self.dispsize[0]*0.25), self.dispsize[1]/2)
        if epos == None:
            epos = (int(self.dispsize[0]*0.75), self.dispsize[1]/2)

        pygame.draw.line(self.screen, colour, spos, epos, pw)


    def draw_polygon(self, pointlist, colour=None, pw=1, fill=True):

        """Draws a polygon on the screen"""

        if colour == None:
            colour = self.fgc
        if fill == True:
            pw = 0

        pygame.draw.polygon(self.screen, colour, pointlist, pw)


    def draw_fixation(self, fixtype='cross', colour=None, pos=None, pw=1, diameter=12):

        """Draws a fixation cross or dot on the screen"""

        if fixtype not in ['cross','dot']:
            fixtype == 'cross'
            print("Error in libscreen.Screen.draw_fixation: fixtype not recognized; fixtype set to default ('cross')")
        if colour == None:
            colour = self.fgc
        if pos == None:
            pos = (self.dispsize[0]/2, self.dispsize[1]/2)

        if fixtype == 'cross':
            pygame.draw.line(self.screen, colour, (pos[0]-diameter/2, pos[1]), (pos[0]+diameter/2, pos[1]), pw)
            pygame.draw.line(self.screen, colour, (pos[0], pos[1]-diameter/2), (pos[0], pos[1]+diameter/2), pw)
        elif fixtype == 'dot':
            pygame.draw.circle(self.screen, colour, pos, diameter/2, 0)


    def draw_text(self, text='', colour=None, pos=None):

        """Draws a text on the screen"""

        if colour == None:
            colour = self.fgc
        if pos == None:
            pos = (self.dispsize[0]/2, self.dispsize[1]/2)

        print("Error in libscreen.Screen.draw_text: function not supported yet")


    def set_background_colour(self, colour=None):

        """Set the background colour to colour"""

        if colour != None:
            self.bgc = colour


class PsychoPyScreen:

    """A class for PsychoPy Screen objects, for visual stimuli (to be displayed via a Display object)"""

    def create(self, screen=None):

        """Returns a screen for the display (optionally filled with a screen entered by user)"""

        self.screen = []

        if screen != None:
            self.clear()
            self.copy(screen)


    def clear(self, colour=None):

        """Clears the screen and fill it with a colour (default=backgroun colour)"""

        if colour == None:
            colour = self.bgc
        
        self.screen = []
        self.draw_rect(colour=colour, x=0, y=0, w=self.dispsize[0], h=self.dispsize[1], fill=True)


    def copy(self, screen):

        """Copies a screen to the current screen"""

        self.screen = copy.copy(screen.screen)
            

    def draw_circle(self, colour=None, pos=None, r=50, pw=1, fill=False):

        """Draws a circle on the screen"""

        if colour == None:
            colour = self.fgc
        if pos == None:
            pos = (self.dispsize[0]/2, self.dispsize[1]/2)

        colour = rgb2psychorgb(colour)
        pos = pos2psychopos(pos,dispsize=self.dispsize)

        if fill:
            self.screen.append(Circle(expdisplay, radius=r, edges=32, pos=pos, lineColor=colour, lineColorSpace='rgb', fillColor=colour, fillColorSpace='rgb'))
        else:
#            self.screen.append(Circle(expdisplay, radius=r-pw, edges=32, pos=pos, lineColor=colour, lineColorSpace='rgb', fillColor=rgb2psychorgb(self.bgc), fillColorSpace='rgb'))
            self.screen.append(Circle(expdisplay, radius=r-pw, edges=32, pos=pos, lineColor=colour, lineColorSpace='rgb'))
        

    def draw_ellipse(self, colour=None, x=None, y=None, w=50, h=50, pw=1, fill=False):

        """Draws a rectangle on the screen"""

        if colour == None:
            colour = self.fgc
        if x == None:
            x = 0
        if y == None:
            y = 0

        pos = x,y
        colour = rgb2psychorgb(colour)
        pos = pos2psychopos(pos,dispsize=self.dispsize)
        pos = pos[0] + w/2, pos[1] - h/2

        self.screen.append(GratingStim(expdisplay, tex=None, mask="circle", pos=pos, size=(w,h), color=colour))
        if not fill:
            self.screen.append(GratingStim(expdisplay, tex=None, mask="circle", pos=pos, size=(w-2*pw,h-2*pw), color=rgb2psychorgb(self.bgc)))

        
    def draw_rect(self, colour=None, x=None, y=None, w=50, h=50, pw=1, fill=False):

        """Draws a rectangle on the screen"""

        if colour == None:
            colour = self.fgc
        if x == None:
            x = self.dispsize[0]/2
        if y == None:
            y = self.dispsize[1]/2

        pos = x,y
        colour = rgb2psychorgb(colour)
        pos = pos2psychopos(pos,dispsize=self.dispsize)
        pos = pos[0] + w/2, pos[1] - h/2

        self.screen.append(GratingStim(expdisplay, tex=None, mask=None, pos=pos, size=[w,h], color=colour))
        if not fill:
            self.screen.append(GratingStim(expdisplay, tex=None, mask=None, pos=pos, size=[w-2,h-2], color=rgb2psychorgb(self.bgc)))


    def draw_line(self, colour=None, spos=None, epos=None, pw=1):

        """Draws a line on the screen"""

        if colour == None:
            colour = self.fgc
        if spos == None:
            spos = (int(self.dispsize[0]*0.25), self.dispsize[1]/2)
        if epos == None:
            epos = (int(self.dispsize[0]*0.75), self.dispsize[1]/2)

        colour = rgb2psychorgb(colour)
        spos = pos2psychopos(spos,dispsize=self.dispsize)
        epos = pos2psychopos(epos,dispsize=self.dispsize)
        
        self.screen.append(Line(expdisplay, start=spos, end=epos, lineColor=colour, lineColorSpace='rgb', lineWidth=pw))


    def draw_polygon(self, pointlist, colour=None, pw=1, fill=True):

        """Draws a polygon on the screen"""

        if colour == None:
            colour = self.fgc

        colour = rgb2psychorgb(colour)
        pl = []
        for pos in pointlist:
            pl.append(pos2psychopos(pos,dispsize=self.dispsize))

        if fill:
            self.screen.append(ShapeStim(expdisplay, lineWidth=pw, lineColor=colour, lineColorSpace='rgb', fillColor=colour, fillColorSpace='rgb',vertices=pointlist, closeShape=True))
        else:
            self.screen.append(ShapeStim(expdisplay, lineWidth=pw, lineColor=colour, lineColorSpace='rgb', fillColor=rgb2psychorgb(self.bgc), fillColorSpace='rgb',vertices=pointlist, closeShape=True))

            
    def draw_fixation(self, fixtype='cross', colour=None, pos=None, pw=1, diameter=12):

        """Draws a fixation cross or dot on the screen"""

        if fixtype not in ['cross','dot']:
            fixtype == 'cross'
            print("Error in libscreen.Screen.draw_fixation: fixtype not recognized; fixtype set to default ('cross')")
        if colour == None:
            colour = self.fgc
        if pos == None:
            pos = (self.dispsize[0]/2, self.dispsize[1]/2)

        if fixtype == 'cross':
            self.draw_line(colour=colour, spos=(pos[0]-diameter/2, pos[1]), epos=(pos[0]+diameter/2, pos[1]), pw=pw)
            self.draw_line(colour=colour, spos=(pos[0], pos[1]+diameter/2), epos=(pos[0], pos[1]-diameter/2), pw=pw)
        elif fixtype == 'dot':
            self.draw_circle(colour=colour, pos=pos, r=diameter/2, pw=0, fill=True)


    def draw_text(self, text='text', colour=None, pos=None):

        """Draws a text on the screen"""

        if colour == None:
            colour = self.fgc
        if pos == None:
            pos = (self.dispsize[0]/2, self.dispsize[1]/2)

        colour = rgb2psychorgb(colour)
        pos = pos2psychopos(pos,dispsize=self.dispsize)

        self.screen.append(TextStim(expdisplay, text=str(text), pos=pos, color=colour))


    def set_background_colour(self, colour=None):

        """Set the background colour to colour"""

        if colour != None:
            self.bgc = colour


# # # # # # #
# functions #
# # # # # # #

def pos2psychopos(pos, dispsize=None):

    """Returns a converted position tuple (x,y)"""

    if dispsize == None:
        dispsize = tuple(psychopy.visual.openWindows[constants.SCREENNR].size)

    x = pos[0] - dispsize[0]/2
    y = (pos[1] - dispsize[1]/2) * -1

    return (x,y)


def psychopos2pos(pos, dispsize=None):

    """Returns a converted position tuple (x,y)"""

    if dispsize == None:
        dispsize = tuple(psychopy.visual.openWindows[constants.SCREENNR].size)

    x = pos[0] + dispsize[0]/2
    y = (pos[1] * -1) + dispsize[1]/2

    return (x,y)


def rgb2psychorgb(rgbgun):

    """Returns a converted RGB gun (from values between 0 and 255 to values between -1 and 1)"""

    psyrgb = []

    for val in rgbgun:
        psyrgb.append((val/127.5)-1)

    return tuple(psyrgb)

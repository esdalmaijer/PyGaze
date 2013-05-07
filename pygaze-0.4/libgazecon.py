## This file is part of PyGaze - the open-source toolbox for eye tracking
##
##    PyGaze is a Python module for easily creating gaze contingent experiments
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
# version: 0.3 (20-03-2013)



try:
    import constants
except:
    import defaults as constants

try:
    import psychopy
    from psychopy.visual import Aperture
except:
    if constants.DISPTYPE == 'psychopy':
        print("Error in libgazecon: PsychoPy could not be loaded!")

try:
    import pygame
    import pygame.display
    import pygame.draw
except:
    if constants.DISPTYPE == 'pygame':
        print("Error in libgazecon: PyGame could not be loaded!")

from libscreen import pos2psychopos, psychopos2pos

class FRL:
    
    """Gaze contingent FRL"""
    
    def __init__(self, disptype=constants.DISPTYPE, pos=constants.FRLPOS, dist=constants.FRLDIST, size=constants.FRLSIZE):

        """Initializes FRL object (pos: FRL position in relation to gaze position; dist: FRL distance in pixels; size: FRL size in pixels)"""

        # FRL characteristics
        self.pos = pos
        self.dist = dist
        self.size = size

        # FRL distance
        self.frlxdis = ((constants.FRLDIST**2)/2)**0.5 # horizontal distance between mouse position and FRL-centre
        self.frlydis = ((constants.FRLDIST**2)/2)**0.5 # vertical distance between mouse position and FRL-centre
        # FRL position
        if pos == 'center':
            self.frlcor = (0, 0)
        elif pos == 'top':
            self.frlcor = (0, -constants.FRLDIST)
        elif pos == 'topright':
            self.frlcor = (-self.frlxdis, self.frlydis)
        elif pos == 'right':
            self.frlcor = (constants.FRLDIST, 0)
        elif pos == 'bottomright':
            self.frlcor = (-self.frlxdis, -self.frlydis)
        elif pos == 'bottom':
            self.frlcor = (0, constants.FRLDIST)
        elif pos == 'bottomleft':
            self.frlcor = (self.frlxdis, -self.frlydis)
        elif pos == 'left':
            self.frlcor = (-constants.FRLDIST, 0)
        elif pos == 'topleft':
            self.frlcor = (self.frlxdis, self.frlydis)
        else:
            print("ERROR! FRL position argument (in constants) not recognized.")
            print("FRL position set to center.")
            self.frlcor = (0, 0)

        if disptype in ['pygame','psychopy']:
            self.disptype = disptype
        else:
            self.disptype = 'pygame'
            print("Error in libgazecon.FRL.__init__: disptype not recognized; set to default ('pygame')")

        if self.disptype == 'pygame':
            self.__class__ = PyGameFRL
        elif self.disptype == 'psychopy':
            self.__class__ = PsychoPyFRL
            self.frl = Aperture(psychopy.visual.openWindows[constants.SCREENNR], self.size, pos=pos2psychopos(self.frlcor), shape='circle', units='pix')
        else:
            self.__class__ = PyGameFRL
            print("Error in libgazecon.FRL.__init__: self.disptype was not recognized, which is very unexpected and should not happen! PyGameFRL is used")


class PyGameFRL:

    """Gaze contingent FRL based on PyGame"""
    
    def get_pos(self, gazepos):
        
        """Returns FRL position tuple, based on gaze position (x,y)"""

        return (gazepos[0]-self.frlcor[0], gazepos[1]-self.frlcor[1])


    def update(self, display, stimscreen, gazepos):

        """Returns display with FRL, showing stimulus screen inside of FRL and mask screen everywhere else"""

        # frl position
        frlpos = self.get_pos(gazepos)

        # reset display surface
        display.fill()
        
        # draw new FRL
        updaterects = []
        r = self.size/2
        h = 1 # pixel, updaterectheight (FRL actually consists of a stack of rectangles, h is the height of an individual rectangle)
        # top side
        for y in range(0,r):
            # right end of rectangle
            y = r - y # reverse y
            x = (r**2-y**2)**0.5
            # rectangle coordinates
            updaterect = [frlpos[0]-x,frlpos[1]-h*y,2*x,h]
            # update screen part
            display.expdisplay.set_clip(updaterect)
            display.expdisplay.blit(stimscreen.screen,(0,0))
        # bottom side
        for y in range(0,r+1):
            # right end of rectangle
            x = (r**2-y**2)**0.5
            # rectangle coordinates
            updaterect = [frlpos[0]-x,frlpos[1]+h*y,2*x,h]
            # update screen part
            display.expdisplay.set_clip(updaterect)
            display.expdisplay.blit(stimscreen.screen,(0,0))

        # unset clip and update display
        display.expdisplay.set_clip(None)
        display.show()


class PsychoPyFRL:

    """Gaze contingent FRL based on PyGame"""
    
    def get_pos(self, gazepos):
        
        """Returns FRL position tuple, based on gaze position (x,y)"""

        return gazepos[0]-self.frlcor[0], gazepos[1]-self.frlcor[1]


    def update(self, display, stimscreen, gazepos):

        """Updates the display with FRL, showing stimulus screen inside of FRL and mask screen everywhere else"""

        # FRL position
        frlpos = pos2psychopos(self.get_pos(gazepos))

        # set FRL
        self.frl.setPos(frlpos)
        self.frl.enable()

        # draw stimuli
        display.fill(stimscreen)

        # update screen
        display.show()

        # unset FRL
        self.frl.disable()

    
class Cursor:
    
    """Gaze contingent cursor"""

    def __init__(self, ctype=constants.CURSORTYPE, size=constants.CURSORSIZE, colour=constants.CURSORCOLOUR, fill=constants.CURSORFILL, penw=constants.CURSORPENWIDTH):

        """Initializes cursor object (ctype: cursor type; size: cursor size; pos: circle position in relation to gaze position)"""

        # cursor characteristics
        if ctype in ['rectangle', 'ellipse', 'plus', 'cross', 'arrow']:
            self.ctype = ctype
        else:
            self.ctype = 'arrow'
            print("Cursor type could not be recognized! Cursor type set to 'arrow'.")
            
        self.fill = fill
        self.penw= penw
        if fill:
            self.figpenw = 0
        else:
            self.figpenw = penw
        
        if type(size) == int:
            self.size = (size, size)
        elif type(size) == tuple or type(size) == list:
            if len(size) == 2:
                self.size = size
        else:
            self.size = (size[0], size[1])
            print("Too many entries for cursor size! Only the first two are used.")
            
        if type(colour) == tuple or type(colour) == list:
            if len(colour) == 3 or len(colour) == 4:
                self.colour = colour
            else:
                self.colour = colour[:4]
                print("Too many list entries for cursor colour! Only the first four are used.")
        else:
            if colour in pygame.colordict.THECOLORS:
                self.colour = pygame.colordict.THECOLORS[colour]
            else:
                self.colour = (0,0,0)
                print("Cursor colour could not be recognized! Cursor colour set to 'black'.")
            


    def update(self, screen, stimsurface, gazepos):

        """Returns display surface, showing a cursor on the gaze location"""

        # draw stimsurface to screen
        screen.blit(stimsurface,(0,0))
        # draw cursor
        if self.ctype == 'rectangle':
            pygame.draw.rect(screen, self.colour, [gazepos[0]-(self.size[0]/2), gazepos[1]-(self.size[1]/2), self.size[0], self.size[1]], self.figpenw)
        if self.ctype == 'ellipse':
            pygame.draw.ellipse(screen, self.colour, [gazepos[0]-(self.size[0]/2), gazepos[1]-(self.size[1]/2), self.size[0], self.size[1]], self.figpenw)
        if self.ctype == 'plus':
            pygame.draw.line(screen, self.colour, (gazepos[0]-(self.size[0]/2),gazepos[1]), (gazepos[0]+(self.size[0]/2),gazepos[1]), self.penw)
            pygame.draw.line(screen, self.colour, (gazepos[0],gazepos[1]-(self.size[1]/2)), (gazepos[0],gazepos[1]+(self.size[1]/2)), self.penw)
        if self.ctype == 'cross':
            pygame.draw.line(screen, self.colour, (gazepos[0]-(self.size[0]/2),gazepos[1]-(self.size[1]/2)), (gazepos[0]+(self.size[0]/2),gazepos[1]+(self.size[1]/2)), self.penw)
            pygame.draw.line(screen, self.colour, (gazepos[0]-(self.size[0]/2),gazepos[1]+(self.size[1]/2)), (gazepos[0]+(self.size[0]/2),gazepos[1]-(self.size[1]/2)), self.penw)
        if self.ctype == 'arrow':
            pygame.draw.polygon(screen, self.colour, [(gazepos[0]+self.size[0],gazepos[1]+(0.5*self.size[1])),(gazepos[0],gazepos[1]),(gazepos[0]+(0.5*self.size[0]),gazepos[1]+self.size[1])], self.figpenw)
            pygame.draw.line(screen, self.colour, (gazepos[0],gazepos[1]), (gazepos[0]+self.size[0],gazepos[1]+self.size[1]), self.penw)

        return screen


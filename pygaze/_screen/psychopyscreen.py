# -*- coding: utf-8 -*-
#
# This file is part of PyGaze - the open-source toolbox for eye tracking
#
#    PyGaze is a Python module for easily creating gaze contingent experiments
#    or other software (as well as non-gaze contingent experiments/software)
#    Copyright (C) 2012-2013  Edwin S. Dalmaijer
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>

from pygaze import settings
import pygaze
from pygaze._misc.misc import pos2psychopos, psychopos2pos, rgb2psychorgb

from pygaze._screen.basescreen import BaseScreen
# we try importing the copy_docstr function, but as we do not really need it
# for a proper functioning of the code, we simply ignore it when it fails to
# be imported correctly
try:
    from pygaze._misc.misc import copy_docstr
except:
    pass

import copy
import math
import os.path

import psychopy
from psychopy.visual import Circle
from psychopy.visual import Rect
from psychopy.visual import ShapeStim
from psychopy.visual import TextStim
from psychopy.visual import ImageStim
# Line seems to be broken; see PsychoPyScreen.draw_line below
#from psychopy.visual import Line

# try importing PIL
try:
    from PIL import Image
    pilimp = True
except:
    try:
        import Image
        pilimp = True
    except:
        pilimp = False
        print("pygaze.screen.psychopyscreen: PIL's Image class could not be loaded; image scaling with PsychoPy disptype is now impossible!")


class PsychoPyScreen(BaseScreen):

    """A class for PsychoPy Screen objects, for visual stimuli (to be displayed via a Display object)"""
    
    def __init__(self, dispsize=settings.DISPSIZE, fgc=settings.FGC,
        bgc=settings.BGC, screennr=settings.SCREENNR,
        mousevisible=settings.MOUSEVISIBLE, screen=None, **args):
        
        """
        Constructor.
        
        TODO: docstring
        """

        # try to copy docstring (but ignore it if it fails, as we do
        # not need it for actual functioning of the code)
        try:
            copy_docstr(BaseScreen, PsychoPyScreen)
        except:
            # we're not even going to show a warning, since the copied
            # docstring is useful for code editors; these load the docs
            # in a non-verbose manner, so warning messages would be lost
            pass
        
        self.dispsize = dispsize
        self.fgc = fgc
        self.bgc = bgc
        self.screennr = screennr
        self.mousevis = mousevisible
        self.create(screen=screen)

    def create(self, screen=None):

        """Creates a new Screen object, filled with either the background
        colour or specified screen
        
        arguments
        None
        
        keyword arguments
        screen    -- a libscreen.Screen object, to be displayed on the
                   new screen or None for the background colour
        returns
        Nothing    -- sets the self.screen property to a PyGame Surface
                   or a list of PsychoPy stimuli, depening on the
                   disptype
        """

        self.screen = []
        self.clear()
        if screen != None:
            self.copy(screen)

    def clear(self, colour=None, color=None):

        """Clears the screen and fills it with a colour
        
        arguments
        None
        
        keyword arguments
        colour    -- the colour to fill the screen with (a colour name
                   (e.g. 'red') or a RGB(A) tuple (e.g. (255,0,0) or 
                   (255,0,0,255))) or None for the default background
                   colour, self.bgc (default = None)
        
        returns
        Nothing    -- clears self.screen property
        """

        if color is None and colour is None:
            pass
        elif color is None and colour is not None:
            pass
        elif color is not None and colour is None:
            colour = color
        elif colour != color:
            raise Exception("The arguments 'color' and 'colour' are the same, but set to different values: color={}, colour={}".format(color,colour))
            
        if colour == None:
            colour = self.bgc
        
        self.screen = []
        self.draw_rect(colour=colour, x=0, y=0, w=self.dispsize[0], \
            h=self.dispsize[1], fill=True)


    def copy(self, screen):

        """Copies a screen to the current screen
        
        arguments
        screen    -- a libscreen.Screen object
        
        returns
        Nothing    -- sets the self.screen property to a copy of
                   screen.screen
        """

        self.screen = copy.copy(screen.screen)
            

    def draw_circle(self, colour=None, color=None, pos=None, r=50, pw=1, \
        fill=False):

        """Draws a circle on the screen
        
        arguments
        None
        
        keyword arguments
        colour    -- colour for the circle (a colour name (e.g. 'red') or
                   a RGB(A) tuple (e.g. (255,0,0) or (255,0,0,255))) or
                   None for the default foreground colour, self.fgc
                   (default = None)
        pos        -- circle center, an (x,y) position tuple or None for a
                   central position (default = None)
        r        -- circle radius (default = 50)
        pw        -- penwidth: circle line thickness (default = 1)
        fill        -- Boolean indicating whether circle should be filled or
                   not (default = False)
        
        returns
        Nothing    -- draws a circle on (PyGame) or adds a Circle stimulus
                   to (PsychoPy) the self.screen property
        """
        
        if color is None and colour is None:
            pass
        elif color is None and colour is not None:
            pass
        elif color is not None and colour is None:
            colour = color
        elif colour != color:
            raise Exception("The arguments 'color' and 'colour' are the same, but set to different values: color={}, colour={}".format(color,colour))

        if colour is None:
            colour = self.fgc
        if pos is None:
            pos = (self.dispsize[0]/2, self.dispsize[1]/2)

        colour = rgb2psychorgb(colour)
        pos = pos2psychopos(pos,dispsize=self.dispsize)

        if fill:
            self.screen.append(Circle(pygaze.expdisplay, radius=r, edges=32, \
                pos=pos, lineWidth=pw, lineColor=colour, \
                lineColorSpace='rgb', fillColor=colour, fillColorSpace='rgb'))
        else:
            self.screen.append(Circle(pygaze.expdisplay, radius=r-pw, \
                edges=32, pos=pos, lineWidth=pw, lineColor=colour, \
                lineColorSpace='rgb'))
        

    def draw_ellipse(self, colour=None, color=None, x=None, y=None, w=50, \
        h=50, pw=1, fill=False):

        """Draws an ellipse on the screen
        
        arguments
        None
        
        keyword arguments
        colour    -- colour for the circle (a colour name (e.g. 'red') or
                   a RGB(A) tuple (e.g. (255,0,0) or (255,0,0,255))) or
                   None for the default foreground colour, self.fgc
                   (default = None)
        x        -- x coordinate of the rectangle in which the ellipse is
                   drawn or None for a horizontal centrally drawn
                   ellipse (default = None)
        y        -- y coordinate of the rectangle in which the ellipse is
                   drawn or None for a vertical centrally drawn
                   ellipse (default = None)
        w        -- width of the rectangle in which the ellipse is drawn
                   (default = 50)
        h        -- height of the rectangle in which the ellipse is drawn
                   (default = 50)
        pw        -- penwidth: circle line thickness (default = 1)
        fill        -- Boolean indicating whether ellipse should be filled
                   or not (default = False)
        
        returns
        Nothing    -- draws an ellipse on (PyGame) or adds a GratinsStim
                   stimulus to (PsychoPy) the self.screen property
        """

        if color is None and colour is None:
            pass
        elif color is None and colour is not None:
            pass
        elif color is not None and colour is None:
            colour = color
        elif colour != color:
            raise Exception("The arguments 'color' and 'colour' are the same, but set to different values: color={}, colour={}".format(color,colour))

        if colour is None:
            colour = self.fgc
        if x is None:
            x = 0
        if y is None:
            y = 0

        pos = x,y
        colour = rgb2psychorgb(colour)
        pos = pos2psychopos(pos,dispsize=self.dispsize)
        pos = pos[0] + w/2, pos[1] - h/2

        if fill:
            self.screen.append(Circle(pygaze.expdisplay, lineWidth=pw, \
                lineColor=colour, lineColorSpace='rgb', fillColor=colour, \
                fillColorSpace='rgb', pos=pos, size=(w,h)))
        else:
            self.screen.append(Circle(pygaze.expdisplay, lineWidth=pw, \
                lineColor=colour, lineColorSpace='rgb', fillColor=None, \
                pos=pos, size=(w,h)))

        
    def draw_rect(self, colour=None, color=None, x=None, y=None, w=50, h=50, \
        pw=1, fill=False):

        """Draws a rectangle on the screen
        
        arguments
        None
        
        keyword arguments
        colour    -- colour for the circle (a colour name (e.g. 'red') or
                   a RGB(A) tuple (e.g. (255,0,0) or (255,0,0,255))) or
                   None for the default foreground colour, self.fgc
                   (default = None)
        x        -- x coordinate of the rectangle or None for a
                   horizontal centrally drawn rectangle (default = None)
        y        -- y coordinate of the rectangle or None for a
                   vertical centrally drawn rectangle (default = None)
        w        -- width of the rectangle (default = 50)
        h        -- height of the rectangle (default = 50)
        pw        -- penwidth: ellipse line thickness (default = 1)
        fill        -- Boolean indicating whether rectangle should be filled
                   or not (default = False)
        
        returns
        Nothing    -- draws a rectangle on (PyGame) or adds a GratinsStim
                   stimulus to (PsychoPy) the self.screen property
        """

        if color is None and colour is None:
            pass
        elif color is None and colour is not None:
            pass
        elif color is not None and colour is None:
            colour = color
        elif colour != color:
            raise Exception("The arguments 'color' and 'colour' are the same, but set to different values: color={}, colour={}".format(color,colour))

        if colour is None:
            colour = self.fgc
        if x is None:
            x = self.dispsize[0]/2
        if y is None:
            y = self.dispsize[1]/2

        pos = x,y
        colour = rgb2psychorgb(colour)
        pos = pos2psychopos(pos,dispsize=self.dispsize)
        pos = pos[0] + w/2, pos[1] - h/2

        if fill:
            self.screen.append(Rect(pygaze.expdisplay, width=w, height=h, \
                lineWidth=pw, lineColor=colour, lineColorSpace='rgb', \
                fillColor=colour, fillColorSpace='rgb', pos=pos))
        else:
            self.screen.append(Rect(pygaze.expdisplay, width=w, height=h, \
                lineWidth=pw, lineColor=colour, lineColorSpace='rgb', \
                fillColor=None, pos=pos))


    def draw_line(self, colour=None, color=None, spos=None, epos=None, pw=1):

        """Draws a line on the screen
        
        arguments
        None
        
        keyword arguments
        colour    -- colour for the circle (a colour name (e.g. 'red') or
                   a RGB(A) tuple (e.g. (255,0,0) or (255,0,0,255))) or
                   None for the default foreground colour, self.fgc
                   (default = None)
        spos        -- line start, an (x,y) position tuple or None for a
                   quarter x and a central y position (default = None)
        epos        -- line end, an (x,y) position tuple or None for a
                   three-quarter x and a central y position (default =
                   None)
        pw        -- penwidth: line thickness (default = 1)
        
        returns
        Nothing    -- draws a line on (PyGame) or adds a Line stimulus to
                   (PsychoPy) the self.screen property
        """

        if color is None and colour is None:
            pass
        elif color is None and colour is not None:
            pass
        elif color is not None and colour is None:
            colour = color
        elif colour != color:
            raise Exception("The arguments 'color' and 'colour' are the same, but set to different values: color={}, colour={}".format(color,colour))

        if colour is None:
            colour = self.fgc
        if spos is None:
            spos = (int(self.dispsize[0]*0.25), self.dispsize[1]/2)
        if epos is None:
            epos = (int(self.dispsize[0]*0.75), self.dispsize[1]/2)

        colour = rgb2psychorgb(colour)
        spos = pos2psychopos(spos,dispsize=self.dispsize)
        epos = pos2psychopos(epos,dispsize=self.dispsize)
        
        # The `Line` class appears to be broken in a recent update of
        # PsychoPy. Hence the fallback to `ShapeStim`. See also:
        # <https://groups.google.com/forum/#!topic/psychopy-dev/1sKn6RrqH-8>
        #self.screen.append(Line(pygaze.expdisplay, start=spos, end=epos, \
        #    lineColor=colour, lineColorSpace='rgb', lineWidth=pw))
        stim = ShapeStim(pygaze.expdisplay, lineWidth=pw, \
            vertices=[spos, epos], lineColor=colour)

        self.screen.append(stim)


    def draw_polygon(self, pointlist, colour=None, color=None, pw=1, \
        fill=True):

        """Draws a polygon on the screen
        
        arguments
        pointlist    -- a list of (x,y) tuples resembling the cornerpoints
                   of the polygon
        
        keyword arguments
        colour    -- colour for the circle (a colour name (e.g. 'red') or
                   a RGB(A) tuple (e.g. (255,0,0) or (255,0,0,255))) or
                   None for the default foreground colour, self.fgc
                   (default = None)
        pw        -- penwidth: polygon line thickness (default = 1)
        fill        -- Boolean indicating whether polygon should be filled
                   or not (default = False)
        
        returns
        Nothing    -- draws a polygon on (PyGame) or adds a ShapeStim
                   stimulus to (PsychoPy) the self.screen property
        """

        if color is None and colour is None:
            pass
        elif color is None and colour is not None:
            pass
        elif color is not None and colour is None:
            colour = color
        elif colour != color:
            raise Exception("The arguments 'color' and 'colour' are the same, but set to different values: color={}, colour={}".format(color,colour))

        if colour is None:
            colour = self.fgc

        colour = rgb2psychorgb(colour)
        pl = []
        for pos in pointlist:
            pl.append(pos2psychopos(pos,dispsize=self.dispsize))

        if fill:
            self.screen.append(ShapeStim(pygaze.expdisplay, lineWidth=pw, \
                lineColor=colour, lineColorSpace='rgb', fillColor=colour, \
                fillColorSpace='rgb',vertices=pl, closeShape=True))
        else:
            self.screen.append(ShapeStim(pygaze.expdisplay, lineWidth=pw, \
                lineColor=colour, lineColorSpace='rgb', \
                fillColor=rgb2psychorgb(self.bgc), fillColorSpace='rgb', \
                vertices=pl, closeShape=True))

            
    def draw_fixation(self, fixtype="cross", colour=None, color=None, \
        pos=None, pw=1, diameter=12):

        """Draws a fixation (cross, x or dot) on the screen
        
        arguments
        None
        
        keyword arguments
        fixtype    -- type of fixation mark, should be either of the
                   following strings:
                    "cross" -- a '+'
                    "x"     -- a 'x'
                    "dot"       -- a filled circle
                   (default = "cross")
        colour    -- colour for the circle (a colour name (e.g. 'red') or
                   a RGB(A) tuple (e.g. (255,0,0) or (255,0,0,255))) or
                   None for the default foreground colour, self.fgc
                   (default = None)
        pos        -- fixation center, an (x,y) position tuple or None for
                   a central position (default = None)
        pw        -- penwidth: fixation line thickness (default = 1)
        diameter    -- diameter of the fixation mark in pixels (default =
                   12)
        
        returns
        Nothing    -- draws on (PyGame) or adds stimuli to (PsychoPy) the
                   self.screen property
        """
        
        if color is None and colour is None:
            pass
        elif color is None and colour is not None:
            pass
        elif color is not None and colour is None:
            colour = color
        elif colour != color:
            raise Exception("The arguments 'color' and 'colour' are the same, but set to different values: color={}, colour={}".format(color,colour))

        if fixtype not in ["cross","x","dot"]:
            raise Exception("Error in libscreen.Screen.draw_fixation: fixtype {} not recognized; fixtype should be one of 'cross','x','dot'".format(fixtype))
        if colour is None:
            colour = self.fgc
        if pos is None:
            pos = (self.dispsize[0]/2, self.dispsize[1]/2)

        r = int(diameter/2.0)
        if fixtype == "cross":
            self.draw_line(colour=colour, spos=(pos[0]-r, pos[1]), \
                epos=(pos[0]+r, pos[1]), pw=pw)
            self.draw_line(colour=colour, spos=(pos[0], pos[1]+r), \
                epos=(pos[0], pos[1]-r), pw=pw)
        elif fixtype == "x":
            x = int(math.cos(math.radians(45)) * r)
            y = int(math.sin(math.radians(45)) * r)
            self.draw_line(colour=colour, spos=(pos[0]-x, pos[1]-y), \
                epos=(pos[0]+x, pos[1]+y), pw=pw)
            self.draw_line(colour=colour, spos=(pos[0]-x, pos[1]+y), \
                epos=(pos[0]+x, pos[1]-y), pw=pw)
        elif fixtype == "dot":
            self.draw_circle(colour=colour, pos=pos, r=r, pw=0, fill=True)


    def draw_text(self, text="text", colour=None, color=None, pos=None, \
            centre=None, center=None, font="mono", fontsize=12, \
            antialias=True, wrap_width=None):

        """Draws a text on the screen
        
        arguments
        None
        
        keyword arguments
        text        -- string to be displayed (newlines are allowed and will
                   be recognized) (default = 'text')
        colour    -- colour for the circle (a colour name (e.g. 'red') or
                   a RGB(A) tuple (e.g. (255,0,0) or (255,0,0,255))) or
                   None for the default foreground colour, self.fgc
                   (default = None)
        pos        -- text position, an (x,y) position tuple or None for a
                   central position (default = None)
        center    -- Boolean indicating is the pos keyword argument should
                   indicate the text centre (True) or the top right
                   coordinate (False) (default = True)
        font        -- font name (a string value); should be the name of a
                   font included in the PyGaze resources/fonts directory
                   (default = 'mono')
        fontsize    -- fontsize in pixels (an integer value) (default = 12)
        antialias    -- Boolean indicating whether text should be antialiased
                   or not (default = True)
        
        returns
        Nothing    -- renders and draws a surface with text on (PyGame) or
                   adds SimpleTextStim to (PsychoPy) the self.screen
                   property
        """

        if color is None and colour is None:
            pass
        elif color is None and colour is not None:
            pass
        elif color is not None and colour is None:
            colour = color
        elif colour != color:
            raise Exception("The arguments 'color' and 'colour' are the same, but set to different values: color={}, colour={}".format(color,colour))

        if center is None and centre is None:
            centre = True
        elif center is None and centre is not None:
            pass
        elif center is not None and centre is None:
            centre = center
        elif centre != center:
            raise Exception("The arguments 'center' and 'centre' are the same, but set to different values: center={}, centre={}".format(center,centre))

        if colour is None:
            colour = self.fgc
        if pos is None:
            pos = (self.dispsize[0]/2, self.dispsize[1]/2)

        if centre:
            align = "center"
        else:
            align = "left"

        colour = rgb2psychorgb(colour)
        pos = pos2psychopos(pos,dispsize=self.dispsize)

        self.screen.append(TextStim(pygaze.expdisplay, text=str(text), \
            font=font, pos=pos, color=colour, height=fontsize, \
            antialias=antialias, alignHoriz=align, \
            fontFiles=pygaze.FONTFILES, wrapWidth=wrap_width))
        # PsychoPy deprecated "alignHoriz", but in version 3.2.4 (and maybe
        # also others, who knows?) its replacements "alignText" and
        # "anchorHoriz" are unknown keyword arguments to __init__. Yet,
        # "alignHoriz" does NOT work any longer. I guess alignment is just
        # broken now? The ugly workaround below will NOT work for those broken
        # versions of PsychoPy, but will at least not crash them.
        self.screen[-1].anchorHoriz = align
        self.screen[-1].alignText = align


    def draw_image(self, image, pos=None, scale=None):
        
        """Draws an image on the screen
        
        arguments
        image        -- a full path to an image file
        
        keyword arguments
        pos        -- image center position, an (x,y) position tuple or
                   None for a central position (default = None)
        scale    -- scale factor for the image or None for no scaling
                   (default = None)
        
        returns
        Nothing    -- loads and draws an image surface on (PyGame) or
                   adds SimpleImageStim to (PsychoPy) the self.screen
                   property
        """
        
        if pos is None:
            pos = (self.dispsize[0]/2, self.dispsize[1]/2)
        
        pos = pos2psychopos(pos,dispsize=self.dispsize)
        
        if scale is None:
            imgsize = None
        else:
            if pilimp:
                img = Image.open(image)
                imgsize = (img.size[0]*scale, img.size[1]*scale)
            else:
                imgsize = None
                print("WARNING! libscreen.Screen: PIL's Image class could not be loaded; image scaling with PsychoPy disptype is now impossible!")
            
        self.screen.append(ImageStim(pygaze.expdisplay, image=image, \
            pos=pos, size=imgsize))


    def set_background_colour(self, colour=None, color=None):

        """Set the background colour to colour
        
        arguments
        None
        
        keyword arguments
        colour    -- colour for the circle (a colour name (e.g. 'red') or
                   a RGB(A) tuple (e.g. (255,0,0) or (255,0,0,255))) or
                   None for the default foreground colour, self.fgc
                   (default = None)
        
        returns
        Nothing    -- sets bgc property to specified colour
        """

        if color is None and colour is None:
            pass
        elif color is None and colour is not None:
            pass
        elif color is not None and colour is None:
            colour = color
        elif colour != color:
            raise Exception("The arguments 'color' and 'colour' are the same, but set to different values: color={}, colour={}".format(color,colour))

        if colour is not None:
            self.bgc = colour

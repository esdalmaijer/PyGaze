# -*- coding: utf-8 -*-

class AOI:

    """Area Of Interest"""

    def __init__(self, aoitype, pos, size):

        """Initializes an AOI object

        arguments
        aoitype        --    string specifying the type of AOI; should be
                    'rectangle', 'circle' or 'ellipse'
        pos        --    a (x,y) position tuple
        size        --    either a single integer or a [width,height] list
                    of integers

        keyword arguments
        None
        """

        # check AOI type
        if aoitype not in ['rect','rectangle','circle','ellipse']:
            raise Exception("Error in libgazecon.AOI.__init__: aoitype %s not recognized; use one of 'rectangle', 'circle', 'ellipse'" % aoitype)
        self.aoitype = aoitype

        # check AOI position
        if type(pos) not in [tuple, list]:
            raise Exception("Error in libgazecon.AOI.__init__: pos should be an (x,y) tuple or list")
        else:
            self.pos = pos

        # check AOI size
        if type(size) in [int,float]:
            size = [size, size]
        elif type(size) == tuple:
            size = [size[0],size[1]]
        elif type(size) == list:
            pass
        else:
            raise Exception("Error in libgazecon.AOI.__init__: size should be either an integer value or a [width,height] list of integer values")
        self.size = [int(size[0]),int(size[1])]

        # check if aoitype and size match
        if self.aoitype == 'circle' and self.size[0] != self.size[1]:
            raise Exception("Error in libgazecon.AOI.__init__: libgazecon.AOI.__init__: a circle does not have different width and height arguments! Either use 'ellipse' as aoitype or a single integer size value")

        # calculate radius (used for circle)
        self.r = self.size[0]/2

        # equalize 'rect' aoitype input
        if self.aoitype == 'rect':
            self.aoitype = 'rectangle'


    def contains(self, pos):

        """Checks if a position is within the AOI

        arguments
        pos        --    a (x,y) position tuple

        keyword arguments
        None

        returns
        True/False    --    True if the passed position is within the AOI,
                    False if not
        """

        if self.aoitype == 'circle':

            if (self.pos[0]-pos[0])**2 + (self.pos[1]-pos[1])**2 < self.r**2:
                return True
            else:
                return False

        elif self.aoitype == 'rectangle':

            if (pos[0] > self.pos[0] and pos[0] < self.pos[0]+self.size[0]) and (pos[1] > self.pos[1] and pos[1] < self.pos[1]+self.size[1]):
                return True
            else:
                return False

        elif self.aoitype == 'ellipse':

            if ((self.pos[0]-pos[0])/(self.size[0]/2))**2 + ((self.pos[1]-pos[1])/(self.size[1]/2))**2 <= 1:
                return True
            else:
                return False

        else:
            raise Exception("Error in libgazecon.AOI.contains: unknown aoitype %s; use one of 'rectangle', 'circle', 'ellipse'" % self.aoitype)

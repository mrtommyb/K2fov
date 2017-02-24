"""This file defines a representation of the Kepler Field of View, `KeplerFov`.
"""
import numpy as np

try:
    import matplotlib.pyplot as mp
    import matplotlib
except ImportError:
    pass

from . import projection as proj
from . import rotate2 as r
from . import greatcircle as gcircle
from . import definefov

from . import DEFAULT_PADDING


"""
According to Instrument Handbook page 47, mod3 is in the +y direction
coordinates (+x is in the direction of the telescope pointing).

According to Flight Segment Users' Manual, p92 the sun shield is in
the +y  directions.

So in the model used in KeplerFov, at ra,dec=0, a roll angle of 0
means pointing the solar array due North.

In two-wheel mode, we will want the roll angle equal to the solar
angle.
"""


def getFovAngleFromSpacecraftRoll(yaxis_deg):
    """The y-axis vector (perpendicular to the solar arrays)
    lies 193 degrees clockwise of the angle
    from the centre of the FOV to the centre of mod 3

    As a diagram:

        4  3  2
     9  8  7  6  5
    14 13 12 11 10
          \
           \
            \
             \ y-axis of S/C in this direction

   This function converts from angles relative to spacecraft y-axis
   to angles relative to the FOV
   """
    return yaxis_deg + 13.0 + 180 - 90


def getSpacecraftRollAngleFromFovAngle(fovAngle_deg):
    """See notes on getFovAngleFromSpacecraftYAxisAngle()"""

    return fovAngle_deg - 13.0 - 180 + 90


class KeplerFov():
    def __init__(self, ra_deg, dec_deg, roll_deg,
                 brokenChannels=[5, 6, 7, 8,  17, 18, 19, 20,  9, 10, 11, 12]):
        """
        A representation of the Kepler Field of View designed
        for planning target observations.

        Inputs:
        ra_deg, dec_deg (floats) The direction to point the boresight
                        of the telescope. Note that while any
                        legal ra/dec is accepted by this class,
                        allowed values in the two wheel
                        mission are tightly constrained. Values
                        are in degrees

        roll_deg        Roll of the boresight. a roll of zero
                        orients the FOV so that mod 3 is due North.
                        Use getFovAngleFromSpacecraftRoll()
                        to convert from spacecraft roll values

        brokenChannels  Numbers of the CCD channels which are no longer
                        functioning.  Defaults to the channels that make up
                        Modules 3, 7, and 4.


        Values for the prime mission are:
        ra_deg = 290.66666667
        dec_deg = +44.5
        rollAngle_deg = 33.0 + n*90, where n is the season number
        """
        # default map is set by setPointing()
        # This is used for calculations of where objects lie within
        # a channel, and is always a Gnomic projection centred on
        # the boresight
        self.defaultMap = None

        self.brokenChannels = brokenChannels
        self.plateScale_arcsecPerPix = 3.98

        self.mods = list(range(1, 25))
        # Remove the 4 FGS mods
        self.mods.pop(0)
        self.mods.pop(3)
        self.mods.pop(-4)

        # Relative vectors to the module corners.
        # If the spacecraft was pointed at (ra, dec) = (0,0) with mod3
        # pointed north, r.raDecFromVec() of these values would give
        # The ra and decs of the corners of the modules.
        self.origin = definefov.loadOriginVectors()

        self.ra0_deg = ra_deg
        self.dec0_deg = dec_deg
        self.roll0_deg = roll_deg

        self.currentRaDec = None
        self.setPointing(ra_deg, dec_deg, roll_deg)

    ###
    # Code related to pointing the spacecraft
    ###

    def getOrigin(self, cartesian=False):
        """Return the ra/decs of the channel corners if the S/C
        is pointed at the origin (ra,dec = 0,0)

        Inputs:
        cartesian   (bool) If True, return each channel corner
                    as a unit vector

        Returns:
        A 2d numpy array. Each row represents a channel corner
        The columns are module, output, channel, ra, dec

        If cartestian is True, ra, and dec are replaced by the
        coordinates of a 3 vector
        """
        out = self.origin.copy()

        if cartesian is False:
            out = self.getRaDecs(out)
        return out

    def setPointing(self, ra_deg, dec_deg, roll_deg):
        t = self.computePointing(ra_deg, dec_deg, roll_deg)
        self.currentRaDec = t
        self.defaultMap = proj.Gnomic(ra_deg, dec_deg)

        self.ra0_deg = ra_deg
        self.dec0_deg = dec_deg
        self.roll0_deg = roll_deg

    def computePointing(self, ra_deg, dec_deg, roll_deg, cartesian=False):
        """Compute a pointing model without changing the internal object pointing"""
        # Roll FOV
        Rrotate = r.rotateInXMat(roll_deg)  # Roll

        # Slew from ra/dec of zero
        Ra = r.rightAscensionRotationMatrix(ra_deg)
        Rd = r.declinationRotationMatrix(dec_deg)
        Rslew = np.dot(Ra, Rd)

        R = np.dot(Rslew, Rrotate)

        slew = self.origin*1
        for i, row in enumerate(self.origin):
            slew[i, 3:6] = np.dot(R, row[3:6])

        if cartesian is False:
            slew = self.getRaDecs(slew)
        return slew

    def getRaDecs(self, mods):
        """Internal function converting cartesian coords to
        ra dec"""
        raDecOut = np.empty( (len(mods), 5))
        raDecOut[:,0:3] = mods[:,0:3]

        for i, row in enumerate(mods):
            raDecOut[i, 3:5] = r.raDecFromVec(row[3:6])
        return raDecOut

    def getCoordsOfChannelCorners(self):
        """Get ra/decs of corners of channels.

        Input:
        (none)

        Returns:
        A 2d numpy array.

        Each row represents a single corner of a channel.
        The columns are:
        module, output, channel, ra (degrees), dec (degrees)

        Note that the locations of the FGS channels are
        included in this output. FGS channels are 85-88
        inclusive
        """
        return self.currentRaDec

    def getBoresight(self):
        # Trap potential negative values for ra
        alpha = self.ra0_deg
        if alpha < 0:
            alpha += 360.

        return alpha, self.dec0_deg, self.roll0_deg


    ###
    # Sky -> pixel code
    ###

    def isOnSiliconList(self, ra_deg, dec_deg, padding_pix=DEFAULT_PADDING):
        """similar to isOnSilicon() but takes lists as input"""
        ch, col, row = self.getChannelColRowList(ra_deg, dec_deg)
        out = np.zeros(len(ch), dtype=bool)
        for channel in set(ch):
            mask = (ch == channel)
            if channel in self.brokenChannels:
                continue
            if channel > 84:
                continue
            out[mask] = self.colRowIsOnSciencePixelList(col[mask], row[mask], padding_pix)
        return out

    def getChannelColRowList(self, ra, dec, wantZeroOffset=False,
                         allowIllegalReturnValues=True):
        """similar to getChannelColRow() but takes lists as input"""
        try:
            ch = self.pickAChannelList(ra, dec)
        except ValueError:
            logger.warning("WARN: %.7f %.7f not on any channel" % (ra, dec))
            return (0, 0, 0)

        col = np.zeros(len(ch))
        row = np.zeros(len(ch))
        for channel in set(ch):
            mask = (ch == channel)
            col[mask], row[mask] = self.getColRowWithinChannelList(ra[mask], dec[mask], channel, 
                                                        wantZeroOffset, allowIllegalReturnValues)
        return (ch, col, row)

    def pickAChannelList(self, ra_deg, dec_deg):
        """Similar to pickAChannel() but takes lists as input.

        This will require AstroPy to be installed.
        """
        try:
            from astropy.coordinates import SkyCoord
            from astropy import units as u
        except ImportError:
            raise ImportError("AstroPy needs to be installed to use this feature.")
        cRa = self.currentRaDec[:, 3]  # Ra of each channel corner
        cDec = self.currentRaDec[:, 4]  # dec of each channel corner
        catalog = SkyCoord(cRa*u.deg, cDec*u.deg)
        position = SkyCoord(ra_deg*u.deg, dec_deg*u.deg)
        idx, _, _ = position.match_to_catalog_sky(catalog)
        return self.currentRaDec[idx, 2]

    def getColRowWithinChannelList(self, ra, dec, ch, wantZeroOffset=False,
                               allowIllegalReturnValues=True):
        """similar to getColRowWithinChannel() but takes lists as input"""
        x, y = self.defaultMap.skyToPix(ra, dec)
        kepModule = self.getChannelAsPolygon(ch)
        r = np.array(list(zip(x, y))) - kepModule.polygon[0, :]

        v1 = kepModule.polygon[1, :] - kepModule.polygon[0, :]
        v3 = kepModule.polygon[3, :] - kepModule.polygon[0, :]

        colFrac = np.dot(r, v1) / np.linalg.norm(v1)**2
        rowFrac = np.dot(r, v3) / np.linalg.norm(v3)**2

        col = colFrac*(1106-17) + 17
        row = rowFrac*(1038-25) + 25

        if not allowIllegalReturnValues:
            if not self.colRowIsOnSciencePixel(col, row):
                msg = "Request position %7f %.7f " % (ra, dec)
                msg += "does not lie on science pixels for channel %i " % (ch)
                msg += "[ %.1f %.1f]" % (col, row)
                raise ValueError(msg)

        if not wantZeroOffset:
            col += 1
            row += 1

        return (col, row)

    def colRowIsOnSciencePixelList(self, col, row, padding=DEFAULT_PADDING):
        """similar to colRowIsOnSciencePixelList() but takes lists as input"""
        out = np.ones(len(col), dtype=bool)
        col_arr = np.array(col)
        row_arr = np.array(row)
        mask = np.bitwise_or(col_arr < 12. - padding, col_arr > 1111 + padding)
        out[mask] = False
        mask = np.bitwise_or(row_arr < 20. - padding, row_arr > 1043 + padding)
        out[mask] = False
        return out

    def isOnSilicon(self, ra_deg, dec_deg, padding_pix=DEFAULT_PADDING):
        """Returns True if the given location is observable with a science CCD.

        Parameters
        ----------
        ra_deg : float
            Right Ascension (J2000) in decimal degrees.

        dec_deg : float
            Declination (J2000) in decimal degrees.

        padding : float
            Objects <=  this many pixels off the edge of a channel are counted
            as inside.  This allows one to compensate for the slight
            inaccuracy in `K2fov` that results from e.g. the lack of optical
            distortion modeling.
        """
        ch, col, row = self.getChannelColRow(ra_deg, dec_deg)
        # Modules 3 and 7 are no longer operational
        if ch in self.brokenChannels:
            return False
        # K2fov encodes the Fine Guidance Sensors (FGS) as
        # "channel" numbers 85-88; they are not science CCDs.
        if ch > 84:
            return False
        return self.colRowIsOnSciencePixel(col, row, padding_pix)

    def getChannelColRow(self, ra, dec, wantZeroOffset=False,
                         allowIllegalReturnValues=True):
        """Returns (channel, column, row) given an (ra, dec) coordinate.

        Returns (0, 0, 0) or a ValueError if the coordinate is not on silicon.
        """
        try:
            ch = self.pickAChannel(ra, dec)
        except ValueError:
            logger.warning("WARN: %.7f %.7f not on any channel" % (ra, dec))
            return (0, 0, 0)

        col, row = self.getColRowWithinChannel(ra, dec, ch, wantZeroOffset,
                                               allowIllegalReturnValues)
        return (ch, col, row)

    def pickAChannel(self, ra_deg, dec_deg):
        """Returns the channel number closest to a given (ra, dec) coordinate.
        """
        # Could improve speed by doing this in the projection plane
        # instead of sky coords
        cRa = self.currentRaDec[:, 3]  # Ra of each channel corner
        cDec = self.currentRaDec[:, 4]  # dec of each channel corner

        dist = cRa * 0
        for i in range(len(dist)):
            dist[i] = gcircle.sphericalAngSep(cRa[i], cDec[i], ra_deg, dec_deg)

        i = np.argmin(dist)
        return self.currentRaDec[i, 2]


    def getColRowWithinChannel(self, ra, dec, ch, wantZeroOffset=False,
                               allowIllegalReturnValues=True):
        """Returns (col, row) given a (ra, dec) coordinate and channel number.
        """
        # How close is a given ra/dec to the origin of a KeplerModule?
        x, y = self.defaultMap.skyToPix(ra, dec)
        kepModule = self.getChannelAsPolygon(ch)
        r = np.array([x[0],y[0]]) - kepModule.polygon[0, :]

        v1 = kepModule.polygon[1, :] - kepModule.polygon[0, :]
        v3 = kepModule.polygon[3, :] - kepModule.polygon[0, :]

        # Divide by |v|^2 because you're normalising v and r
        colFrac = np.dot(r, v1) / np.linalg.norm(v1)**2
        rowFrac = np.dot(r, v3) / np.linalg.norm(v3)**2

        # This is where it gets a little hairy. The channel "corners"
        # supplied to me actually represent points 5x5 pixels inside
        # the science array. Which isn't what you'd expect.
        # These magic numbers are the pixel numbers of the corner
        # edges given in fov.txt
        col = colFrac*(1106-17) + 17
        row = rowFrac*(1038-25) + 25

        if not allowIllegalReturnValues:
            if not self.colRowIsOnSciencePixel(col, row):
                msg = "Request position %7f %.7f " % (ra, dec)
                msg += "does not lie on science pixels for channel %i " % (ch)
                msg += "[ %.1f %.1f]" % (col, row)
                raise ValueError(msg)

        # Convert from zero-offset to one-offset coords
        if not wantZeroOffset:
            col += 1
            row += 1

        return (col, row)

    def colRowIsOnSciencePixel(self, col, row, padding=DEFAULT_PADDING):
        """Is col row on a science pixel?

        Ranges taken from Fig 25 or Instrument Handbook (p50)

        Padding allows for the fact that distortion means the
        results from getColRowWithinChannel can be off by a bit.
        Setting padding > 0 means that objects that are computed
        to lie a small amount off silicon will return True.

        To be conservative, set padding to negative
        """
        if col < 12. - padding or col > 1111 + padding:
            return False

        if row < 20 - padding or row > 1043 + padding:
            return False
        return True

    def getColRowWithinFgsCh(self, ra, dec, ch, wantZeroOffset=False,
                             allowIllegalReturnValues=True):
        """How close is a given ra/dec to the origin of an FGS mod

        Returns col and row of the position.
        """
        x, y = self.defaultMap.skyToPix(ra, dec)
        kepModule = self.getChannelAsPolygon(ch)
        r = np.array([x[0],y[0]]) - kepModule.polygon[0,:]

        v1 = kepModule.polygon[1,:] - kepModule.polygon[0,:]
        v3 = kepModule.polygon[3,:] - kepModule.polygon[0,:]

        colFrac = np.dot(r, v1) / np.linalg.norm(v1)**2
        rowFrac = np.dot(r, v3) / np.linalg.norm(v3)**2

        col = colFrac*(547)
        row = rowFrac*(527)

        if not allowIllegalReturnValues:
            if not self.colRowIsOnFgsPixel(col, row):
                msg = "Request position %7f %.7f " %(ra, dec)
                msg += "does not lie on FGS pixels for channel %i " %(ch)
                msg += "[ %.1f %.1f]" %(col, row)
                raise ValueError(msg)

        # Convert from zero-offset to one-offset coords
        if not wantZeroOffset:
            col += 1
            row += 1

        return (col, row)

    def colRowIsOnFgsPixel(self, col, row, padding=-50):
        """Is col row on a science pixel?

        #See Kepler Flight Segment User's Manual (SP0039-702) \S 5.4 (p88)

        Inputs:
        col, row (floats or ints)
        padding    If padding <0, pixel must be on silicon and this many
                   pixels away from the edge of the CCD to return True

        Returns:
        boolean
        """
        if col < 12. - padding  or col > 547 + padding:
            return False

        if row < 0 - padding or row > 527 + padding :
            return False
        return True

    ###
    # Pixel --> sky
    ###
    def getRaDecForChannelColRow(self, ch, col, row, oneOffsetPixels=True):

        # To FGS channels correctly
        if ch > 84:
            return self.getRaDecForFgsChannelColRow(ch, col, row,\
                oneOffsetPixels)

        if oneOffsetPixels:
            col -= 1
            row -= 1

        # Convert col row to colFrac, rowFrac
        # See notes in getColRowWithinChannel
        colFrac = (col-17.) / (1106.-17.)
        rowFrac = (row-25.) / (1038.-25.)

        # Get basis vectors for channel. vZero is vector close
        # to readout of chip (c,r) = (0,0)
        # vCol is a vector in increasing column direction
        kepModule = self.getChannelAsPolygon(ch)
        vZero = kepModule.polygon[0,:]
        vCol = kepModule.polygon[1,:] - vZero
        vRow = kepModule.polygon[3,:] - vZero

        # Where on the projected plane does col,row lie?
        projectionXy = vZero + (colFrac*vCol) + (rowFrac*vRow)

        # Call pixToSky
        x, y = projectionXy
        a, d = self.defaultMap.pixToSky(x, y)

        return [a[0], d[0]]

    def getRaDecForFgsChannelColRow(self, ch, col, row, oneOffsetPixels=True):
        if oneOffsetPixels:
            col -= 1
            row -= 1

        # Convert col row to colFrac, rowFrac
        # Offsets here haven't been rigourously checked.
        colFrac = (col-0.) / (547.)
        rowFrac = (row-0.) / (527.)

        # Get basis vectors for channel. vZero is vector close
        # to readout of chip (c,r) = (0,0)
        # vCol is a vector in increasing column direction
        kepModule = self.getChannelAsPolygon(ch)
        vZero = kepModule.polygon[0,:]
        vCol = kepModule.polygon[1,:] - vZero
        vRow = kepModule.polygon[3,:] - vZero

        # Where on the projected plane does col,row lie?
        projectionXy = vZero + (colFrac*vCol) + (rowFrac*vRow)

        # Call pixToSky
        x, y = projectionXy
        a, d = self.defaultMap.pixToSky(x, y)
        return [a[0], d[0]]

    ###
    #  Polygon code: sky <--> pix and other functions use
    #  these polygons to represent a single channel on the FOV
    ###
    def getAllChannelsAsPolygons(self, maptype=None):
        """Return slew the telescope and return the corners of the modules
        as Polygon objects.

        If a projection is supplied, the ras and
        decs are mapped onto x, y using that projection
        """
        polyList = []
        for ch in self.origin[:, 2]:
            poly = self.getChannelAsPolygon(ch, maptype)
            polyList.append(poly)
        return polyList

    def getChannelAsPolygon(self, chNumber, maptype=None):
        if maptype is None:
            maptype = self.defaultMap

        radec = self.currentRaDec
        idx = np.where(radec[:, 2].astype(np.int) == chNumber)[0]

        if not np.any(idx):
            raise ValueError("%i is not a valid channel number" % (chNumber))

        x, y = maptype.skyToPix(radec[idx, 3], radec[idx, 4])
        return KeplerModOut(chNumber, x=x, y=y)


    ###
    # Plotting code
    ###

    def plotPointing(self, maptype=None, colour='b', mod3='r', showOuts=True, **kwargs):
        """Plot the FOV
        """

        if maptype is None:
            maptype=self.defaultMap

        radec = self.currentRaDec
        for ch in radec[:,2][::4]:

            idx = np.where(radec[:,2].astype(np.int) == ch)[0]
            idx = np.append(idx, idx[0])  #% points to draw a box

            c = colour
            if ch in self.brokenChannels:
                c = mod3
            maptype.plot(radec[idx, 3], radec[idx, 4], '-', color=c, **kwargs)
            #Show the origin of the col and row coords for this ch
            if showOuts:
                maptype.plot(radec[idx[0], 3], radec[idx[0],4], 'o', color=c)


    def plotOutline(self, maptype=None, colour='#AAAAAA', **kwargs):
        """Plot an outline of the FOV.
        """

        if maptype is None:
            maptype=self.defaultMap

        xarr = []
        yarr = []
        radec = self.currentRaDec
        for ch in [20,4,11,28,32, 71,68, 84, 75, 60, 56, 15 ]:
            idx = np.where(radec[:,2].astype(np.int) == ch)[0]
            idx = idx[0]    #Take on the first one
            x, y = maptype.skyToPix(radec[idx][3], radec[idx][4])
            xarr.append(x)
            yarr.append(y)

        verts = np.empty( (len(xarr), 2))
        verts[:,0] = xarr
        verts[:,1] = yarr

        #There are two ways to specify line colour
        ec = kwargs.pop('ec', "none")
        ec = kwargs.pop('edgecolor', ec)
        p = matplotlib.patches.Polygon(verts, fill=True, ec=ec, fc=colour, **kwargs)
        mp.gca().add_patch(p)


    def plotSpacecraftYAxis(self, maptype=None):
        """Plot a line pointing in the direction of the spacecraft
        y-axis (i.e normal to the solar panel
        """

        if maptype is None:
            maptype=self.defaultMap
        #Plot direction of spacecraft +y axis. The subtraction of
        #90 degrees accounts for the different defintions of where
        #zero roll is.
        yAngle_deg = getSpacecraftRollAngleFromFovAngle(self.roll0_deg)
        yAngle_deg -=90

        a,d = gcircle.sphericalAngDestination(self.ra0_deg, self.dec0_deg, -yAngle_deg, 12.0)
        x0, y0 = maptype.skyToPix(self.ra0_deg, self.dec0_deg)
        x1, y1 = maptype.skyToPix(a, d)
        mp.plot([x0, x1], [y0, y1], 'k-')


    def plotChIds(self, maptype=None, modout=False):
        """Print the channel numbers on the plotting display

        Note:
        ---------
        This method will behave poorly if you are plotting in
        mixed projections. Because the channel vertex polygons
        are already projected using self.defaultMap, applying
        this function when plotting in a different reference frame
        may cause trouble.
        """
        if maptype is None:
            maptype = self.defaultMap

        polyList = self.getAllChannelsAsPolygons(maptype)
        for p in polyList:
            p.identifyModule(modout=modout)


    def getWcsForChannel1(self, ch):
        raise NotImplementedError("getWcsForChannel doesn't work")
        crpix =np.array( [500, 500])    #Rough guess at centre
        a,d = self.getRaDecForChannelColRow(ch, crpix[0], crpix[1])
        crval = np.array([a,d])

        #Get rotation of channel relative to FOV
        kepModule = self.getChannelAsPolygon(ch)
        vZero =  kepModule.polygon[0,:]
        vCol = kepModule.polygon[1,:] - vZero
        vRow = kepModule.polygon[3,:] - vZero
        ang_rad = np.arctan2(vCol[1], vCol[0])
        #ang_rad -= np.radians(.2308)   #Debugging code

        if np.cross(vCol, vRow) >= 0:
            sign = +1
        else:
            sign = -1

        CD = np.empty( (2,2))
        CD[0,0] = np.cos(ang_rad)
        CD[0,1] = np.sin(ang_rad)
        CD[1,0] = -np.sin(ang_rad)
        CD[1,1] = np.cos(ang_rad)

        if sign < 0:
            CD[1,:] *= -1

        CD *= self.plateScale_arcsecPerPix/3600.

        return crval, crpix, CD




###############################################
# Polygon and KepModule code
################################################

class Polygon():
    def __init__(self, x=None, y=None, pointList=None):
        """
        An abstract class to represent a polygon in space

        Input:
        ------------
        pointList   A list of (x,y) pairs. Eg
                    [ (0,0), (1,0), (0,1), (1.1)]

                    The edges of the polygon join adjacent elements
                    of this list, so the order matters. The last
                    point is assumed to connect to the first point.
        """

        if x is not None and y is not None:
            pointList = []
            for xi, yi in zip(x, y):
                pointList.append( (xi, yi))

        if pointList is None:
            raise ValueError("Must supply x,y or pointList")

        self.polygon = np.array(pointList)


    def __str__(self):
        return self.polygon.__str__()

    def __repr__(self):
        return self.polygon.__repr__()


    def isPointInside(self, xp, yp):
        """Is the given point inside the polygon?

        Input:
        ------------
        xp, yp
            (floats) Coordinates of point in same units that
            array vertices are specified when object created.
        Returns:
        -----------
        **True** / **False**
        """

        point = np.array([xp, yp]).transpose()
        polygon = self.polygon
        numVert, numDim = polygon.shape

        #Subtract each point from the previous one.
        polyVec = np.roll(polygon, -1, 0) - polygon
        #Get the vector from each vertex to the given point
        pointVec = point - polygon

        crossProduct = np.cross(polyVec, pointVec)

        if np.all(crossProduct < 0) or np.all(crossProduct > 0):
            return True
        return False

    def draw(self, **kwargs):
        """Draw the polygon

        Optional Inputs:
        ------------
        All optional inputs are passed to ``matplotlib.patches.Polygon``

        Notes:
        ---------
        Does not accept maptype as an argument.
        """

        ax = mp.gca()
        shape = matplotlib.patches.Polygon(self.polygon, **kwargs)
        ax.add_artist(shape)


class KeplerModOut(Polygon):
    def __init__(self, channel, x=None, y=None, pointList=None):
        """A Polygon with a channel identification attached to it"""
        Polygon.__init__(self, x,y,pointList)
        self.channel = channel

    def getChannel(self):
        return self.channel


    def identifyModule(self, modout=False):
        """Write the name of a channel/modout on a plot

        Optional Inputs:
        -----------
        modout
            (boolean). If True, write module and output. Otherwise
            write channel number

        Returns:
        ------------
        **None**

        Output:
        -----------
        Channel numbers are written to the current axis.

        """
        x,y = np.mean(self.polygon, 0)

        if modout:
            modout = modOutFromChannel(self.channel)
            mp.text(x, y, "%i-%i" %(modout[0], modout[1]), fontsize=8, \
                ha="center", clip_on=True)
        else:
            mp.text(x,y, "%i" %(self.channel), fontsize=8, \
                ha="center", clip_on=True)




#########################################################
#  channel <--> mod out
#########################################################

def channelFromModOut(mod, out):
    lookup = loadChannelModOutLookup()
    return lookup[mod, out]


def modOutFromChannel(ch):
    lookup = loadChannelModOutLookup()
    idx = lookup == ch
    idx[:,0] = False

    if not np.any(idx):
        raise ValueError("Illegal channel request")

    if np.sum(idx) > 1:
        raise ValueError("Channel number begins at 1, not zero")

    modout = np.where(idx)
    mod = modout[0][0]
    out = modout[1][0]
    return (mod, out)


def loadChannelModOutLookup():
    lookup = np.array( [ \
       [ 0,    0,    0,    0,    0], \
       [ 1,   85,    0,    0,    0], \
       [ 2,    1,    2,    3,    4], \
       [ 3,    5,    6,    7,    8], \
       [ 4,    9,   10,   11,   12], \
       [ 5,   86,    0,    0,    0], \
       [ 6,   13,   14,   15,   16], \
       [ 7,   17,   18,   19,   20], \
       [ 8,   21,   22,   23,   24], \
       [ 9,   25,   26,   27,   28], \
       [10,   29,   30,   31,   32], \
       [11,   33,   34,   35,   36], \
       [12,   37,   38,   39,   40], \
       [13,   41,   42,   43,   44], \
       [14,   45,   46,   47,   48], \
       [15,   49,   50,   51,   52], \
       [16,   53,   54,   55,   56], \
       [17,   57,   58,   59,   60], \
       [18,   61,   62,   63,   64], \
       [19,   65,   66,   67,   68], \
       [20,   69,   70,   71,   72], \
       [21,   87,    0,    0,    0], \
       [22,   73,   74,   75,   76], \
       [23,   77,   78,   79,   80], \
       [24,   81,   82,   83,   84], \
       [25,   88,    0,    0,    0], \
       ])

    return lookup


#####################################################################
#####################################################################
#####################################################################

#def getRaDecOut(vectors):
    #raDecOut = np.empty( (len(vectors), 2))
    #for i, row in enumerate(vectors):
        #raDecOut[i] = r.raDecFromVec(row)
    #return raDecOut

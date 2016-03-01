"""This file defines the projection classes."""
try:
    import matplotlib.pyplot as mp
except Exception:
    pass

import numpy as np
from . import rotate


class Projection():
    """Base Projection class. Used for mapping ra and dec into
    Euclidean space based on a given projection.

    The primary reference for projections is Calabretta and Greisen
    (2002), A&A 395, 1077

    The base class implements the Plate Carree projection (\S 5.2.3)
    which just maps ra dec to xy -- i.e what you would blindly do
    if you knew no different. If distortion is not a concern
    this is an acceptable approach

    """
    def __init__(self):
        self.ra0_deg = 0
        self.dec0_deg = 0

    def skyToPix(self, ra_deg, dec_deg):
        return ra_deg, dec_deg

    def pixToSky(self, x, y):
        return x, y

    def eulerRotate(self, ra_deg, dec_deg):
        ra_deg, dec_deg = self.parseInputs(ra_deg, dec_deg)

        #Transform ra dec into angle away from tangent point
        #using the rotation matrix
        theta_rad= np.empty( (len(ra_deg),) )
        phi_rad = theta_rad * 0
        R = self.Rmatrix
        for i in range(len(ra_deg)):
            #Convert the ra/dec to a vector, then rotate so
            #that the tangent point is at [1,0,0]. Then pull out
            #the angle relative to the x-axis, and the angle
            #around the y-z plane.
            #@TODO: Can I make this faster with dot products?
            vec =rotate.vecFromRaDec(ra_deg[i], dec_deg[i])
            aVec = np.dot(R, vec)

            #aVec = (sint, cost*cosp, cost*sinp)
            sint = aVec[0]
            cost = np.hypot(aVec[1], aVec[2])
            theta = np.arctan2(sint, cost)

            cost = np.cos(theta)
            cosp = aVec[1] / cost
            sinp = aVec[2] / cost
            phi = np.arctan2(sinp, cosp)

            if phi < 0:
                phi += 2*np.pi
            if phi > 2*np.pi:
                phi -= 2*np.pi


            #Just to be explicit
            theta_rad[i] = theta
            phi_rad[i] = phi
        return theta_rad, phi_rad



    def parseInputs(self, ra_deg, dec_deg):
        try:
            len(ra_deg)
        except TypeError:
            ra_deg = np.array([ra_deg])

        try:
            len(dec_deg)
        except TypeError:
            dec_deg = np.array([dec_deg])

        #If ra/dec aren't arrays, make them arrays
        if not isinstance(ra_deg, np.ndarray):
            ra_deg = np.array(ra_deg)

        if not isinstance(dec_deg, np.ndarray):
            dec_deg = np.array(dec_deg)


        if np.logical_xor(len(ra_deg) == 1, len(dec_deg) == 1):
            if len(ra_deg) == 1:
                ra_deg = dec_deg *0 + ra_deg[0]
            else:
                dec_deg = ra_deg * 0 + dec_deg[0]

        if len(ra_deg) != len(dec_deg):
            raise ValueError("Input ra and dec arrays must be same length")

        return ra_deg, dec_deg

    def isPositiveMap(self):
        """Returns true if increasing ra increases pix in skyToPix()
        """
        x0, y0 = self.skyToPix(self.ra0_deg, self.dec0_deg)
        x1, y1 = self.skyToPix(self.ra0_deg + 1/3600., self.dec0_deg)

        if x1 > x0:
            return True
        return False


    def plot(self, ra_deg, dec_deg, *args, **kwargs):
        x,y = self.skyToPix(ra_deg, dec_deg)
        self._plot(x, y, *args, **kwargs)

    def scatter(self,  ra_deg, dec_deg, *args, **kwargs):
        x,y = self.skyToPix(ra_deg, dec_deg)
        mp.scatter(x,y, *args, **kwargs)


    def text(self, ra_deg, dec_deg, s, *args, **kwargs):
        x,y = self.skyToPix(ra_deg, dec_deg)
        mp.text(x, y, s, *args, **kwargs)



    def plotGrid(self, numLines=(5,5), lineWidth=1, colour="#777777"):
        """Plot NUMLINES[0] vertical gridlines and NUMLINES[1] horizontal gridlines,
        while keeping the initial axes bounds that were present upon its calling.
        Will not work for certain cases.
        """
        x1, x2, y1, y2 = mp.axis()
        ra1, dec0 = self.pixToSky(x1, y1)
        ra0, dec1 = self.pixToSky(x2, y2)

        xNum, yNum = numLines
        self.raRange, self.decRange  = self.getRaDecRanges(numLines)

        #import pdb; pdb.set_trace()
        #Guard against Ra of zero within the plot
        a1 = np.abs(ra1-ra0)
        a2 = np.abs( min(ra0, ra1) - (max(ra0, ra1) - 360))
        if a2 < a1:     #Then we straddle 360 degrees in RA
            if ra0 < ra1:
                ra1 -= 360
            else:
                ra0 -= 360


        #Draw lines of constant dec
        lwr = min(ra0, ra1)
        upr = max(ra0, ra1)
        stepX = round((upr-lwr) / float(xNum))
        ra_deg = np.arange(lwr - 3*stepX, upr + 3.5*stepX, 1, dtype=np.float)
        for dec in self.decRange:
            self.plotLine(ra_deg, dec, '-', color = colour, linewidth = lineWidth)


        #Draw lines of const ra
        lwr = min(dec0, dec1)
        upr = max(dec0, dec1)
        stepY = round((upr-lwr) / float(yNum))
        dec_deg = np.arange(dec0 - 3*stepY, dec1 + 3.5*stepY, 1, dtype=np.float)
        for ra in self.raRange:
            self.plotLine(ra, dec_deg, '-', color = colour, linewidth = lineWidth)

        mp.axis([x1, x2, y1, y2])



    def labelAxes(self, numLines=(5,5)):
        """Put labels on axes

        Note: I should do better than this by picking round numbers
        as the places to put the labels.

        Note: If I ever do rotated projections, this simple approach
        will fail.
        """

        x1, x2, y1, y2 = mp.axis()
        ra1, dec0 = self.pixToSky(x1, y1)
        raRange, decRange = self.getRaDecRanges(numLines)
        ax = mp.gca()

        x_ticks = self.skyToPix(raRange, dec0)[0]
        y_ticks = self.skyToPix(ra1, decRange)[1]

        ax.xaxis.set_ticks(x_ticks)
        ax.xaxis.set_ticklabels([str(int(i)) for i in raRange])
        mp.xlabel("Right Ascension (deg)")

        ax.yaxis.set_ticks(y_ticks)
        ax.yaxis.set_ticklabels([str(int(i)) for i in decRange])
        mp.ylabel("Declination (deg)")


    def getRaDecRanges(self, numLines):
        """Pick suitable values for ra and dec ticks

        Used by plotGrid and labelAxes
        """
        x1, x2, y1, y2 = mp.axis()

        ra0, dec0 = self.pixToSky(x1, y1)
        ra1, dec1 = self.pixToSky(x2, y2)

        #Deal with the case where ra range straddles 0.
        #Different code for case where ra increases left to right, or decreases.
        if self.isPositiveMap():
            if ra1 < ra0:
                ra1 += 360
        else:
            if ra0 < ra1:
                ra0 += 360

        raMid = .5*(ra0+ra1)
        decMid = .5*(dec0+dec1)


        xNum, yNum = numLines
        stepX = round((ra1 - ra0) / xNum)
        stepY = round((dec1 - dec0) / yNum)

        rangeX = stepX * (xNum - 1)
        rangeY = stepY * (yNum - 1)

        raStart = np.round(raMid - rangeX/2.)
        decStart = np.round(decMid - rangeY/2.)

        raRange = np.arange(raStart, raStart + stepX*xNum, stepX)
        decRange = np.arange(decStart, decStart + stepY*yNum, stepY)
        raRange = np.fmod(raRange, 360.)

        return raRange, decRange


    def plotLine(self, ra_deg, dec_deg, *args, **kwargs):
        ra_deg, dec_deg = self.parseInputs(ra_deg, dec_deg)
        x,y = self.skyToPix(ra_deg, dec_deg, catchInvalid=False)

        diffX = np.abs(np.diff(x))
        idx1 = diffX > 3*np.mean(diffX)
        idx1[idx1 + 1] = True

        diffY = np.abs(np.diff(y))
        idx2 = diffY > 3*np.mean(diffY)

        j = 0
        i0 = 0
        if len(idx2) > 0:
            idx2[-1] = True

        idx = np.where(np.logical_or(idx1, idx2))[0]
        for j in range(len(idx)):
            i1 = idx[j]
            self._plot(x[i0:i1], y[i0:i1], *args, **kwargs)
            i0 = i1+1



    def _plot(self, x, y, *args,  **kwargs):
        mp.plot(x,y, *args, **kwargs)


class PlateCaree(Projection):
    """Synonym for the base class"""
    pass


class HammerAitoff(Projection):
    def __init__(self, ra0_deg, dec0_deg):
        Projection.__init__(self)
        self.ra0_deg = ra0_deg
        self.dec0_deg = dec0_deg

        self.ra0_deg = ra0_deg
        self.dec0_deg = dec0_deg

        #This projection assumes ra ranges from -180 to +180
        #if self.ra0_deg > 180:
            #self.ra0_deg -= 360

        #Construct rotation matrix used to convert ra/dec into
        #angle relative to tangent point
        Rdec = rotate.declinationRotationMatrix(-self.dec0_deg)
        Rra = rotate.rightAscensionRotationMatrix(-self.ra0_deg)
        self.Rmatrix = np.dot(Rra, Rdec)

    def skyToPix(self, ra_deg, dec_deg, **kwargs):
        sin = np.sin
        cos = np.cos

        #Parse inputs and allocate space for outputs
        ra_deg, dec_deg = self.parseInputs(ra_deg, dec_deg)
        long_deg = ra_deg * 0
        lat_deg = long_deg * 0

        #Get longitude and latitude relative to defined origin.
        for i in range(len(ra_deg)):
            vec = rotate.vecFromRaDec(ra_deg[i], dec_deg[i])
            aVec = np.dot( self.Rmatrix, vec)
            long_deg[i], lat_deg[i] = rotate.raDecFromVec(aVec)

        long_deg = np.fmod(long_deg + 180, 360.)
        long_rad = np.radians(long_deg) - np.pi #[-pi,pi]
        lat_rad = np.radians(lat_deg)

        #long_rad = np.fmod(long_rad+ np.pi, 2*np.pi)

        gamma = 1 + cos(lat_rad)* cos(long_rad/2.)
        gamma = np.sqrt(2/gamma)
        x = -2*gamma*cos(lat_rad)*sin(long_rad/2)
        y = gamma*sin(lat_rad)

        return x, y

    def pixToSky(self, x, y):
        raise NotImplementedError("pixToSky not defined!")

    def labelAxes(self, nLabel=5):
        """Put labels on axes"""
        raise NotImplementedError("Axis labels not available in HA yet")


class Gnomic(Projection):
    def __init__(self, ra0_deg, dec0_deg):
        self.ra0_deg = ra0_deg
        self.dec0_deg = dec0_deg

        #Construct rotation matrix used to convert ra/dec into
        #angle relative to tangent point
        Rdec = rotate.declinationRotationMatrix(-self.dec0_deg)
        Rra = rotate.rightAscensionRotationMatrix(-self.ra0_deg)
        self.Rmatrix = np.dot(Rdec, Rra)


        #Check I created the matrix correctly.
        origin = rotate.vecFromRaDec(self.ra0_deg, self.dec0_deg)
        origin = np.dot(self.Rmatrix, origin)
        assert( np.fabs(origin[0] -1 ) < 1e-9)
        assert( np.fabs(origin[1]) < 1e-9)
        assert( np.fabs(origin[2]) < 1e-9)

    def skyToPix(self, ra_deg, dec_deg, catchInvalid=True):
        ra_deg, dec_deg = self.parseInputs(ra_deg, dec_deg)

        #Transform ra dec into angle away from tangent point
        #using the rotation matrix
        theta_rad= np.empty( (len(ra_deg),) )
        phi_rad = theta_rad * 0
        R = self.Rmatrix
        for i in range(len(ra_deg)):
            #Convert the ra/dec to a vector, then rotate so
            #that the tangent point is at [1,0,0]. Then pull out
            #the angle relative to the x-axis, and the angle
            #around the y-z plane.
            #@TODO: Can I make this faster with dot products?
            vec =rotate.vecFromRaDec(ra_deg[i], dec_deg[i])
            aVec = np.dot(R, vec)

            #aVec = (sint, cost*cosp, cost*sinp)
            sint = aVec[0]
            cost = np.hypot(aVec[1], aVec[2])
            theta = np.arctan2(sint, cost)

            #Points more than 90 deg from tangent point need to be
            #caught, or they'll be projected 180-i degrees from tangent
            #point.
            if catchInvalid and theta < 0:
                raise ValueError("Point (%.7f %.7f) not projectable" \
                    %(ra_deg[i], dec_deg[i]))

            cost = np.cos(theta)
            cosp = aVec[1] / cost
            sinp = aVec[2] / cost
            phi = np.arctan2(sinp, cosp)

            if phi < 0:
                phi += 2*np.pi
            if phi > 2*np.pi:
                phi -= 2*np.pi


            #Just to be explicit
            theta_rad[i] = theta
            phi_rad[i] = phi


        #Project onto tangent plane. Negative x because we are inside
        #sphere looking out (matches astronomical convention
        r = 1/(np.tan(theta_rad) + 1e-10) #Prevent division by zero
        x = - r * np.cos(phi_rad)
        y = r * np.sin(phi_rad)

        return x, y

    def pixToSky(self, x, y):
        x, y = self.parseInputs(x, y)

        R = self.Rmatrix
        invR = np.matrix(R.transpose())
        ra_deg = np.empty( (len(x),))
        dec_deg = np.empty( (len(x),))

        for i in range(len(x)):
            #-x because we are inside sphere looking out. This
            #matches the astronomical convention.
            phi_rad = np.arctan2(y,-x)
            r = np.hypot(x,y)
            theta_rad = np.arctan(r)

            aVec = np.zeros((3,))
            aVec[0] = np.cos(theta_rad)
            aVec[1] = np.sin(theta_rad)*np.cos(phi_rad)
            aVec[2] = np.sin(theta_rad)*np.sin(phi_rad)


            vec = np.dot(invR, aVec)
            vec = np.array(vec)[0]    #Convert to 1d array
            ra_deg[i], dec_deg[i] = rotate.raDecFromVec(vec)
        return ra_deg, dec_deg


class Cylindrical(Projection):
    """Stunted cyclindical projection that assumes
    projection point is always at sky point 0,0
    """
    def __init__(self):
        self.ra0_deg = 0
        self.dec0_deg = 0

    def skyToPix(self, ra_deg, dec_deg, **kwargs):
        x = np.radians(ra_deg)
        y = np.sin( np.radians(dec_deg))
        return x, y

    def pixToSky(self, x, y, **kwargs):
        ra = np.degrees(x)
        dec = np.degrees(np.arcsin(y))
        return ra, dec


class Cylindrical2(Projection):
    """Stunted cyclindical projection that hacks at changing ra0
    but insists in dec0 being fixed.

    Wikipedia calls this the Lambert cylindrical equal area projection
    http://en.wikipedia.org/wiki/Lambert_cylindrical_equal-area_projection
    """
    def __init__(self, ra0_deg):
        self.ra0_deg = ra0_deg
        self.dec0_deg = 0

    def skyToPix(self, ra_deg, dec_deg, **kwargs):
        #Cast as nd array
        ra_deg = np.atleast_1d(ra_deg)

        ra_deg -= self.ra0_deg
        #Wrap around if necessary
        if np.any(ra_deg < 0):
            ra_deg[ ra_deg<0] += 360


        x = np.radians(-ra_deg)
        y = np.sin( np.radians(dec_deg))
        return x, y

    #def pixToSky(self, x, y, **kwargs):
        #ra = np.degrees(x)
        #dec = np.degrees(np.arcsin(y))
        #return ra, dec

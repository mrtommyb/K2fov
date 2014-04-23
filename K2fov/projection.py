try:
    import matplotlib.pyplot as mp
except ImportError:
    pass
import numpy as np
import rotate

__version__ = "$Id: projection.py 36 2014-01-23 22:19:15Z fergalm $"
__URL__ = "$URL: http://svn.code.sf.net/p/keplertwowheel/code/py/projection.py $"


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
        pass

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


    def plot(self, ra_deg, dec_deg, *args, **kwargs):
        x,y = self.skyToPix(ra_deg, dec_deg)
        try:
            plot_degrees = kwargs.pop('plot_degrees')
        except KeyError:
            plot_degrees=False
        if plot_degrees:
            x,y = np.degrees(x), np.degrees(y)
        self._plot(x, y, *args, **kwargs)

    def scatter(self,  ra_deg, dec_deg, *args, **kwargs):
        x,y = self.skyToPix(ra_deg, dec_deg)
        mp.scatter(x,y, *args, **kwargs)


    def text(self, ra_deg, dec_deg, s, *args, **kwargs):
        x,y = self.skyToPix(ra_deg, dec_deg)
        mp.text(x, y, s, *args, **kwargs)

    def plotGrid(self, lineWidth=1, stepInDegrees=15, colour="#777777", \
        raRange=[0,360], decRange=[-90, 90]):

        ra0, ra1 = raRange
        dec0, dec1 = decRange
        step=stepInDegrees

        c = colour
        ra_deg = np.arange(ra0-1*step, ra1+1.5*step, 1, dtype=np.float)
        for dec in np.arange(dec0, dec1+ 1*step, step):
            self.plotLine(ra_deg, dec, '-', color=c, linewidth=lineWidth)

        dec = np.arange(dec0-step, dec1+1.5*step, 1, dtype=float)
        for ra in np.arange(ra0, ra1+step, step):
            self.plotLine(ra, dec, '-', color=c, linewidth=lineWidth)

        ##Useful for debugging
        #self.plotLine(0, dec,'r-', linewidth=lineWidth)
        #self.plotLine(180, dec,'c-', linewidth=lineWidth)


    def plotLine(self, ra_deg, dec_deg, *args, **kwargs):
        ra_deg, dec_deg = self.parseInputs(ra_deg, dec_deg)
        x,y = self.skyToPix(ra_deg, dec_deg)

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



    def skyToPix(self, ra_deg, dec_deg):
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


    def skyToPix(self, ra_deg, dec_deg):
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


        #Project onto tangent plane
        #theta_rad = np.pi/2. - theta_rad
        r = 1/(np.tan(theta_rad) + 1e-10) #Prevent division by zero
        x = r * np.cos(phi_rad)
        y = r * np.sin(phi_rad)

        #print x, y
        return x, y


    def pixToSky(self, x, y):
        x, y = self.parseInputs(x, y)

        R = self.Rmatrix
        invR = np.matrix(R.transpose())
        ra_deg = np.empty( (len(x),))
        dec_deg = np.empty( (len(x),))

        for i in range(len(x)):
            phi_rad = np.arctan2(y,x)
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


    def skyToPix(self, ra_deg, dec_deg):
        x = np.radians(ra_deg)
        y = np.sin( np.radians(dec_deg))
        return x, y

    def pixToSky(self, x, y):
        ra = np.degrees(x)
        dec = np.degrees(np.arcsin(y))
        return ra, dec


def main():
    mp.clf()
    p = HammerAitoff(45,23)
    #p = Projection()

    #import pdb; pdb.set_trace()
    #print p.skyToPix(30,0)
    #print p.skyToPix(30,30)
    #print p.skyToPix(90, 30)
    #print p.skyToPix(181,30)

    #print p.skyToPix(270,0)

    #ra = np.arange(-180, 180, 15)
    #p.plot(ra, 0, 'r-')
    #p.plot(ra, 30, 'g-')
    #p.plot(ra, 45, 'b-')
    #p.plot(ra, 75, 'c-')
    #p.plot(ra, 90, 'k-')

    #dec = np.arange(-90, 91, 5)
    #p.plot(0, dec, 'r-')
    #p.plot(45, dec, 'g-')
    #p.plot(90, dec, 'b-')
    #p.plot(135, dec, 'c-')
    #p.plot(180, dec, 'k-')


    #p.plot(225, dec, 'g-')
    #p.plot(270, dec, 'b-')
    #p.plot(315, dec, 'c-')
    #p.plot(350, dec, 'k-')

    #conv = {3: tools.toFloat}
    #filename = "../twowheel/brighthd.txt"
    #data = np.loadtxt(filename, delimiter=";", usecols=(0,1,2, 3), converters=conv)
    #p.plot(data[:,0], data[:,1], 'k,')

    p.plotGrid()
    plotEcliptic(p)








##############################################################3

##############################################################3

##############################################################3

##############################################################3













def plotEcliptic(maptype=Projection()):
    """Plot Ra and Dec of ecliptic

    Taken from http://www.dur.ac.uk/john.lucey/users/solar_year.html
    His lambda is equal to ra, according to
    http://www.princeton.edu/~achaney/tmve/wiki100k/docs/Ecliptic_coordinate_system.html
    """


    ra = np.empty(360)
    dec = np.empty(360)
    for i in np.arange(360):
        ra[i] = i + 2.45*np.sin (2 * i * np.pi/180.)
        dec[i] =23.5*np.sin( i*np.pi/180.)

    maptype.plotLine(ra, dec, 'r-', lw=4, label="Ecliptic")

import matplotlib.pyplot as mp
import numpy as np

import projection as proj
import  fov

#import scenery

def main():
    wantPlot = True
    zoom = False

    ra_deg = 98.15766666666666
    dec_deg = 21.594944444444444
    scRoll_deg = 157.6053108

    fovRoll_deg = fov.getFovAngleFromSpacecraftRoll(scRoll_deg)
    k = fov.KeplerFov(ra_deg, dec_deg, fovRoll_deg)

    #Position of example star, WASP-67
    ra_deg, dec_deg = 103.67845833333334, 24.245555555555555


    #Get coordinates of channel corners.
    raDec = k.getCoordsOfChannelCorners()

    #Is a given ra/dec on silicon?
    try:
        ch = k.pickAChannel(ra_deg, dec_deg)
        print "Star is on channel %i Mod-out %s" %(ch, fov.modOutFromChannel(ch))
    except ValueError:
        print "Star is not on silicon"
        print "Caution: Stars within 5 pix of channel edges are not found by this algorithm"


    ch, col, row = k.getChannelColRow(ra_deg, dec_deg)
    print "Star is on channel %i Col %.1f Row %.1f" %(ch, col, row)


    if wantPlot:
        mp.clf()
        #ph is a projection class, in this case HammerAitoff. Pass this
        #class to all FOV plotting commands so it knows how to do the
        #plotting. ph also implements matplotlib's plot, scatter and text
        #commands
        #ph = proj.HammerAitoff(0,0)
        ph = proj.Cylindrical()
        ph.plotGrid()

        k.plotPointing(ph)

        #scenery.plotEcliptic(ph)
        plotWithLabel(ph, ra_deg, dec_deg, "HD 50554")

        if zoom:
            mp.axis([.88, 1.36, -0.60, -0.20])
            k.plotChIds(ph, modout=True)
        mp.show()





def plotWithLabel(maptype, ra, dec, label):
    x,y = maptype.skyToPix(ra, dec)
    mp.plot(x, y, 'ro')
    mp.text(x, y, label)


if __name__ == "__main__":
    main()

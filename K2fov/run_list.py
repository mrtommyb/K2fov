
##find out if targets are on silicon

from __future__ import division
import sys
sys.path.append('/Users/tom/gitcode/K2_fov/K2_fov/')
import numpy as np
import matplotlib.pyplot as plt
import K2onSilicon

import csv

if __name__ == '__main__':
    fieldnum = 0

    infile = 'GO00.csv'

    r = csv.reader(open('GO00.csv','rU'))

    t  = [x for x in r]
    t1  = np.array(t).T

    ra_sources_deg = t1[3,1:].astype('float')
    dec_sources_deg = t1[4,1:].astype('float')

    ra_deg, dec_deg, scRoll_deg = K2onSilicon.getRaDecRollFromFieldnum(
        fieldnum)

    fovRoll_deg = K2onSilicon.fov.getFovAngleFromSpacecraftRoll(scRoll_deg)
    k = K2onSilicon.fov.KeplerFov(ra_deg, dec_deg, fovRoll_deg)

    raDec = k.getCoordsOfChannelCorners()

    onSilicon = map(K2onSilicon.onSiliconCheck,
        ra_sources_deg,dec_sources_deg,np.repeat(k,len(ra_sources_deg)))

    nearSilicon = map(K2onSilicon.nearSiliconCheck,
        ra_sources_deg,dec_sources_deg,np.repeat(k,len(ra_sources_deg)))

    onSilicon = np.array(onSilicon,dtype=bool)
    nearSilicon = np.array(nearSilicon, dtype=bool)

    ##savetable

    ### doesnt' work properly!!!
    SiliconFlag = np.zeros_like(onSilicon,dtype=bool)
    SiliconFlag = np.where(nearSilicon,1,SiliconFlag)
    SiliconFlag = np.where(onSilicon,2,SiliconFlag)
    SiliconFlag = np.insert(SiliconFlag.astype(str),0,'SiliconFlag')
    outfile = 'GO00_Silicon.csv'
    newarr = np.zeros([np.shape(t1)[0]+1,np.shape(t1)[1]],dtype=str)
    newarr[0:np.shape(t1)[0],0:np.shape(t1)[1]] = t1
    newarr[-1] = SiliconFlag

    np.savetxt('GO00_Silicon.csv', newarr.T)




    do_plot = True
    do_degrees = True
    if do_plot:
        ph = K2onSilicon.proj.Cylindrical()
        targets = ph.skyToPix(ra_sources_deg, dec_sources_deg)
        if do_degrees:
            k.plotPointing(ph,showOuts=False,plot_degrees=True)
            fig = plt.gcf()
            ax = fig.gca()
            ax = fig.add_subplot(111)
            ax.scatter(np.degrees(targets[0]),
                np.degrees(targets[1]),s=0.5)
            ax.scatter(np.degrees(targets[0][nearSilicon]),
                np.degrees(targets[1][nearSilicon]),color='b',s=1)
            ax.scatter(np.degrees(targets[0][onSilicon]),
                np.degrees(targets[1][onSilicon]),color='r',s=1)

            ax.set_xlabel('R.A. [degrees]',fontsize=16)
            ax.set_ylabel('Declination [degrees]',fontsize=16)

        else:
            k.plotPointing(ph,showOuts=False)
            fig = plt.gcf()
            ax = fig.gca()
            ax = fig.add_subplot(111)
            ax.scatter(targets[0],
                targets[1],s=0.5)
            ax.scatter(targets[0][nearSilicon],
                targets[1][nearSilicon],color='b',s=1)
            ax.scatter(targets[0][onSilicon],
                targets[1][onSilicon],color='r',s=1)

            ax.set_xlabel('R.A. [radians]',fontsize=16)
            ax.set_ylabel('Declination [radians]',fontsize=16)



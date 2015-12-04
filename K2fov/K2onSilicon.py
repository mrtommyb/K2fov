"""
The code will accept a file containing a minimum of two columns RA Dec.
where RA and Dec are in decimal degrees
"""
from __future__ import division, print_function
import sys
import json
import logging

try:
    import numpy as np
except ImportError:
    print('You need numpy installed')
    sys.exit(1)

try:
    import matplotlib.pyplot as plt
    got_mpl = True
except ImportError:
    print('You need matplotlib installed to get a plot')
    got_mpl = False

from . import projection as proj
from . import fov


params = {
            'axes.linewidth': 1.5,
            'axes.labelsize': 24,
            'font.family': 'sans-serif',
            'font.size': 22,
            'legend.fontsize': 14,
            'xtick.labelsize': 16,
            'ytick.labelsize': 16,
            'text.usetex': False,
         }
if got_mpl:
    plt.rcParams.update(params)


def angSepVincenty(ra1, dec1, ra2, dec2):
    """
    Vincenty formula for distances on a sphere
    """
    ra1_rad = np.radians(ra1)
    dec1_rad = np.radians(dec1)
    ra2_rad = np.radians(ra2)
    dec2_rad = np.radians(dec2)

    sin_dec1, cos_dec1 = np.sin(dec1_rad), np.cos(dec1_rad)
    sin_dec2, cos_dec2 = np.sin(dec2_rad), np.cos(dec2_rad)
    delta_ra = ra2_rad - ra1_rad
    cos_delta_ra, sin_delta_ra = np.cos(delta_ra), np.sin(delta_ra)

    diffpos = np.arctan2(np.sqrt((cos_dec2 * sin_delta_ra) ** 2 +
                         (cos_dec1 * sin_dec2 -
                          sin_dec1 * cos_dec2 * cos_delta_ra) ** 2),
                         sin_dec1 * sin_dec2 + cos_dec1 * cos_dec2 * cos_delta_ra)

    return np.degrees(diffpos)


def parse_file(infile):
    try:
        a, b, mag = np.atleast_2d(
                            np.genfromtxt(
                                        infile,
                                        usecols=[0, 1, 2],
                                        delimiter=','
                                        )
                    ).T
    except IOError:
        print('There seems to be a problem with the input file, the format should be: RA_degrees (J2000), \
            Dec_degrees (J2000), Magnitude. There should be no header, columns should be seperated by a comma')
        sys.exit(1)
    return a, b, mag


def onSiliconCheck(ra_deg, dec_deg, FovObj):
    try:
        dist = angSepVincenty(FovObj.ra0_deg, FovObj.dec0_deg, ra_deg, dec_deg)
        if dist >= 90.:
            return False
        ch = FovObj.pickAChannel(ra_deg, dec_deg)
        ch, col, row = FovObj.getChannelColRow(ra_deg, dec_deg)
        # exclude modules 3 and 7
        if ch in [5, 6, 7, 8, 17, 18, 19, 20]:
            return False
        # return (ch,col,row)
        return True
    except ValueError:
        return False


def nearSiliconCheck(ra_deg, dec_deg, FovObj, max_sep=8.2):
    dist = angSepVincenty(FovObj.ra0_deg, FovObj.dec0_deg, ra_deg, dec_deg)
    if dist <= max_sep:
        return True
    else:
        return False


def getFieldInfo(fieldnum):
    """Returns a dictionary containing the metadata of a K2 Campaign field.

    Raises a ValueError if the field number is unknown.

    Parameters
    ----------
    fieldnum : int
        Campaign field number (e.g. 0, 1, 2, ...)

    Returns
    -------
    field : dict
        The dictionary contains the keys
        'ra', 'dec', 'roll' (floats in decimal degrees),
        'start', 'stop', (strings in YYYY-MM-DD format)
        and 'comments' (free text).
    """
    try:
        from . import CAMPAIGN_DICT_FILE
        CAMPAIGN_DICT = json.load(open(CAMPAIGN_DICT_FILE))
        info = CAMPAIGN_DICT["c{0}".format(fieldnum)]
        # Print warning messages if necessary
        if fieldnum == 100:
            logging.warning("You are using the K2 first light field, "
                            "you almost certainly do not want to do this")
        elif "preliminary" in info and info["preliminary"] == "True":
            logging.warning("The field you are searching is not yet fixed "
                            "and is only the proposed position. "
                            "Do not use this position for target selection.")
        return info
    except KeyError:
        raise ValueError("Field {0} not set in this version "
                         "of the code".format(fieldnum))


def getRaDecRollFromFieldnum(fieldnum):
    """Returns ra, dec, and roll for a campaign.

    All values returned are in decimal degrees.
    """
    info = getFieldInfo(fieldnum)
    return (info["ra"], info["dec"], info["roll"])


def getKeplerFov(fieldnum):
    """Returns a `fov.KeplerFov` object for a given campaign.

    Parameters
    ----------
    fieldnum : int
        K2 Campaign number.

    Returns
    -------
    fovobj : `fov.KeplerFov` object
        Details the footprint of the requested K2 campaign.
    """
    ra, dec, scRoll = getRaDecRollFromFieldnum(fieldnum)
    # convert from SC roll to FOV coordinates
    # do not use the fovRoll coords anywhere else
    # they are internal to this script only
    fovRoll = fov.getFovAngleFromSpacecraftRoll(scRoll)
    return fov.KeplerFov(ra, dec, fovRoll)


def K2onSilicon(infile, fieldnum):
    ra_sources_deg, dec_sources_deg, mag = parse_file(infile)

    if np.shape(ra_sources_deg)[0] > 500:
        logging.warning("There are {0} sources in your target list, "
                        "this could take some time".format(np.shape(ra_sources_deg)[0]))

    ra_deg, dec_deg, scRoll_deg = getRaDecRollFromFieldnum(fieldnum)

    # convert from SC roll to FOV coordinates
    # do not use the fovRoll coords anywhere else
    # they are internal to this script only
    fovRoll_deg = fov.getFovAngleFromSpacecraftRoll(scRoll_deg)

    # initialize class
    k = fov.KeplerFov(ra_deg, dec_deg, fovRoll_deg)

    raDec = k.getCoordsOfChannelCorners()

    onSilicon = list(
                    map(
                        onSiliconCheck,
                        ra_sources_deg,
                        dec_sources_deg,
                        np.repeat(k, len(ra_sources_deg))
                        )
                    )

    nearSilicon = list(
                    map(
                        nearSiliconCheck,
                        ra_sources_deg,
                        dec_sources_deg,
                        np.repeat(k, len(ra_sources_deg))
                        )
                    )

    onSilicon = np.array(onSilicon, dtype=bool)
    nearSilicon = np.array(nearSilicon, dtype=bool)

    if got_mpl:
        almost_black = '#262626'
        light_grey = np.array([float(248)/float(255)]*3)
        ph = proj.PlateCaree()
        k.plotPointing(ph, showOuts=False, plot_degrees=False)
        targets = ph.skyToPix(ra_sources_deg, dec_sources_deg)
        targets = np.array(targets)
        fig = plt.gcf()
        ax = fig.gca()
        ax = fig.add_subplot(111)
        ax.scatter(*targets, color='#fc8d62', s=7, label='not on silicon')
        ax.scatter(targets[0][onSilicon], targets[1][onSilicon],
                   color='#66c2a5', s=8, label='on silicon')
        ax.set_xlabel('R.A. [degrees]', fontsize=16)
        ax.set_ylabel('Declination [degrees]', fontsize=16)
        ax.invert_xaxis()
        ax.minorticks_on()
        legend = ax.legend(loc=0, frameon=True, scatterpoints=1)
        rect = legend.get_frame()
        rect.set_alpha(0.3)
        rect.set_facecolor(light_grey)
        rect.set_linewidth(0.0)
        texts = legend.texts
        for t in texts:
            t.set_color(almost_black)
        fig.savefig('targets_fov.png', dpi=300)
        plt.close('all')

    siliconFlag = np.zeros_like(ra_sources_deg)

    # prints zero if target is not on silicon
    siliconFlag = np.where(nearSilicon, 0, siliconFlag)

    # prints a 2 if target is on silicon
    siliconFlag = np.where(onSilicon, 2, siliconFlag)

    outarr = np.array([ra_sources_deg, dec_sources_deg, mag, siliconFlag])
    np.savetxt('targets_siliconFlag.csv', outarr.T, delimiter=', ',
               fmt=['%10.10f', '%10.10f', '%10.2f', '%i'])

    if got_mpl:
        print('I made two files: targets_siliconFlag.csv and targets_fov.png')
    else:
        print('I made one file: targets_siliconFlag.csv')


def K2onSilicon_main(args=None):
    """Function called when `K2onSilicon` is executed on the command line."""
    import argparse
    parser = argparse.ArgumentParser(
        description="Run K2onSilicon to find which targets in a "
                    "list call on active silicon for a given K2 campaign.")
    parser.add_argument('csv_file', type=str,
                        help="Name of input csv file with targets, column are "
                             "Ra_degrees, Dec_degrees, Kepmag")
    parser.add_argument('campaign', type=int, help='K2 Campaign number')
    args = parser.parse_args(args)
    K2onSilicon(args.csv_file, args.campaign)


if __name__ == '__main__':
    K2onSilicon_main()

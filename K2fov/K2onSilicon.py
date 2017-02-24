"""
The code will accept a file containing a minimum of two columns RA Dec.
where RA and Dec are in decimal degrees
"""
from __future__ import division, print_function
import sys

from . import logger

# Try importing numpy
try:
    import numpy as np
except Exception:
    logger.error('You need numpy installed')
    sys.exit(1)

# Try importing matplotlib
try:
    import matplotlib.pyplot as pl
    got_mpl = True
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
    pl.rcParams.update(params)
except Exception:
    logger.warning('You need matplotlib installed to get a plot')
    got_mpl = False

from . import fields
from . import projection as proj
from . import DEFAULT_PADDING


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


def parse_file(infile, exit_on_error=True):
    """Parse a comma-separated file with columns "ra,dec,magnitude".
    """
    try:
        a, b, mag = np.atleast_2d(
                            np.genfromtxt(
                                        infile,
                                        usecols=[0, 1, 2],
                                        delimiter=','
                                        )
                    ).T
    except IOError as e:
        if exit_on_error:
            logger.error("There seems to be a problem with the input file, "
                         "the format should be: RA_degrees (J2000), Dec_degrees (J2000), "
                         "Magnitude. There should be no header, columns should be "
                         "separated by a comma")
            sys.exit(1)
        else:
            raise e
    return a, b, mag


def onSiliconCheck(ra_deg, dec_deg, FovObj, padding_pix=DEFAULT_PADDING):
    """Check a single position."""
    dist = angSepVincenty(FovObj.ra0_deg, FovObj.dec0_deg, ra_deg, dec_deg)
    if dist >= 90.:
        return False
    # padding_pix=3 means that objects less than 3 pixels off the edge of
    # a channel are counted inside, to account for inaccuracies in K2fov.
    return FovObj.isOnSilicon(ra_deg, dec_deg, padding_pix=padding_pix)


def onSiliconCheckList(ra_deg, dec_deg, FovObj, padding_pix=DEFAULT_PADDING):
    """Check a list of positions."""
    dist = angSepVincenty(FovObj.ra0_deg, FovObj.dec0_deg, ra_deg, dec_deg)
    mask = (dist < 90.)
    out = np.zeros(len(dist), dtype=bool)
    out[mask] = FovObj.isOnSiliconList(ra_deg[mask], dec_deg[mask], padding_pix=padding_pix)
    return out


def nearSiliconCheck(ra_deg, dec_deg, FovObj, max_sep=8.2):
    dist = angSepVincenty(FovObj.ra0_deg, FovObj.dec0_deg, ra_deg, dec_deg)
    if dist <= max_sep:
        return True
    else:
        return False


def getRaDecRollFromFieldnum(fieldnum):
    """Returns ra, dec, and roll for a campaign.

    All values returned are in decimal degrees.
    """
    info = fields.getFieldInfo(fieldnum)
    return (info["ra"], info["dec"], info["roll"])


def K2onSilicon(infile, fieldnum, do_nearSiliconCheck=False):
    """Checks whether targets are on silicon during a given campaign.

    This function will write a csv table called targets_siliconFlag.csv,
    which details the silicon status for each target listed in `infile`
    (0 = not on silicon, 2 = on silion).

    Parameters
    ----------
    infile : str
        Path to a csv table with columns ra_deg,dec_deg,magnitude (no header).

    fieldnum : int
        K2 Campaign number.

    do_nearSiliconCheck : bool
        If `True`, targets near (but not on) silicon are flagged with a "1".
    """
    ra_sources_deg, dec_sources_deg, mag = parse_file(infile)
    n_sources = np.shape(ra_sources_deg)[0]
    if n_sources > 500:
        logger.warning("Warning: there are {0} sources in your target list, "
                       "this could take some time".format(n_sources))

    k = fields.getKeplerFov(fieldnum)
    raDec = k.getCoordsOfChannelCorners()

    onSilicon = list(
                    map(
                        onSiliconCheck,
                        ra_sources_deg,
                        dec_sources_deg,
                        np.repeat(k, len(ra_sources_deg))
                        )
                    )
    onSilicon = np.array(onSilicon, dtype=bool)

    if do_nearSiliconCheck:
        nearSilicon = list(
                        map(
                            nearSiliconCheck,
                            ra_sources_deg,
                            dec_sources_deg,
                            np.repeat(k, len(ra_sources_deg))
                            )
                        )
        nearSilicon = np.array(nearSilicon, dtype=bool)

    if got_mpl:
        almost_black = '#262626'
        light_grey = np.array([float(248)/float(255)]*3)
        ph = proj.PlateCaree()
        k.plotPointing(ph, showOuts=False)
        targets = ph.skyToPix(ra_sources_deg, dec_sources_deg)
        targets = np.array(targets)
        fig = pl.gcf()
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
        pl.close('all')

    # prints zero if target is not on silicon
    siliconFlag = np.zeros_like(ra_sources_deg)

    # print a 1 if target is near but not on silicon
    if do_nearSiliconCheck:
        siliconFlag = np.where(nearSilicon, 1, siliconFlag)

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

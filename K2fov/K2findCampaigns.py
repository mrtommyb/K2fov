"""Implements the `K2findCampaigns` tools.

These tools allow to check whether a position or object is visible in any
campaign.  This complements K2onSilicon, which only determines whether an
object is on silicon for a single campaign.
"""
import sys
import argparse
import numpy as np

from . import fields
from . import logger
from . import Highlight
from .K2onSilicon import parse_file, onSiliconCheck


def printChannelColRow(campaign, ra, dec):
    """Prints the channel, col, row for a given campaign and coordinate."""
    fovobj = fields.getKeplerFov(campaign)
    ch, col, row = fovobj.getChannelColRow(ra, dec)
    print("Position in C{}: channel {}, col {:.0f}, row {:.0f}.".format(campaign, int(ch), col, row))


def findCampaigns(ra, dec):
    """Returns a list of the campaigns that cover a given position.

    Parameters
    ----------
    ra, dec : float, float
        Position in decimal degrees (J2000).

    Returns
    -------
    campaigns : list of int
        A list of the campaigns that cover the given position.
    """
    # Temporary disable the logger to avoid the preliminary field warnings
    logger.disabled = True
    campaigns_visible = []
    for c in fields.getFieldNumbers():
        fovobj = fields.getKeplerFov(c)
        if onSiliconCheck(ra, dec, fovobj):
            campaigns_visible.append(c)
    # Re-enable the logger
    logger.disabled = True
    return campaigns_visible


def findCampaignsByName(target):
    """Returns a list of the campaigns that cover a given target.

    Parameters
    ----------
    target : str
        Name of the celestial object.

    Returns
    -------
    campaigns : list of int
        A list of the campaigns that cover the given target name.

    ra, dec : float, float
        Resolved coordinates in decimal degrees (J2000).

    Exceptions
    ----------
    Raises an ImportError if AstroPy is not installed.
    Raises a ValueError if `name` cannot be resolved to coordinates.
    """
    # Is AstroPy (optional dependency) installed?
    try:
        from astropy.coordinates import SkyCoord
        from astropy.coordinates.name_resolve import NameResolveError
        from astropy.utils.data import conf
        conf.remote_timeout = 90
    except ImportError:
        print('Error: AstroPy needs to be installed for this feature.')
        sys.exit(1)
    # Translate the target name into celestial coordinates
    try:
        crd = SkyCoord.from_name(target)
    except NameResolveError:
        raise ValueError('Could not find coordinates '
                         'for target "{0}".'.format(target))
    # Find the campaigns with visibility
    return findCampaigns(crd.ra.deg, crd.dec.deg), crd.ra.deg, crd.dec.deg


def save_context_plots(ra, dec, targetname=""):
    from . import plot
    output_fn = "K2findCampaigns.png"
    print("Writing {0}".format(output_fn))
    myplot = plot.create_context_plot(ra, dec, name=targetname)
    myplot.fig.savefig(output_fn, dpi=300)

    output_fn = "K2findCampaigns-zoom.png"
    print("Writing {0}".format(output_fn))
    myplot = plot.create_context_plot_zoomed(ra, dec, name=targetname)
    myplot.fig.savefig(output_fn, dpi=300)


def K2findCampaigns_main(args=None):
    """Exposes K2findCampaigns to the command line."""
    parser = argparse.ArgumentParser(
                    description="Check if a celestial coordinate is "
                                "(or was) observable by any past or future "
                                "observing campaign of NASA's K2 mission.")
    parser.add_argument('ra', nargs=1, type=float,
                        help="Right Ascension in decimal degrees (J2000).")
    parser.add_argument('dec', nargs=1, type=float,
                        help="Declination in decimal degrees (J2000).")
    parser.add_argument('-p', '--plot', action='store_true',
                        help="Produce a plot showing the target position "
                             "with respect to all K2 campaigns.")
    args = parser.parse_args(args)
    ra, dec = args.ra[0], args.dec[0]
    campaigns = findCampaigns(ra, dec)
    # Print the result
    if len(campaigns):
        print(Highlight.GREEN + "Success! The target is on silicon "
              "during K2 campaigns {0}.".format(campaigns) + Highlight.END)
    else:
        print(Highlight.RED + "Sorry, the target is not on silicon "
              "during any K2 campaign." + Highlight.END)
    # Print the pixel positions
    for c in campaigns:
        printChannelColRow(c, ra, dec)
    # Make a context plot if the user requested so
    if args.plot:
        save_context_plots(ra, dec, "Your object")


def K2findCampaigns_byname_main(args=None):
    """Exposes K2findCampaigns to the command line."""
    parser = argparse.ArgumentParser(
                    description="Check if a target is "
                                "(or was) observable by any past or future "
                                "observing campaign of NASA's K2 mission.")
    parser.add_argument('name', nargs=1, type=str,
                        help="Name of the object.  This will be passed on "
                             "to the CDS name resolver "
                             "to retrieve coordinate information.")
    parser.add_argument('-p', '--plot', action='store_true',
                        help="Produce a plot showing the target position "
                             "with respect to all K2 campaigns.")
    args = parser.parse_args(args)
    targetname = args.name[0]
    try:
        campaigns, ra, dec = findCampaignsByName(targetname)
    except ValueError:
        print("Error: could not retrieve coordinates for {0}.".format(targetname))
        print("The target may be unknown or there may be a problem "
              "connecting to the coordinate server.")
        sys.exit(1)
    # Print the result
    if len(campaigns):
        print(Highlight.GREEN +
              "Success! {0} is on silicon ".format(targetname) +
              "during K2 campaigns {0}.".format(campaigns) +
              Highlight.END)
    else:
        print(Highlight.RED + "Sorry, {} is not on silicon "
              "during any K2 campaign.".format(targetname) + Highlight.END)
    # Print the pixel positions
    for c in campaigns:
        printChannelColRow(c, ra, dec)
    # Make a context plot if the user requested so
    if args.plot:
        save_context_plots(ra, dec, targetname=targetname)


def K2findCampaigns_csv_main(args=None):
    """Exposes K2findCampaigns-csv to the command line."""
    parser = argparse.ArgumentParser(
                    description="Check which objects listed in a CSV table "
                                "are (or were) observable by NASA's K2 mission.")
    parser.add_argument('input_filename', nargs=1, type=str,
                        help="Path to a comma-separated table containing "
                             "columns 'ra,dec,kepmag' (decimal degrees) "
                             "or 'name'.")
    args = parser.parse_args(args)
    input_fn = args.input_filename[0]
    output_fn = input_fn + '-K2findCampaigns.csv'
    # First, try assuming the file has the classic "ra,dec,kepmag" format
    try:
        ra, dec, kepmag = parse_file(input_fn, exit_on_error=False)
        campaigns = np.array([findCampaigns(ra[idx], dec[idx])
                              for idx in range(len(ra))])
        output = np.array([ra, dec, kepmag, campaigns])
        print("Writing {0}.".format(output_fn))
        np.savetxt(output_fn, output.T, delimiter=', ',
                   fmt=['%10.10f', '%10.10f', '%10.2f', '%s'])
    # If this fails, assume the file has a single "name" column
    except ValueError:
        names = [name.strip() for name in open(input_fn, "r").readlines()
                 if len(name.strip()) > 0]
        print("Writing {0}.".format(output_fn))
        output = open(output_fn, "w")
        for target in names:
            try:
                campaigns, ra, dec = findCampaignsByName(target)
            except ValueError:
                campaigns = []
            output.write("{0}, {1}\n".format(target, campaigns))
            output.flush()
        output.close()

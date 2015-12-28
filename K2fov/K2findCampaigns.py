"""Implements the K2findCampaigns tool.

The tool allows to check whether a position or object is visible in any
campaign.  This complements K2onSilicon, which only determines whether an
object is on silicon for a single campaign.
"""
import argparse
import numpy as np

from . import fields
from . import logger
from . import Highlight
from .K2onSilicon import (parse_file, onSiliconCheck)


def findCampaigns(ra, dec):
    """Returns a list of the campaigns that cover a given position."""
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
    # parser.add_argument('-p', '--plot', action='store_true',
    #                    help="Produce a plot showing the target position "
    #                         "with respect to all K2 campaigns. ")
    args = parser.parse_args(args)
    campaigns = findCampaigns(args.ra, args.dec)
    # Print the result
    if len(campaigns):
        print(Highlight.GREEN + "Success! The target is on silicon "
              "during K2 campaigns {0}.".format(campaigns) + Highlight.END)
    else:
        print(Highlight.RED + "Sorry, the target is not on silicon "
              "during any K2 campaign." + Highlight.END)
    # if args.plot:


def K2findCampaigns_csv_main(args=None):
    """Exposes K2findCampaigns-csv to the command line."""
    parser = argparse.ArgumentParser(
                    description="Check which objects listed in a CSV table "
                                "are (or were) observable by NASA's K2 mission.")
    parser.add_argument('input_filename', nargs=1, type=str,
                        help="Path to a comma-separated table containing columns 'ra,dec,kepmag' with ra and dec in decimal degrees.")
    #parser.add_argument('-p', '--plot', nargs=1, metavar="filename",
    #                    help="Produce a plot showing the target positions "
    #                         "with respect to all K2 campaigns.")
    args = parser.parse_args(args)
    ra, dec, kepmag = parse_file(args.input_filename[0])
    campaigns = np.array([findCampaigns(ra[idx], dec[idx])
                          for idx in range(len(ra))])
    output = np.array([ra, dec, kepmag, campaigns])
    output_fn = 'K2findCampaigns-output.csv'
    logger.info("Writing {0}.".format(output_fn))
    np.savetxt(output_fn, output.T, delimiter=', ',
               fmt=['%10.10f', '%10.10f', '%10.2f', '%s'])

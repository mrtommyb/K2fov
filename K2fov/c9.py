"""Functions that detail the K2C9 microlensing superstamp.
"""
from __future__ import print_function

import os
import json
import numpy as np

from . import PACKAGEDIR, logger, getKeplerFov

__all__ = ['inMicrolensRegion', 'pixelInMicrolensRegion']

# Load the JSON file that defines the C9 superstamp
SUPERSTAMP_FN = os.path.join(PACKAGEDIR, "data", "k2-c9-microlens-region.json")
SUPERSTAMP = json.load(open(SUPERSTAMP_FN))

# Late targets
LATE_TARGETS_FN = os.path.join(PACKAGEDIR, "data", "k2-c9b-late-targets.json")
LATE_TARGETS = json.load(open(LATE_TARGETS_FN))


def inMicrolensRegion_main(args=None):
    """Exposes K2visible to the command line."""
    import argparse
    parser = argparse.ArgumentParser(
                    description="Check if a celestial coordinate is "
                                "inside the K2C9 microlensing superstamp.")
    parser.add_argument('ra', nargs=1, type=float,
                        help="Right Ascension in decimal degrees (J2000).")
    parser.add_argument('dec', nargs=1, type=float,
                        help="Declination in decimal degrees (J2000).")
    args = parser.parse_args(args)
    if inMicrolensRegion(args.ra[0], args.dec[0]):
        print("Yes! The coordinate is inside the K2C9 superstamp.")
    else:
        print("Sorry, the coordinate is NOT inside the K2C9 superstamp.")


def inMicrolensRegion(ra_deg, dec_deg, padding=0):
    """Returns `True` if the given sky oordinate falls on the K2C9 superstamp.

    Parameters
    ----------
    ra_deg : float
        Right Ascension (J2000) in decimal degrees.

    dec_deg : float
        Declination (J2000) in decimal degrees.

    padding : float
        Target must be at least `padding` pixels away from the edge of the
        superstamp. (Note that CCD boundaries are not considered as edges
        in this case.)

    Returns
    -------
    onMicrolensRegion : bool
        `True` if the given coordinate is within the K2C9 microlens superstamp.
    """
    fov = getKeplerFov(9)
    try:
        ch, col, row = fov.getChannelColRow(ra_deg, dec_deg,
                                            allowIllegalReturnValues=False)
        return maskInMicrolensRegion(ch, col, row, padding=padding)
    except ValueError:
        return False


def pixelInMicrolensRegion(ch, col, row):
    """Returns `True` if the given pixel falls inside the K2C9 superstamp.

    The superstamp is used for microlensing experiment and is an almost
    contiguous area of 2.8e6 pixels.
    """
    # First try the superstamp
    try:
        vertices_col = SUPERSTAMP["channels"][str(int(ch))]["vertices_col"]
        vertices_row = SUPERSTAMP["channels"][str(int(ch))]["vertices_row"]
        # The point is in one of 5 channels which constitute the superstamp
        # so check if it falls inside the polygon for this channel
        if isPointInsidePolygon(col, row, vertices_col, vertices_row):
            return True
    except KeyError:  # Channel does not appear in file
        pass

    # Then try the late target masks
    for mask in LATE_TARGETS["masks"]:
        if mask["channel"] == ch:
            vertices_col = mask["vertices_col"]
            vertices_row = mask["vertices_row"]
            if isPointInsidePolygon(col, row, vertices_col, vertices_row):
                return True

    return False


def maskInMicrolensRegion(ch, col, row, padding=0):
    """Is a target in the K2C9 superstamp, including padding?

    This function is identical to pixelInMicrolensRegion, except it takes
    the extra `padding` argument. The coordinate must be within the K2C9
    superstamp by at least `padding` number of pixels on either side of the
    coordinate.  (Note that this function does not check whether something is
    close to the CCD boundaries, it only checks whether something is close
    to the edge of stamp.)
    """
    if padding == 0:
        return pixelInMicrolensRegion(ch, col, row)

    combinations = [[col - padding, row],
                    [col + padding, row],
                    [col, row - padding],
                    [col, row + padding]]
    for col, row in combinations:
        # Science pixels occupy columns 12 - 1111, rows 20 - 1043
        if col < 12:
            col = 12
        if col > 1111:
            col = 1111
        if row < 20:
            row = 20
        if row > 1043:
            row = 1043
        if not pixelInMicrolensRegion(ch, col, row):
            return False
    return True

def isPointInsidePolygon(x, y, vertices_x, vertices_y):
    """Check if a given point is inside a polygon.

    Parameters vertices_x[] and vertices_y[] define the polygon.
    The number of array elements is equal to number of vertices of the polygon.
    This function works for convex and concave polygons.

    Parameters
    ----------
    vertices_x, vertices_y : lists or arrays of floats
        Vertices that define the polygon.

    x, y : float
        Coordinates of the point to check.

    Returns
    -------
    inside : bool
        `True` if the point is inside the polygon.
    """
    inside = False
    for i in range(len(vertices_x)):
        j = i - 1
        if ((vertices_x[i] > x) != (vertices_x[j] > x)):
            if (y < (x - vertices_x[i]) *
                    (vertices_y[i] - vertices_y[j]) /
                    (vertices_x[i] - vertices_x[j]) +
                    vertices_y[i]):
                inside = not inside
    return inside


class C9FootprintPlot(object):
    """Create a plot showing the C9 footprint and superstamp.
    """
    def __init__(self, axes=None):
        if axes is None:
            import matplotlib.pyplot as pl
            params = {
                        'axes.linewidth': 1.,
                        'axes.labelsize': 20,
                        'font.family': 'sans-serif',
                        'font.size': 22,
                        'legend.fontsize': 14,
                        'xtick.labelsize': 16,
                        'ytick.labelsize': 16,
                        'text.usetex': False,
                     }
            pl.rcParams.update(params)
            self.fig = pl.figure(figsize=(8, 4.5))
            self.ax = self.fig.add_subplot(111)
        else:
            self.ax = axes

        self.ax.set_ylim([-30, -14])
        self.ax.set_xlim([280, 260])
        self.ax.set_xlabel("RA [deg]")
        self.ax.set_ylabel("Dec [deg]")

    def plot_outline(self, annotate_late_targets=False, annotate_channels=False):
        """Plots the coverage of both the channels and the C9 superstamp."""
        fov = getKeplerFov(9)
        # Plot the superstamp
        superstamp_patches = []
        for ch in SUPERSTAMP["channels"]:
            v_col = SUPERSTAMP["channels"][ch]["vertices_col"]
            v_row = SUPERSTAMP["channels"][ch]["vertices_row"]
            radec = np.array([
                                fov.getRaDecForChannelColRow(int(ch),
                                                             v_col[idx],
                                                             v_row[idx])
                                for idx in range(len(v_col))
                              ])
            patch = self.ax.fill(radec[:, 0], radec[:, 1],
                                 lw=0, facecolor="#27ae60", zorder=100)
            superstamp_patches.append(patch)

        # Plot the late target masks
        late_target_patches = []
        for mask in LATE_TARGETS["masks"]:
            ch = mask["channel"]
            v_col = mask["vertices_col"]
            v_row = mask["vertices_row"]
            radec = np.array([
                                fov.getRaDecForChannelColRow(int(ch),
                                                             v_col[idx],
                                                             v_row[idx])
                                for idx in range(len(v_col))
                              ])
            patch = self.ax.fill(radec[:, 0], radec[:, 1],
                                 lw=0, facecolor="#27ae60", zorder=201)
            late_target_patches.append(patch)
            if annotate_late_targets and 'context' not in mask["name"]:
                self.ax.text(np.mean(radec[:, 0]), np.mean(radec[:, 1]), '  ' + mask["name"],
                             ha="left", va="center",
                             zorder=950, fontsize=10,
                             color="#c0392b", clip_on=True)

        # Plot all channel outlines
        channel_patches = []
        corners = fov.getCoordsOfChannelCorners()
        for ch in np.arange(1, 85, dtype=int):
            if ch in fov.brokenChannels:
                continue  # certain channel are no longer used
            idx = np.where(corners[::, 2] == ch)
            mdl = int(corners[idx, 0][0][0])
            out = int(corners[idx, 1][0][0])
            ra = corners[idx, 3][0]
            dec = corners[idx, 4][0]
            patch = self.ax.fill(np.concatenate((ra, ra[:1])),
                                 np.concatenate((dec, dec[:1])),
                                 lw=0, facecolor="#cccccc", zorder=50)
            channel_patches.append(patch)
            if annotate_channels:
                txt = "{}.{}\n#{}".format(mdl, out, ch)
                self.ax.text(np.mean(ra), np.mean(dec), txt,
                             ha="center", va="center",
                             zorder=900, fontsize=14,
                             color="#000000", clip_on=True)
        return superstamp_patches, channel_patches


def plot_c9(output_fn="c9.png"):
    p = C9FootprintPlot()
    p.plot_outline(annotate_channels=True, annotate_late_targets=True)
    p.fig.tight_layout()
    p.fig.savefig(output_fn)
    p.fig.show()

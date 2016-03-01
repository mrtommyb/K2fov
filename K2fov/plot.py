"""Make pretty footprint plots.

This file contains plotting code by Geert.
Alternative plotting routines from Fergal are available.
"""
import sys
import numpy as np

from . import getKeplerFov, logger

# Now try loading matplotlib
try:
    import matplotlib.pyplot as pl
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
    logger.error('This feature requires matplotlib to be installed.')
    sys.exit(1)


class K2FootprintPlot(object):

    def __init__(self, axes=None, figsize=(16, 5)):
        if axes is None:
            self.fig = pl.figure(figsize=figsize)
            self.ax = self.fig.add_subplot(111)
        else:
            self.ax = axes
        self.ax.set_ylim([-35, 35])
        self.ax.set_xlim([0, 360])
        self.ax.set_xlabel("RA [deg]")
        self.ax.set_ylabel("Dec [deg]")
        try:
            self.fig.tight_layout()
        except AttributeError:  # We didn't create a fig above
            pass

    def plot_campaigns(self, campaigns=18):
        """Plot the outlines of all campaigns."""
        for c in range(campaigns):
            self.plot_campaign_outline(c)

    def plot_campaign_outline(self, campaign=0, facecolor="#666666"):
        """Plot the outline of a campaign as a contiguous gray patch.

        Parameters
        ----------
        campaign : int
            K2 Campaign number.

        facecolor : str
            Color of the patch.
        """
        # The outline is composed of two filled rectangles,
        # defined by the first coordinate of the corner of four channels each
        fov = getKeplerFov(campaign)
        corners = fov.getCoordsOfChannelCorners()
        for rectangle in [[4, 75, 84, 11], [15, 56, 71, 32]]:
            ra_outline, dec_outline = [], []
            for channel in rectangle:
                idx = np.where(corners[::, 2] == channel)
                ra_outline.append(corners[idx, 3][0][0])
                dec_outline.append(corners[idx, 4][0][0])
            self.ax.fill(ra_outline + ra_outline[:1],
                         dec_outline + dec_outline[:1],
                         facecolor=facecolor, zorder=151, lw=0)
        # Print the campaign number on top of the outline
        ra, dec, roll = fov.getBoresight()
        self.ax.text(ra, dec, "{}".format(campaign),
                     fontsize=18, color="white", ha="center", va="center",
                     zorder=155)

    def plot_campaign(self, campaign=0, annotate_channels=True):
        """Plot all the active channels of a campaign."""
        fov = getKeplerFov(campaign)
        corners = fov.getCoordsOfChannelCorners()

        for ch in np.arange(1, 85, dtype=int):
            if ch in fov.brokenChannels:
                continue  # certain channel are no longer used
            idx = np.where(corners[::, 2] == ch)
            mdl = int(corners[idx, 0][0][0])
            out = int(corners[idx, 1][0][0])
            ra = corners[idx, 3][0]
            dec = corners[idx, 4][0]
            self.ax.fill(np.concatenate((ra, ra[:1])),
                         np.concatenate((dec, dec[:1])),
                         lw=0, facecolor="#bbbbbb", zorder=90)
            if annotate_channels:
                txt = "K2C{0}\n{1}.{2}\n#{3}".format(campaign, mdl, out, ch)
                self.ax.text(np.mean(ra), np.mean(dec), txt,
                             ha="center", va="center",
                             zorder=91, fontsize=10,
                             color="#666666", clip_on=True)

    def plot_ecliptic(self, size=100):
        try:
            from astropy.coordinates import SkyCoord
        except ImportError:
            logger.error("You need to install AstroPy for this feature.")
            return None
        try:
            icrs = SkyCoord(np.linspace(0, 359, num=size), 0,
                            unit="deg", frame="barycentrictrueecliptic").icrs
            self.ax.plot(icrs.ra, icrs.dec, lw=2, color="#666666")
        except ValueError:
            # only AstroPy 1.1 and up support ecliptic coordinates;
            # avoid crashing if an older version of AstroPy is at play
            pass

    def plot_galactic(self, size=150, color="#bbbbbb", textcolor="#777777"):
        try:
            from astropy.coordinates import SkyCoord
        except ImportError:
            logger.error("You need to install AstroPy for this feature.")
            return None
        icrs = SkyCoord(np.linspace(0, 359, num=size), 0,
                        unit="deg", frame="galactic").icrs
        self.ax.plot(icrs.ra, icrs.dec, lw=20, color=color)
        self.ax.text(116, -17, "Galactic Plane", rotation=-60,
                     fontsize=12, color=textcolor)

    def plot(self):
        self.plot_galactic()
        self.plot_ecliptic()
        self.plot_campaigns()


def create_context_plot(ra, dec, name="Your object"):
    """Creates a K2FootprintPlot showing a given position in context
    with respect to the campaigns."""
    plot = K2FootprintPlot()
    plot.plot_galactic()
    plot.plot_ecliptic()
    for c in range(0, 11):
        plot.plot_campaign_outline(c, facecolor="#666666")
    for c in [11, 12, 13, 14, 15, 16, 17, 18]:
        plot.plot_campaign_outline(c, facecolor="green")
    plot.ax.scatter(ra, dec, marker='x', s=250, lw=3, color="red", zorder=500)
    plot.ax.text(ra, dec - 2, name,
                 ha="center", va="top", color="red",
                 fontsize=20, fontweight='bold', zorder=501)
    return plot


def create_context_plot_zoomed(ra, dec, name="Your object", size=3):
    """Creates a K2FootprintPlot showing a given position in context
    with respect to the campaigns."""
    plot = K2FootprintPlot(figsize=(8, 8))
    for c in range(0, 19):
        plot.plot_campaign(c)
    plot.ax.scatter(ra, dec, marker='x', s=250, lw=3, color="red", zorder=500)
    plot.ax.text(ra, dec - 0.05*size, name,
                 ha="center", va="top", color="red",
                 fontsize=20, fontweight='bold', zorder=501)
    plot.ax.set_xlim([ra - size/2., ra + size/2.])
    plot.ax.set_ylim([dec - size/2., dec + size/2.])
    return plot


if __name__ == "__main__":
    plot = K2FootprintPlot()
    plot.plot_galactic()
    plot.plot_ecliptic()
    for c in range(0, 9):
        plot.plot_campaign_outline(c, facecolor="#666666")
    for c in [9, 10]:
        plot.plot_campaign_outline(c, facecolor="red")
    for c in [11, 12, 13, 14, 15, 16, 17, 18]:
        plot.plot_campaign_outline(c, facecolor="green")
    plot.fig.show()

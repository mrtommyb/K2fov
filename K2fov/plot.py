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
    from matplotlib.ticker import FuncFormatter
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


def rafmt(x, pos):
    """Formatter function for Right Ascension."""
    return "{:.0f}°".format(x)


def decfmt(x, pos):
    """Formatter function for Declination."""
    return "{:+.0f}°".format(x)


class K2FootprintPlot(object):

    def __init__(self, axes=None, figsize=(16, 5)):
        if axes is None:
            self.fig = pl.figure(figsize=figsize)
            self.ax = self.fig.add_subplot(111)
        else:
            self.ax = axes
        self.ax.set_xticks(np.arange(0, 361, 30))
        self.ax.set_ylim([-37, 37])
        self.ax.set_xlim([360, 0])
        self.ax.xaxis.set_major_formatter(FuncFormatter(rafmt))
        self.ax.yaxis.set_major_formatter(FuncFormatter(decfmt))
        self.ax.set_xlabel("RA")
        self.ax.set_ylabel("Dec")
        try:
            self.fig.tight_layout()
        except AttributeError:  # We didn't create a fig above
            pass

    def plot_campaigns(self, campaigns=19):
        """Plot the outlines of all campaigns."""
        for c in range(campaigns):
            self.plot_campaign_outline(c)

    def plot_campaign_outline(self, campaign=0, facecolor="#666666", text=None):
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
            ra = np.array(ra_outline + ra_outline[:1])
            dec = np.array(dec_outline + dec_outline[:1])
            if campaign == 1002:  # Overlaps the meridian
                ra[ra > 180] -= 360
            myfill = self.ax.fill(ra, dec,
                                  facecolor=facecolor,
                                  zorder=151, lw=0)
        # Print the campaign number on top of the outline
        if text is None:
            text = "{}".format(campaign)
        ra_center, dec_center, _ = fov.getBoresight()
        if campaign == 6:
            dec_center -= 2
        elif campaign == 12:
            ra_center += 0.5
            dec_center -= 1.7
        elif campaign == 16:
            dec_center += 1.5
        elif campaign == 18:
            dec_center -= 1.5
        elif campaign == 19:
            dec_center += 1.7
        offsets = {5: (40, -20), 16: (-20, 40), 18: (-15, -50)}
        if campaign in [5]:
            pl.annotate(text, xy=(ra_center, dec_center),
                        xycoords='data', ha='center',
                        xytext=offsets[campaign], textcoords='offset points',
                        size=18, zorder=0, color=facecolor,
                        arrowprops=dict(arrowstyle="-", ec=facecolor, lw=2))
        else:
            self.ax.text(ra_center, dec_center, text,
                         fontsize=18, color="white",
                         ha="center", va="center",
                         zorder=155)
        return myfill

    def plot_campaign(self, campaign=0, annotate_channels=True, zorder=90,
                      lw=0, edgecolor='black', facecolor="#999999"):
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
            #if np.any(ra > 340):  # Engineering test field overlaps meridian
            #    ra[ra > 180] -= 360
            dec = corners[idx, 4][0]
            self.ax.fill(np.concatenate((ra, ra[:1])),
                         np.concatenate((dec, dec[:1])),
                         lw=lw, edgecolor=edgecolor,
                         facecolor=facecolor, zorder=zorder)
            if annotate_channels:
                txt = "K2C{0}\n{1}.{2}\n#{3}".format(campaign, mdl, out, ch)
                txt = "{1}.{2}\n#{3}".format(campaign, mdl, out, ch)
                self.ax.text(np.mean(ra), np.mean(dec), txt,
                             ha="center", va="center",
                             zorder=91, fontsize=10,
                             color="#000000", clip_on=True)

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
        self.ax.text(114, -12, "Galactic Plane", rotation=65,
                     fontsize=12, color=textcolor)

    def plot(self):
        self.plot_galactic()
        self.plot_ecliptic()
        self.plot_campaigns()


class K2GalacticFootprintPlot(object):

    def __init__(self, axes=None, figsize=(11, 6)):
        if axes is None:
            self.fig = pl.figure(figsize=figsize)
            self.ax = self.fig.add_subplot(111)
        else:
            self.ax = axes
        self.ax.set_ylim([-90, 90])
        self.ax.set_xlim([190, -180])
        self.ax.set_xlabel("Galactic longitude [deg]")
        self.ax.set_ylabel("Galactic latitude [deg]")
        try:
            self.fig.tight_layout()
        except AttributeError:  # We didn't create a fig above
            pass

    def plot_ecliptic(self, size=100):
        try:
            from astropy.coordinates import SkyCoord
        except ImportError:
            logger.error("You need to install AstroPy for this feature.")
            return None
        try:
            gal = SkyCoord(np.linspace(0, 359, num=size), 0,
                           unit="deg", frame="barycentrictrueecliptic").galactic
            # Hack to avoid line crossing zero:
            l = gal.l.deg
            l[l > 180] -= 360
            idx = np.argsort(l)
            self.ax.plot(l[idx], gal.b.deg[idx], lw=2, color="#666666")
        except ValueError:
            # only AstroPy 1.1 and up support ecliptic coordinates;
            # avoid crashing if an older version of AstroPy is at play
            pass

    def plot_campaigns(self, campaigns=19):
        """Plot the outlines of all campaigns."""
        for c in range(campaigns):
            self.plot_campaign_outline(c)

    def plot_campaign_outline(self, campaign=0, facecolor="#666666", text=None, dashed=False):
        """Plot the outline of a campaign as a contiguous gray patch.

        Parameters
        ----------
        campaign : int
            K2 Campaign number.

        facecolor : str
            Color of the patch.
        """
        try:
            from astropy.coordinates import SkyCoord
        except ImportError:
            logger.error("You need to install AstroPy for this feature.")
            return None
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

            crd = SkyCoord(ra_outline, dec_outline, unit='deg')
            l = crd.galactic.l.deg
            if campaign not in [4, 13, 1713]:
                l[l > 180] -= 360
            l, b = list(l), list(crd.galactic.b.deg)
            if dashed:
                myfill = self.ax.fill(l + l[:1],
                                      b + b[:1],
                                      facecolor=facecolor, zorder=151, lw=2, ls='dashed',
                                      edgecolor='white')
                #myfill = self.ax.plot(l + l[:1],
                #                      b + b[:1],
                #                      zorder=200, lw=2,
                #                      ls='dotted', color='white')
            else:
                myfill = self.ax.fill(l + l[:1],
                                      b + b[:1],
                                      facecolor=facecolor, zorder=151, lw=0)
        # Print the campaign number on top of the outline
        ra, dec, roll = fov.getBoresight()
        gal = SkyCoord(ra, dec, unit='deg').galactic
        l, b = gal.l.deg, gal.b.deg
        if l > 180:
            l -= 360
        if text is None:
            text = "{}".format(campaign)
        self.ax.text(l, b, text,
                     fontsize=14, color="white", ha="center", va="center",
                     zorder=255)
        return myfill

    def plot(self):
        self.plot_campaigns()


def create_context_plot(ra, dec, name="Your object"):
    """Creates a K2FootprintPlot showing a given position in context
    with respect to the campaigns."""
    plot = K2FootprintPlot()
    plot.plot_galactic()
    plot.plot_ecliptic()
    for c in range(0, 120):
        plot.plot_campaign_outline(c, facecolor="#666666")
    #for c in [11, 12, 13, 14, 15, 16]:
    #    plot.plot_campaign_outline(c, facecolor="green")
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
    for c in [11, 12, 13, 14, 15, 16]:
        plot.plot_campaign_outline(c, facecolor="green")
    plot.fig.show()

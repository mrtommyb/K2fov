"""Sanity check: are all entries of an observed target list on silicon?"""
import os
import numpy as np

from K2fov.K2onSilicon import getKeplerFov, onSiliconCheck

TESTDIR = os.path.dirname(os.path.abspath(__file__))

def test_c7():
    """Are all the targets we observed in C7 on silicon?"""
    c7fov = getKeplerFov(7)
    targetlist_fn = os.path.join(TESTDIR, "K2Campaign7targets.csv")
    targetlist = np.genfromtxt(targetlist_fn,
                               delimiter=",", dtype=None, names=True)
    ra, dec = targetlist["RA_J2000_deg"], targetlist["Dec_J2000_deg"]
    mask = ~np.isnan(ra) & ~np.isnan(dec)
    for idx in np.where(mask)[0][::500]:
        assert(onSiliconCheck(ra[idx], dec[idx], c7fov))
        # A source +20 deg away should not be on silicon
        assert(not onSiliconCheck(ra[idx] + 20, dec[idx], c7fov))


if __name__ == "__main__":
    test_c7()

"""Sanity check: are all entries of an observed target list on silicon?"""
import os
import numpy as np

from .. import getKeplerFov
from ..K2onSilicon import onSiliconCheck

# Where is this test script located?
TESTDIR = os.path.dirname(os.path.abspath(__file__))


def test_targetlists():

    def run_test(campaign):
        """Are entries in the target list of a given campaign on silicon?"""
        fov = getKeplerFov(campaign)
        targetlist_fn = os.path.join(TESTDIR,
                                     "data",
                                     "K2Campaign{0}targets.csv".format(campaign))
        targetlist = np.genfromtxt(targetlist_fn,
                                   delimiter=",", dtype=None, names=True)
        ra, dec = targetlist["RA_J2000_deg"], targetlist["Dec_J2000_deg"]
        mask = ~np.isnan(ra) & ~np.isnan(dec)
        for idx in np.where(mask)[0][::500]:  # Speed-up: check every 500th
            # All the sources in the target list should be on silicon
            assert(onSiliconCheck(ra[idx], dec[idx], fov))
            assert(not onSiliconCheck(ra[idx] + 20, dec[idx], fov))

    # We test all the target lists available at the time of writing this test
    for campaign in [0, 1, 2, 3, 4, 5, 6, 7, 8]:
        run_test(campaign)


if __name__ == "__main__":
    test_targetlists()

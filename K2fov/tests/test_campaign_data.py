"""These tests ensure that the K2 pointing information that was hardcoded
into K2fov in version 1.9.2 is consistent with the info provided by the
'k2-campaigns.json' file that was introduced after.

To run these tests, simply run "py.test" in the K2fov source tree.
"""
import json

import K2fov
from K2fov.K2onSilicon import getRaDecRollFromFieldnum

CAMPAIGN_DICT = json.load(open(K2fov.CAMPAIGN_DICT_FILE))


def old_getRaDecRollFromFieldnum(fieldnum):
    """The code below is copied from K2fov v1.9.2,
    i.e. before the JSON file was added."""
    if fieldnum == 100:
        ra_deg = 290.6820
        dec_deg = -22.6664
        scRoll_deg = -171.8067
    elif fieldnum == 0:
        ra_deg = 98.2964079
        dec_deg = 21.5878901
        scRoll_deg = 177.4810830
    elif fieldnum == 1:
        ra_deg = 173.939610
        dec_deg = 1.4172989
        scRoll_deg = 157.641206
    elif fieldnum == 2:
        ra_deg = 246.1264
        dec_deg = -22.4473
        scRoll_deg = 171.2284
    elif fieldnum == 3:
        ra_deg = 336.66534641438909
        dec_deg = -11.096663792177043
        scRoll_deg = -158.49481806598479
    elif fieldnum == 4:
        ra_deg = 59.0759116
        dec_deg = 18.6605794
        scRoll_deg = -167.6992793
    elif fieldnum == 5:
        ra_deg = 130.1576478
        dec_deg = 16.8296140
        scRoll_deg = 166.0591297
    elif fieldnum == 6:
        ra_deg = 204.8650344
        dec_deg = -11.2953585
        scRoll_deg = 159.6356000
    elif fieldnum == 7:
        ra_deg = 287.82850661398538
        dec_deg = -23.360018153291808
        scRoll_deg = -172.78037532313485
    elif fieldnum == 8:
        ra_deg = 16.3379975
        dec_deg = 5.2623459
        scRoll_deg = -157.3538761
    elif fieldnum == 9:
        ra_deg = 270.3544823
        dec_deg = -21.7798098
        scRoll_deg = 0.4673417
    elif fieldnum == 10:
        ra_deg = 186.7794430
        dec_deg = -4.0271572
        scRoll_deg = 157.6280500
    elif fieldnum == 11:
        ra_deg = 260.3880071
        dec_deg = -23.9759578
        scRoll_deg = 176.5837078
    elif fieldnum == 12:
        ra_deg = 351.6775368
        dec_deg = -5.095648
        scRoll_deg = -156.7203394
    elif fieldnum == 13:
        ra_deg = 72.7968465
        dec_deg = 20.7863018
        scRoll_deg = -172.6384788
    elif fieldnum == 14:
        ra_deg = 159.9670000
        dec_deg = 7.1323713
        scRoll_deg = 159.022
    elif fieldnum == 15:
        ra_deg = 231.6012920
        dec_deg = -19.6081960
        scRoll_deg = 166.296
    elif fieldnum == 16:
        ra_deg = 320.9966284
        dec_deg = -16.4559528
        scRoll_deg = -161.897
    elif fieldnum == 17:
        ra_deg = 188.3497679
        dec_deg = -1.9586535
        scRoll_deg = -22.290
    elif fieldnum == 18:
        ra_deg = 112.6389009
        dec_deg = 20.2271914
        scRoll_deg = 172.044
    else:
        raise NotImplementedError

    return (ra_deg, dec_deg, scRoll_deg)


def test_coordinates_file():
    """Are the coordinates in the "k2-campaigns.json" file identical
    to those that were hardcoded in v1.9.2?"""
    campaigns = [100] + list(range(0, 19))
    for c in campaigns:
        test_ra, test_dec, test_roll = old_getRaDecRollFromFieldnum(c)
        jsoninfo = CAMPAIGN_DICT["c{}".format(c)]
        assert(jsoninfo['ra'] == test_ra)
        assert(jsoninfo['dec'] == test_dec)
        assert(jsoninfo['roll'] == test_roll)


def test_coordinates_function():
    """Are the coordinates in the "k2-campaigns.json" file identical
    to those that were hardcoded in v1.9.2?"""
    campaigns = [100] + list(range(0, 19))
    for c in campaigns:
        test_ra, test_dec, test_roll = old_getRaDecRollFromFieldnum(c)
        ra, dec, roll = getRaDecRollFromFieldnum(c)
        assert(ra == test_ra)
        assert(dec == test_dec)
        assert(roll == test_roll)


if __name__ == "__main__":
    test_coordinates()

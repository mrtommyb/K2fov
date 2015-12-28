"""Functions to expose the details of the different K2 Campaign Fields.
"""
import os
import json

from . import PACKAGEDIR, logger
from . import fov

__all__ = ['getFieldNumbers', 'getFieldInfo', 'getKeplerFov']


_campaign_dict_cache = None


def _getCampaignDict():
    """Returns a dictionary specifying the details of all campaigns."""
    global _campaign_dict_cache
    if _campaign_dict_cache is None:
        # All pointing parameters and dates are stored in a JSON file
        fn = os.path.join(PACKAGEDIR, "data", "k2-campaign-parameters.json")
        _campaign_dict_cache = json.load(open(fn))
    return _campaign_dict_cache


def getFieldNumbers():
    """Returns all the field numbers of campaigns defined so far.

    Returns
    -------
    numbers : list
        Valid field numbers, e.g. [0, 1, 2, ..., 17, 18]
    """
    return _getCampaignDict()["field_numbers"]


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
        info = _getCampaignDict()["c{0}".format(fieldnum)]
        # Print warning messages if necessary
        if fieldnum == 100:
            logger.warning("Warning: you are using the K2 first light field, "
                           "you almost certainly do not want to do this")
        elif "preliminary" in info and info["preliminary"] == "True":
            logger.warning("Warning: the position of field {0} is preliminary. "
                           "Do not use this position for your final "
                           "target selection!".format(fieldnum))
        return info
    except KeyError:
        raise ValueError("Field {0} not set in this version "
                         "of the code".format(fieldnum))


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
    info = getFieldInfo(fieldnum)
    ra, dec, scRoll = info["ra"], info["dec"], info["roll"]
    # convert from SC roll to FOV coordinates
    # do not use the fovRoll coords anywhere else
    # they are internal to this script only
    fovRoll = fov.getFovAngleFromSpacecraftRoll(scRoll)
    return fov.KeplerFov(ra, dec, fovRoll)

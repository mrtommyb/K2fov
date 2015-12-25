from __future__ import (division, absolute_import)

import os
import logging
logger = logging.getLogger(__name__)

# Where are the K2 Campaign parameters stored?
PACKAGEDIR = os.path.dirname(os.path.abspath(__file__))
# The pointing parameters and dates of each campaign are stored in a JSON file
CAMPAIGN_DICT_FILE = os.path.join(PACKAGEDIR, "data",
                                  "k2-campaign-parameters.json")

# Optical distortions can cause the results from K2fov to be off by a bit.
# The padding parameter compensates for this; setting padding > 0 means
# that objects that are computed to lie a small amount off silicon will
# be considered on silicon.
DEFAULT_PADDING = 3  # pixels

# Add fields.* and K2onSilicon() to the root namespace
from .fields import *
from .K2onSilicon import K2onSilicon

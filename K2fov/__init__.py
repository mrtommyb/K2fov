from __future__ import (division, absolute_import)

# Where are the K2 Campaign parameters stored?
import os
PACKAGEDIR = os.path.dirname(os.path.abspath(__file__))
CAMPAIGN_DICT_FILE = os.path.join(PACKAGEDIR, "data",
                                  "k2-campaign-parameters.json")

from .K2onSilicon import K2onSilicon

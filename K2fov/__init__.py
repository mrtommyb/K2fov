#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (division, absolute_import)

import os
PACKAGEDIR = os.path.dirname(os.path.abspath(__file__))
CAMPAIGN_DICT_FILE = os.path.join(PACKAGEDIR, "data", "k2-campaigns.json")

from .K2onSilicon import K2onSilicon

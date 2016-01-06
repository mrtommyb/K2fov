#!/usr/bin/env python
import sys
import os

if "publish" in sys.argv[-1]:
    os.system("python setup.py sdist upload")
    sys.exit()

try:
    from setuptools import setup
    setup
except ImportError:
    from distutils.core import setup
    setup


# Command-line tools
entry_points = {'console_scripts': [
    'K2onSilicon = K2fov.K2onSilicon:K2onSilicon_main',
    'k2onsilicon = K2fov.K2onSilicon:K2onSilicon_main',
    'K2inMicrolensRegion = K2fov.c9:inMicrolensRegion_main',
    'k2inmicrolensregion = K2fov.c9:inMicrolensRegion_main',
    'K2findCampaigns = K2fov.K2findCampaigns:K2findCampaigns_main',
    'k2findcampaigns = K2fov.K2findCampaigns:K2findCampaigns_main',
    'K2findCampaigns-byname = K2fov.K2findCampaigns:K2findCampaigns_byname_main',
    'k2findcampaigns-byname = K2fov.K2findCampaigns:K2findCampaigns_byname_main',
    'K2findCampaigns-csv = K2fov.K2findCampaigns:K2findCampaigns_csv_main',
    'k2findcampaigns-csv = K2fov.K2findCampaigns:K2findCampaigns_csv_main'
]}

setup(name='K2fov',
      version='3.0.2',
      description='Find which targets are in the field of view of K2',
      author='Fergal Mullally, Tom Barclay, Geert Barentsen',
      author_email='tom@tombarclay.com',
      url='https://github.com/KeplerGO/K2fov',
      packages=['K2fov'],
      package_data={'K2fov': ['data/*.json']},
      install_requires=["numpy>=1.8"],
      entry_points=entry_points,
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Intended Audience :: Science/Research",
          "Topic :: Scientific/Engineering :: Astronomy",
          ],
      )

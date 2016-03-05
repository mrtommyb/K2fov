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

# Load the __version__ variable without importing the package
exec(open('K2fov/version.py').read())

# Command-line tools; we're not using "entry_points" for now due to
# a bug in pip which turns all the tools into lowercase
scripts = ['scripts/K2onSilicon',
           'scripts/K2findCampaigns',
           'scripts/K2findCampaigns-byname',
           'scripts/K2findCampaigns-csv',
           'scripts/K2inMicrolensRegion']

setup(name='K2fov',
      version=__version__,
      description='Find which targets are in the field of view of K2',
      author='Fergal Mullally, Tom Barclay, Geert Barentsen',
      author_email='tom@tombarclay.com',
      url='https://github.com/KeplerGO/K2fov',
      packages=['K2fov'],
      package_data={'K2fov': ['data/*.json']},
      install_requires=["numpy>=1.8"],
      scripts=scripts,
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3",
          "Intended Audience :: Science/Research",
          "Topic :: Scientific/Engineering :: Astronomy",
          ],
      )

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
    'K2onSilicon = K2fov.K2onSilicon:K2onSilicon_main'
]}

setup(name='K2fov',
      version='2.0.1',
      description='Find which targets are in the field of view of K2',
      author='Tom Barclay',
      author_email='tom@tombarclay.com',
      url='https://github.com/mrtommyb/K2fov',
      packages=['K2fov'],
      package_data={'K2fov': ['data/*.json']},
      install_requires=["numpy>=1.8"],
      entry_points=entry_points,
      )

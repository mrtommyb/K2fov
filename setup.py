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

setup(name='K2fov',
      version='2.0.0',
      description='Find which targets are in the field of view of K2',
      author='Tom Barclay',
      author_email='tom@tombarclay.com',
      url='https://github.com/mrtommyb/K2fov',
      packages=['K2fov'],
      data_files=[('K2fov/data', ['K2fov/data/k2-campaigns.json'])],
      install_requires=["numpy"],
      )

#!/usr/bin/env python


try:
    from setuptools import setup
    setup
except ImportError:
    from distutils.core import setup
    setup

setup(name='K2_fov',
      version='1.0',
      description='Find which targets are in the field of view of K2',
      author='Tom Barclay',
      author_email='tom@tombarclay.com',
      url='https://github.com/mrtommyb/K2_fov',
      packages=['K2_fov'],
      install_requires=["numpy"],)


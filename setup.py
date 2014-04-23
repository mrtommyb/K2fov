#!/usr/bin/env python


try:
    from setuptools import setup
    setup
except ImportError:
    from distutils.core import setup
    setup

setup(name='K2fov',
      version='1.2.5',
      description='Find which targets are in the field of view of K2',
      author='Tom Barclay',
      author_email='tom@tombarclay.com',
      url='https://github.com/mrtommyb/K2fov',
      packages=['K2fov'],
      install_requires=["numpy"],)


#!/usr/bin/env python
from setuptools import setup

setup(name='gymGharrafa',
      version='0.0.1',
      package_dir = {"gym_gharrafa": "gym_gharrafa"},
      install_requires=['gym',
                        'pandas',
                        'cfg_load']
      )

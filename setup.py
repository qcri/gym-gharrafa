#!/usr/bin/env python
from setuptools import setup
import setuptools

setup(name='gymGharrafa',
      version='0.0.1',
      #package_dir = {"gymGharrafa": "gymGharrafa"},
      #packages = ["gymGharrafa"],
      packages = setuptools.find_packages(),
      install_requires=['gym',
                        'pandas',
                        'cfg_load'],
    include_package_data=True
      )

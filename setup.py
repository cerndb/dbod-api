#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2015, CERN
# This software is distributed under the terms of the GNU General Public
# Licence version 3 (GPL Version 3), copied verbatim in the file "LICENSE".
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as Intergovernmental Organization
# or submit itself to any jurisdiction.

"""
DB On Demand REST API server setup file
"""

from setuptools import setup, find_packages

setup(name='apiato',
      version='0.9.7',
      description='CERN Apiato REST API',
      author='CERN',
      author_email='icot@cern.ch',
      license='GPLv3',
      maintainer='Ignacio Coterillo',
      maintainer_email='icot@cern.ch',
      url='https://github.com/cerndb/dbod-api',
      packages=find_packages(),
      scripts=['bin/apiato'],
      test_suite="",
      install_requires=[
          'ConfigParser',
          'tornado',
          'nose',
          'mock',
          'requests',
          'timeout_decorator',
          ],
     )

#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2015, CERN
# This software is distributed under the terms of the GNU General Public
# Licence version 3 (GPL Version 3), copied verbatim in the file "LICENSE".
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as Intergovernmental Organization
# or submit itself to any jurisdiction.

"""
DB On Demand metadata REST API server setup file
"""

from distutils.core import setup

setup(name='dbod_metadata',
      version='0.1',
      description='DB On Demand metadata server',
      author='icot',
      author_email='icot@cern.ch',
      url='',
      packages=['dbod_metadata'],
      scripts=['bin/dbod_metadata'],
      requires=[
          'Flask',
          'pyOpenSSL',
          'psycopg2',
          ],
     )

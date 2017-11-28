#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2016, CERN
# This software is distributed under the terms of the GNU General Public
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as Intergovernmental Organization
# or submit itself to any jurisdiction.

import logging
import unittest
import sys
import os.path

from apiato.config import load

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

class ConfigTest(unittest.TestCase):
    """Test configuration loading"""

    def test_config_file_not_found(self):
        with self.assertRaises(SystemExit) as cm:
            config = load('/path/to/unexisting/file')
        self.assertEqual(cm.exception.code, 1)

    @unittest.skipUnless(os.path.isfile('/tmp/api_missing_section.cfg'),'Skipping as no missing section file was found')
    def test_config_missing_section(self):
        with self.assertRaises(SystemExit) as cm:
            config = load('/tmp/api_missing_section.cfg')
        self.assertEqual(cm.exception.code, 2)
    
    @unittest.skipUnless(os.path.isfile('/tmp/api_missing_option.cfg'),'Skipping as no missing section file was found')
    def test_config_missing_option(self):
        with self.assertRaises(SystemExit) as cm:
            config = load('/tmp/api_missing_option.cfg')
        self.assertEqual(cm.exception.code, 2)


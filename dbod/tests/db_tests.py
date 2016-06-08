#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2015, CERN
# This software is distributed under the terms of the GNU General Public
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as Intergovernmental Organization
# or submit itself to any jurisdiction.

import unittest
from types import *
import json
import logging
import sys
import requests
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

class Test(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        pass

    @classmethod
    def tearDownClass(self):
        pass
        
    def setUp(self):
        pass

    def tearDown(self):
        pass
        
    def test_connection(self):
        response = requests.get("http://localhost:3000")
        print response.json()
        self.assertEquals(response.status_code, 200)
        
    def test_metadata(self):
        response = requests.get("http://localhost:3000/metadata")
        print response.json()
        self.assertEquals(response.status_code, 200)
        
    def test_metadata_has_5_instances(self):
        response = requests.get("http://localhost:3000/metadata")
        print response.json()
        data = response.json()
        self.assertEquals(len(data), 5)
        

if __name__ == "__main__":
    unittest.main()

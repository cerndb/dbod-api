
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

class Metadata(unittest.TestCase):
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
        
    def test_single_instance_by_name(self):
        response = requests.get("http://localhost:5443/api/v1/metadata/entity/dbod01", verify=False)
        data = response.json()["response"]
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(data), 1)
        self.assertEquals(data[0]["db_name"], "dbod01")
        self.assertTrue(data[0]["volumes"] != None)
        self.assertTrue(data[0]["host"] != None)
        
    def test_no_instance_by_name(self):
        response = requests.get("http://localhost:5443/api/v1/metadata/entity/invalid", verify=False)
        self.assertEquals(response.status_code, 404)
        
    def test_single_instance_by_host(self):
        response = requests.get("http://localhost:5443/api/v1/metadata/host/host03", verify=False)
        data = response.json()["response"]
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(data), 1)
        self.assertTrue(data[0]["volumes"] != None)
        self.assertEquals(data[0]["host"], "host03")
        
    def test_multiple_instances_by_host(self):
        response = requests.get("http://localhost:5443/api/v1/metadata/host/host01", verify=False)
        data = response.json()["response"]
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(data), 4)
        list = []
        for i in range(4):
            self.assertEquals(data[i]["host"], "host01")
            self.assertTrue(data[i]["volumes"] != None)
            self.assertNotIn(data[i]["db_name"], list)
            list.append(data[i]["db_name"])
        self.assertEquals(len(list), 4)
        
    def test_no_instance_by_host(self):
        response = requests.get("http://localhost:5443/api/v1/metadata/host/invalid", verify=False)
        self.assertEquals(response.status_code, 404)
    
        
        
#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2015, CERN
# This software is distributed under the terms of the GNU General Public
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as Intergovernmental Organization
# or submit itself to any jurisdiction.

import tornado.web
import json
import urllib
import logging

from tornado.testing import AsyncHTTPTestCase
from tornado.testing import get_unused_port
from timeout_decorator import timeout

from dbod.api.api import *

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

class EntityTest(AsyncHTTPTestCase):
    def get_app(self):
        return tornado.web.Application(handlers, debug=True)

    @timeout(5)
    def test_create_entity(self):
        response = self.fetch("/api/v1/entity/testdb", method='DELETE')
        
        entity = """{
        "username": "testuser", "category": "TEST", "creation_date":"2016-07-20", 
        "version": "5.6.17", "db_type": "MYSQL", "port": "5505", "host": "testhost", "db_name": "testdb", 
        "volumes": [
            {"vgroup": "ownergroup", "file_mode": "0755", "server": "NAS-server", "mount_options": "rw,bg,hard", 
            "owner": "TSM", "mounting_path": "/MNT/data1"}, 
            {"vgroup": "ownergroup", "file_mode": "0755", 
            "server": "NAS-server", "mount_options": "rw,bg,hard", "owner": "TSM", "mounting_path": "/MNT/bin"}
        ]}"""
        
        # Create the instance
        response = self.fetch("/api/v1/entity/create", method='POST', body=entity)
        self.assertEquals(response.code, 201)
        
        # Check the metadata for this new instance
        response = self.fetch("/api/v1/metadata/entity/testdb")
        self.assertEquals(response.code, 200)
        data = json.loads(response.body)["response"]
        self.assertEquals(data[0]["db_name"], "testdb")
        self.assertEquals(len(data[0]["volumes"]), 2)
        self.assertEquals(data[0]["port"], "5505")  # Reminder: the port is saved as a String in DB
        
        # Delete the created instance
        response = self.fetch("/api/v1/entity/testdb", method='DELETE')
        self.assertEquals(response.code, 204)
        
        # Check again, the metadata should be empty
        response = self.fetch("/api/v1/metadata/entity/testdb")
        self.assertEquals(response.code, 404)
    
    
    

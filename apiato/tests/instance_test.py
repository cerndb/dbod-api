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
import base64

from tornado.testing import AsyncHTTPTestCase
from tornado.testing import get_unused_port
from timeout_decorator import timeout

from apiato.api.api import *

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

class InstanceTest(AsyncHTTPTestCase):
    """Class to test instances endpoint"""
    authentication = "basic " + base64.b64encode(config.get('api','user') + ":" + config.get('api','pass'))
    
    def get_app(self):
        return tornado.web.Application(handlers, debug=True)

    @timeout(5)
    def test_create_instance(self):
        """Creation of a new instance in a correct way"""
        instance = """{
        "owner": "testuser", "category": "TEST", "creation_date":"2016-07-20", 
        "version": "5.6.17", "type_id": 2, "host_id": 1, "name": "testdb", "state": "MAINTENANCE", "status": "ACTIVE",
        "volumes": [
            {"group": "ownergroup", "file_mode": "0755", "server": "NAS-server", "mount_options": "rw,bg,hard", "volume_type_id": 1,
            "owner": "TSM", "mounting_path": "/MNT/data1"}, 
            {"group": "ownergroup", "file_mode": "0755", "server": "NAS-server", "mount_options": "rw,bg,hard", "volume_type_id": 1,
            "owner": "TSM", "mounting_path": "/MNT/bin"}
        ],
        "attributes": [{
            "port": "5505",
            "notifications": "false"
        }]}"""
        
        # Create the instance
        response = self.fetch("/api/v1/instance/create", method='POST', headers={'Authorization': self.authentication}, body=instance)
        self.assertEquals(response.code, 201)
        created_id = json.loads(response.body)[0]["insert_instance"]
        logging.info("Created with ID: " + str(created_id))
        
        # Check the metadata for this new instance
        response = self.fetch("/api/v1/metadata/instance/testdb")
        self.assertEquals(response.code, 200)
        data = json.loads(response.body)["response"]
        self.assertEquals(data[0]["db_name"], "testdb")
        self.assertEquals(len(data[0]["volumes"]), 2)
        self.assertEquals(len(data[0]["attributes"]), 2)
        self.assertEquals(data[0]["attributes"]["port"], "5505")  # Reminder: the port is saved as a String in DB
        self.assertEquals(data[0]["attributes"]["notifications"], "false")  # Reminder: the port is saved as a String in DB
        
        # Delete the created instance
        response = self.fetch("/api/v1/instance/" + str(created_id), method='DELETE', headers={'Authorization': self.authentication})
        self.assertEquals(response.code, 204)
        
        # Check again, the metadata should be empty
        response = self.fetch("/api/v1/metadata/instance/testdb")
        self.assertEquals(response.code, 404)
        
    @timeout(5)
    def test_create_basic_instance(self):
        """Creation of an instance with only basic (required) data"""
        instance = """{
        "owner": "testuser", "category": "TEST", "creation_date":"2016-07-20",
        "version": "5.6.17", "type_id": 2, "db_size": "100", "host_id": 1, "name": "testdb", "state": "MAINTENANCE", "status": "ACTIVE"
        }"""

        # Create the instance
        response = self.fetch("/api/v1/instance/testdb", method='POST', headers={'Authorization': self.authentication}, body=instance)
        self.assertEquals(response.code, 201)
        created_id = json.loads(response.body)[0]["insert_instance"]
        logging.info("Created with ID: " + str(created_id))

        # Check the metadata for this new instance
        response = self.fetch("/api/v1/metadata/instance/testdb")
        self.assertEquals(response.code, 200)
        data = json.loads(response.body)["response"]
        self.assertEquals(data[0]["db_name"], "testdb")
        self.assertEquals(data[0]["hosts"][0], "host01")
        self.assertEquals(data[0]["username"], "testuser")
        self.assertEquals(data[0]["type"], "MYSQL")
        self.assertEquals(data[0]["version"], "5.6.17")
        self.assertTrue(not data[0]["volumes"])
        self.assertTrue(not data[0]["attributes"])

        # Delete the created instance
        response = self.fetch("/api/v1/instance/" + str(created_id), method='DELETE', headers={'Authorization': self.authentication})
        self.assertEquals(response.code, 204)

        # Check again, the metadata should be empty
        response = self.fetch("/api/v1/metadata/instance/testdb")
        self.assertEquals(response.code, 404)


    @timeout(5)
    def test_edit_instance_username(self):
        """Edit the owner correctly"""
        instance = """{"owner": "newuser"}"""
        restore = """{"owner": "user01"}"""

        # Edit the instance
        response = self.fetch("/api/v1/instance/1", method='PUT', headers={'Authorization': self.authentication}, body=instance)
        self.assertEquals(response.code, 200)

        # Check the metadata for this instance
        response = self.fetch("/api/v1/metadata/instance/apiato01")
        self.assertEquals(response.code, 200)
        data = json.loads(response.body)["response"]
        self.assertEquals(data[0]["username"], "newuser")

        # Restore the instance
        response = self.fetch("/api/v1/instance/1", method='PUT', headers={'Authorization': self.authentication}, body=restore)
        self.assertEquals(response.code, 200)

    @timeout(5)
    def test_edit_instance_dbname(self):
        """Edit the dbname correctly"""
        instance = """{"name": "newdb01"}"""
        restore = """{"name": "apiato01"}"""

        # Edit the instance
        response = self.fetch("/api/v1/instance/1", method='PUT', headers={'Authorization': self.authentication}, body=instance)
        self.assertEquals(response.code, 200)

        # Check the metadata for this instance
        response = self.fetch("/api/v1/metadata/instance/newdb01")
        self.assertEquals(response.code, 200)
        data = json.loads(response.body)["response"]
        self.assertEquals(data[0]["db_name"], "newdb01")

        # Restore the instance
        response = self.fetch("/api/v1/instance/1", method='PUT', headers={'Authorization': self.authentication}, body=restore)
        self.assertEquals(response.code, 200)



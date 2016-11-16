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

from dbod.api.api import *

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

class AttributeTest(AsyncHTTPTestCase):
    """Class to test attributes endpoint"""
    authentication = "basic " + base64.b64encode(config.get('api','user') + ":" + config.get('api','pass'))
    
    def get_app(self):
        return tornado.web.Application(handlers, debug=True)
    
    @timeout(5)
    def create_test_instance(self):
        """Create a new empty instance to run the tests to it"""
        response = self.fetch("/api/v1/instance/testdb", method='DELETE', headers={'Authorization': self.authentication})
        
        instance = """{
        "username": "testuser", "class": "TEST", "creation_date":"2016-10-20", 
        "version": "5.6.17", "db_type": "MYSQL", "hosts": ["testhost"], "db_name": "testdb", 
        "volumes": [
            {"group": "ownergroup", "file_mode": "0755", "server": "NAS-server", "mount_options": "rw,bg,hard", 
            "owner": "TSM", "mounting_path": "/MNT/data1"}, 
            {"group": "ownergroup", "file_mode": "0755", "server": "NAS-server", "mount_options": "rw,bg,hard", 
            "owner": "TSM", "mounting_path": "/MNT/bin"}
        ],
        "attributes": {
            "port": "5505"
        }}"""
        
        # Create the instance
        response = self.fetch("/api/v1/instance/testdb", method='POST', headers={'Authorization': self.authentication}, body=instance)
        self.assertEquals(response.code, 201)
        
    @timeout(5)
    def delete_test_instance(self):
        """Destroy the created test instance"""
        response = self.fetch("/api/v1/instance/testdb", method='DELETE', headers={'Authorization': self.authentication})
        

    @timeout(5)
    def test_get_attribute(self):
        """Get the port attribute"""
        self.create_test_instance()
        
        response = self.fetch("/api/v1/instance/testdb/attribute/port")
        self.assertEquals(response.code, 200)
        
        # Check the port value is correct
        self.assertEquals(response.body, "5505")
        
        self.delete_test_instance()
    
    @timeout(5)
    def test_get_attributes(self):
        """Get all the instance attributes"""
        self.create_test_instance()
        
        response = self.fetch("/api/v1/instance/testdb/attribute")
        self.assertEquals(response.code, 200)
        
        # Check the port value is correct
        data = json.loads(response.body)
        self.assertEquals(len(data), 1)
        self.assertEquals(data["port"], "5505")
        
        self.delete_test_instance()
        
    @timeout(5)
    def test_get_attribute_no_instance(self):
        """Get the port attribute when instance doesn't exist"""
        response = self.fetch("/api/v1/instance/testdb/attribute/port")
        self.assertEquals(response.code, 404)
    
    @timeout(5)
    def test_get_attributes_no_instance(self):
        """Get all the instance attributes when instance doesn't exist"""
        response = self.fetch("/api/v1/instance/testdb/attribute")
        self.assertEquals(response.code, 404)
        
    @timeout(5)
    def test_add_attribute(self):
        """Add a new attribute to the instance"""
        self.create_test_instance()
        
        attribute = """{"test_attribute": "test_value"}"""
        response = self.fetch("/api/v1/instance/testdb/attribute", method='POST', headers={'Authorization': self.authentication}, body=attribute)
        self.assertEquals(response.code, 201)
        
        # Get the new attribute
        response = self.fetch("/api/v1/instance/testdb/attribute/test_attribute")
        self.assertEquals(response.code, 200)
        self.assertEquals(response.body, "test_value")
        
        # Get and check all the attributes
        response = self.fetch("/api/v1/instance/testdb/attribute")
        self.assertEquals(response.code, 200)
        data = json.loads(response.body)
        self.assertEquals(len(data), 2)
        self.assertEquals(data["test_attribute"], "test_value")
        
        self.delete_test_instance()
        
    @timeout(5)
    def test_add_attributes(self):
        """Add some new attributes to the instance"""
        self.create_test_instance()
        
        attribute = """{"test_attribute1": "test_value1", "test_attribute2": "test_value2"}"""
        response = self.fetch("/api/v1/instance/testdb/attribute", method='POST', headers={'Authorization': self.authentication}, body=attribute)
        self.assertEquals(response.code, 201)
        
        # Get the new attribute
        response = self.fetch("/api/v1/instance/testdb/attribute/test_attribute1")
        self.assertEquals(response.code, 200)
        self.assertEquals(response.body, "test_value1")
        response = self.fetch("/api/v1/instance/testdb/attribute/test_attribute2")
        self.assertEquals(response.code, 200)
        self.assertEquals(response.body, "test_value2")
        
        # Get and check all the attributes
        response = self.fetch("/api/v1/instance/testdb/attribute")
        self.assertEquals(response.code, 200)
        data = json.loads(response.body)
        self.assertEquals(len(data), 3)
        self.assertEquals(data["test_attribute1"], "test_value1")
        self.assertEquals(data["test_attribute2"], "test_value2")
        
        self.delete_test_instance()
        
    @timeout(5)
    def test_add_null_attribute(self):
        """Add a null attribute to the instance"""
        self.create_test_instance()
        
        attribute = """{"test_attribute": null}"""
        response = self.fetch("/api/v1/instance/testdb/attribute", method='POST', headers={'Authorization': self.authentication}, body=attribute)
        self.assertEquals(response.code, 400) # Bad Request
        
        self.delete_test_instance()
        
    @timeout(5)
    def test_add_null_attribute(self):
        """Add a null attribute to the instance"""
        self.create_test_instance()
        
        attribute = """{"test_attribute": null}"""
        response = self.fetch("/api/v1/instance/testdb/attribute", method='POST', headers={'Authorization': self.authentication}, body=attribute)
        self.assertEquals(response.code, 400) # Bad Request
        
        self.delete_test_instance()
        
    @timeout(5)
    def test_add_existing_attribute(self):
        """Add an existing attribute to the instance"""
        self.create_test_instance()
        
        attribute = """{"port": "5500"}"""
        response = self.fetch("/api/v1/instance/testdb/attribute", method='POST', headers={'Authorization': self.authentication}, body=attribute)
        self.assertEquals(response.code, 409) # Conflict
        
        self.delete_test_instance()
        
    @timeout(5)
    def test_add_attribute_no_instance(self):
        """Add a new attribute to an instance doesn't exist"""
        attribute = """{"test_attribute": "test_value"}"""
        response = self.fetch("/api/v1/instance/testdb/attribute", method='POST', headers={'Authorization': self.authentication}, body=attribute)
        self.assertEquals(response.code, 404)
        
    @timeout(5)
    def test_edit_existing_attribute(self):
        """Edit an existing attribute of the instance"""
        self.create_test_instance()
        
        attribute = "6611"
        response = self.fetch("/api/v1/instance/testdb/attribute/port", method='PUT', headers={'Authorization': self.authentication}, body=attribute)
        self.assertEquals(response.code, 204)
        
        # Get the new value
        response = self.fetch("/api/v1/instance/testdb/attribute/port")
        self.assertEquals(response.code, 200)
        self.assertEquals(response.body, "6611")
        
        self.delete_test_instance()
        
    @timeout(5)
    def test_edit_non_existing_attribute(self):
        """Edit a non existing attribute of the instance"""
        self.create_test_instance()
        
        attribute = "cls01"
        response = self.fetch("/api/v1/instance/testdb/attribute/cluster", method='PUT', headers={'Authorization': self.authentication}, body=attribute)
        self.assertEquals(response.code, 404)
        
        # Check it was not created
        response = self.fetch("/api/v1/instance/testdb/attribute/cluster")
        self.assertEquals(response.code, 404)
        
        self.delete_test_instance()
        
    @timeout(5)
    def test_edit_attribute_no_instance(self):
        """Edit an attribute of a non existing instance"""
        attribute = "6611"
        response = self.fetch("/api/v1/instance/testdb/attribute/port", method='PUT', headers={'Authorization': self.authentication}, body=attribute)
        self.assertEquals(response.code, 404)
        
    @timeout(5)
    def test_delete_existing_attribute(self):
        """Delete an existing attribute of the instance"""
        self.create_test_instance()
        
        response = self.fetch("/api/v1/instance/testdb/attribute/port", method='DELETE', headers={'Authorization': self.authentication})
        self.assertEquals(response.code, 204)
        
        # Get the new value
        response = self.fetch("/api/v1/instance/testdb/attribute/port")
        self.assertEquals(response.code, 404)
        
        self.delete_test_instance()
        
    @timeout(5)
    def test_delete_non_existing_attribute(self):
        """Delete an non existing attribute of the instance"""
        self.create_test_instance()
        
        response = self.fetch("/api/v1/instance/testdb/attribute/cluster", method='DELETE', headers={'Authorization': self.authentication})
        self.assertEquals(response.code, 404)
        
        # Check the port value is correct
        response = self.fetch("/api/v1/instance/testdb/attribute/port")
        self.assertEquals(response.code, 200)
        self.assertEquals(response.body, "5505")
        
        self.delete_test_instance()
        
    @timeout(5)
    def test_delete_attribute_no_instance(self):
        """Delete an attribute of a non existing instance"""
        response = self.fetch("/api/v1/instance/testdb/attribute/port", method='DELETE', headers={'Authorization': self.authentication})
        self.assertEquals(response.code, 404)

    
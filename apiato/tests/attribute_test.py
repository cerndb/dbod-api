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

class AttributeTest(AsyncHTTPTestCase):
    """Class to test attributes endpoint"""
    authentication = "basic " + base64.b64encode(config.get('api','user') + ":" + config.get('api','pass'))
    
    def get_app(self):
        return tornado.web.Application(handlers, debug=True)
    
    @timeout(5)
    def create_instance(self):
        """Create a new empty instance to run the tests to it"""
        response = self.fetch("/api/v1/instance/testdbat", method='DELETE', headers={'Authorization': self.authentication})
        
        instance = """{
        "owner": "testuser", "category": "TEST", "creation_date":"2016-07-20", 
        "version": "5.6.17", "type_id": 2, "host_id": 1, "name": "testdbat", "state": "MAINTENANCE", "status": "ACTIVE",
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
        response = self.fetch("/api/v1/instance/testdbat", method='POST', headers={'Authorization': self.authentication}, body=instance)
        
    @timeout(5)
    def delete_instance(self):
        """Destroy the created test instance"""
        response = self.fetch("/api/v1/instance/testdbat", method='DELETE', headers={'Authorization': self.authentication})
        

    @timeout(5)
    def test_get_attribute(self):
        """Get the port attribute"""
        self.create_instance()
        
        response = self.fetch("/api/v1/instance/testdbat/attribute/port")
        self.assertEquals(response.code, 200)
        
        # Check the port value is correct
        port = json.loads(response.body).get('value')
        self.assertEquals(port, "5505")
        
        self.delete_instance()
    
    @timeout(5)
    def test_get_attributes(self):
        """Get all the instance attributes"""
        self.create_instance()
        metadata = self.fetch("/api/v1/instance/testdbat/metadata")

        logging.debug("Metadata: %s" % (metadata))

        response = self.fetch("/api/v1/instance/testdbat/attribute")
        self.assertEquals(response.code, 200)
        
        # Check the port value is correct
        data = json.loads(response.body)
        port = data.get('port')
        notifications = data.get('notifications')
        self.assertEquals(len(data), 2)
        self.assertEquals(port, "5505")
        self.assertEquals(notifications, "false")
        
        self.delete_instance()
        
    @timeout(5)
    def test_get_attribute_no_instance(self):
        """Get the port attribute when instance doesn't exist"""
        response = self.fetch("/api/v1/instance/testdbatnoexist/attribute/port")
        self.assertEquals(response.code, 404)
    
    @timeout(5)
    def test_get_attributes_no_instance(self):
        """Get all the instance attributes when instance doesn't exist"""
        response = self.fetch("/api/v1/instance/testdbatnoexist/attribute")
        self.assertEquals(response.code, 404)
        
    @timeout(5)
    def test_add_attribute(self):
        """Add a new attribute to the instance"""
        self.create_instance()
        
        attribute = """{"test_attribute": "test_value"}"""
        response = self.fetch("/api/v1/instance/testdbat/attribute", method='POST', headers={'Authorization': self.authentication}, body=attribute)
        self.assertEquals(response.code, 201)
        
        # Get the new attribute
        response = self.fetch("/api/v1/instance/testdbat/attribute/test_attribute")
        self.assertEquals(response.code, 200)
        value = json.loads(response.body).get('value')
        self.assertEquals(value, "test_value")
        
        
        # Get and check all the attributes
        response = self.fetch("/api/v1/instance/testdbat/attribute")
        self.assertEquals(response.code, 200)
        data = json.loads(response.body)
        logging.debug("attributes: %s" % (data))
        self.assertEquals(len(data), 3)
        self.assertEquals(data["test_attribute"], "test_value")
        
        self.delete_instance()
        
    @timeout(5)
    def test_add_attributes(self):
        """Add some new attributes to the instance"""
        self.create_instance()
        
        attribute = """{"test_attribute1": "test_value1", "test_attribute2": "test_value2"}"""
        response = self.fetch("/api/v1/instance/testdbat/attribute", method='POST', headers={'Authorization': self.authentication}, body=attribute)
        self.assertEquals(response.code, 201)
        
        # Get the new attribute
        response = self.fetch("/api/v1/instance/testdbat/attribute/test_attribute1")
        self.assertEquals(response.code, 200)
        value = json.loads(response.body).get('value')
        self.assertEquals(value, "test_value1")
        response = self.fetch("/api/v1/instance/testdbat/attribute/test_attribute2")
        self.assertEquals(response.code, 200)
        value = json.loads(response.body).get('value')
        self.assertEquals(value, "test_value2")
        
        # Get and check all the attributes
        response = self.fetch("/api/v1/instance/testdbat/attribute")
        self.assertEquals(response.code, 200)
        data = json.loads(response.body)
        self.assertEquals(len(data), 4)
        self.assertEquals(data["test_attribute1"], "test_value1")
        self.assertEquals(data["test_attribute2"], "test_value2")
        
        self.delete_instance()
        
    @timeout(5)
    def test_add_null_attribute(self):
        """Add a null attribute to the instance"""
        self.create_instance()
        
        attribute = """{"test_attribute": null}"""
        response = self.fetch("/api/v1/instance/testdbat/attribute", method='POST', headers={'Authorization': self.authentication}, body=attribute)
        self.assertEquals(response.code, 400) # Bad Request
        
        self.delete_instance()
        
    @timeout(5)
    def test_add_existing_attribute(self):
        """Add an existing attribute to the instance"""
        self.create_instance()
        
        attribute = """{"port": "5500"}"""
        response = self.fetch("/api/v1/instance/testdbat/attribute", method='POST', headers={'Authorization': self.authentication}, body=attribute)
        self.assertEquals(response.code, 409) # Conflict
        
        self.delete_instance()
        
    @timeout(5)
    def test_add_attribute_no_instance(self):
        """Add a new attribute to an instance doesn't exist"""
        attribute = """{"test_attribute": "test_value"}"""
        response = self.fetch("/api/v1/instance/testdbat/attribute", method='POST', headers={'Authorization': self.authentication}, body=attribute)
        self.assertEquals(response.code, 400)
        
    @timeout(5)
    def test_edit_existing_attribute(self):
        """Edit an existing attribute of the instance"""
        self.create_instance()
        
        attribute = "6611"
        response = self.fetch("/api/v1/instance/testdbat/attribute/port", method='PUT', headers={'Authorization': self.authentication}, body=attribute)
        self.assertEquals(response.code, 200)
        
        # Get the new value
        response = self.fetch("/api/v1/instance/testdbat/attribute/port")
        self.assertEquals(response.code, 200)
        port = json.loads(response.body).get('value')
        self.assertEquals(port, "6611")
        
        self.delete_instance()
        
    @timeout(5)
    def test_edit_non_existing_attribute(self):
        """Edit a non existing attribute of the instance"""
        self.create_instance()
        
        attribute = "cls01"
        response = self.fetch("/api/v1/instance/testdbat/attribute/cluster", 
                method='PUT', headers={'Authorization': self.authentication}, body = attribute)
        self.assertEquals(response.code, 500)
        
        # Check it was not created
        response = self.fetch("/api/v1/instance/testdbat/attribute/cluster")
        self.assertEquals(response.code, 404)
        
        self.delete_instance()
        
    @timeout(5)
    def test_edit_attribute_no_instance(self):
        """Edit an attribute of a non existing instance"""
        attribute = "6611"
        response = self.fetch("/api/v1/instance/testdbnot/attribute/port", method='PUT', headers={'Authorization': self.authentication}, body=attribute)
        self.assertEquals(response.code, 500)
        
    @timeout(5)
    def test_delete_existing_attribute(self):
        """Delete an existing attribute of the instance"""
        self.create_instance()
        
        response = self.fetch("/api/v1/instance/testdbat/attribute/port", method='DELETE', headers={'Authorization': self.authentication})
        self.assertEquals(response.code, 204)
        
        # Get the new value
        response = self.fetch("/api/v1/instance/testdbat/attribute/port")
        self.assertEquals(response.code, 404)
        
        self.delete_instance()
        
    @timeout(5)
    def test_delete_non_existing_attribute(self):
        """Delete an non existing attribute of the instance"""
        self.create_instance()
        
        response = self.fetch("/api/v1/instance/testdbat/attribute/cluster", method='DELETE', headers={'Authorization': self.authentication})
        self.assertEquals(response.code, 204)
        
        self.delete_instance()
        
    @timeout(5)
    def test_delete_attribute_no_instance(self):
        """Delete an attribute of a non existing instance"""
        response = self.fetch("/api/v1/instance/testdbnot/attribute/port", method='DELETE', headers={'Authorization': self.authentication})
        self.assertEquals(response.code, 204)

    

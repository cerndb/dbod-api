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

class InstanceTest(AsyncHTTPTestCase):
    """Class to test instances endpoint"""
    authentication = "basic " + base64.b64encode(config.get('api','user') + ":" + config.get('api','pass'))
    
    def get_app(self):
        return tornado.web.Application(handlers, debug=True)

    @timeout(5)
    def test_create_instance(self):
        """Creation of a new instance in a correct way"""
        response = self.fetch("/api/v1/instance/testdb", method='DELETE', headers={'Authorization': self.authentication})
        
        instance = """{
        "username": "testuser", "category": "TEST", "creation_date":"2016-07-20", 
        "version": "5.6.17", "db_type": "MYSQL", "port": "5505", "host": "testhost", "db_name": "testdb", 
        "volumes": [
            {"vgroup": "ownergroup", "file_mode": "0755", "server": "NAS-server", "mount_options": "rw,bg,hard", 
            "owner": "TSM", "mounting_path": "/MNT/data1"}, 
            {"vgroup": "ownergroup", "file_mode": "0755", "server": "NAS-server", "mount_options": "rw,bg,hard", 
            "owner": "TSM", "mounting_path": "/MNT/bin"}
        ]}"""
        
        # Create the instance
        response = self.fetch("/api/v1/instance/create", method='POST', headers={'Authorization': self.authentication}, body=instance)
        self.assertEquals(response.code, 201)
        
        # Check the metadata for this new instance
        response = self.fetch("/api/v1/metadata/instance/testdb")
        self.assertEquals(response.code, 200)
        data = json.loads(response.body)["response"]
        self.assertEquals(data[0]["db_name"], "testdb")
        self.assertEquals(len(data[0]["volumes"]), 2)
        self.assertEquals(data[0]["port"], "5505")  # Reminder: the port is saved as a String in DB
        
        # Delete the created instance
        response = self.fetch("/api/v1/instance/testdb", method='DELETE', headers={'Authorization': self.authentication})
        self.assertEquals(response.code, 204)
        
        # Check again, the metadata should be empty
        response = self.fetch("/api/v1/metadata/instance/testdb")
        self.assertEquals(response.code, 404)
        
    @timeout(5)
    def test_create_existing_instance(self):
        """Creation of an instance that already exists"""
        instance = """{
        "username": "testuser", "category": "TEST", "creation_date":"2016-07-20", 
        "version": "5.6.17", "db_type": "MYSQL", "port": "5505", "host": "testhost", "db_name": "dbod01", 
        "volumes": [
            {"vgroup": "ownergroup", "file_mode": "0755", "server": "NAS-server", "mount_options": "rw,bg,hard", 
            "owner": "TSM", "mounting_path": "/MNT/data1"}, 
            {"vgroup": "ownergroup", "file_mode": "0755", "server": "NAS-server", "mount_options": "rw,bg,hard",
            "owner": "TSM", "mounting_path": "/MNT/bin"}
        ]}"""
        
        # Create the instance
        response = self.fetch("/api/v1/instance/create", method='POST', headers={'Authorization': self.authentication}, body=instance)
        self.assertEquals(response.code, 409)
    
    @timeout(5)
    def test_create_instance_invalid_fields(self):
        """Creation of an instance with an undefined required field (db_type)"""
        instance = """{
        "username": "testuser", "category": "TEST", "creation_date":"2016-07-20", 
        "version": "5.6.17", "port": "5505", "host": "testhost", "db_name": "very_long_name", 
        "volumes": [
            {"vgroup": "ownergroup", "file_mode": "0755", "server": "NAS-server", "mount_options": "rw,bg,hard", 
            "owner": "TSM", "mounting_path": "/MNT/data1"}, 
            {"vgroup": "ownergroup", "file_mode": "0755", "server": "NAS-server", "mount_options": "rw,bg,hard", 
            "owner": "TSM", "mounting_path": "/MNT/bin"}
        ]}"""
        
        # Create the instance
        response = self.fetch("/api/v1/instance/create", method='POST', headers={'Authorization': self.authentication}, body=instance)
        self.assertEquals(response.code, 400)
        
    @timeout(5)
    def test_create_instance_no_port(self):
        """Creation of an instance without port"""
        instance = """{
        "username": "testuser", "category": "TEST", "creation_date":"2016-07-20", 
        "version": "5.6.17", "db_type": "MYSQL", "host": "testhost", "db_name": "very_long_name", 
        "volumes": [
            {"vgroup": "ownergroup", "file_mode": "0755", "server": "NAS-server", "mount_options": "rw,bg,hard", 
            "owner": "TSM", "mounting_path": "/MNT/data1"}, 
            {"vgroup": "ownergroup", "file_mode": "0755", "server": "NAS-server", "mount_options": "rw,bg,hard", 
            "owner": "TSM", "mounting_path": "/MNT/bin"}
        ]}"""
        
        # Create the instance
        response = self.fetch("/api/v1/instance/create", method='POST', headers={'Authorization': self.authentication}, body=instance)
        self.assertEquals(response.code, 400)
    
    @timeout(5)
    def test_create_instance_no_volumes(self):
        """Creation of an instance without volumes"""
        instance = """{
        "username": "testuser", "category": "TEST", "creation_date":"2016-07-20", 
        "version": "5.6.17", "db_type": "MYSQL", "port": "5505", "host": "testhost", "db_name": "very_long_name"}"""
        
        # Create the instance
        response = self.fetch("/api/v1/instance/create", method='POST', headers={'Authorization': self.authentication}, body=instance)
        self.assertEquals(response.code, 400)
        
    @timeout(5)
    def test_edit_instance_username(self):
        """Edit the username correctly"""
        instance = """{"username": "newuser"}"""
        restore = """{"username": "user01"}"""
        
        # Edit the instance
        response = self.fetch("/api/v1/instance/dbod01", method='PUT', headers={'Authorization': self.authentication}, body=instance)
        self.assertEquals(response.code, 204)
        
        # Check the metadata for this instance
        response = self.fetch("/api/v1/metadata/instance/dbod01")
        self.assertEquals(response.code, 200)
        data = json.loads(response.body)["response"]
        self.assertEquals(data[0]["username"], "newuser")
        
        # Restore the instance
        response = self.fetch("/api/v1/instance/dbod01", method='PUT', headers={'Authorization': self.authentication}, body=restore)
        self.assertEquals(response.code, 204)
        
    @timeout(5)
    def test_edit_instance_dbname(self):
        """Edit the dbname correctly"""
        instance = """{"db_name": "newdb01"}"""
        restore = """{"db_name": "dbod01"}"""
        
        # Edit the instance
        response = self.fetch("/api/v1/instance/dbod01", method='PUT', headers={'Authorization': self.authentication}, body=instance)
        self.assertEquals(response.code, 204)
        
        # Check the metadata for this instance
        response = self.fetch("/api/v1/metadata/instance/newdb01")
        self.assertEquals(response.code, 200)
        data = json.loads(response.body)["response"]
        self.assertEquals(data[0]["db_name"], "newdb01")
        
        # Restore the instance
        response = self.fetch("/api/v1/instance/newdb01", method='PUT', headers={'Authorization': self.authentication}, body=restore)
        self.assertEquals(response.code, 204)
        
    @timeout(5)
    def test_edit_instance_port(self):
        """Edit the port correctly"""
        instance = """{"port": "3005"}"""
        restore = """{"port": "5501"}"""
        
        # Edit the instance
        response = self.fetch("/api/v1/instance/dbod01", method='PUT', headers={'Authorization': self.authentication}, body=instance)
        self.assertEquals(response.code, 204)
        
        # Check the metadata for this instance
        response = self.fetch("/api/v1/metadata/instance/dbod01")
        self.assertEquals(response.code, 200)
        data = json.loads(response.body)["response"]
        self.assertEquals(data[0]["port"], "3005")
        
        # Restore the instance
        response = self.fetch("/api/v1/instance/dbod01", method='PUT', headers={'Authorization': self.authentication}, body=restore)
        self.assertEquals(response.code, 204)
        
    @timeout(5)
    def test_edit_instance_port_and_host(self):
        """Edit the host and port correctly"""
        instance = """{"port": "3005", "host": "newhost"}"""
        restore = """{"port": "5501", "host": "host01"}"""

        # Edit the instance
        response = self.fetch("/api/v1/instance/dbod01", method='PUT', headers={'Authorization': self.authentication}, body=instance)
        self.assertEquals(response.code, 204)
        
        # Check the metadata for this instance
        response = self.fetch("/api/v1/metadata/instance/dbod01")
        self.assertEquals(response.code, 200)
        data = json.loads(response.body)["response"]
        self.assertEquals(data[0]["port"], "3005")
        self.assertEquals(data[0]["host"], "newhost")
        
        # Restore the instance
        response = self.fetch("/api/v1/instance/dbod01", method='PUT', headers={'Authorization': self.authentication}, body=restore)
        self.assertEquals(response.code, 204)
        
    @timeout(5)
    def test_edit_instance_volumes(self):
        """Edit volumes correctly"""
        instance = """{"volumes": [
            {"vgroup": "testgroup", "file_mode": "0755", "server": "NAS-server", "mount_options": "rw,bg,hard", 
            "owner": "TSM", "mounting_path": "/MNT/data1"}, 
            {"vgroup": "testgroup", "file_mode": "0755", "server": "NAS-server", "mount_options": "rw,bg,hard", 
            "owner": "TSM", "mounting_path": "/MNT/test"},
            {"vgroup": "testgroup", "file_mode": "0755", "server": "NAS-server", "mount_options": "rw,bg,hard", 
            "owner": "TSM", "mounting_path": "/MNT/bin"}
        ]}"""
        restore = """{"volumes": [
            {"vgroup": "ownergroup", "file_mode": "0755", "server": "NAS-server", "mount_options": "rw,bg,hard", 
            "owner": "TSM", "mounting_path": "/MNT/data1"}, 
            {"vgroup": "ownergroup", "file_mode": "0755", "server": "NAS-server", "mount_options": "rw", 
            "owner": "TSM", "mounting_path": "/MNT/bin"}
        ]}"""
        
        # Edit the instance
        response = self.fetch("/api/v1/instance/dbod01", method='PUT', headers={'Authorization': self.authentication}, body=instance)
        self.assertEquals(response.code, 204)
        
        # Check the metadata for this instance
        response = self.fetch("/api/v1/metadata/instance/dbod01")
        self.assertEquals(response.code, 200)
        data = json.loads(response.body)["response"]
        self.assertEquals(len(data[0]["volumes"]), 3)
        self.assertEquals(data[0]["volumes"][0]["vgroup"], "testgroup")
        self.assertEquals(data[0]["volumes"][1]["vgroup"], "testgroup")
        self.assertEquals(data[0]["volumes"][2]["vgroup"], "testgroup")
        self.assertEquals(data[0]["volumes"][1]["mounting_path"], "/MNT/test")
        
        # Restore the instance
        response = self.fetch("/api/v1/instance/dbod01", method='PUT', headers={'Authorization': self.authentication}, body=restore)
        self.assertEquals(response.code, 204)
        
        
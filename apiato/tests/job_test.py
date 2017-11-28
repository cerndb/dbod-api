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

import base64
import tornado.web

from mock import patch
from mock import MagicMock
from tornado.testing import AsyncHTTPTestCase
from timeout_decorator import timeout

from apiato.api.api import handlers
from apiato.config import config
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

class JobTest(AsyncHTTPTestCase, unittest.TestCase):
    """Class for testing Job endpoint with nosetest"""
    
    authentication = "basic " + \
                     base64.b64encode(config.get('api', 'user') + \
                     ":" + config.get('api', 'pass'))
    
    def get_app(self):
        return tornado.web.Application(handlers)
        
    @timeout(5)
    def create_instance(self):
        """Create a new empty instance to run the tests to it"""
        response = self.fetch("/api/v1/instance/testjobs", method='DELETE', headers={'Authorization': self.authentication})
        
        instance = """{
        "owner": "testuser", "category": "TEST", "creation_date":"2016-07-20", 
        "version": "5.6.17", "type_id": 2, "host_id": 1, "name": "testjobs", "state": "MAINTENANCE", "status": "ACTIVE",
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
        response = self.fetch("/api/v1/instance/testjobs", method='POST', headers={'Authorization': self.authentication}, body=instance)
        
    @timeout(5)
    def delete_instance(self):
        """Destroy the created test instance"""
        response = self.fetch("/api/v1/instance/testjobs", method='DELETE', headers={'Authorization': self.authentication})
        
    @timeout(5)
    def test_get_jobs_empty(self):
        """Get the jobs of the instance when there are no jobs"""
        self.create_instance()
        
        response = self.fetch("/api/v1/instance/testjobs/job", headers={'Authorization': self.authentication})
        self.assertEquals(response.code, 200)
        
        # Check the port value is correct
        response = json.loads(response.body).get('response')
        self.assertEquals(len(response), 0)
        
        self.delete_instance()
        
    @timeout(5)
    def test_get_jobs_one(self):
        """Get the jobs of an instance having only one job"""
        response = self.fetch("/api/v1/instance/apiato02/job", headers={'Authorization': self.authentication})
        self.assertEquals(response.code, 200)
        
        # Check the port value is correct
        response = json.loads(response.body).get('response')
        self.assertEquals(len(response), 1)
        self.assertEquals(response[0]["username"], "user02")
        self.assertEquals(response[0]["db_name"], "apiato02")
        
    @timeout(5)
    def test_get_jobs_many(self):
        """Get the jobs of an instance having many jobs"""
        response = self.fetch("/api/v1/instance/apiato01/job", headers={'Authorization': self.authentication})
        self.assertEquals(response.code, 200)
        
        # Check the port value is correct
        response = json.loads(response.body).get('response')
        self.assertEquals(len(response), 5)
        self.assertEquals(response[0]["db_name"], "apiato01")
        self.assertEquals(response[1]["db_name"], "apiato01")
        self.assertEquals(response[2]["db_name"], "apiato01")
        self.assertEquals(response[3]["db_name"], "apiato01")
        self.assertEquals(response[4]["db_name"], "apiato01")
        
    @timeout(5)
    def test_get_job(self):
        """Get a job correctly"""
        response = self.fetch("/api/v1/instance/apiato01/job/1", headers={'Authorization': self.authentication})
        self.assertEquals(response.code, 200)
        
        response = json.loads(response.body).get('response')
        self.assertIsNotNone(response["log"])
        
    @timeout(5)
    def test_get_job_different_instance(self):
        """Get a job from different instance"""
        response = self.fetch("/api/v1/instance/apiato01/job/6", headers={'Authorization': self.authentication})
        self.assertEquals(response.code, 401)
        
    @timeout(5)
    def test_get_job_no_exists(self):
        """Get an inexistent job"""
        response = self.fetch("/api/v1/instance/apiato01/job/60000", headers={'Authorization': self.authentication})
        self.assertEquals(response.code, 404)
        
    @timeout(5)
    def test_get_job_instance_no_exists(self):
        """Get a job from inexistent instance"""
        response = self.fetch("/api/v1/instance/noexists/job/6", headers={'Authorization': self.authentication})
        self.assertEquals(response.code, 404)
        
    @timeout(5)
    def test_get_jobs_instance_no_exists(self):
        """Get jobs from inexistent instance"""
        response = self.fetch("/api/v1/instance/noexists/job", headers={'Authorization': self.authentication})
        self.assertEquals(response.code, 404)
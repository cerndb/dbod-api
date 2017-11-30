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
    def test_instance_list(self):
        """Get the list of instances an user can access (1)"""
        auth_header = '{"owner": "user01", "groups": ["testgroupB"], "admin": false}'
        
        response = self.fetch("/api/v1/instance", headers={'Authorization': self.authentication, 'Auth':auth_header })
        self.assertEquals(response.code, 200)
        
        # Check the port value is correct
        response = json.loads(response.body)
        self.assertEquals(len(response), 3)
        
    @timeout(5)
    def test_list_instances_user1(self):
        """Get the list of instances an user can access (2)"""
        auth_header = '{"owner": "user01", "groups": [], "admin": false}'
        
        response = self.fetch("/api/v1/instance", headers={'Authorization': self.authentication, 'Auth':auth_header })
        self.assertEquals(response.code, 200)
        
        # Check the port value is correct
        response = json.loads(response.body)
        self.assertEquals(len(response), 2)
        
    @timeout(5)
    def test_list_instances_user2(self):
        """Get the list of instances an user can access (3)"""
        auth_header = '{"owner": "user01", "groups": ["no_exists"], "admin": false}'
        
        response = self.fetch("/api/v1/instance", headers={'Authorization': self.authentication, 'Auth':auth_header })
        self.assertEquals(response.code, 200)
        
        # Check the port value is correct
        response = json.loads(response.body)
        self.assertEquals(len(response), 2)
        
    @timeout(5)
    def test_list_instances_user3(self):
        """Get the list of instances an user can access (3)"""
        auth_header = '{"owner": "user01", "groups": ["no_exists"], "admin": false}'
        
        response = self.fetch("/api/v1/instance", headers={'Authorization': self.authentication, 'Auth':auth_header })
        self.assertEquals(response.code, 200)
        
        # Check the port value is correct
        response = json.loads(response.body)
        self.assertEquals(len(response), 2)
        
    @timeout(5)
    def test_list_instances_user4(self):
        """Get the list of instances an user can access (4)"""
        auth_header = '{"owner": "user01", "groups": [], "admin": false}'
        
        response = self.fetch("/api/v1/instance", headers={'Authorization': self.authentication, 'Auth':auth_header })
        self.assertEquals(response.code, 200)
        
        # Check the port value is correct
        response = json.loads(response.body)
        self.assertEquals(len(response), 2)
        
    @timeout(5)
    def test_list_instances_user5(self):
        """Get the list of instances an user can access (5)"""
        auth_header = '{"owner": "no_exists", "groups": ["testgroupA"], "admin": false}'
        
        response = self.fetch("/api/v1/instance", headers={'Authorization': self.authentication, 'Auth':auth_header })
        self.assertEquals(response.code, 200)
        
        # Check the port value is correct
        response = json.loads(response.body)
        self.assertEquals(len(response), 2)
        
    @timeout(5)
    def test_list_instances_admin1(self):
        """Get the list of instances an admin can access (1)"""
        auth_header = '{"owner": "user01", "groups": ["testgroupB"], "admin": true}'
        
        response = self.fetch("/api/v1/instance", headers={'Authorization': self.authentication, 'Auth':auth_header })
        self.assertEquals(response.code, 200)
        
        # Check the port value is correct
        response = json.loads(response.body)
        self.assertEquals(len(response), 8)
        
    @timeout(5)
    def test_list_instances_admin2(self):
        """Get the list of instances an admin can access (2)"""
        auth_header = '{"owner": "user01", "groups": [], "admin": true}'
        
        response = self.fetch("/api/v1/instance", headers={'Authorization': self.authentication, 'Auth':auth_header })
        self.assertEquals(response.code, 200)
        
        # Check the port value is correct
        response = json.loads(response.body)
        self.assertEquals(len(response), 8)
        
    @timeout(5)
    def test_list_instances_admin3(self):
        """Get the list of instances an admin can access (3)"""
        auth_header = '{"owner": "no_exists", "groups": [], "admin": true}'
        
        response = self.fetch("/api/v1/instance", headers={'Authorization': self.authentication, 'Auth':auth_header })
        self.assertEquals(response.code, 200)
        
        # Check the port value is correct
        response = json.loads(response.body)
        self.assertEquals(len(response), 8)
        
    @timeout(5)
    def test_list_instances_only_owner(self):
        """Get the list of instances if only owner param was specified"""
        auth_header = '{"owner": "user01"}'
        
        response = self.fetch("/api/v1/instance", headers={'Authorization': self.authentication, 'Auth':auth_header })
        self.assertEquals(response.code, 400)

    @timeout(5)
    def test_list_instances_only_egroup(self):
        """Get the list of instances if only egroup param was specified"""
        auth_header = '{"egroup": ["testgroupB"]}'
        
        response = self.fetch("/api/v1/instance", headers={'Authorization': self.authentication, 'Auth':auth_header })
        self.assertEquals(response.code, 400)
        
    @timeout(5)
    def test_list_instances_only_admin(self):
        """Get the list of instances if only egroup param was specified"""
        auth_header = '{"admin": true}'
        
        response = self.fetch("/api/v1/instance", headers={'Authorization': self.authentication, 'Auth':auth_header })
        self.assertEquals(response.code, 400)

    @timeout(5)
    def test_instance_no_auth_header(self):
        """Get the list of instances sending no auth header"""
        response = self.fetch("/api/v1/instance", headers={'Authorization': self.authentication })
        self.assertEquals(response.code, 400)

    @timeout(5)
    def test_instance_invalid_auth_header(self):
        """Get the list of instances sending invalid auth header"""
        auth_header = '{"owner": "no_exists", "groups": [], "admin": true'  # Missing closing bracket
        response = self.fetch("/api/v1/instance", headers={'Authorization': self.authentication, 'Auth':auth_header })
        self.assertEquals(response.code, 400)

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

from dbod.api.api import handlers
from dbod.config import config
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

class HostTest(AsyncHTTPTestCase, unittest.TestCase):
    """Class for testing Host endpoint with nosetest"""
    
    authentication = "basic " + base64.b64encode(config.get('api', 'user') + ":" + config.get('api', 'pass'))

    def get_app(self):
        return tornado.web.Application(handlers)

    @timeout(5)
    def test_get_valid_name(self):
        """ test a successful get method with a valid given name"""

        # Check the data for the given host
        print "test_get_host_metadata"
        response = self.fetch("/api/v1/host/host01")
        self.assertEquals(response.code, 200)
        data = json.loads(response.body)["response"]
        self.assertEquals(data[0]["name"], "host01")
        self.assertEquals(data[0]["memory"], 12)

    @timeout(5)
    def test_create_delete_host(self):

        """test for create and delete a host with the right data"""

        host = """{"name": "host05", "memory": "512" }"""
        print "test_create_delete_host"

        # Create the host
        response = self.fetch("/api/v1/host/create", method='POST', headers={'Authorization': self.authentication}, body=host)
        self.assertEquals(response.code, 201)

        # Check for this new host
        response = self.fetch("/api/v1/host/host05")
        self.assertEquals(response.code, 200)
        data = json.loads(response.body)["response"]
        self.assertEquals(data[0]["name"], "host05")
        self.assertEquals(data[0]["memory"], 512)


        # Delete the created host
        response = self.fetch("/api/v1/host/" + str(data[0]["id"]) , method='DELETE', headers={'Authorization': self.authentication})
        self.assertEquals(response.code, 201)

        # Check again, the metadata should be empty
        response = self.fetch("/api/v1/names/host05")
        self.assertEquals(response.code, 404)

    @timeout(5)
    def test_insert_duplicate_host(self):

        """test for create an already existing host"""
        host = """{"name": "host01", "memory": "512" }"""

        # Create the host
        response = self.fetch("/api/v1/host/create", method='POST', headers={'Authorization': self.authentication}, body=host)
        self.assertEquals(response.code, 400)



    @timeout(5)
    def test_update_host(self):
        """test for update a host"""
        current_host = """{"memory": "12" }"""
        new_host = """{"memory": "1200" }"""

        response = self.fetch("/api/v1/host/1" , method='PUT', headers={'Authorization': self.authentication}, body=new_host)
        self.assertEquals(response.code, 201)

        # Check the cluster update
        response = self.fetch("/api/v1/host/host01")
        self.assertEquals(response.code, 200)
        data = json.loads(response.body)["response"]
        self.assertEquals(data[0]["memory"], 1200)

        # Restore the instance
        response = self.fetch("/api/v1/host/1", method='PUT', headers={'Authorization': self.authentication}, body=current_host)
        self.assertEquals(response.code, 201)

        # Check the cluster update (restore)
        response = self.fetch("/api/v1/host/host01")
        self.assertEquals(response.code, 200)
        data = json.loads(response.body)["response"]
        self.assertEquals(data[0]["memory"], 12)


    @timeout(5)
    def test_get_invalid_cluster(self):
        print "test_get_invalid_host"
        response = self.fetch("/api/v1/host/invalid")
        self.assertEquals(response.code, 404)



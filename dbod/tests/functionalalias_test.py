#!/usr/bin/env python
"""Testing functional alias endpoint"""
# -*- coding: utf-8 -*-

# Copyright (C) 2015, CERN
# This software is distributed under the terms of the GNU General Public
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as Intergovernmental Organization
# or submit itself to any jurisdiction.

import json
import unittest
import base64
import requests
import tornado.web

from mock import patch
from mock import MagicMock
from tornado.testing import AsyncHTTPTestCase
from timeout_decorator import timeout

from dbod.api.api import handlers
from dbod.config import config

class FunctionalAliasTest(AsyncHTTPTestCase, unittest.TestCase):
    """Class for testing functional alias with nosetest"""


    name_test = "dbod42"
    alias_test = "dbod-dbod-42.cern.ch"
    authentication = "basic " + base64.b64encode(config.get('api', 'user') + ":" + config.get('api', 'pass'))
    
    def get_app(self):
        return tornado.web.Application(handlers)

    @timeout(5)
    def test_get_single_alias_by_name(self):
        """test for getting the right data"""
        print "test_get_single_alias_by_name"
        name = 'dbod01'
        response = self.fetch("/api/v1/instance/alias/%s" %(name))
        data = json.loads(response.body)["response"]
        self.assertEquals(response.code, 200)

        self.assertEquals(len(data), 1)
        self.assertEquals(data[0]["alias"], "dbod-dbod-01.cern.ch")
        self.assertTrue(data[0]["dns_name"] != None)
        self.assertEquals(response.headers['Content-Type'], 'application/json; charset=UTF-8')


    @timeout(5)
    def test_get_invalid_instance_name(self):
        """test when the instance name does not exist"""
        print "test_get_invalid_instance_name"
        response = self.fetch("/api/v1/instance/alias/%s" %(self.name_test))
        data = response.body
        self.assertEquals(response.code, 404)
        self.assertEquals(len(data), 69)
        self.assertEquals(response.headers['Content-Type'], 'text/html; charset=UTF-8')


    # @timeout(5)
    def test_novalid_instance(self):
         """test when the given instance does not exist"""
         response = self.fetch("/api/v1/instance/alias/some_instance")
         self.assertEquals(response.code, 404)


    @timeout(5)
    def test_create_delete_a_valid_alias(self):
        """test insert a new alias (dns_name is available) and delete the data inserted"""
        print "test_post_valid_request"

        funtional_alias = """{"instance_id" : "5", "alias" : "dbod-dbod-05.cern.ch" }"""

        response = self.fetch("/api/v1/instance/alias/create", method="POST", headers={'Authorization': self.authentication}, body=funtional_alias)
        self.assertEquals(response.code, 201)

        # confirm you get back the right data
        response = self.fetch("/api/v1/instance/alias/dbod05")
        data = json.loads(response.body)["response"]
        self.assertEquals(len(data), 1)
        self.assertEquals(data[0]["alias"], "dbod-dbod-05.cern.ch")
        self.assertTrue(data[0]["dns_name"] != None)

        # delete what has been created
        self.fetch("/api/v1/instance/alias/" + str(data[0]["id"]), headers={'Authorization': self.authentication}, method="DELETE")

    # @timeout(5)
    def test_post_duplicate(self):
        """test when there is a request to insert an instance which already exists"""
        print "test_post_duplicate"
        funtional_alias = """{"instance_id" : "1", "alias" : "dbod-dop-01.cern.ch" }"""
        response = self.fetch("/api/v1/instance/alias/dbod01", method="POST", headers={'Authorization': self.authentication}, body=funtional_alias)
        self.assertEquals(response.code, 201)

        # confirm you get back the right data
        response = self.fetch("/api/v1/instance/alias/dbod01")
        data = json.loads(response.body)["response"]
        self.assertEquals(len(data), 1)
        self.assertEquals(data[0]["alias"], "dbod-dbod-01.cern.ch")

    # @timeout(5)
    def test_post_no_dns(self):
        """test when there are no any dns available"""
        funtional_alias = """{"instance_id" : "5", "alias" : "dbod-dbod-05.cern.ch" }"""

        response = self.fetch("/api/v1/instance/alias/create", method="POST", headers={'Authorization': self.authentication}, body=funtional_alias)
        self.assertEquals(response.code, 201)


        funtional_alias = """{"instance_id" : "6", "alias" : "dbod-dbod-06.cern.ch" }"""

        response = self.fetch("/api/v1/instance/alias/create", method="POST", headers={'Authorization': self.authentication}, body=funtional_alias)
        self.assertEquals(response.code, 201)

        # confirm you get back the right data
        response = self.fetch("/api/v1/instance/alias/dbod06")
        self.assertEquals(response.code, 404)

        # delete what has been created
        self.fetch("/api/v1/instance/alias/5", headers={'Authorization': self.authentication}, method="DELETE")



    @timeout(5)
    def test_post_no_valid_argument(self):
        """test if the provided argument is not valid"""
        funtional_alias = """{"instance_id" : "10"}"""

        response = self.fetch("/api/v1/instance/alias/create", method="POST", headers={'Authorization': self.authentication}, body=funtional_alias)
        self.assertEquals(response.code, 400)


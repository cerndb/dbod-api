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

from tornado.testing import AsyncHTTPTestCase
from tornado.testing import get_unused_port
from timeout_decorator import timeout

from apiato.api.api import *

class MetadataTest(AsyncHTTPTestCase):
    def get_app(self):
        return tornado.web.Application(handlers)

    @timeout(5)
    def test_single_instance_by_name(self):
        response = self.fetch("/api/v1/instance/apiato01/metadata")
        data = json.loads(response.body)["response"]
        self.assertEquals(response.code, 200)
        self.assertEquals(len(data), 1)
        self.assertEquals(data[0]["db_name"], "apiato01")
        self.assertEquals(len(data[0]["hosts"]), 1)
        self.assertTrue(data[0]["volumes"] != None)
    
    @timeout(5)
    def test_no_instance_by_name(self):
        response = self.fetch("/api/v1/instance/invalid/metadata")
        self.assertEquals(response.code, 404)
    
    @timeout(5)
    def test_single_instance_by_host(self):
        response = self.fetch("/api/v1/host/host03/metadata")
        data = json.loads(response.body)["response"]
        self.assertEquals(response.code, 200)
        self.assertEquals(len(data), 1)
        self.assertTrue(data[0]["volumes"] != None)
        self.assertEquals(data[0]["hosts"][0], "host03")
    

    
    @timeout(5)
    def test_no_instance_by_host(self):
        response = self.fetch("/api/v1/host/invalid/metadata")
        self.assertEquals(response.code, 404)
        
    @timeout(5)
    def test_invalid_class(self):
        response = self.fetch("/api/v1/invalid/invalid/metadata")
        self.assertEquals(response.code, 400)
    

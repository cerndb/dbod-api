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
import base64
import logging

from tornado.testing import AsyncHTTPTestCase
from tornado.testing import get_unused_port
from timeout_decorator import timeout

from dbod.api.api import *

class ClusterTest(AsyncHTTPTestCase):

    """Class to test instances endpoint"""
    authentication = "basic " + base64.b64encode(config.get('api','user') + ":" + config.get('api','pass'))

    def get_app(self):
        return tornado.web.Application(handlers, debug=True)


    @timeout(5)
    def test_create_delete_cluster(self):
        """test for create and delete a cluster with the right data"""
        response = self.fetch("/api/v1/cluster/testcluster", method='DELETE', headers={'Authorization': self.authentication})

        instance = """{
        "owner": "testuser", "class": "TEST", "expiry_date": "2016-11-20", "e_group": "testgroupZ"
        "version": "3.9", "type": "ZOOKEEPER", "name": "testcluster", "state":"RUNNING", "STATUS":"ACTIVE"
        "attributes": {
            "port": "2108"
        }}"""

        # Create the instance
        response = self.fetch("/api/v1/cluster/create", method='POST', headers={'Authorization': self.authentication}, body=instance)
        self.assertEquals(response.code, 201)

        # Check the metadata for this new cluster
        response = self.fetch("/api/v1/metadata/cluster/testcluster")
        self.assertEquals(response.code, 200)
        data = json.loads(response.body)["response"]
        self.assertEquals(data[0]["name"], "testcluster")
        self.assertEquals(len(data[0]["volumes"]), 2)
        self.assertEquals(len(data[0]["attributes"]), 1)
        self.assertEquals(data[0]["attributes"]["port"], "2108")  # Reminder: the port is saved as a String in DB

        # Delete the created instance
        response = self.fetch("/api/v1/cluster/testcluster", method='DELETE', headers={'Authorization': self.authentication})
        self.assertEquals(response.code, 204)

        # Check again, the metadata should be empty
        response = self.fetch("/api/v1/metadata/instance/testdb")
        self.assertEquals(response.code, 404)

    @timeout(5)
    def test_no_cluster(self):
        response = self.fetch("/api/v1/cluster/metadata/invalid")
        self.assertEquals(response.code, 404)

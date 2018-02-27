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

from apiato.api.api import *

class ClusterTest(AsyncHTTPTestCase):

    """Class to test instances endpoint"""
    authentication = "basic " + base64.b64encode(config.get('api','user') + ":" + config.get('api','pass'))

    def get_app(self):
        return tornado.web.Application(handlers, debug=True)

    @timeout(5)
    def test_get_cluster_by_name(self):

        """test getting a cluster by name"""

        # Check the data for the given cluster
        print "test_cluster_metadata"
        response = self.fetch("/api/v1/cluster/cluster01")
        self.assertEquals(response.code, 200)
        data = json.loads(response.body)["response"]
        self.assertEquals(data[0]["name"], "cluster01")
        self.assertEquals(len(data[0]["instances"]), 2)
        self.assertEquals(len(data[0]["attributes"]), 2)
        self.assertEquals(data[0]["attributes"]["user"], "zookeeper")



    @timeout(5)
    def test_create_delete_cluster(self):

        """test for create and delete a cluster with the right data"""

        cluster = """{"owner": "testuser", "category": "TEST", "creation_date": "2016-11-20", "e_group": "testgroupZ", "version": "3.9", "type_id": 1, "name": "testcluster", "state": "RUNNING", "status": "ACTIVE", "attributes": [{"testp01" : "testvalue" },{"testp02" :"testvalue"}]}"""
        print "test_create_delete_cluster"

        # Create the instance
        response = self.fetch("/api/v1/cluster/create", method='POST', headers={'Authorization': self.authentication}, body=cluster)
        self.assertEquals(response.code, 201)

        # Check for this new cluster
        response = self.fetch("/api/v1/cluster/testcluster")
        self.assertEquals(response.code, 200)
        data = json.loads(response.body)["response"]
        self.assertEquals(data[0]["name"], "testcluster")
        self.assertEquals(len(data[0]["attributes"]), 2)
        self.assertEquals(data[0]["attributes"]["testp01"], "testvalue")  # Reminder: the port is saved as a String in DB

        # Delete the created instance
        response = self.fetch("/api/v1/cluster/" + str(data[0]["id"]) , method='DELETE', headers={'Authorization': self.authentication})
        self.assertEquals(response.code, 204)

        # Check again, the metadata should be empty
        response = self.fetch("/api/v1/cluster/testcluster")
        self.assertEquals(response.code, 404)


    def test_update_cluster(self):
        """test for update a cluster"""
        current_cluster = """{ "e_group" : "testgroupZ"}"""
        new_cluster = """{ "e_group" : "testgroupX"}"""

        response = self.fetch("/api/v1/cluster/1" , method='PUT', headers={'Authorization': self.authentication}, body=new_cluster)
        self.assertEquals(response.code, 200)

        # Check the cluster update
        response = self.fetch("/api/v1/cluster/cluster01")
        self.assertEquals(response.code, 200)
        data = json.loads(response.body)["response"]
        self.assertEquals(data[0]["e_group"], "testgroupX")

        # Restore the instance
        response = self.fetch("/api/v1/cluster/1", method='PUT', headers={'Authorization': self.authentication}, body=current_cluster)
        self.assertEquals(response.code, 200)

        # Check the cluster update (restore)
        response = self.fetch("/api/v1/cluster/cluster01")
        self.assertEquals(response.code, 200)
        data = json.loads(response.body)["response"]
        self.assertEquals(data[0]["e_group"], "testgroupZ")


    @timeout(5)
    def test_get_invalid_cluster(self):
        print "test_get_invalid_cluster"
        response = self.fetch("/api/v1/cluster/invalid")
        self.assertEquals(response.code, 404)

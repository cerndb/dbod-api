#!/usr/bin/env python
"""Testing Magnum Clusters endpoint"""
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

class MagnumClustersTest(AsyncHTTPTestCase, unittest.TestCase):

    authentication = "basic " + \
                     base64.b64encode(config.get('api', 'user') + \
                     ":" + config.get('api', 'pass'))

    def get_app(self):
        return tornado.web.Application(handlers)

    def test_get_clusters(self):

        response = self.fetch("/api/v1/magnum/clusters/k8s-test", method="GET")#, headers={'Authorization': self.authentication})
        print 2, response.code, response.body

    @timeout(15)
    def test_post_clusters(self):
        body = {"name":"k8s-test",
                "discovery_url":None,
                "master_count":1,
                "cluster_template_id":"5b2ee3b5-2f85-4917-be7c-11a2c82031ad",
                "node_count":1,
                "create_timeout":60,
                "keypair":"dbod-magnum"}
        response = self.fetch("/api/v1/magnum/clusters/", 
			     method="POST", 
			     headers={'Authorization': self.authentication},
			     body=json.dumps(body))
	print 2, response.code, response.body

    def test_put_clusters(self):
        body = {"path":"/node_count","value":2,"op":"replace"}
        response = self.fetch("/api/v1/magnum/clusters/k8s-test", 
			     method="PUT", 
			     headers={'Authorization': self.authentication},
			     body=json.dumps(body))
	print 2, response.code, response.body

    def test_delete_clusters(self):
        response = self.fetch("/api/v1/magnum/clusters/k8s-test", 
			     method="DELETE", 
			     headers={'Authorization': self.authentication})
	print 2, response.code, response.body

#!/usr/bin/env python
"""Testing Kubernetes Clusters endpoint"""
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

class KubernetesClustersTest(AsyncHTTPTestCase, unittest.TestCase):

    authentication = "basic " + \
                     base64.b64encode(config.get('api', 'user') + \
                     ":" + config.get('api', 'pass'))

    def get_app(self):
        return tornado.web.Application(handlers)

    def test_get_clusters(self):
        response = self.fetch("/api/v1/beta/kubernetes/k8s-test2/namespaces/default/deployments/mysql-depl", method="GET")
        print response.body, response.code

    def test_post_clusters(self):
        body = json.load(open('mysql-depl.json'))
        response = self.fetch("/api/v1/kubernetes/k8s-test2/namespaces/default/deployments",
                             method="POST",
                             headers={'Authorization': self.authentication},
                             body=json.dumps(body))
        print 2, response.code

    def test_delete_clusters(self):
        response = self.fetch("/api/v1/beta/kubernetes/k8s-test/namespaces/default/deployments/mysql-depl",
                              method="DELETE",
                              headers={'Authorization': self.authentication})
        print response.body, response.code


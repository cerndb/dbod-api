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

from dbod.api.api import *

class ClusterTest(AsyncHTTPTestCase):
    def get_app(self):
        return tornado.web.Application(handlers)

    @timeout(5)
    def test_clustert(self):
        response = self.fetch("/api/v1/cluster/metadata/cluster01")
        data = json.loads(response.body)["response"]
        self.assertEquals(response.code, 200)
        self.assertEquals(data["name"],"cluster01")
        self.assertEquals(len(data["instances"]), 2)
        self.assertEquals(data["instances"][0]["name"], "node01")
        self.assertEquals(data["instances"][1]["name"], "node02")
        self.assertTrue(data[i]["volumes"] != None)
        self.assertEquals(len(data["attributes"]), 2)



    @timeout(5)
    def test_no_cluster(self):
        response = self.fetch("/api/v1/cluster/invalid")
        self.assertEquals(response.code, 404)

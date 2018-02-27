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
    def test_get_volume_by_instance_name(self):

        """test getting a volume by name"""

        # Check the data for the given cluster
        print "test_volume_metadata"
        response = self.fetch("/api/v1/volume/apiato01")
        self.assertEquals(response.code, 200)
        data = json.loads(response.body)["response"]
        self.assertEquals(len(data), 2)



    @timeout(5)
    def test_create_delete_volume(self):

        """test for create and delete a volume with the right data"""

        cluster = """{"instance_id": 3, "volume_type_id": "2", "server": "NAS-server", "mounting_path": "/MNT/data01", "attributes": [{ "test": "testvalue"}, {"test01" : "test01value" }], "file_mode": "0755", "owner": "TSM", "group": "ownergroup", "mount_options": "rw,bg,hard"}"""
        print "test_create_delete_volume"

        # Insert the volume
        response = self.fetch("/api/v1/volume/apiato03", method='POST', headers={'Authorization': self.authentication}, body=cluster)
        self.assertEquals(response.code, 201)

        # Check for the new volume
        response = self.fetch("/api/v1/volume/apiato03")
        self.assertEquals(response.code, 200)
        data = json.loads(response.body)["response"]
        self.assertEquals(len(data), 1)


        # Delete the created instance
        response = self.fetch("/api/v1/volume/" + str(data[0]["id"]) , method='DELETE', headers={'Authorization': self.authentication})
        self.assertEquals(response.code, 204)

        # Check again, the metadata should be empty
        response = self.fetch("/api/v1/volume/apiato03")
        self.assertEquals(response.code, 404)



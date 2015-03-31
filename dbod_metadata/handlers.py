#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2015, CERN
# This software is distributed under the terms of the GNU General Public
# Licence version 3 (GPL Version 3), copied verbatim in the file "LICENSE".
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as Intergovernmental Organization
# or submit itself to any jurisdiction.

"""
REST API Server for the DB On Demand System
"""

from dbod_metadata.dbops import entity_metadata, host_metadata
import tornado.web

class DocHandler(tornado.web.RequestHandler):
    """Generates api endpoint documentation"""
    def get(self):
        response = """Please use :
            http://hostname:port/api/v1/entity/<entity_name>\n
            http://hostname:port/api/v1/host/<hostname>\n"""
        self.write(response)

class EntityHandler(tornado.web.RequestHandler):
    def get(self, entity):
        """Returns metadata for a certain entity"""
        response = entity_metadata(entity)
        self.write(response)

class HostHandler(tornado.web.RequestHandler):
    def get(self, host):
        """Returns an object containing the metadata for all the entities
            on a certain host"""
        response = host_metadata(host)
        self.write(response)

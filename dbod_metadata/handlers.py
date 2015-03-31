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
import tornado.log

app_log = tornado.log.logging.getLogger("tornado.application")
app_log.setLevel(tornado.log.logging.DEBUG)

# HTTP API status codes
NOT_FOUND = 404

class DocHandler(tornado.web.RequestHandler):
    """Generates api endpoint documentation"""
    def get(self):
        response = """Please use :
            <p>http://hostname:port/api/v1/entity/NAME</p>
            <p>http://hostname:port/api/v1/host/HOSTNAME</p>"""
        self.write(response)

class EntityHandler(tornado.web.RequestHandler):
    def get(self, entity):
        """Returns metadata for a certain entity"""
        response = entity_metadata(entity)
        app_log.debug(response)
        if response:
            self.write(response)
        else:
            raise tornado.web.HTTPError(NOT_FOUND)

class HostHandler(tornado.web.RequestHandler):
    def get(self, host):
        """Returns an object containing the metadata for all the entities
            on a certain host"""
        response = host_metadata(host)
        if response:
            app_log.debug(response)
            self.write(response)
        else:
            raise tornado.web.HTTPError(NOT_FOUND)

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

from dbod.api.handlers import *
from dbod.api.instanceops import *
from dbod.config import CONFIG
import tornado.web
import tornado.log
import base64
import functools
import logging
import json


class InstanceHandler(tornado.web.RequestHandler):
    """Retrieves instances by a specific field: dbname, host, status"""
    def get(self, dbname):
        response = get_instances_by_dbname(dbname)
        if response:
            json_str = json.dumps(response)
            self.set_header("Content-Type", "application/json")
            self.write(json_str)
        else:
            logging.warning("No instances found")
            raise tornado.web.HTTPError(NOT_FOUND)
            
class InstanceListAllHandler(tornado.web.RequestHandler):
    """Retrieves all the active instances"""
    def get(self):
        response = get_instances_by_status(1)
        if response:
            json_str = json.dumps(response)
            self.set_header("Content-Type", "application/json")
            self.write(json_str)
        else:
            logging.warning("No instances found")
            raise tornado.web.HTTPError(NOT_FOUND)
            
class InstanceListExpiredHandler(tornado.web.RequestHandler):
    """Retrieves all the expired instances"""
    def get(self):
        response = get_instances_by_status(0)
        if response:
            json_str = json.dumps(response)
            self.set_header("Content-Type", "application/json")
            self.write(json_str)
        else:
            logging.warning("No instances found")
            raise tornado.web.HTTPError(NOT_FOUND)
            
class InstanceListByHostHandler(tornado.web.RequestHandler):
    """Retrieves all the instances by an specified host"""
    def get(self, host):
        response = get_instances_by_host(host)
        if response:
            json_str = json.dumps(response)
            self.set_header("Content-Type", "application/json")
            self.write(json_str)
        else:
            logging.warning("No instances found")
            raise tornado.web.HTTPError(NOT_FOUND)
            
class InstanceListHostHandler(tornado.web.RequestHandler):
    """Retrieves the list of hosts and the memory of each one"""
    def get(self):
        response = get_host_list()
        if response:
            json_str = json.dumps(response)
            self.set_header("Content-Type", "application/json")
            self.write(json_str)
        else:
            logging.warning("No hosts found: %s", value)
            raise tornado.web.HTTPError(NOT_FOUND)
            


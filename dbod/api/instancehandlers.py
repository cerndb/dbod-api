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
    def get(self, field, value):
        query = {'dbname': get_instances_by_dbname, 'host': get_instances_by_host, 'status': get_instances_by_status}
        try:
            response = query[field](value)
        except:
            logging.warning("Invalid field: %s", field)
            raise tornado.web.HTTPError(NOT_FOUND)

        if response:
            json_str = json.dumps(response)
            self.write(json_str)
        else:
            logging.warning("Instance not found: %s", value)
            raise tornado.web.HTTPError(NOT_FOUND)
            
class InstanceListAllHandler(tornado.web.RequestHandler):
    """Retrieves all the instances, or all the instances of the user if username is provided"""
    def get(self, username=None):
        if username:
            response = get_instances_by_username(username)
            if response:
                json_str = json.dumps(response)
                self.write(json_str)
            else:
                logging.warning("Username not found: %s", username)
                raise tornado.web.HTTPError(NOT_FOUND)
        else:
            response = get_all_instances()
            if response:
                json_str = json.dumps(response)
                self.write(json_str)
            else:
                logging.warning("No instances found")
                raise tornado.web.HTTPError(NOT_FOUND)
            
class InstanceHostHandler(tornado.web.RequestHandler):
    """Retrieves the list of hosts and the memory of each one"""
    def get(self):
        response = get_host_list()
        if response:
            json_str = json.dumps(response)
            self.write(json_str)
        else:
            logging.warning("No hosts found: %s", value)
            raise tornado.web.HTTPError(NOT_FOUND)
            


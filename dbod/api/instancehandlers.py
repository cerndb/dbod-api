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
    def get(self, dbname):
        response = get_instance(dbname)
        if response:
            logging.debug(response)
            json_str = json.dumps( response )
            logging.debug(json_str)
            self.write(json_str)
        else:
            logging.warning("Instance not found: %s", dbname)
            raise tornado.web.HTTPError(NOT_FOUND)


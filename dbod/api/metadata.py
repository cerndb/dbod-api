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

import tornado.web
import logging
import requests

from dbod.api.base import *
from dbod.config import config

class Metadata(tornado.web.RequestHandler):
    def get(self, **args):
        self.set_header("Content-Type", 'application/json')
        """Returns instance metadata"""
        url = config.get('postgrest', 'metadata_url')
        name = args.get('name')
        etype = args.get('class')
        if url and name:
            if etype == u'instance':
                composed_url = url + '?db_name=eq.' + name
            elif etype == u'host':
                composed_url = url + '?host=eq.' + name
            else:
                logging.error("Unsupported endpoint")
                raise tornado.web.HTTPError(NOT_FOUND)
            logging.debug('Requesting ' + composed_url)
            response = requests.get(composed_url, verify=False)
            if response.ok:
                data = response.json()
                if data:
                    self.write({'response' : data})
                else: 
                    logging.error("Instance metadata not found: " + name)
                    raise tornado.web.HTTPError(NOT_FOUND)
            else: 
                logging.error("Error fetching instance metadata: " + name)
                raise tornado.web.HTTPError(response.status_code)
        else:
            logging.error("Internal instance metadata endpoint not configured")
            raise tornado.web.HTTPError(NOT_FOUND)

#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2015, CERN
# This software is distributed under the terms of the GNU General Public
# Licence version 3 (GPL Version 3), copied verbatim in the file "LICENSE".
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as Intergovernmental Organization
# or submit itself to any jurisdiction.

"""
Metadata module, which includes all the classes related with metadata endpoints.
"""

import tornado.web
import logging
import requests
import json

from dbod.api.base import *
from dbod.config import config

class Metadata(tornado.web.RequestHandler):
    """The handler of /metadata/<class>/<name>"""
    def get(self, **args):
        """Returns the metadata of a host or an instance"""
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
                raise tornado.web.HTTPError(BAD_REQUEST)
            logging.info('Requesting ' + composed_url)
            response = requests.get(composed_url, verify=False)
            data = response.json()
            if response.ok and data:
                logging.debug("response: " + json.dumps(data))
                self.write({'response' : data})
            elif response.ok:
                logging.warning("Instance metadata not found: " + name)
                raise tornado.web.HTTPError(NOT_FOUND)
            else:
                logging.error("Error fetching instance metadata: " + response.text)
                raise tornado.web.HTTPError(response.status_code)
        else:
            logging.error("Internal instance metadata endpoint not configured")
            raise tornado.web.HTTPError(NOT_FOUND)

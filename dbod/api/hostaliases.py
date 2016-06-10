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
import json
import requests

from dbod.config import config

class HostAliases(tornado.web.RequestHandler):
    def get(self, host):
        """list of ip-aliases registered in a host"""
        url = config.get('postgrest', 'host_aliases_url')
        if url:
            composed_url = url + '?host=eq.' + host
            logging.debug('Requesting ' + composed_url )
            response = requests.get(composed_url)
            if response.ok:
                data = json.loads(response.text)
                d = data.pop()
                self.write(d.get('aliases'))
            else: 
                logging.error("Error fetching aliases in host: " + host)
                raise tornado.web.HTTPError(NOT_FOUND)
        else:
            logging.error("Internal host aliases endpoint not configured")

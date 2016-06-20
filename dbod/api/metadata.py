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

class Metadata(tornado.web.RequestHandler):
    def get(self, **args):
        self.set_header("Content-Type", 'application/json')
        """Returns entity metadata"""
        url = config.get('postgrest', 'entity_metadata_url')
        name = args.get('name')
        etype = args.get('class')
        if url:
            if etype == u'entity':
                composed_url = url + '?db_name=eq.' + name
            else:
                composed_url = url + '?host=eq.' + name
            logging.debug('Requesting ' + composed_url )
            response = requests.get(composed_url)
            if response.ok:
                data = json.loads(response.text)
                if data != []:
                    if etype == u'entity':
                        d = data.pop()
                        self.write(d)
                    else:
                        self.write(json.dumps(data))
                else: 
                    logging.error("Entity metadata not found: " + name)
                    raise tornado.web.HTTPError(NOT_FOUND)
            else: 
                logging.error("Error fetching entity metadata: " + name)
                raise tornado.web.HTTPError(response.status_code)
        else:
            logging.error("Internal entity metadata endpoint not configured")

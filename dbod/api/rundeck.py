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

class RundeckResources(tornado.web.RequestHandler):
    def get(self):
        """Returns an valid resources.xml file to import target entities in 
            Rundeck"""
        url = config.get('postgrest', 'rundeck_resources_url')
        if url:
            response = requests.get(url)
            if response.ok:
                data = json.loads(response.text)
                d = {}
                for entry in data:
                    d[entry[u'db_name']] = entry
                self.set_header('Content-Type', 'text/xml')
                # Page Header
                self.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                self.write('<project>\n')
                for instance in sorted(d.keys()):
                    body = d[instance]
                    text = ('<node name="%s" description="" hostname="%s" username="%s" type="%s" subcategory="%s" port="%s" tags="%s"/>\n' % 
                            ( instance, # Name
                              body.get(u'hostname'),
                              body.get(u'username'),
                              body.get(u'category'), 
                              body.get(u'db_type'), 
                              body.get(u'port'), 
                              body.get(u'tags')
                              ))
                    self.write(text)
                self.write('</project>\n')
            else: 
                logging.error("Error fetching Rundeck resources.xml")
                raise tornado.web.HTTPError(NOT_FOUND)
        else:
            logging.error("Internal Rundeck resources endpoint not configured")

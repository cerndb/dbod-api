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
import json
import urllib

from dbod.api.base import *
from dbod.config import config

class Job(tornado.web.RequestHandler):

    @http_basic_auth
    def get(self, **args):
        job_id = args.get('id')
        db_name = args.get('db_name')

        # Get instance information
        instance_id = get_instance_id_by_name(db_name)
        
        if not instance_id:
            logging.error("Instance not found for name: " + db_name)
            raise tornado.web.HTTPError(NOT_FOUND)

        if job_id:
            # Get an specific job
            response = requests.get(config.get('postgrest', 'job_url') + "?id=eq." + job_id)
            if response.ok:
                data = response.json()
                if data:
                    logging.debug("Received data: " + data)
                    if int(data[0]["instance_id"]) == instance_id:
                        self.write({'response' : data})
                        self.set_status(OK)
                    else:
                        logging.error("No rights to access job id: " + job_id + " from instance: " + db_name)
                        raise tornado.web.HTTPError(UNAUTHORIZED)
                else: 
                    logging.error("Job id not found: " + db_name)
                    raise tornado.web.HTTPError(NOT_FOUND)
        else:
            # Get all jobs for this instance starting from the most recent one
            response = requests.get(config.get('postgrest', 'job_url') + "?instance_id=eq." + str(instance_id))
            if response.ok:
                data = response.json()
                logging.debug(data)
                if data:
                    self.write({'response' : data})
                    self.set_status(OK)
                else: 
                    logging.error("Instance not found for name: " + db_name)
                    raise tornado.web.HTTPError(NOT_FOUND)
            else:
                logging.error("Instance not found for name: " + db_name)
                raise tornado.web.HTTPError(NOT_FOUND)

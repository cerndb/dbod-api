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

from apiato.api.base import *
from apiato.config import config

class Job(tornado.web.RequestHandler):

    def get(self, **args):
        job_id = args.get('id')
        db_name = args.get('db_name')

        try:
            instance_id = int(db_name) # If instance is an Integer, we are receiving the ID
        except:
            instance_id = get_instance_id_by_name(db_name)
        
        if not instance_id:
            logging.error("Instance not found for instance: " + db_name)
            raise tornado.web.HTTPError(NOT_FOUND)

        if job_id:
            # Get an specific job
            arguments = {'instance_id': 'eq.' + str(instance_id), 'id': 'eq.' + str(job_id)}
            response = requests.get(config.get('postgrest', 'rundeck_job_url'), params=arguments)
            if response.ok:
                data = response.json()
                if data:
                    logging.debug("Received data: " + str(data))
                    self.write({'response' : data[0]})
                    self.set_status(OK)
                else: 
                    logging.error("Job id not found: " + job_id)
                    raise tornado.web.HTTPError(NOT_FOUND)
        else:
            # Get all jobs for this instance starting from the most recent one
            arguments = {'instance_id': 'eq.' + str(instance_id)}
            response = make_full_get_request(config.get('postgrest', 'rundeck_job_url'), self.request, arguments)
            if response.ok:
                data = response.json()
                #logging.debug(data)
                if data:
                    result = {'response' : data}
                    add_meta(response, result)
                    self.write(result)
                    self.set_status(OK)
                else:
                    result = {'response' : []}
                    add_meta(response, result)
                    self.write(result)
                    self.set_status(OK)
            else:
                logging.error("Error getting jobs for instance: " + db_name)
                raise tornado.web.HTTPError(response.status_code, response.reason)
    
    def post(self, **args):
        """
        The *POST* method inserts a new job into the database wih all the
        information that is needed for tracking it.

        In the request body we specify all the information of the *job*
        All the information is sent to a stored procedure in PostgreSQL which 
        will insert the data in the related tables.
        
        .. note::
            
        :param id: this argument is not used, however it has to exist for compatibility with the rest of endpoints
        :type id: str
        :raises: HTTPError - in case of an internal error
        :request body:  json
        """

        logging.debug(self.request.body)
        job = {'in_json': json.loads(self.request.body)}
        
        # Insert the job in database using PostgREST
        insert_job_url = config.get('postgrest', 'insert_rundeck_job_url')
        response = requests.post(insert_job_url, 
                json=job, headers={'Prefer': 'return=representation'})
        if response.ok:
            logging.info("Inserted Job with Rundeck ID : " + repr(job["in_json"]["rundeck_id"]))
            logging.debug(response.text)
            self.set_status(CREATED)
        else:
            logging.error("Error creating the job: " + response.text)
            raise tornado.web.HTTPError(response.status_code)

class Job_filter(tornado.web.RequestHandler):
    """
    This is the handler of **/api/v1/job** endpoint.

    The request methods implemented for this endpoint are:

    * :func:`get`

    """

    get_jobs_url = config.get('postgrest', 'get_jobs_url')

    def get(self, *args):
        """
        The *GET* method returns a list of e_groups owning resources

        :rtype: json -- the response of the request
        :raises: HTTPError - if there is an internal error or if the response is empty
        """
        auth_header = self.request.headers.get('auth')
        logging.debug("Auth header : %s" % (auth_header))
        if auth_header is None:
            raise tornado.web.HTTPError(BAD_REQUEST, "No 'auth' header found.")
        
        try:
            auth = json.loads(auth_header)
        except:
            raise tornado.web.HTTPError(BAD_REQUEST, "Error parsing JSON 'auth' header.")

        logging.debug("RPC Url : %s" % (self.get_jobs_url))

        response = make_full_post_request(self.get_jobs_url, self.request, dict(), auth)

        if response.ok:
            logging.debug(response.text)
            result = {'response': json.loads(response.text)}
            add_meta(response, result)
            self.write(result)
            self.set_status(OK)
        else:
            logging.error("Response: %s" % (response.text))
            raise tornado.web.HTTPError(response.status_code)

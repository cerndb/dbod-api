#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2015, CERN
# This software is distributed under the terms of the GNU General Public
# Licence version 3 (GPL Version 3), copied verbatim in the file "LICENSE".
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as Intergovernmental Organization
# or submit itself to any jurisdiction.

"""
Rundeck module, which includes the rundeck classes and endpoints.
"""

import tornado.web
import logging
import json
import requests
import time

from dbod.api.base import *
from dbod.config import config

class RundeckResources(tornado.web.RequestHandler):
    """The class of /rundeck/resources.xml"""
    def get(self):
        """Returns a valid resources.xml file to import target entities in 
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
                logging.debug('<?xml version="1.0" encoding="UTF-8"?>')
                self.write('<?xml version="1.0" encoding="UTF-8"?>')
                logging.debug('<project>')
                self.write('<project>')
                for instance in sorted(d.keys()):
                    body = d[instance]
                    text = ('<node name="%s" description="" hostname="%s" username="%s" type="%s" subcategory="%s" port="%s" tags="%s"/>' % 
                            ( instance, # Name
                              body.get(u'hostname'),
                              body.get(u'username'),
                              body.get(u'category'), 
                              body.get(u'db_type'), 
                              body.get(u'port'), 
                              body.get(u'tags')
                              ))
                    logging.debug(text)
                    self.write(text)
                logging.debug('</project>')
                self.write('</project>')
            else: 
                logging.error("Error fetching Rundeck resources.xml")
                raise tornado.web.HTTPError(NOT_FOUND)
        else:
            logging.error("Internal Rundeck resources endpoint not configured")
            
class RundeckJobs(tornado.web.RequestHandler):
    """Class to manage the endpoints used to execute and visualize jobs execution in Rundeck
       /rundeck/jobs/<job>/<node>"""
    def get(self, **args):
        """Returns the output of a job execution"""
        job = args.get('job')
        response = self.__get_output__(job)
        if response.ok:
            logging.debug("response: " + response.text)
            self.write({'response' : json.loads(response.text)})
        else:
            logging.error("Error reading job from Rundeck: " + response.text)
            raise tornado.web.HTTPError(response.status_code)

    @http_basic_auth
    def post(self, **args):
        """Executes a new Rundeck job and returns the output"""
        job = args.get('job')
        node = args.get('node')
        response_run = self.__run_job__(job, node)
        if response_run.ok:
            data = json.loads(response_run.text)
            exid = str(data["id"])
            timeout = 20
            while timeout > 0:
                response_output = self.__get_output__(exid)
                if response_output.ok:
                    output = json.loads(response_output.text)
                    if output["execState"] != "running":
                        if output["execState"] == "succeeded":
                            logging.debug("response: " + response_output.text)
                            self.write({'response' : json.loads(response_output.text)})
                            timeout = 0
                        else:
                            logging.warning("The job completed with errors: " + exid)
                            raise tornado.web.HTTPError(BAD_GATEWAY)
                    else:
                        timeout -= 1
                        time.sleep(0.500)
                else:
                    logging.error("Error reading the job from Rundeck: " + response_output.text)
                    raise tornado.web.HTTPError(response_output.status_code)
        else:
            logging.error("Error running the job: " + response_run.text)
            raise tornado.web.HTTPError(response_run.status_code)
        
    def __get_output__(self, execution):
        """Returns the output of a job execution"""
        api_job_output = config.get('rundeck', 'api_job_output').format(execution)
        return requests.get(api_job_output, headers={'Authorization': config.get('rundeck', 'api_authorization')}, verify=False)
            
    def __run_job__(self, job, node):
        """Executes a new Rundeck job and returns the output"""
        jobid = config.get('rundeck-jobs', job)
        if jobid:
            run_job_url = config.get('rundeck', 'api_run_job').format(jobid)
            return requests.post(run_job_url, headers={'Authorization': config.get('rundeck', 'api_authorization')}, verify=False, data = {'filter':'name: ' + node})
        
        
        
        

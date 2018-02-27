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

from apiato.api.base import *
from apiato.config import config

class RundeckResources(tornado.web.RequestHandler):
    """The class of /rundeck/resources.xml"""
    def get(self):
        """Returns a valid resources.xml file to import target entities in 
            Rundeck"""
        response = requests.get(config.get('postgrest', 'rundeck_resources_url'))
        if response.ok:
            data = json.loads(response.text)
            d = {}
            for entry in data:
                d[entry[u'name']] = entry
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
                self.set_status(OK)
            logging.debug('</project>')
            self.write('</project>')
        else: 
            logging.error("Error fetching Rundeck resources.xml")
            raise tornado.web.HTTPError(NOT_FOUND)
            
class RundeckJobs(tornado.web.RequestHandler):
    """
    This is the handler of **/rundeck/jobs/<job>/<node>** endpoint.

    The class manages the endpoints used to execute and visualize jobs execution in Rundeck.

    .. note::

        You need to be authenticated in order to execute a job.
    """
    @http_basic_auth
    def get(self, **args):
        """
        The *GET* method returns the output of a job execution"""
        job = args.get('job')
        if (job is None):
            raise tornado.web.HTTPError(BAD_REQUEST, "Parameter 'job' not specified")

        if (not isinstance(job, (int, long))):
            raise tornado.web.HTTPError(BAD_REQUEST, "Parameter 'job' is not a number")

        response = self.__get_output__(job)
        if response.ok:
            logging.debug("response: " + response.text)
            try:
                self.write({'response' : json.loads(response.text)})
                self.set_status(OK)
            except:
                raise tornado.web.HTTPError(NOT_ACCEPTABLE, "Error parsing Rundeck response")
        else:
            logging.error("Error reading job from Rundeck: " + response.text)
            raise tornado.web.HTTPError(response.status_code)

    @http_basic_auth
    def post(self, **args):
        """
        The *POST* method executes a new Rundeck job and returns the output.
        
        The job and its hash has to be defined in the *api.cfg* configuration file in order to a specific job to be able to be executed.
        
        :param job: the name of the job to be executed which is listed in the configuration file
        :type job: str
        :param node: the name of the node you want the job to be executed
        :type node: str
        :raises: HTTPError - if the job didn't succeed or if the timeout has exceeded or in case of an internal error

        When a job is executed the request call hangs and waits for a response for a maximum time of 10 seconds. The api constantly calls rundeck's api to check if the job has finished. When it finishes it prints out the response or raises an error if it didn't succeed.
        """
        job = args.get('job')
        node = args.get('node')
        if (job is None):
            raise tornado.web.HTTPError(BAD_REQUEST, "Parameter 'job' not specified")

        if (node is None):
            raise tornado.web.HTTPError(BAD_REQUEST, "Parameter 'node' not specified")

        try:
            jobid = config.get('rundeck-jobs', job)
            logging.debug("Found 'jobid' for " + job + " = " + jobid)
        except:
            raise tornado.web.HTTPError(BAD_REQUEST, "Job '{0}' is not valid".format(job))

        response_run = self.__run_job__(jobid, node)
        if response_run.ok:
            try:
                data = json.loads(response_run.text)
            except:
                logging.debug("Reponse: " + response_run.text)
                raise tornado.web.HTTPError(NOT_ACCEPTABLE, "Error parsing Rundeck response")

            exid = str(data["id"])
            timeout = int(config.get('rundeck', 'timeout')) * 2
            while timeout > 0:
                response_output = self.__get_output__(exid)
                if response_output.ok:
                    try:
                        output = json.loads(response_output.text)
                    except:
                        continue
                    if output["execCompleted"]:
                        if output["execState"] == "succeeded":
                            logging.debug("response: " + response_output.text)
                            self.set_status(OK)
                            self.finish({'response' : output})
                            return
                        else:
                            logging.warning("The job completed with errors: " + exid)
                            raise tornado.web.HTTPError(BAD_GATEWAY)
                    else:
                        timeout -= 1
                        time.sleep(0.500)
                else:
                    logging.error("Error reading the job from Rundeck: " + response_output.text)
                    raise tornado.web.HTTPError(response_output.status_code)
            if timeout <= 0:
                logging.error("Rundeck job timed out: " + job)
                raise tornado.web.HTTPError(GATEWAY_TIMEOUT)
        else:
            logging.error("Error running the job: " + response_run.text)
            raise tornado.web.HTTPError(response_run.status_code)
        
    def __get_output__(self, execution):
        """Returns the output of a job execution"""
        api_job_output = config.get('rundeck', 'api_job_output').format(execution)
        logging.debug("Sending request: " + api_job_output)
        return requests.get(api_job_output, headers={'Authorization': config.get('rundeck', 'api_authorization')}, verify=False)
        
    def __run_job__(self, jobid, node):
        """Executes a new Rundeck job and returns the output"""
        run_job_url = config.get('rundeck', 'api_run_job').format(jobid)
        headers = {'Authorization': config.get('rundeck', 'api_authorization')}
        data = {'filter':'name: ' + node}
        logging.debug("Sending request: " + run_job_url + " with headers: " + str(headers) + " and data: " + str(data))
        return requests.post(run_job_url, headers=headers, verify=False, data=data)


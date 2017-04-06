#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2015, CERN
# This software is distributed under the terms of the GNU General Public
# Licence version 3 (GPL Version 3), copied verbatim in the file "LICENSE".
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Magnum Module"""

import logging
import json
import requests
import tornado.web
import tornado.gen
from dbod.api.base import *
from dbod.config import config
import shlex
from subprocess import check_output, CalledProcessError
from os import mkdir, path
import time


class MagnumClusters(tornado.web.RequestHandler):
    """This is the handler of **/instance/containers/<name>** endpoint"""

    headers = {'Content-Type': 'application/json'}
    cloud = config.get('containers-provider', 'cloud')
    certs_dir = config.get(cloud, 'cluster_certs_dir')

    @cloud_auth(cloud)
    def get(self, **args):
        composed_url = self.magnum_config(args)

        data, status_code = get_function(composed_url, headers=self.headers)
        if data:
            logging.debug("response: " + json.dumps(data))
            self.write({'response' : data})
        else:
            logging.error("Error fetching magnum's resources in this endpoint: " + composed_url)
            raise tornado.web.HTTPError(status_code)

    @cloud_auth(cloud)
    @http_basic_auth
    def post(self, **args):
        composed_url = self.magnum_config(args)
        try:
            cluster_specs = json.loads(self.request.body)
            logging.debug("Creation parameters: " + json.dumps(cluster_specs))
        except ValueError:
            logging.error("No JSON object could be decoded from request body")
            raise tornado.web.HTTPError(BAD_REQUEST)

        new_cluster = cluster_specs['name']
        _, status_code = get_function(composed_url + '/' + new_cluster, headers=self.headers)
        if status_code == 200 or status_code == 409:
            logging.error("Multiple clusters exist with same name.")
            self.set_status(CONFLICT)
        else:
            response = requests.post(composed_url, json=cluster_specs, headers=self.headers)
            if response.ok:
                print self.request.uri
                data = response.json()
                logging.info("New cluster created with name: %s and UUID: %s" %(new_cluster, data["uuid"]))
                logging.info("Call GET %s/%s to check when the creation finishes." %(self.request.uri, new_cluster))

                self.write({'response' : data})
                self.set_status(ACCEPTED)
            else:
                logging.error("Error in creating the magnum cluster: " + response.text)
                self.set_status(response.status_code)



    @cloud_auth(cloud)
    @http_basic_auth
    def put(self, **args):
        composed_url = self.magnum_config(args)

        try:
            cluster_specs = json.loads(self.request.body)
            logging.debug("Creation parameters: " + json.dumps(cluster_specs))
        except ValueError:
            logging.error("No JSON object could be decoded")
            raise tornado.web.HTTPError(BAD_REQUEST)

        response = requests.patch(composed_url, json=[cluster_specs], headers=self.headers)
        if response.ok:
            data = response.json()
            logging.info("New cluster specs for %s are being applied." %(composed_url))
            logging.info("Call GET %s to check when the update finishes." %(composed_url))

            self.write({'response' : data})
            self.set_status(ACCEPTED)
        else:
            logging.error("Error in updating the magnum cluster: " + response.text)
            self.set_status(response.status_code)

    @cloud_auth(cloud)
    @http_basic_auth
    def delete(self, **args):
        composed_url = self.magnum_config(args)
        ident = args.get('name')
        response = requests.delete(composed_url, headers=self.headers)
        if response.ok:
            logging.info("Delete cluster %s" %(ident))
            logging.info("Call GET %s to check when the deletion finishes." %(self.request.uri))
	    cluster_certs_dir = self.certs_dir + '/' + ident
	    cmd = "mv " + cluster_certs_dir + ' ' + cluster_certs_dir + ".old"
	    if path.isdir(cluster_certs_dir):
		try:
		    check_output(cmd.split())
		    logging.debug("Delete(renaming) certs directory: " + cluster_certs_dir)
		except CalledProcessError as e:
		    logging.warning("Failed to run the command %s with args %s" %(e.cmd))
                    logging.warning("Command failed with return code: %s and output: %s" %(e.returncode, e.output))

            self.set_status(NO_CONTENT)
        else:
            logging.error("Error in deleting the magnum cluster: " + response.text)
            self.set_status(response.status_code)

    def magnum_config(self, args):
        token_header = 'X-Subject-Token'
        auth_header = 'X-Auth-Token'
        url = config.get(self.cloud, 'cluster_url')

        logging.debug('Arguments:' + str(self.request.arguments))

        xtoken = {auth_header: args.get(token_header)}
        self.headers.update(xtoken)
        base_url = args.get('resource')
        ident = args.get('name')
        composed_url = url
        if base_url:
            composed_url = url + '/' + base_url
        if ident:
            composed_url = composed_url + '/' + ident
        logging.info('Requesting ' + composed_url)
        return composed_url


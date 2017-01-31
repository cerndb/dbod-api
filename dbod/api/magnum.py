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
import tornado.escape
from dbod.api.base import *
from dbod.config import config

class MagnumClusters(tornado.web.RequestHandler):
    """This is the handler of **/instance/containers/<name>** endpoint"""

    token_header = 'X-Subject-Token'
    auth_header = 'X-Auth-Token'
    url = config.get('openstack', 'magnum_cluster_url')
    headers = {'Content-Type': 'application/json'}
    acc_base_urls = ['clusters', 'bays', 'clustertemplates', 'baymodels']

    @keystone_auth
    def get(self, **args):
        xtoken = {self.auth_header: args.get(self.token_header.replace('-','_'))}
        logging.debug('Arguments:' + str(self.request.arguments))

        base_url = args.get('class')
        ident = args.get('name')

        if base_url in self.acc_base_urls:
            composed_url = self.url + '/' + base_url
            if ident:
                composed_url = composed_url + '/' + ident
            logging.info('Requesting ' + composed_url)
            response = requests.get(composed_url, headers=xtoken)
            data = response.json()
            if response.ok and data:
                logging.debug("response: " + json.dumps(data))
                self.write({'response' : data})
            elif response.ok:
                logging.warning("Magnum resources don't exist in this endpoint: " + composed_url)
                raise tornado.web.HTTPError(NOT_FOUND)
            else:
                logging.error("Error fetching magnum's resources in this endpoint" + composed_url)
                raise tornado.web.HTTPError(response.status_code)
        else:
            logging.error("Unsupported endpoint")
            raise tornado.web.HTTPError(NOT_FOUND)


    @keystone_auth
    @http_basic_auth
    def post(self, **args):
        xtoken = {self.auth_header: args.get(self.token_header.replace('-','_'))}

        logging.debug('Arguments:' + str(self.request.arguments))
        base_url = args.get('class')
        #ident = args.get('name')

        try:
            cluster_specs = json.loads(self.request.body)
            logging.debug("Creation parameters: " + json.dumps(cluster_specs))
        except ValueError:
            logging.error("No JSON object could be decoded")
            raise tornado.web.HTTPError(BAD_REQUEST)

        self.headers.update(xtoken)

        if base_url in self.acc_base_urls:
            composed_url = self.url + '/' + base_url
            check_req = requests.get(composed_url+'/'+cluster_specs["name"], headers=self.headers)
            if check_req.status_code == 409 or check_req.ok:
                logging.error("Multiple clusters exist with same name.")
                self.set_status(CONFLICT)
            else: 
                response = requests.post(composed_url, json=cluster_specs, headers=xtoken)
                if response.ok:
                    data = response.json()
                    logging.info("New cluster created with name: %s and UUID: %s" %(cluster_specs["name"], data["uuid"]))
                    logging.info("Call GET /api/v1/magnum/clusters/%s to check when the creation finishes." %(cluster_specs["name"]))
                    
                    self.write({'response' : data})
                    self.set_status(ACCEPTED)
                else:
                    logging.error("Error in creating the magnum cluster: " + response.text)
                    self.set_status(response.status_code)
        else:
            logging.error("Unsupported endpoint")
            raise tornado.web.HTTPError(NOT_FOUND)


    @keystone_auth
    @http_basic_auth
    def put(self, **args):
        xtoken = {self.auth_header: args.get(self.token_header.replace('-','_'))}

        logging.debug('Arguments:' + str(self.request.arguments))
        base_url = args.get('class')
        ident = args.get('name')

        try:
            cluster_specs = json.loads(self.request.body)
            logging.debug("Creation parameters: " + json.dumps(cluster_specs))
        except ValueError:
            logging.error("No JSON object could be decoded")
            raise tornado.web.HTTPError(BAD_REQUEST)

        self.headers.update(xtoken)

        if base_url in self.acc_base_urls and ident:
            composed_url = self.url + '/' + base_url + '/' + ident
            response = requests.patch(composed_url, json=[cluster_specs], headers=xtoken)
            if response.ok:
                data = response.json()
                logging.info("New cluster specs for %s are being applied." %(ident))
                logging.info("Call GET /api/v1/magnum/clusters/%s to check when the update finishes." %(ident))
                
                self.write({'response' : data})
                self.set_status(ACCEPTED)
            else:
                logging.error("Error in updating the magnum cluster: " + response.text)
                self.set_status(response.status_code)
        else:
            logging.error("Unsupported endpoint")
            raise tornado.web.HTTPError(NOT_FOUND)

    @keystone_auth
    @http_basic_auth
    def delete(self, **args):
        xtoken = {self.auth_header: args.get(self.token_header.replace('-','_'))}

        logging.debug('Arguments:' + str(self.request.arguments))
        base_url = args.get('class')
        ident = args.get('name')

        self.headers.update(xtoken)

        if base_url in self.acc_base_urls and ident:
            composed_url = self.url + '/' + base_url + '/' + ident
            response = requests.delete(composed_url, headers=xtoken)
            if response.ok:
                logging.info("New cluster specs for %s applied." %(ident))
                logging.info("Call GET /api/v1/magnum/clusters/%s to check when the deletion finishes." %(ident))
                
                self.set_status(NO_CONTENT)
            else:
		print response.text
                logging.error("Error in deleting the magnum cluster: " + response.text)
                self.set_status(response.status_code)
        else:
            logging.error("Unsupported endpoint")
            raise tornado.web.HTTPError(NOT_FOUND)


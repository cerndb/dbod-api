#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2015, CERN
# This software is distributed under the terms of the GNU General Public
# Licence version 3 (GPL Version 3), copied verbatim in the file "LICENSE".
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Kubernetes Module"""

import logging
import json
import yaml
import requests
import tornado.web
import tornado.escape
from dbod.api.base import *
from dbod.config import config

class KubernetesClusters(tornado.web.RequestHandler):
    """This is the handler of **/kubernetes/<class>/<name>** endpoint"""

    token_header = 'X-Subject-Token'
    auth_header = 'X-Auth-Token'
    headers = {'Content-Type': 'application/json'}
    cloud = config.get('containers-provider', 'cloud')
    coe = config.get(cloud, 'coe')

    @cloud_auth(coe)
    def get(self, **args):
        composed_url, cert, key, ca = self._config(args)

        logging.debug("Request to " + composed_url)
        response = requests.get(composed_url, cert=(cert, key), verify=ca)
        if response.ok:
            data = response.json()
            logging.info("response: " + json.dumps(data))
            self.write({'response': data})
        else:
            logging.error("Error in fetching %s 's resources from %s" %(self.coe, composed_url))
            self.set_status(response.status_code)

    @cloud_auth(coe)
    @http_basic_auth
    def post(self, **args):
        composed_url, cert, key, ca = self._config(args)

        try:
            specs = json.loads(self.request.body)
            logging.debug("Creation parameters: %s" %(specs))
        except ValueError:
            logging.error("No JSON object could be decoded from request body")
            raise tornado.web.HTTPError(BAD_REQUEST)

        resource = args.get('resource')
        subresource = args.get('subresource')
        if specs['kind'] != resource and specs['kind'] != subresource:
            logging.warning("Ensure that your request 'kind:%s' is for this endpoint" %(specs['kind']))

        logging.debug("Request to " + composed_url)
        response = requests.post(composed_url,
                                 json=specs,
                                 cert=(cert, key),
                                 verify=ca,
                                 headers=self.headers)
        if response.ok:
            data = response.json()
            logging.info("response: " + json.dumps(data))
            self.write({'response': data})
        else:
            logging.error("Error in fetching %s 's resources from %s" %(self.coe, composed_url))
            self.set_status(response.status_code)


    @cloud_auth(coe)
    @http_basic_auth
    def delete(self, **args):
        composed_url, cert, key, ca = self._config(args)

        logging.debug("Request to " + composed_url)
        response = requests.delete(composed_url,
                                   cert=(cert, key),
                                   verify=ca,
                                   headers=self.headers)
        if response.ok:
            data = response.json()
            logging.info("response: " + json.dumps(data))
            self.write({'response': data})
        else:
            logging.error("Error in fetching %s 's resources from %s" %(self.coe, composed_url))
            self.set_status(response.status_code)

    def _config(self, args):
        logging.debug('Arguments:' + str(self.request.arguments))

        cluster_name = args.get('cluster')
        resource = args.get('resource')
        ident = args.get('name')
        subresource = args.get('subresource')
        subname = args.get('subname')
        cluster_certs_dir = config.get(self.cloud, 'cluster_certs_dir') + '/' + cluster_name

        kubeApi = self._api_master(cluster_name)
        if self.request.uri.split('/')[3] == 'beta':
            apiVersion = 'apis/extensions/v1beta1'
        else:
            apiVersion = 'api/v1'
        #kubeApi = kubeList[0]
        composed_url = kubeApi + '/' + apiVersion
        if resource:
            composed_url = composed_url + '/' + resource
            if ident:
                composed_url = composed_url + '/' + ident
                if subresource:
                    composed_url = composed_url + '/' + subresource
                    if subname:
                        composed_url = composed_url + '/' + subname
        cert = cluster_certs_dir + '/cert.pem'
        key = cluster_certs_dir + '/key.pem'
        ca = cluster_certs_dir + '/ca.pem'
        return composed_url, cert, key, ca

    @cloud_auth(cloud)
    def _api_master(self, cluster_name, **args):
        token_header = 'X-Subject-Token'
        auth_header = 'X-Auth-Token'

        xtoken = {auth_header: args.get(token_header)}
        self.headers.update(xtoken)

        url = config.get(self.cloud, 'cluster_url')
        composed_url = url + '/' + 'clusters' + '/' + cluster_name
        data, status_code = get_function(composed_url, self.headers)
        if status_code == 200:
            kubeApiList = data['api_address']
            logging.debug("Kubernetes master(s) api: " + str(kubeApiList))
            return kubeApiList
        else:
            logging.error("Error fetching magnum's resources in this endpointi: " + self.url + '/' + magnum_cluster)
            raise tornado.web.HTTPError(response.status_code)


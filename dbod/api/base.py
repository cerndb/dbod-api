#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2015, CERN
# This software is distributed under the terms of the GNU General Public
# Licence version 3 (GPL Version 3), copied verbatim in the file "LICENSE".
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as Intergovernmental Organization
# or submit itself to any jurisdiction.

"""
Base module with common methods and classes used by another endpoints.
"""

import tornado.web
import base64
import functools
import logging
import requests
import json
import urllib

from dbod.config import config

# HTTP API status codes
OK = 200
CREATED = 201 # Request fulfilled resulting in creation of new resource
ACCEPTED = 202
NO_CONTENT = 204 # Succesfull delete
NOT_FOUND = 404
UNAUTHORIZED = 401
CONFLICT = 409
BAD_REQUEST = 400
BAD_GATEWAY = 502
SERVICE_UNAVAILABLE = 503

# Basic HTTP Authentication decorator
def http_basic_auth(fun):
    """Decorator for extracting HTTP basic authentication user/password pairs
    from the request headers and matching them to configurated credentials.
    It will generate an HTTP UNAUTHORIZED (Error code 401) if the request is
    not using HTTP basic authentication.

    Example:
        @http_basic_auth
        def get(self, user, pwd)
    """
    @functools.wraps(fun)
    def wrapper(*args, **kwargs):
        """ Decorator wrapper """
        self = args[0]
        try:
            # Try
            auth = self.request.headers.get('Authorization')
            scheme, _, token = auth.partition(' ')
            if scheme.lower() == 'basic':
                # Decode user and password
                user, _, pwd = base64.decodestring(token).partition(':')
                if user == config.get('api','user') and pwd == config.get('api','pass'):
                    return fun(*args, **kwargs)
                else:
                    # Raise UNAUTHORIZED HTTP Error (401)
                    logging.error("Unauthorized access from: %s",
                        self.request.headers)
                    raise tornado.web.HTTPError(UNAUTHORIZED)

            else:
                # We only support basic authentication
                logging.error("Authentication scheme not recognized")
                return "Authentication scheme not recognized"
        except AttributeError:
            # Raise UNAUTHORIZED HTTP Error (401) if the request is not
            # using autentication (auth will be None and partition() will fail
            logging.error("Unauthorized access from: %s",
                self.request.headers)
            raise tornado.web.HTTPError(UNAUTHORIZED)

    return wrapper

# Openstack authentication through keystone
def keystone_auth(fun):
    @functools.wraps(fun)
    def wrapper(*args, **kwargs):
        token_header = 'X-Subject-Token'

        keystone_url = config.get('openstack','keystone_id_url')
        auth_url = keystone_url + '/auth' + '/tokens'
        auth_json_file = config.get('openstack','dbodpilot_keystone_json')
        try:
            auth_json = json.load(open(auth_json_file, 'r'))
            header = {'Content-Type': 'application/json'}
            response = requests.post(auth_url, 
                                     json=auth_json, 
                                     headers=header)
            if response.ok:
                logging.debug("Token collected for DBoD Pilot Project")
                return fun(X_Subject_Token=response.headers[token_header], *args, **kwargs)
            else:
                logging.error("No Token provided to access openstack with status code: %s" %(response.status_code))
                raise tornado.web.HTTPError(response.status.code)
        except ValueError:
            logging.error("No JSON format of the authentication file provided for keystone.")
            raise tornado.web.HTTPError(BAD_REQUEST)
        except KeyError:
            logging.error("No X-Subject-Token available in headers")
            logging.debug("Headers of the response from keystone: %s" %(response.headers))
            tornado.web.HTTPError(SERVICE_UNAVAILABLE)
    return wrapper        

def get_instance_id_by_name(name):
    """Common function to get the ID of an instance by its name."""
    response = requests.get(config.get('postgrest', 'instance_url') + "?db_name=eq." + name)
    if response.ok:
        data = response.json()
        if data:
            return data[0]["id"]
    return None

class DocHandler(tornado.web.RequestHandler):
    """Shows the list of endpoints available in the API"""
    def get(self):
        logging.info("Generating API endpoints doc")
        response = """Please use :
            <p>http://hostname:port/api/v1/instance/NAME</p>
            <p>http://hostname:port/api/v1/instance/alias/NAME</p>
            <p>http://hostname:port/api/v1/host/aliases/HOSTNAME</p>
            <p>http://hostname:port/api/v1/metadata/instance/NAME</p>
            <p>http://hostname:port/api/v1/metadata/host/HOSTNAME</p>
            <p>http://hostname:port/api/v1/rundeck/resources.xml</p>
            <p>http://hostname:port/api/v1/rundeck/job/JOB/NODE</p>"""
        self.set_header("Content-Type", 'text/html')
        self.write(response)

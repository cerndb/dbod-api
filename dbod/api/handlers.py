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

from dbod.api.dbops import *
from dbod.config import config
import tornado.web
import tornado.log
import base64
import functools
import logging
import json
import requests


# HTTP API status codes
OK = 200
CREATED = 201 # Request fulfilled resulting in creation of new resource
NO_CONTENT = 204 # Succesfull delete
NOT_FOUND = 404
UNAUTHORIZED = 401

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

class DocHandler(tornado.web.RequestHandler):
    """Generates the API endpoint documentation"""
    def get(self):
        logging.info("Generating API endpoints doc")
        response = """Please use :
            <p>http://hostname:port/api/v1/entity/NAME</p>
            <p>http://hostname:port/api/v1/host/HOSTNAME</p>"""
        self.write(response)

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
            

class HostAliases(tornado.web.RequestHandler):
    def get(self, host):
        """list of ip-aliases registered in a host"""
        url = config.get('postgrest', 'host_aliases_url')
        if url:
            composed_url = url + '?host=eq.' + host
            logging.debug('Requesting ' + composed_url )
            response = requests.get(composed_url)
            if response.ok:
                data = json.loads(response.text)
                d = data.pop()
                self.write(d.get('aliases'))
            else: 
                logging.error("Error fetching aliases in host: " + host)
                raise tornado.web.HTTPError(NOT_FOUND)
        else:
            logging.error("Internal host aliases endpoint not configured")
            
class Metadata(tornado.web.RequestHandler):
    def get(self, **args):
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

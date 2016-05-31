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

class EntityHandler(tornado.web.RequestHandler):

    def get(self, entity):
        """Returns metadata for a certain entity"""
        response = get_metadata(entity)
        if response:
            logging.debug(response)
            self.write(response)
        else:
            logging.warning("Entity not found: %s", entity)
            raise tornado.web.HTTPError(NOT_FOUND)

    @http_basic_auth
    def post(self, entity):
        """Returns metadata for a certain entity"""
        try:
            metadata = self.get_argument('metadata')
            response = insert_metadata(entity, metadata)
            if response:
                logging.debug("Metadata successfully created for %s: %s",
                        entity, metadata)
                self.set_status(CREATED)
                self.finish()
        except tornado.web.MissingArgumentError as err:
            logging.error("Missing 'metadata' argument in request!")
            raise tornado.web.MissingArgumentError()
    
    @http_basic_auth
    def put(self, entity):
        """Returns metadata for a certain entity"""
        try:
            metadata = self.get_argument('metadata')
            response = update_metadata(entity, metadata)
            if response:
                logging.debug("Metadata successfully updated for %s: %s",
                        entity, metadata)
                self.set_status(CREATED)
                self.finish()
        except tornado.web.MissingArgumentError as err:
            logging.error("Missing 'metadata' argument in request!")
            raise tornado.web.MissingArgumentError()

    @http_basic_auth
    def delete(self, entity):
        """Returns metadata for a certain entity"""
        response = delete_metadata(entity)
        if response:
            self.set_status(NO_CONTENT)
            self.finish()
        else:
            logging.warning("Entity not found: %s", entity)
            raise tornado.web.HTTPError(NOT_FOUND)

class HostHandler(tornado.web.RequestHandler):
    def get(self, host):
        """Returns an object containing the metadata for all the entities
            on a certain host"""
        response = host_metadata(host)
        if response:
            logging.debug(response)
            self.write(json.dumps(response))
        else:
            logging.warning("Metadata not found for host:  %s", host)
            raise tornado.web.HTTPError(NOT_FOUND)

class FunctionalAliasHandler(tornado.web.RequestHandler):
    def get(self, entity):
        """Returns the functional alias association for an entity"""
        response = get_functional_alias(entity)
        if response:
            logging.debug(response)
            self.write(json.dumps(response))
        else:
            logging.error("Functional alias not found for entity: %s", entity)
            raise tornado.web.HTTPError(NOT_FOUND)

    @http_basic_auth 
    def post(self, entity):
        """Creates a functional alias association for an entity"""
        dnsname = next_dnsname()
        if dnsname:
            try:
                alias = self.get_argument('alias')
                response = update_functional_alias(dnsname[0], entity, alias)
                if response:
                    logging.debug("Functional alias (%s) successfully added for %s",
                            alias, entity)
                    self.set_status(CREATED)
                    self.write(json.dumps(dnsname))
            except tornado.web.MissingArgumentError as err:
                logging.error("Missing 'alias' argument in request!")
                raise tornado.web.MissingArgumentError()
        else:
            logging.error("No available dnsnames found!")
            raise tornado.web.HTTPError(NOT_FOUND)

    @http_basic_auth 
    def delete(self, entity):
        """Removes the functional alias association for an entity.
            If the functional alias doesn't exist it doesn't do anything"""
        dnsname_full = get_functional_alias(entity)
        if dnsname_full:
            dnsname = dnsname_full[0]
            response = update_functional_alias(dnsname, None, None)
            if response:
                logging.debug("Functional alias successfully removed for %s",
                        entity)
                self.set_status(NO_CONTENT)
                self.finish()
        else:
            logging.error("Functional alias not found for entity: %s", entity)
            raise tornado.web.HTTPError(NOT_FOUND)


class RundeckResources(tornado.web.RequestHandler):
    def get(self):
        """Returns an valid resources.xml file to import target entities in 
            Rundeck"""

        import requests
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
        import requests
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
        import requests
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

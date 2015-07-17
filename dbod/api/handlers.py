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
    from the request headers and passing them to the decorated method. It will
    generate an HTTP UNAUTHORIZED (Error code 401) if the request is not using
    HTTP basic authentication.

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
                # Decode user and password and pass them to the decorated
                # method
                user, _, pwd = base64.decodestring(token).partition(':')
                logging.info("Authentiated access for user %s", user)
                return fun(*args, user=user, pwd=pwd, **kwargs)
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
        response = entity_metadata(entity)
        if response:
            logging.debug(response)
            self.write(response)
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

    def post(self, entity, alias):
        """Updates the functional alias association for an entity"""
        dnsname = next_dnsname()
        response = update_functional_alias(dnsname, entity, alias)
        if response:
            logging.debug("Functional alias (%s) successfully added for %s",
                    alias, entity)
            self.set_status(OK)
            self.finish()
        if response:
            logging.debug(response)
            self.write(json.dumps(response))
        else:
            logging.error("Functional alias not found for entity: %s", entity)
            raise tornado.web.HTTPError(NOT_FOUND)
    
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


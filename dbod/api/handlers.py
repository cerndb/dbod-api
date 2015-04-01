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

from dbod.api.dbops import entity_metadata, host_metadata
import tornado.web
import tornado.log
import base64
import functools

app_log = tornado.log.logging.getLogger("tornado.application")
app_log.setLevel(tornado.log.logging.DEBUG)

# HTTP API status codes
NOT_FOUND = 404
UNAUTHORIZED = 401

# Basic HTTP Authentication decorator
def http_basic_auth(f):
    """Decorator for extracting HTTP basic authentication user/password pairs from
    the request headers and passing them to the decorated method. It will return
    generate an HTTP UNAUTHORIZED (Error code 401) if the request is not using
    HTTP basic authentication.

    Example:
        @http_basic_auth
        def get(self, user, pwd)
    """
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        self = args[0]
        try:
            # Try
            auth = self.request.headers.get('Authorization')
            scheme, _, token = auth.partition(' ')
            if scheme.lower() == 'basic':
                # Decode user and password and pass them to the decorated
                # method
                user, _, pwd = base64.decodestring(token).partition(':')
                return f(*args, user=user, pwd=pwd, **kwargs)
            else:
                # We only support basic authentication
                return "Authentication scheme not recognized"
        except AttributeError as e:
            # Raise UNAUTHORIZED HTTP Error (401) if the request is not
            # using autentication (auth will be None and partition() will fail
            raise tornado.web.HTTPError(UNAUTHORIZED)

    return wrapper

class DocHandler(tornado.web.RequestHandler):
    """Generates the API endpoint documentation"""
    @http_basic_auth
    def get(self, user, pwd):
        app_log.debug("user, pass: (%s, %s)" % (user, pwd))
        response = """Please use :
            <p>http://hostname:port/api/v1/entity/NAME</p>
            <p>http://hostname:port/api/v1/host/HOSTNAME</p>"""
        self.write(response)

class EntityHandler(tornado.web.RequestHandler):
    def get(self, entity):
        """Returns metadata for a certain entity"""
        response = entity_metadata(entity)
        app_log.debug(response)
        if response:
            self.write(response)
        else:
            raise tornado.web.HTTPError(NOT_FOUND)

class HostHandler(tornado.web.RequestHandler):
    def get(self, host):
        """Returns an object containing the metadata for all the entities
            on a certain host"""
        response = host_metadata(host)
        if response:
            app_log.debug(response)
            self.write(response)
        else:
            raise tornado.web.HTTPError(NOT_FOUND)

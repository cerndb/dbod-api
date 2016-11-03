#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2015, CERN
# This software is distributed under the terms of the GNU General Public
# Licence version 3 (GPL Version 3), copied verbatim in the file "LICENSE".
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as Intergovernmental Organization
# or submit itself to any jurisdiction.

"""
Main module to initialize the Tornado Server and endpoints
"""

import ConfigParser
import sys, traceback
import tornado.web
#import logging

from tornado.options import parse_command_line, options, define
from tornado.log import LogFormatter, logging
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from dbod.api.base import DocHandler
from dbod.api.rundeck import RundeckResources, RundeckJobs
from dbod.api.metadata import Metadata
from dbod.api.functionalalias import FunctionalAlias
from dbod.api.hostaliases import HostAliases
from dbod.api.instance import Instance
from dbod.config import config

handlers = [
    (r"/", DocHandler),
    (r"/api/v1/instance/([^/]+)", Instance),
    (r"/api/v1/host/aliases/([^/]+)", HostAliases),
    (r"/api/v1/instance/alias/?(?P<db_name>[^\/]+)?", FunctionalAlias),
    (r"/api/v1/metadata/(?P<class>[^\/]+)/?(?P<name>[^\/]+)?", Metadata),
    (r"/api/v1/rundeck/resources.xml", RundeckResources),
    (r"/api/v1/rundeck/job/(?P<job>[^\/]+)/?(?P<node>[^\/]+)?", RundeckJobs),
    ]

class Application():
    """
    This is the main entrypoint of the dbod-api where the main parameters are specified in order to start the server.
    """
    def __init__(self):
        # Set up log file, level and formatting
        options.log_file_prefix = config.get('logging', 'path')
        options.logging = config.get('logging', 'level')
        options.log_to_stderr = config.getboolean('logging', 'stderr')
        
        # Port and arguments
        port = config.get('server', 'port')
        define('port', default=port, help='Port to be used')
        parse_command_line([])
       
        # Override default logging format and date format
        log_format = config.get('logging', 'fmt', raw = True)
        date_format = config.get('logging', 'datefmt', raw = True)
        if date_format:
            formatter = tornado.log.LogFormatter(fmt = log_format, datefmt = date_format)
            for logger in logging.getLogger('').handlers:
                logging.info('Overriding log format for %s' % (logger))
                logger.setFormatter(formatter)

        # Defining handlers
        logging.info("Defining application (url, handler) pairs")
        application = tornado.web.Application(handlers, debug=config.getboolean('tornado', 'debug'))
        
        # Configuring server and SSL
        logging.info("Configuring HTTP server")
        if (config.has_section('ssl')):
            http_server = HTTPServer(application,
                    ssl_options = {
                        "certfile" : config.get('ssl', 'hostcert') ,
                        "keyfile" : config.get('ssl', 'hostkey'),
                        })
        else:
            http_server = HTTPServer(application)
            logging.info("Host certificate undefined, SSL is DISABLED")
            
        # Listening port
        http_server.listen(options.port)
        
        # Starting
        logging.info("Starting application on port: " + str(port))
        tornado.ioloop.IOLoop.instance().start()

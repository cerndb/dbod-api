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
import sys, traceback, re
import tornado.web
#import logging

from tornado.options import parse_command_line, options, define
from tornado.log import LogFormatter, logging
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from apiato.api.base import DocHandler
from apiato.api.rundeck import RundeckResources, RundeckJobs
from apiato.api.metadata import Metadata
from apiato.api.functionalalias import FunctionalAlias
from apiato.api.hostaliases import HostAliases
from apiato.api.host import Host, HostList
from apiato.api.instance import Instance, Instance_filter
from apiato.api.attribute import Attribute
from apiato.api.fim import Fim
from apiato.config import config, optionalConfig
from apiato.api.cluster import Cluster, Cluster_filter
from apiato.api.volume import Volume
from apiato.api.auth import Resources
from apiato.api.job import Job, Job_filter

# This list is a global object because in needs to be accessed
# from the test suites
handlers = [
    (r"/", DocHandler),
    (r"/api/v1/auth/resources", Resources),
    (r"/api/v1/instance/([^/]+)", Instance),
    (r"/api/v1/instance", Instance_filter),
    (r"/api/v1/cluster/([^/]+)", Cluster),
    (r"/api/v1/cluster", Cluster_filter),
    (r"/api/v1/volume/([^/]+)", Volume),
    (r"/api/v1/host/aliases/([^/]+)", HostAliases),
    (r"/api/v1/host/names/([^/]+)", Host),
    (r"/api/v1/host", HostList),
    (r"/api/v1/instance/alias/?(?P<db_name>[^\/]+)?", FunctionalAlias),
    (r"/api/v1/(?P<class>[^\/]+)/(?P<name>[^\/]+)/metadata", Metadata),
    (r"/api/v1/rundeck/resources.xml", RundeckResources),
    (r"/api/v1/rundeck/job/(?P<job>[^\/]+)/?(?P<node>[^\/]+)?", RundeckJobs),
    (r"/api/v1/(?P<class>[^\/]+)/(?P<entity>[^\/]+)/attribute/?(?P<attribute_name>[^\/]+)?", Attribute),
    (r"/api/v1/instance/(?P<db_name>[^\/]+)/job/?(?P<id>[^\/]+)?", Job),
    (r"/api/v1/job", Job_filter),

    # Deprecated, will be deleted in following versions
    (r"/api/v1/metadata/(?P<class>[^\/]+)/?(?P<name>[^\/]+)?", Metadata),  
    (r"/api/v1/fim/([^/]+)", Fim),
    ]

class Application():
    """
    This is the main entrypoint of the apiato-api where the main parameters are
    specified in order to start the server.  
    """

    def __handler_filter(self, handlers, config, optionalConfig):
        """
        Remove handlers which are not to be used when optional functions are
        not configured 
        """
        # Create a copy of the handler list, which we will modify
        res = list(handlers) 
        logging.debug('Active endpoints: %s' % res)
        for section in optionalConfig.keys():
            logging.info('Checking optional configuration section [%s]' % (section))
            try:
                config.items(section)
            except ConfigParser.NoSectionError:
                logging.info('Section not found. Removing related endpoints')
                # Remove handlers whose url matches the missing optional 
                # section names
                for handler in handlers:
                    url, handler_class = handler
                    if re.search(section, url):
                        logging.warning('Removing endpoint [%s]' % url)
                        res.remove(handler)
        logging.info('Active endpoints: %s' % res)
        return res

    def __init__(self):
        """
        Class constructor. Sets up logging, active handlers and application server
        """
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
        # Removing optional handlers from handler list 
        filtered_handlers = self.__handler_filter(handlers, config, optionalConfig)
        logging.info("Defining application (url, handler) pairs")
        application = tornado.web.Application(filtered_handlers, 
                            debug = config.getboolean('tornado', 'debug'))
        
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

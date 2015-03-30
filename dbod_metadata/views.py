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

from flask import Flask
from dbod_metadata.dbops import entity_metadata, host_metadata

import logging

APP = Flask(__name__)
FH = logging.FileHandler('app.log')
APP.logger.addHandler(FH)
APP.logger.setLevel(logging.INFO)

@APP.route("/", methods=['GET'])
def doc():
    """Generates api endpoint documentation"""
    APP.logger.info('GET /: Displaying API endpoints')
    return """Please use :
        http://hostname:port/api/v1/entity/<entity_name>\n
        http://hostname:port/api/v1/host/<hostname>\n"""

@APP.route("/api/v1/entity/<entity>", methods=['GET'])
def get_entity(entity):
    """Returns metadata for a certain entity"""
    APP.logger.info('GET /api/v1/entity/<%s>' % (entity))
    return entity_metadata(entity)


@APP.route("/api/v1/host/<hostname>", methods=['GET'])
def get_host(hostname):
    """Returns an object containing the metadata for all the entities
        on a certain host"""
    APP.logger.info('GET /api/v1/host/<%s>' % (hostname))
    return host_metadata(hostname)

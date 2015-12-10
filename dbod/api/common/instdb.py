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

import cx_Oracle as cx
import logging
from dbod.config import CONFIG

_dsnoracle = cx.makedsn(CONFIG.get('inst_host'), 
                        CONFIG.get('inst_port'), 
                        service_name = CONFIG.get('inst_servname'))
_ORAPOOL = cx.SessionPool(CONFIG.get('inst_user'), 
                        CONFIG.get('inst_pass'), 
                        dsn=_dsnoracle, min=1, max=5, increment=1)

def get_connection():
    """Gets and returns a connection from the pool"""
    try:
        return _ORAPOOL.acquire()
    except cx.DatabaseError as dberr:
        logging.error("Instance Database Error: %s", dberr)

def end_connection(con):
    """Releases a connection back to the pool"""
    _ORAPOOL.release(con)

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

_dsnfim = cx.makedsn(CONFIG.get('fim_host'), CONFIG.get('fim_port'), service_name = CONFIG.get('fim_servname'))
_FIMPOOL = cx.SessionPool(CONFIG.get('fim_user'), CONFIG.get('fim_pass'), dsn=_dsnfim, min=1, max=5, increment=1)

# Get a connection from the pool
def get_fim_connection():
    try:
        return _FIMPOOL.acquire()
    except cx.DatabaseError as dberr:
        logging.error("Oracle Error: %s", dberr)

# Return a connection to the pool
def end_fim_connection(con):
    _FIMPOOL.release(con)

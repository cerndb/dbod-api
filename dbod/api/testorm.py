#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2015, CERN
# This software is distributed under the terms of the GNU General Public
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as Intergovernmental Organization
# or submit itself to any jurisdiction.

"""
This file contains all database related code
"""

import sys, traceback, json
import logging

from dbod.api.instanceClass import Instance
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_CONNECTION_STRING = 'oracle://'

engine = create_engine(DATABASE_CONNECTION_STRING, echo=True)
Session = sessionmaker(bind=engine)

#STATUS CODES
NOT_FOUND = 404

def test_data(entity):

    logging.info("test_data %s", entity)
    session = Session()

    for db_name, username, db_type in session.query(Instance.db_name, Instance.username, Instance.db_type): 
        print db_name, username, db_type
    
    return None


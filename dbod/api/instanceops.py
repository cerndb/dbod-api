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

from psycopg2 import connect, DatabaseError, pool, errorcodes
import sys, traceback, logging

from dbod.api.dbops import *

def get_instance(dbname):
    """Returns a JSON object containing all the data for a dbname"""
    try:
        dbname = str(dbname)
        with POOL.getconn() as conn:
            with conn.cursor() as curs:
                curs.execute("""select * from instance where db_name = %s""",
                        (dbname, ))
                res = curs.fetchone()
                return res if res else None
    except DatabaseError as dberr:
        logging.error("PG Error: %s", dberr.pgerror)
        logging.error("PG Error lookup: %s", errorcodes.lookup(dberr.pgcode))
        return None
    finally:
        POOL.putconn(conn)

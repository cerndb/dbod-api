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
from dbod.api.utils import *
from dbod.api.common.instdb import *

def get_instances_by_dbname(dbname):
    """Returns a JSON object containing all the data for a dbname"""
    try:
        dbname = str(dbname)
        with POOL.getconn() as conn:
            with conn.cursor() as curs:
                curs.execute("""select * from instance where db_name = %s""",
                        (dbname, ))
                rows = curs.fetchall()
                cols = [i[0] for i in curs.description]
                if rows:
                    return create_json_from_result(rows, cols)
                return None
    except DatabaseError as dberr:
        logging.error("PG Error: %s", dberr.pgerror)
        logging.error("PG Error lookup: %s", errorcodes.lookup(dberr.pgcode))
        return None
    finally:
        POOL.putconn(conn)
        
def get_instances_by_host(host):
    """Returns a JSON object containing all the data for a host"""
    try:
        host = str(host)
        with POOL.getconn() as conn:
            with conn.cursor() as curs:
                curs.execute("""select * from instance where host = %s""",
                        (host, ))
                rows = curs.fetchall()
                cols = [i[0] for i in curs.description]
                if rows:
                    return create_json_from_result(rows, cols)
                return None
    except DatabaseError as dberr:
        logging.error("PG Error: %s", dberr.pgerror)
        logging.error("PG Error lookup: %s", errorcodes.lookup(dberr.pgcode))
        return None
    finally:
        POOL.putconn(conn)
        
def get_instances_by_status(status):
    """Returns a JSON object containing all the data for instances with a status"""
    try:
        status = str(status)
        conn = get_inst_connection()
        curs = conn.cursor()
        curs.execute("""SELECT username, db_name, e_group, category, creation_date, expiry_date, db_type, db_size, no_connections, project, description, version, state, status, master, slave, host 
                        FROM dod_instances WHERE status = :status
                        ORDER BY db_name""", {"status": status})
        rows = curs.fetchall()
        cols = [i[0] for i in curs.description]
        if rows:
            return create_json_from_result(rows, cols)
        return None
    except DatabaseError as dberr:
        logging.error("PG Error: %s", dberr.pgerror)
        logging.error("PG Error lookup: %s", errorcodes.lookup(dberr.pgcode))
        return None
    finally:
        end_inst_connection(conn)
        
def get_instances_by_username(username):
    """Returns a JSON object containing all the instances for the user"""
    try:
        username = str(username)
        with POOL.getconn() as conn:
            with conn.cursor() as curs:
                curs.execute("""select * from instance where username = %s""",
                        (username, ))
                rows = curs.fetchall()
                cols = [i[0] for i in curs.description]
                if rows:
                    return create_json_from_result(rows, cols)
                return None
    except DatabaseError as dberr:
        logging.error("PG Error: %s", dberr.pgerror)
        logging.error("PG Error lookup: %s", errorcodes.lookup(dberr.pgcode))
        return None
    finally:
        POOL.putconn(conn)

def get_all_instances():
    """Returns a JSON object containing all the instances"""
    try:
        with POOL.getconn() as conn:
            with conn.cursor() as curs:
                curs.execute("""SELECT username, db_name, e_group, category, creation_date, expiry_date, db_type, db_size, no_connections, project, description, version, state, status, master, slave, host 
                                FROM instance WHERE status = '1'""")
                rows = curs.fetchall()
                cols = [i[0] for i in curs.description]
                if rows:
                    return create_json_from_result(rows, cols)
                return None
    except DatabaseError as dberr:
        logging.error("PG Error: %s", dberr.pgerror)
        logging.error("PG Error lookup: %s", errorcodes.lookup(dberr.pgcode))
        return None
    finally:
        POOL.putconn(conn)
    

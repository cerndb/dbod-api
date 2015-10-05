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
import json, datetime

from dbod.config import CONFIG

# Define the default handler for date objects
json.JSONEncoder.default = lambda self,obj: (obj.isoformat() if isinstance(obj, datetime.date) else None)

try:
    POOL = pool.ThreadedConnectionPool(
            5,  # Min. # of connections
            20, # Max. # of connections
            database = CONFIG.get('db_name'),
            user = CONFIG.get('db_user'),
            host = CONFIG.get('db_host'),
            port = CONFIG.get('db_port'),
            password = CONFIG.get('db_pass'))
except DatabaseError as dberr:
    logging.error("PG Error: %s", errorcodes.lookup(dberr.pgcode[:2]))
    logging.error("PG Error: %s", errorcodes.lookup(dberr.pgcode))

def create_resource(username, db_name, e_group, category, expiry_date, db_type, db_size, no_connections, project, description):
    """Creates an entry in the resources table"""
    try:
        with POOL.getconn() as conn:
            with conn.cursor() as curs:
                logging.debug("Creating resource entry for %s", db_name)
                curs.execute("""insert into dod_instance_request(username, db_name, e_group, category, creation_date, expiry_date, db_type, db_size, no_connections, project, description) 
                                values(%s, %s, %s, %s, now(), NULL, %s, %s, %s, %s, %s)""",
                        (username, db_name, e_group, category, db_type, db_size, no_connections, project, description))
                logging.debug('DB query: %s', curs.query)
                conn.commit()
                return curs.rowcount == 1
    except DatabaseError as dberr:
        logging.error("PG Error: %s", dberr.pgerror)
        logging.error("PG Error lookup: %s", errorcodes.lookup(dberr.pgcode))
        return None
    finally:
        POOL.putconn(conn)
        
def update_resource(entity, metadata):
    """Updates the JSON object containing all the metadata for an entity"""
    try:
        with POOL.getconn() as conn:
            with conn.cursor() as curs:
                logging.debug("Updating metadata entry for %s", entity)
                logging.debug("Metadata: %s", metadata)
                curs.execute("""update metadata set data =%s where db_name = %s""",
                        (metadata, entity,))
                logging.debug('DB query: %s', curs.query)
                conn.commit()
                return curs.rowcount == 1
    except DatabaseError as dberr:
        logging.error("PG Error: %s", dberr.pgerror)
        logging.error("PG Error lookup: %s", errorcodes.lookup(dberr.pgcode))
        return None
    finally:
        POOL.putconn(conn)

def get_resource(resource):
    """Returns an entry in the resources table"""
    try:
        resource = str(resource)
        with POOL.getconn() as conn:
            with conn.cursor() as curs:
                curs.execute("""select * from dod_instance_request where db_name = %s""",
                        (resource, ))
                res = curs.fetchone()
                return res if res else None
    except DatabaseError as dberr:
        logging.error("PG Error: %s", dberr.pgerror)
        logging.error("PG Error lookup: %s", errorcodes.lookup(dberr.pgcode))
        return None
    finally:
        POOL.putconn(conn)
        
def delete_resource(resource):
    """Deletes an entry in the resources table"""
    try:
        with POOL.getconn() as conn:
            with conn.cursor() as curs:
                curs.execute("""delete from dod_instance_request where db_name = %s""", (resource, ))
                logging.debug('DB query: %s', curs.query)
                conn.commit()
                return curs.rowcount == 1
    except DatabaseError as dberr:
        logging.error("PG Error: %s", dberr.pgerror)
        logging.error("PG Error lookup: %s", errorcodes.lookup(dberr.pgcode))
        return None
    finally:
        POOL.putconn(conn)

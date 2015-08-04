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

from dbod.config import CONFIG

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

def get_metadata(entity):
    """Returns a JSON object containing all the metadata for a certain entity"""
    try:
        entity = str(entity)
        with POOL.getconn() as conn:
            with conn.cursor() as curs:
                curs.execute("""select data from metadata where db_name = %s""",
                        (entity, ))
                res = curs.fetchone()
                return res[0] if res else None
    except DatabaseError as dberr:
        logging.error("PG Error: %s", dberr.pgerror)
        logging.error("PG Error lookup: %s", errorcodes.lookup(dberr.pgcode))
        return None
    finally:
        POOL.putconn(conn)


def insert_metadata(entity, metadata):
    """Creates an entry in the metadata table"""
    try:
        with POOL.getconn() as conn:
            with conn.cursor() as curs:
                logging.debug("Creating metadata entry for %s", entity)
                logging.debug("Metadata: %s", metadata)
                curs.execute("""insert into metadata(db_name, data) values(%s, %s)""",
                        (entity, metadata, ))
                logging.debug('DB query: %s', curs.query)
                conn.commit()
                return curs.rowcount == 1
    except DatabaseError as dberr:
        logging.error("PG Error: %s", dberr.pgerror)
        logging.error("PG Error lookup: %s", errorcodes.lookup(dberr.pgcode))
        return None
    finally:
        POOL.putconn(conn)

def update_metadata(entity, metadata):
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

def delete_metadata(entity):
    """Deletes the metadata entry for an entity"""
    try:
        with POOL.getconn() as conn:
            with conn.cursor() as curs:
                curs.execute("""delete from metadata where db_name = %s""",
                        (entity, ))
                logging.debug('DB query: %s', curs.query)
                conn.commit()
                return curs.rowcount == 1
    except DatabaseError as dberr:
        logging.error("PG Error: %s", dberr.pgerror)
        logging.error("PG Error lookup: %s", errorcodes.lookup(dberr.pgcode))
        return None
    finally:
        POOL.putconn(conn)

def host_metadata(host):
    """Returns a JSON object containing the metadata for all the entities
        residing on a host"""
    try:
        with POOL.getconn() as conn:
            with conn.cursor() as curs:
                curs.execute("""select db_name, data
                from (
                    select db_name, json_array_elements(data->'hosts') host, data
                        from metadata)
                    as foo
                    where trim(foo.host::text, '"') = %s""", (host, ))
                res = curs.fetchall() # Either a list of tuples or empty list
                return res if res else None
    except DatabaseError as dberr:
        logging.error("PG Error: %s", errorcodes.lookup(dberr.pgcode[:2]))
        logging.error("PG Error: %s", errorcodes.lookup(dberr.pgcode))
        return None
    finally:
        POOL.putconn(conn)

# Functional aliases related methods
#   The assumption for the first implementation is that the database
#   table contains empty entries for pre-created dnsnames that are
#   considered valid

def next_dnsname():
    """Returns the next dnsname which can be used for a newly created
        instance, if any."""
    try:
        with POOL.getconn() as conn:
            with conn.cursor() as curs:
                curs.execute("""select dns_name
                from functional_aliases
                where db_name is NULL order by dns_name limit 1""")
                return curs.fetchone() # First unused dnsname or None
    except DatabaseError as dberr:
        logging.error("PG Error: %s", errorcodes.lookup(dberr.pgcode[:2]))
        logging.error("PG Error: %s", errorcodes.lookup(dberr.pgcode))
        return None
    finally:
        POOL.putconn(conn)

def update_functional_alias(dnsname, db_name, alias):
    """Updates a dnsname record with its db_name and alias"""
    try:
        with POOL.getconn() as conn:
            with conn.cursor() as curs:
                logging.debug("Updating functional alias record (%s, %s, %s)",
                    dnsname, db_name, alias)
                curs.execute("""update functional_aliases
                set db_name = %s, alias = %s where dns_name = %s""",
                    (db_name, alias, dnsname,))
                conn.commit()
                # Return True if the record was updated succesfully
                return curs.rowcount == 1
    except DatabaseError as dberr:
        logging.error("PG Error: %s", errorcodes.lookup(dberr.pgcode[:2]))
        logging.error("PG Error: %s", errorcodes.lookup(dberr.pgcode))
        return None
    finally:
        POOL.putconn(conn)

def get_functional_alias(db_name):
    """Returns the funcional alias and dnsname for a certain database"""
    try:
        with POOL.getconn() as conn:
            with conn.cursor() as curs:
                curs.execute("""select dns_name, alias
                from functional_aliases
                where db_name = %s""", (db_name,))
                return curs.fetchone()
    except DatabaseError as dberr:
        logging.error("PG Error: %s", errorcodes.lookup(dberr.pgcode[:2]))
        logging.error("PG Error: %s", errorcodes.lookup(dberr.pgcode))
        return None
    finally:
        POOL.putconn(conn)

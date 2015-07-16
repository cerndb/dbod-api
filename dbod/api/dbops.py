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
import ConfigParser
import sys, traceback, json, logging

try:
    # Loads configuration
    config = ConfigParser.ConfigParser()
    config.read('/etc/dbod/api.cfg')
    dbuser = config.get('database', 'user')
    dbhost = config.get('database', 'host')
    db = config.get('database', 'database')
    port = config.get('database', 'port')
    password = config.get('database', 'password')
except IOError as e:
    traceback.print_exc(file=sys.stdout)
    sys.exit(e.code)
except ConfigParser.NoOptionError:
    traceback.print_exc(file=sys.stdout)
    sys.exit(1)

#STATUS CODES
NOT_FOUND = 404

POOL = pool.ThreadedConnectionPool(5, 20,
        database=db, user=dbuser, host=dbhost, port=port, password=password)

def entity_metadata(entity):
    """Returns a JSON object containing all the metadata for a certain entity"""
    try:
        with POOL.getconn() as conn:
            with conn.cursor() as curs:
                curs.execute("""select data from metadata where name = %s""",
                        (entity, ))
                res = curs.fetchone()
                if res:
                    return res[0]
                else:
                    return None
    except DatabaseError as dberr:
        logging.error(errorcodes.lookup(dberr.pgcode[:2]))
        logging.error(errorcodes.lookup(dberr.pgcode))
        return None

def host_metadata(host):
    """Returns a JSON object containing the metadata for all the entities
        residing on a host"""
    try:
        with POOL.getconn() as conn:
            with conn.cursor() as curs:
                curs.execute("""select name, data
                from (
                    select name, json_array_elements(data->'hosts') host, data
                        from metadata)
                    as foo
                    where trim(foo.host::text, '"') = %s""", (host, ))
                res = curs.fetchall()
                if res:
                    return json.dumps(res)
                else:
                    return None
    except DatabaseError as dberr:
        logging.error(errorcodes.lookup(dberr.pgcode[:2]))
        logging.error(errorcodes.lookup(dberr.pgcode))
        return None

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
                where db_name is NULL order by dns_name desc limit 1""")
                res = curs.fetchone()
                if res:
                    return json.dumps(res)
                else:
                    return None
    except DatabaseError as dberr:
        logging.error(errorcodes.lookup(dberr.pgcode[:2]))
        logging.error(errorcodes.lookup(dberr.pgcode))
        return None

def update_functional_alias(dnsname, db_name, alias):
    """Updates a dnsname record with its db_name and alias"""
    try:
        with POOL.getconn() as conn:
            with conn.cursor() as curs:
                curs.execute("""begin""")
                curs.execute("""update functional_aliases
                set db_name = %s, alias = %s where dnsname = %s""", 
                    (db_name, alias, dnsname,))
                curs.execute("""commit""")
                res = curs.statusmessage
                if res:
                    return json.dumps(res)
                else:
                    return None
    except DatabaseError as dberr:
        logging.error(errorcodes.lookup(dberr.pgcode[:2]))
        logging.error(errorcodes.lookup(dberr.pgcode))
        return None

def get_functional_alias(db_name):
    """Returns the funcional alias and dnsname for a certain database"""
    try:
        with POOL.getconn() as conn:
            with conn.cursor() as curs:
                curs.execute("""select dns_name, alias
                from functional_aliases
                where db_name = %s""", (db_name,))
                res = curs.fetchone()
                if res:
                    return json.dumps(res)
                else:
                    return None
    except DatabaseError as dberr:
        logging.error(errorcodes.lookup(dberr.pgcode[:2]))
        logging.error(errorcodes.lookup(dberr.pgcode))
        return None

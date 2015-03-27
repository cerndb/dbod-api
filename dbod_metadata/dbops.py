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

from flask import abort, jsonify
from psycopg2 import connect, DatabaseError
import ConfigParser
import sys, traceback

# Loads configuration
config = ConfigParser.ConfigParser()
with open('/etc/dbod/metadata.cfg') as fp:
    try:
        config.read(fp)
    except IOError as exc:
        traceback.print_exc(file=sys.stdout)
        sys.exit(exc.errno)

dbuser = config.get('database', 'user')
dbhost = config.get('database', 'host')
db = config.get('database', 'dbname')
port = config.get('database', 'port')
password = config.get('database', 'password')

#STATUS CODES
NOT_FOUND = 404

def entity_metadata(entity):
    """Returns a JSON object containing all the metadata for a certain entity"""
    try:
        conn = connect(database=db, user=dbuser, host=dbhost, port=port)
        cur = conn.cursor()
        cur.execute("""select data from metadata where name = %s""", (entity, ))
        res = cur.fetchone()
        cur.close()
        if res:
            return jsonify(res[0])
        else:
            abort(NOT_FOUND)
    except DatabaseError as dberr:
        # Problem connecting to database, return result from cache?
        return jsonify(dberr)

def host_metadata(host):
    """Returns a JSON object containing the metadata for all the entities
        residing on a host"""
    try:
        conn = connect(database=db, user=dbuser, host=dbhost, port=port)
        cur = conn.cursor()
        cur.execute("""select name, data from entities where name in
        (select name
        from (
            select name, json_array_elements(data->'hosts') host
                from metadata)
            as foo
            where trim(foo.host::text, '"') = %s)
        as bar""", (host, ))
        res = cur.fetchall()
        cur.close()
        if res:
            return jsonify(res)
        else:
            abort(NOT_FOUND)
    except DatabaseError as dberr:
        # Problem connecting to database, return result from cache?
        return jsonify(dberr)

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
import dbod.api.common.instdb as instdb
import dbod.api.common.fimdb as fimdb

def get_instances_by_dbname(dbname):
    """Returns a JSON object containing all the data for a dbname"""
    connF = None
    connI = None
    try:
        dbname = str(dbname)
        connI = instdb.get_connection()
        cursI = connI.cursor()
        cursI.execute("""SELECT username, db_name, e_group, category, creation_date, expiry_date, db_type, db_size, no_connections, project, description, version, state, status, master, slave, host 
                        FROM dod_instances WHERE db_name = :db_name AND status = 1
                        ORDER BY db_name""", {"db_name": dbname})
        rowsI = cursI.fetchall()
        colsI = [i[0] for i in cursI.description]
        if rowsI:
            res = create_json_from_result(rowsI, colsI)
        
            # Load the user's data from FIM and join it to the result in Json
            connF = fimdb.get_connection()
            cursF = connF.cursor()
            cursF.execute("""SELECT instance_name, owner_first_name, owner_last_name, owner_login, owner_mail, owner_phone1, owner_phone2, owner_portable_phone, owner_department, owner_group, owner_section
                            FROM fim_ora_ma.db_on_demand WHERE instance_name = :db_name""", {"db_name": dbname})
            rowsF = cursF.fetchall()
            colsF = [i[0] for i in cursF.description]
            if rowsF:
                res["USER"] = create_json_from_result(rowsF, colsF)
            return res
        return None
    except DatabaseError as dberr:
        logging.error("PG Error: %s", dberr.pgerror)
        logging.error("PG Error lookup: %s", errorcodes.lookup(dberr.pgcode))
        return None
    finally:
        if connF != None:
            fimdb.end_connection(connF)
        if connI != None:
            instdb.end_connection(connI)
        
def get_instances_by_host(host):
    """Returns a JSON object containing all the data for a host"""
    try:
        host = str(host)
        conn = instdb.get_connection()
        curs = conn.cursor()
        curs.execute("""SELECT username, db_name, e_group, category, creation_date, expiry_date, db_type, db_size, no_connections, project, description, version, state, status, master, slave, host 
                        FROM dod_instances WHERE host = :host AND status = 1
                        ORDER BY db_name""", {"host": host})
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
        instdb.end_connection(conn)
        
def get_instances_by_status(status):
    """Returns a JSON object containing all the data for instances with a status"""
    try:
        status = str(status)
        conn = instdb.get_connection()
        curs = conn.cursor()
        curs.execute("""SELECT username, db_name, e_group, category, creation_date, expiry_date, db_type, db_size, no_connections, project, description, version, state, status, master, slave, host 
                        FROM dod_instances WHERE status = :status
                        ORDER BY db_name""", {"status": status})
        rows = curs.fetchall()
        cols = [i[0] for i in curs.description]
        if rows:
            res = create_json_from_result(rows, cols)
            
            # Load the user's data from FIM and join it to the result in Json
            connF = fimdb.get_connection()
            cursF = connF.cursor()
            cursF.execute("""SELECT instance_name, owner_first_name, owner_last_name, owner_login, owner_mail, owner_phone1, owner_phone2, owner_portable_phone, owner_department, owner_group, owner_section
                            FROM fim_ora_ma.db_on_demand""")
            rowsF = cursF.fetchall()
            colsF = [i[0] for i in cursF.description]
            if rowsF:
                usersJson = create_dict_from_result(rowsF, colsF, "INSTANCE_NAME")
                for instance in res:
                    if instance["DB_NAME"] in usersJson:
                        instance["USER"] = usersJson[instance["DB_NAME"]]
            return res
        return None
    except DatabaseError as dberr:
        logging.error("PG Error: %s", dberr.pgerror)
        logging.error("PG Error lookup: %s", errorcodes.lookup(dberr.pgcode))
        return None
    finally:
        instdb.end_connection(conn)
        
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

   

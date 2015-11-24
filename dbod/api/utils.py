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

import json
import sys, traceback, logging
from common.instdb import *
from common.fimdb import *

def create_json_from_result(rows, cols):
    res = []
    for row in rows:
        object = {}
        for col, val in zip(cols, row):
            object[col] = val
        res.append(object)
    if len(rows) == 1:
        return res[0]
    return res
    
def test():
    con = get_inst_connection()

    cur = con.cursor()
    cur.execute('select * from dod_instances')
    resultset = cur.fetchall()
    for result in resultset:
        for item in result:
            print (str(item)),
        print ""
    cur.close()
    
    end_inst_connection(con)
    
#test()

def test2():
    con = get_fim_connection()
    
    cur = con.cursor()
    cur.execute('select * from fim_ora_ma.db_on_demand')
    resultset = cur.fetchall()
    for result in resultset:
        for item in result:
            print (str(item)),
        print ""
    cur.close()
    
    end_fim_connection(con)
    
#test2()
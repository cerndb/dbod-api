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

def create_json_from_result(rows, cols):
    """Creates a JSON object from the result (rows and columns) of a database"""
    res = []
    for row in rows:
        object = {}
        for col, val in zip(cols, row):
            object[col] = val
        res.append(object)
    if len(rows) == 1:
        return res[0]
    return res
    
def create_dict_from_result(rows, cols, map):
    """Creates a JSON dictionary from the result (rows and columns) of a 
    database, mapped by the string in the map parameter"""
    res = {}
    for row in rows:
        object = {}
        for col, val in zip(cols, row):
            object[col] = val
        res[object[map]] = object
    return res

#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2015, CERN
# This software is distributed under the terms of the GNU General Public
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as Intergovernmental Organization
# or submit itself to any jurisdiction.

import nose
from types import *
import json
import logging
import sys
import requests
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

#from dbod.api.dbops import *

def empty():
    assert(True)
    
def test_connection():
    response = requests.get("http://localhost:3000")
    assert(response.status_code == 200)

if __name__ == "__main__":
    pass

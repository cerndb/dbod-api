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
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

from dbod.api.dbops import *

def test_entity_metadata():
    metadata =  entity_metadata('pinocho')
    logging.info("Entity metadata for 'pinocho':\n%s", metadata)
    if metadata:
        assert type(metadata) is DictType

def test_host_metadata():
    metadata = host_metadata('db-50019')
    logging.info(metadata)
    if metadata:
        assert type(metadata) is ListType

def test_get_functional_alias():
    falias = get_functional_alias('pinocho')
    logging.info("Functional alias for 'pinocho' %s", falias)
    if falias:
        assert type(falias) is StringType

def test_next_dnsname():
    ndnsname = next_dnsname()
    logging.info("Next free dnsname: %s", ndnsname)
    assert type(ndnsname) is StringType

def test_update_functional_alias():
    dnsname = next_dnsname()
    res = get_functional_alias('test')
    logging.info("Defined functional alias for 'test': %s", res)
    assert update_functional_alias(dnsname, 'test', 'dbod-test') == True
    res = get_functional_alias('test')
    logging.info("Defined functional alias for 'test': %s", res)
    assert update_functional_alias(dnsname, None, None) == True
    res = get_functional_alias('test')
    logging.info("Defined functional alias for 'test': %s", res)

if __name__ == "__main__":
    pass

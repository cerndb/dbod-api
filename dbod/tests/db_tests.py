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
from dbod.api.dbops import *

def test_entity_metadata():
    metadata =  entity_metadata('pinocho')
    assert type(metadata) is DictType

def test_host_metadata():
    metadata = host_metadata('db-50019')
    print type(metadata)
    assert type(metadata) is StringType

def test_get_functional_alias():
    falias = get_functional_alias('pinocho')
    print falias, type(falias)
    assert type(falias) is StringType

def test_next_dnsname():
    ndnsname = next_dnsname()
    print ndnsname, type(ndnsname)
    assert type(ndnsname) is StringType

def test_update_functional_alias():
    dnsname = next_dnsname()
    res = update_functional_alias(dnsname, 'test', 'dbod-test')
    print res
    print get_functional_alias('test')
    #update_functional_alias(dnsname, None, None)
    print get_functional_alias('test')



if __name__ == "__main__":
    pass

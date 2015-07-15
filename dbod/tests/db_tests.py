#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2015, CERN
# This software is distributed under the terms of the GNU General Public
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as Intergovernmental Organization
# or submit itself to any jurisdiction.

import nose
import dbod.api.dbops


def test_entity_metadata():
    pass

def test_host_metadata():
    pass

def test_last_dnsname():
    print dbod.api.dbops.last_dnsname()
    pass

def test_next_dnsname():
    print dbod.api.dbops.next_dnsname()
    pass

def test_add_functional_alias():
    pass

def test_update_functional_alias():
    pass


if __name__ == "__main__":
    pass

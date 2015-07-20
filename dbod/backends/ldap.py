#!/usr/bin/env python
# Copyright (C) 2015, CERN
# This software is distributed under the terms of the GNU General Public
# Licence version 3 (GPL Version 3), copied verbatim in the file "LICENSE".
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as Intergovernmental Organization
# or submit itself to any jurisdiction.

import ldap

def get_ldap_conn(url, protocol, dsn, userdn, password):
    pass

def get_entity(conn, entity_base, scope):
    pass

def load_LDIF(template):
    pass

def add_attributes(conn, entity_base, attributes):
    pass

def modify_attributes(conn, entity_base, attributes):
    pass


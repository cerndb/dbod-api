#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2015, CERN
# This software is distributed under the terms of the GNU General Public
# Licence version 3 (GPL Version 3), copied verbatim in the file "LICENSE".
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as Intergovernmental Organization
# or submit itself to any jurisdiction.

import ConfigParser
import sys, traceback

CONFIG = {}

try:
    # Load configuration from file
    config = ConfigParser.ConfigParser()
    config.read('/etc/dbod/api.cfg')
    CONFIG['db_user'] = config.get('database', 'user')
    CONFIG['db_host'] = config.get('database', 'host')
    CONFIG['db_name'] = config.get('database', 'database')
    CONFIG['db_port'] = config.get('database', 'port')
    CONFIG['db_pass'] = config.get('database', 'password')
    CONFIG['hostcert'] = config.get('ssl', 'hostcert')
    CONFIG['hostkey'] = config.get('ssl', 'hostkey')
    CONFIG['log_file'] = config.get('logging', 'path')
    CONFIG['app_port'] = config.get('server', 'port')
    CONFIG['api_user'] = config.get('api', 'user')
    CONFIG['api_pass'] = config.get('api', 'password')
    CONFIG['inst_user'] = config.get('instdatabase', 'user')
    CONFIG['inst_host'] = config.get('instdatabase', 'host')
    #CONFIG['inst_name'] = config.get('instdatabase', 'database')
    CONFIG['inst_port'] = config.get('instdatabase', 'port')
    CONFIG['inst_pass'] = config.get('instdatabase', 'password')
    CONFIG['inst_servname'] = config.get('instdatabase', 'serv_name')
    CONFIG['fim_user'] = config.get('fimdatabase', 'user')
    CONFIG['fim_host'] = config.get('fimdatabase', 'host')
    #CONFIG['fim_name'] = config.get('fimdatabase', 'database')
    CONFIG['fim_port'] = config.get('fimdatabase', 'port')
    CONFIG['fim_pass'] = config.get('fimdatabase', 'password')
    CONFIG['fim_servname'] = config.get('fimdatabase', 'serv_name')

except IOError as e:
    traceback.print_exc(file=sys.stdout)
    sys.exit(e.code)
except ConfigParser.NoOptionError:
    traceback.print_exc(file=sys.stdout)
    sys.exit(1)



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
    CONFIG['password'] = config.get('database', 'password')
    CONFIG['hostcert'] = config.get('ssl', 'hostcert')
    CONFIG['hostkey'] = config.get('ssl', 'hostkey')
    CONFIG['log_file'] = config.get('logging', 'path')
    CONFIG['app_port'] = config.get('server', 'port')

except IOError as e:
    traceback.print_exc(file=sys.stdout)
    sys.exit(e.code)
except ConfigParser.NoOptionError:
    traceback.print_exc(file=sys.stdout)
    sys.exit(1)



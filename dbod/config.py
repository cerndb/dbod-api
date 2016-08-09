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
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--config", default="/etc/dbod/api.cfg", help="specify the location of the config file")
args, unk = parser.parse_known_args()

config = None

try:
    # Load configuration from file
    config = ConfigParser.ConfigParser()
    config.read(args.config)
except IOError as e:
    traceback.print_exc(file=sys.stdout)
    sys.exit(e.code)
except ConfigParser.NoOptionError:
    traceback.print_exc(file=sys.stdout)
    sys.exit(1)



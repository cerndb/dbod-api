#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2015, CERN
# This software is distributed under the terms of the GNU General Public
# Licence version 3 (GPL Version 3), copied verbatim in the file "LICENSE".
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as Intergovernmental Organization
# or submit itself to any jurisdiction.

"""
Configuration module, which reads and parses the configuration file.
"""

import ConfigParser
import sys, traceback
import argparse

# Dictionary with the required present fields in the config file
requiredConfig = {
        'server' : [ 'port' ] ,
        'logging' : [ 'path', 'level', 'stderr', 'datefmt' ],
        'api' : [ 'user', 'pass' ], 
        'postgrest': [ 
            'rundeck_resources_url', 
            'host_aliases_url', 
            'metadata_url', 
            'instance_url', 
            'volume_url', 
            'attribute_url', 
            'functional_alias_url'
            ], 
        }

optionalConfig = {
                  'rundeck' : [ 
                      'timeout',
                      'api_run_job', 
                      'api_job_output', 
                      'api_authorization'
                      ], 
                  'rundeck-jobs' : [
                      'get-snapshots'
                      ]
                  }


def load( config_file = None ):
    """
    Reads configuration file
    """
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument(
                "-c", "--config", default="/etc/apiato/api.cfg", 
                help = "specify the location of the config file"
                )
        args, unk = parser.parse_known_args()

        # Load configuration from file
        config = ConfigParser.ConfigParser()
        config.add_section('tornado')
        config.set('tornado', 'debug', 'false')
        if config_file:
            number_read_files = config.read(config_file)
        else:
            number_read_files = config.read(args.config)

        # check the config file exist and can be read
        if len(number_read_files) != 1:
            print "Configuration file '{0}' cannot be read or does not exist. Stopping.".format(args.config)
            sys.exit(1)
        
        # Force load of all required fields to avoid errors in runtime
        for section, options in requiredConfig.items():
            for option in options:
                try:
                    config.get(section, option)
                except ConfigParser.NoSectionError:
                    print "Section '{0}' not present in config file. Stopping.".format(section)
                    sys.exit(2)
                except ConfigParser.NoOptionError:
                    print "Option '{0}' not present in section {1} in config file. Stopping.".format(option, section)
                    sys.exit(2)
        return config
        
    except IOError as e:
        traceback.print_exc(file=sys.stdout)
        sys.exit(e.code)

# Loads config
config = load()


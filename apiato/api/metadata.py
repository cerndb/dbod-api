#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2015, CERN
# This software is distributed under the terms of the GNU General Public
# Licence version 3 (GPL Version 3), copied verbatim in the file "LICENSE".
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as Intergovernmental Organization
# or submit itself to any jurisdiction.

"""
Metadata module, which includes all the classes related with metadata endpoints.
"""

import tornado.web
import logging
import requests
import json

from apiato.api.base import *
from apiato.config import config

class Metadata(tornado.web.RequestHandler):
    """
    This is the handler of **/metadata/<class>/<name>** endpoint.

    This endpoint takes 2 arguments:

    * *<class>* - "*host*" or "*instance*" 
    * *<name>* - the name of a *host* or of a *database* 

    Things that are given for the development of this endpoint:
    
    * We request indirectly a `Postgres <https://www.postgresql.org/>`_ database through `PostgREST <http://postgrest.com/>`_ which returns a response in JSON format
    * The database's table/view that is used for this endpoint is called *metadata* and provides information about the metadata of a database instance(s).
    * Here is an example of this table:

    +--+--------+---------+-------------+---------------------------------------+
    |id|username| db_name |    hosts    |               attributes              |
    +==+========+=========+=============+=======================================+
    |42|  apiato  |apiato-db42|{apiato-host42}|{"port": "5432", "shared_buffers": "1"}|
    +--+--------+---------+-------------+---------------------------------------+

    The request method implemented for this endpoint is just the :func:`get`.

    """
    def get(self, **args):
        """Returns the metadata of a host or an instance
        The *GET* method returns the instance(s)' metadata given the *host* or the *database name*. 
        (No any special headers for this request)

        :param class: "host" or "instance"
        :type class: str
        :param name: the host or database name which is given in the url
        :type name: str
        :rtype: json - the response of the request 

                * in case of "*host*" it returns all the instances' metadata that are hosted in the specified host
                * in casse of "*instance*" it returns the metadata of just the given database

        :raises: HTTPError - when the <class> argument is not valid ("host" or "instance") or the given host or database name does not exist or in case of an internal error

        """
        name = args.get('name')
        etype = args.get('class')
        if name:
            if etype == u'instance':
                composed_url = config.get('postgrest', 'metadata_url') + '?db_name=eq.' + name
            elif etype == u'host':
                composed_url = config.get('postgrest', 'metadata_url') + '?hosts=@>.{' + name + '}'
            else:
                logging.error("Unsupported endpoint")
                raise tornado.web.HTTPError(BAD_REQUEST)
            logging.info('Requesting ' + composed_url)
            response = requests.get(composed_url, verify=False)
            data = response.json()
            if response.ok and data:
                logging.debug("response: " + json.dumps(data))
                self.write({'response' : data})
                self.set_status(OK)
            elif response.ok:
                logging.warning("Instance metadata not found: " + name)
                raise tornado.web.HTTPError(NOT_FOUND)
            else:
                logging.error("Error fetching instance metadata: " + response.text)
                raise tornado.web.HTTPError(response.status_code)
        else:
            logging.error("Unsupported endpoint")
            raise tornado.web.HTTPError(BAD_REQUEST)

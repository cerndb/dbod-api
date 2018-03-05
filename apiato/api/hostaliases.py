#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2015, CERN
# This software is distributed under the terms of the GNU General Public
# Licence version 3 (GPL Version 3), copied verbatim in the file "LICENSE".
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as Intergovernmental Organization
# or submit itself to any jurisdiction.

#Host Aliases module

import tornado.web
import logging
import requests

from apiato.api.base import *
from apiato.config import config

class HostAliases(tornado.web.RequestHandler):
    """
    This the handler of **/host/aliases/<host>** endpoint.
    
    Things that are given for the development of this endpoint:

    * We request indirectly a `Postgres <https://www.postgresql.org/>`_ database through `PostgREST <http://postgrest.com/>`_ which returns a response in JSON format
    * The database's table/view that is used for this endpoint is called *host_aliases* and provides information for the instance aliases association with a host.
    * The columns of this table are like that:

    +----+-------------+----------------------------------------------------------+
    | id |    name     |                         aliases                          |
    +====+=============+==========================================================+
    | 41 | dbod-host42 | dbod-alias42-user1.cern.ch, dbod-alias42-user2.cern.ch   |
    +----+-------------+----------------------------------------------------------+

        * The *host* is the hostname of the machine that the database instances has been created
        * The *aliases* are the aliases of the databases that exist in this host/machine 

    The request method implemented for this endpoint is just the :func:`get`.

    """
    def get(self, host):

        """ 
        The *GET* method returns the list of ip-aliases registered in a host.
        (No any special headers for this request)

        :param host: the host name which is given in the url
        :type host: str
        :rtype: json -- the response of the request
        :raises: HTTPError - when the requested host or the requested url does not exist

        """

        composed_url = config.get('postgrest', 'host_aliases_url') + '?name=eq.' + host
        logging.info('Requesting ' + composed_url )
        response = requests.get(composed_url)
        data = response.json()
        if response.ok and data:
            logging.debug("response: " + response.text)
            self.write({'response' : data})
            self.set_status(OK)
        elif response.ok:
            logging.warning("Host aliases not found: " + host)
            raise tornado.web.HTTPError(NOT_FOUND)
        else: 
            logging.error("Error fetching aliases: " + response.text)
            raise tornado.web.HTTPError(NOT_FOUND)

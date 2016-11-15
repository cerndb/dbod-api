#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2015, CERN
# This software is distributed under the terms of the GNU General Public
# Licence version 3 (GPL Version 3), copied verbatim in the file "LICENSE".
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as Intergovernmental Organization
# or submit itself to any jurisdiction.

"""
cluster module, which includes all the classes related with cluster endpoints.
"""

import tornado.web
import logging
import requests
import json

from dbod.api.base import *
from dbod.config import config

class Cluster(tornado.web.RequestHandler):
    """
    This is the handler of **/cluster/<class>/<name>** endpoint.

    This endpoint takes 1 arguments:

    * *<name>* - the name of a *cluster*

    Things that are given for the development of this endpoint:

    * We request indirectly a `Postgres <https://www.postgresql.org/>`_ database through `PostgREST <http://postgrest.com/>`_ which returns a response in JSON format
    * The database's table/view that is used for this endpoint is called *cluster* and provides metadata about a cluster and its instances.
    * Here is an example of this table:

    --ToDO

    The request method implemented for this endpoint is just the :func:`get`.

    """
    def get(self, **args):
        """Returns the metadata of a host or an instance
        The *GET* method returns the instance(s)' metadata given the *host* or the *database name*.
        (No any special headers for this request)

        :param name: the database name which is given in the url
        :type name: str
        :rtype: json - the response of the request
        :raises: HTTPError - when the given cluster name does not exist or in case of an internal error

        """
        name = args.get('name')
        if name:
            composed_url = config.get('postgrest', 'metadata_url') + '?name=eq.' + name
            logging.info('Requesting ' + composed_url)
            response = requests.get(composed_url, verify=False)
            data = response.json()
            if response.ok and data:
                logging.debug("response: " + json.dumps(data))
                self.write({'response' : data})
            elif response.ok:
                logging.warning("Instance metadata not found: " + name)
                raise tornado.web.HTTPError(NOT_FOUND)
            else:
                logging.error("Error fetching instance metadata: " + response.text)
                raise tornado.web.HTTPError(response.status_code)
        else:
            logging.error("Unsupported endpoint")
            raise tornado.web.HTTPError(BAD_REQUEST)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2015, CERN
# This software is distributed under the terms of the GNU General Public
# Licence version 3 (GPL Version 3), copied verbatim in the file "LICENSE".
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as Intergovernmental Organization
# or submit itself to any jurisdiction.

"""
FIM module, which has the endpoint to read FIM's data
"""

import tornado.web
import logging
import requests
import json

from apiato.api.base import *
from apiato.config import config

class Fim(tornado.web.RequestHandler):
    """
    This is the handler of **/fim/<name>** endpoint.

    This endpoint takes 1 arguments:

    * *<name>* - the name of a *database* 

    Things that are given for the development of this endpoint:
    
    * We request indirectly a `Postgres <https://www.postgresql.org/>`_ database through `PostgREST <http://postgrest.com/>`_ which returns a response in JSON format
    * The database's table/view that is used for this endpoint is called *db_on_demand* and provides information about the metadata of a database instance(s).

    The request method implemented for this endpoint is just the :func:`get`.

    """
    def get(self, name):
        """Returns the FIM's data for an instance
        (No any special headers for this request)

        :param name: the database name which is given in the url
        :type name: str
        :rtype: json - the response of the request, which will include all the information for the given database

        :raises: HTTPError - whene th given database name does not exist or in case of an internal error

        """
        
        response = requests.get(config.get('postgrest', 'fim_url') + '?instance_name=eq.' + name, verify=False)
        if response.ok:
            data = response.json()
            if data:
                logging.debug("data: " + json.dumps(data))
                self.write({'data' : data})
                self.set_status(OK)
            else:
                logging.error("Instance not found in FIM: " + name)
                raise tornado.web.HTTPError(NOT_FOUND)
        else:
            logging.error("Error fetching instance information: " + response.text)
            raise tornado.web.HTTPError(response.status_code)


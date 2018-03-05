#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2015, CERN
# This software is distributed under the terms of the GNU General Public
# Licence version 3 (GPL Version 3), copied verbatim in the file "LICENSE".
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as Intergovernmental Organization
# or submit itself to any jurisdiction.


#Functional alias module

import logging
import json
import requests
import tornado.web
import tornado.escape
from apiato.api.base import *
from apiato.config import config

class Type(tornado.web.RequestHandler):
    """
    This is the handler of **/<class>/types** endpoint.

    Things that are given for the development of this endpoint:

    * We request indirectly a `Postgres <https://www.postgresql.org/>`_ database through `PostgREST <http://postgrest.com/>`_ which returns a response in JSON format
    * The database's table that is used for this endpoint is called *host* and provides information for the functional alias association with an instance.
    * The columns of this table are like that:

    +----+--------+-------------+
    | id |  type  | description |
    +====+========+=============+
    | 42 | mysql  | MySQL Type  |
    +----+--------+-------------+

        * The *id* field is the type id, referenced by other resources
        * The *type* in this example is the type of an instance
        * The *description* is an optional field to include a short description

    The request methods implemented for this endpoint are:

    * :func:`get`

    """

    instance_url = config.get('postgrest', 'instance_type_url')
    volume_url = config.get('postgrest', 'volume_type_url')
    cluster_url = config.get('postgrest', 'cluster_type_url')

    def get(self, **args):
        """
        The *GET* method returns the list of types of the selected resource class.
        (No any special headers for this request)

        :param class: the class of the resource (instance/cluster/volume)
        :type class: str
        :rtype: json -- the response of the request
        :raises: HTTPError - when the requested name does not exist or if there is an internal 
        error or if the response is empty
        """

        class_n = args.get('class')
        logging.info('Requested ' + str(class_n) + ' types.')
        
        if class_n == 'instance':
            url = self.instance_url
        elif class_n == 'volume':
            url = self.volume_url
        elif class_n == 'cluster':
            url = self.cluster_url
        else:
            logging.error("Trying to get types of unknown class: " + str(class_n))
            raise tornado.web.HTTPError(NOT_FOUND)

        if url:
            response = requests.get(url)
            data = response.json()
            if response.ok and data:
                logging.debug("response: " + json.dumps(data))
                self.write({'response' : data})
                self.set_status(OK)
            else:
                logging.error("Error fetching types for class '" + str(class_n) + "': " + response.text)
                raise tornado.web.HTTPError(response.status_code)
        else:
            logging.warning("Not url configured for: " + str(class_n))
            raise tornado.web.HTTPError(NOT_FOUND)

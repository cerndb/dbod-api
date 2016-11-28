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
from dbod.api.base import *
from dbod.config import config

class Host(tornado.web.RequestHandler):
   
    """
    This is the handler of **/host/names/<name>** endpoint.

    Things that are given for the development of this endpoint:

    * We request indirectly a `Postgres <https://www.postgresql.org/>`_ database through `PostgREST <http://postgrest.com/>`_ which returns a response in JSON format
    * The database's table that is used for this endpoint is called *host* and provides information for the functional alias association with an instance.
    * The columns of this table are like that:

    +----+-----------+--------+
    | id |  name     | memory |
    +====+===========+========+
    | 42 | dbod-db42 |  1024  |
    +----+-----------+--------+

        * The *name* in this example is the hostname of a node
        * The *memory* is the memory of the node expressed as integer in megabytes

    The request methods implemented for this endpoint are:

    * :func:`get`
    * :func:`post`
    * :func:`put`
    * :func:`delete` 

    .. note::

      You need to provide a <*username*> and a <*password*> to use
      :func:`post`, :func:`put`, and :func:`delete` methods or to 
      provide manually the *Authorization* header.

    """

    url = config.get('postgrest', 'host_url')

    def get(self, name):

        """
        The *GET* method returns the host's memory according to the example given above.
        (No any special headers for this request)

        :param name: the hostname which is given in the url
        :type name: str
        :rtype: json -- the response of the request
        :raises: HTTPError - when the requested name does not exist or if there is an internal 
        error or if the response is empty
        """

        response = requests.get(config.get('postgrest', 'host_url') + "?name=eq." + name)
        if response.ok:
            data = response.json()
            if data:
                self.write({'response' : data})
                self.set_status(OK)
            else:
                logging.error("host metadata not found: " + name)
                raise tornado.web.HTTPError(NOT_FOUND)
        else:
            logging.error("Host metadata not found: " + name)
            raise tornado.web.HTTPError(NOT_FOUND)

    @http_basic_auth
    def post(self, id):

        """
        The *POST* method inserts a new *name* and its *memory* size according to the example above. 
        You don't have to specify anything about the *id* since this field should be specified as *serial*.

        .. note::

            This method is not successful:

            * if the *name* already exists
            * if the format of the *request body* is not right
            * if headers have to be specified
            * if the client does not have the right authorization header 
           
        :param id: the new id which is given in the url
        :type id: str
        :raises: HTTPError - when the *url* or the *request body* format or the *headers* are not right orthere is an internal error
        :request body: memory=<memory_int_MB> - the memory (integer in MB) to be inserted for the given *name* which is given in the *body* of the request
        """

        logging.debug(self.request.body)

        try:
            host = {'in_json': json.loads(self.request.body)}

            # Insert the instance in database using PostREST
            response = requests.post(config.get('postgrest', 'insert_host_url'), json=host, headers={'Prefer': 'return=representation'})
            if response.ok:
                logging.debug(response.text)
                self.set_status(CREATED)
            else:
                logging.error("Error inserting the host: " + response.text)
                raise tornado.web.HTTPError(response.status_code)
        except:
            logging.error("Argument not recognized or not defined.")
            logging.error("Try adding header 'Content-Type:application/x-www-form-urlencoded'")
            raise tornado.web.HTTPError(BAD_REQUEST)

	
    @http_basic_auth   
    def put(self, id):
        """
        The *PUT* method updates the *host*.


        .. note::

            In order to be able to use *PUT* method possibly you have to specify this header:
            'Content-Type: application/x-www-form-urlencoded'.

            This method is not successful:

            * if the *host* does not exist
            * if the format of the *request body* is not right
            * if headers have to be specified
            * if the client does not have the right authorization header 
           
        :param name: the new name which is given in the url
        :type name: str
        :raises: HTTPError - when the *url* or the *request body* format or the *headers* are not right orthere is an internal error
        :request body: memory=<memory_int_MB> - the memory (integer in MB) to be inserted for the given *name* which is given in the *body* of the request
        """
        logging.debug(self.request.body)
        host = {'id': id, 'in_json': json.loads(self.request.body)}
        response = requests.post(config.get('postgrest', 'update_host_url'), json=host, headers={'Prefer': 'return=representation'})
        if response.ok:
            logging.info("Update host: " + id)
            logging.debug(response.text)
            self.set_status(CREATED)
        else:
            logging.error("Error updating the host: " + response.text)
            raise tornado.web.HTTPError(response.status_code)

    @http_basic_auth
    def delete(self, id):
        """
        The *DELETE* method deletes an entry from the table given the *name* in the url.
        You don't have to specify anything about the *id*.


        .. note::
            
            This method is not successful:

            * if the *name* does not exist
            * if headers have to be specified
            * if the client does not have the right authorization header 
           
        :param name: the new name which is given in the url
        :type name: str
        :raises: HTTPError - when there is an internal error or the requested name does not exist
        :request body: memory=<memory_int_MB> - the memory (integer in MB) to be inserted for the given *name* which is given in the *body* of the request
        """
        logging.debug(self.request.body)
        host = {'id': id}

        # Insert the instance in database using PostREST
        response = requests.post(config.get('postgrest', 'delete_host_url'), json=host, headers={'Prefer': 'return=representation'})
        if response.ok:
            logging.info("Delete host " + host["id"])
            logging.debug(response.text)
            self.set_status(CREATED)
        else:
            logging.error("Error delete the host: " + response.text)
            raise tornado.web.HTTPError(response.status_code)


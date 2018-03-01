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
    | 42 | apiato-db42 |  1024  |
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

    def get(self, name, *args):
        """
        The *GET* method returns the host's memory according to the example given above.
        (No any special headers for this request)

        :param name: the hostname which is given in the url
        :type name: str
        :rtype: json -- the response of the request
        :raises: HTTPError - when the requested name does not exist or if there is an internal 
        error or if the response is empty
        """

        logging.debug('Arguments:' + str(self.request.arguments))
        composed_url = self.url + '?name=eq.' + name + '&select=memory,id'
        logging.info("Requesting " + composed_url)
        response = requests.get(composed_url)
        data = response.json()
        if response.ok and data:
            logging.debug("response: " + json.dumps(data))
            self.write({'response' : data})
        elif response.ok:
            logging.warning("Name provided is not found in the table of the database: " + name)
            raise tornado.web.HTTPError(NOT_FOUND)
        else:
            logging.error("Error fetching name: " + response.text)
            raise tornado.web.HTTPError(response.status_code)

    @http_basic_auth
    def post(self, name, *args):
        """
        The *POST* method inserts a new *name* and its *memory* size according to the example above. 
        You don't have to specify anything about the *id* since this field should be specified as *serial*.

        .. note::

            This method is not successful:

            * if the *name* already exists
            * if the format of the *request body* is not right
            * if headers have to be specified
            * if the client does not have the right authorization header 
           
        :param name: the new name which is given in the url
        :type name: str
        :raises: HTTPError - when the *url* or the *request body* format or the *headers* are not right orthere is an internal error
        :request body: memory=<memory_int_MB> - the memory (integer in MB) to be inserted for the given *name* which is given in the *body* of the request
        """

        logging.debug('Arguments:' + str(self.request.arguments))
        try:
            memory = int(self.get_argument('memory'))
            logging.debug("memory: %s" %(memory))

            headers = {'Prefer': 'return=representation', 
                        'Content-Type': 'application/json'}
            insert_data = {"name": name,
                           "memory": memory}
            logging.debug("Data to insert: %s" %(insert_data))
            composed_url = self.url + '?name=eq.' + name
            logging.debug('Requesting insertion: ' + composed_url)
            
            response = requests.post(composed_url, json=insert_data, headers=headers)
            if response.ok:
                    logging.info('Data inserted in the table')
                    logging.debug(response.text)
                    self.set_status(CREATED)
            else:
                    logging.error("Duplicate entry or backend problem: " + response.text)
                    self.set_status(response.status_code)
                    raise tornado.web.HTTPError(response.status_code)

        except tornado.web.MissingArgumentError:
            logging.error("Bad argument given in the POST body request")
            logging.error("Try entering 'memory=<memory_int_MB>'")
            logging.error("Or try adding this header: \
                          'Content-Type: application/x-www-form-urlencoded'")
            self.set_status(BAD_REQUEST)
            raise tornado.web.HTTPError(BAD_REQUEST)
        except ValueError:
            logging.error("The value of the argument in the request body \
                        should be an integer")
            logging.error("Try entering 'memory=<memory_int_MB>'")
            self.set_status(BAD_REQUEST)
            raise tornado.web.HTTPError(BAD_REQUEST)

    @http_basic_auth   
    def put(self, name, *args):
        """
        The *PUT* method updates the *memory* size of the given *name* according to the example above.
        You don't have to specify anything about the *id* since this field should be specified as *serial*.


        .. note::
            
            In order to be able to use *PUT* method possibly you have to specify this header:
            'Content-Type: application/x-www-form-urlencoded'.

            This method is not successful:

            * if the *name* does not exist
            * if the format of the *request body* is not right
            * if headers have to be specified
            * if the client does not have the right authorization header 
           
        :param name: the new name which is given in the url
        :type name: str
        :raises: HTTPError - when the *url* or the *request body* format or the *headers* are not right orthere is an internal error
        :request body: memory=<memory_int_MB> - the memory (integer in MB) to be inserted for the given *name* which is given in the *body* of the request
        """

        logging.debug('Arguments:' + str(self.request.arguments))
        try:
            memory = int(self.get_argument('memory'))
            logging.debug("memory: %s" %(memory))
                
            headers = {'Prefer': 'return=representation', 
                    'Content-Type': 'application/json'}
            update_data = {"name": name,
                        "memory": memory}
            logging.debug("Data to insert: %s" %(update_data))
            composed_url = self.url + '?name=eq.' + name
            logging.debug('Requesting insertion: ' + composed_url)
            response = requests.patch(composed_url, json=update_data, headers=headers)
            if response.ok:
                logging.info('Data updated in the table')
                logging.debug(response.text)
                self.set_status(OK)
            else:
                logging.error("Error while updating the new name: " + response.text)
                self.set_status(response.status_code)
                raise tornado.web.HTTPError(response.status_code)

        except tornado.web.MissingArgumentError:
            logging.error("Bad argument given in the POST body request")
            logging.error("Try entering 'memory=<memory_int_MB>'")
            logging.error("Or try adding this header: \
                            'Content-Type: application/x-www-form-urlencoded'")
            self.set_status(BAD_REQUEST)
            raise tornado.web.HTTPError(BAD_REQUEST)

        except ValueError:
            logging.error("The value of the argument in the request body \
                    should be an integer")
            logging.error("Try entering 'memory=<memory_int_MB>'")
            self.set_status(BAD_REQUEST)
            raise tornado.web.HTTPError(BAD_REQUEST)

    @http_basic_auth
    def delete(self, name, *args):
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
        headers = {'Prefer': 'return=representation',
            'Content-Type': 'application/json'}
        composed_url = self.url + '?name=eq.' + name
        response = requests.delete(composed_url, headers=headers)
        logging.info("Requesting deletion of: " + name)
        if response.ok:
            logging.info("Data deleted")
            logging.debug(response.text)
            self.set_status(NO_CONTENT)
        else:
            logging.error("Error during deletion with code %s: %s" \
                    %(response.status_code, response.text) )
            logging.error("The given name does not exist in the table")
            raise tornado.web.HTTPError(response.status_code)

class HostList(tornado.web.RequestHandler):
    """
    This is the handler of **/host** endpoint.

    Things that are given for the development of this endpoint:

    * We request indirectly a `Postgres <https://www.postgresql.org/>`_ database through `PostgREST <http://postgrest.com/>`_ which returns a response in JSON format
    * The database's table that is used for this endpoint is called *host* and provides information for the functional alias association with an instance.
    * The columns of this table are like that:

    +----+-----------+--------+
    | id |  name     | memory |
    +====+===========+========+
    | 42 | apiato-db42 |  1024  |
    +----+-----------+--------+

        * The *name* in this example is the hostname of a node
        * The *memory* is the memory of the node expressed as integer in megabytes

    The request methods implemented for this endpoint are:

    * :func:`get`

    """

    url = config.get('postgrest', 'host_url')

    def get(self, *args):
        """
        The *GET* method returns the full list of hosts, with the 3 fields specified above.
        (No any special headers for this request)

        :rtype: json -- the response of the request
        :raises: HTTPError - when the requested name does not exist or if there is an internal 
        error or if the response is empty
        """

        logging.info("Requesting " + self.url)
        response = requests.get(self.url)
        data = response.json()
        if response.ok and data:
            logging.debug("List of hosts returned")
            self.write({'response' : data})
        else:
            logging.error("Error fetching hosts: " + response.text)
            raise tornado.web.HTTPError(response.status_code)
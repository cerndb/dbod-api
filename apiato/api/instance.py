#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2015, CERN
# This software is distributed under the terms of the GNU General Public
# Licence version 3 (GPL Version 3), copied verbatim in the file "LICENSE".
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as Intergovernmental Organization
# or submit itself to any jurisdiction.

"""
REST API Server for the DB On Demand System
"""

import tornado.web
import logging
import requests
import json
import urllib

from apiato.api.base import *
from apiato.config import config

class Instance(tornado.web.RequestHandler):
    """
    This is the handler of **/instance/<database name>** endpoint.

    Things that are given for the development of this endpoint:

    * We request indirectly a `Postgres <https://www.postgresql.org/>`_ database through `PostgREST <http://postgrest.com/>`_ which returns a response in JSON format
    * The database's tables/views that are used for this endpoint are 

        * *instance* - an example of this could look like this:

            +---+----------+---------++--------+-------+-----------+
            |id | username | db_name | db_type |version|    host   |
            +===+==========+=========+=========+=======+===========+
            |42 |dbod-usr42|dbod-db42| MYSQL   | 5.6.x |dbod-host42|
            +---+----------+---------+---------+-------+-----------+

        * *attribute*

            +--+------------+-------------------------+------------+
            |id| instance_id|           name          |  value     |
            +==+============+=========================+============+
            |24|     42     |port                     | 5432       |
            +--+------------+-------------------------+------------+
            |25|     42     |buffer_pool_size         | 1G         |
            +--+------------+-------------------------+------------+

        * *volume* - an example of this is like the following:

            +--+-------------+---------+-----------+-------------+
            |id| instance_id |file_mode|  server   |mounting_path|
            +==+=============+=========+===========+=============+
            |24|      42     |   0755  | NAS-server|  /MNT/data  |
        +--+-------------+---------+-----------+-------------+

        \* *(instance)id == (attribute/volume)instance_id*
        
        \*\* the id s are autoincremented (type serial)

      All of them provide the appropriate information for the creation/update/deletion of an instance.
  
    The request methods implemented for this endpoint are:

    * :func:`get`
    * :func:`post` - (creation)
    * :func:`put` - (update)
    * :func:`delete` - (deletion)

    .. note::

      You need to provide a <*username*> and a <*password*> or to provide
      manually the *Authorization* header in order to alter the database's
      content and specifically for :func:`post`, :func:`put` and :func:`delete`
      methods 

    """


    def get(self, name):
        """
        The *GET* method returns am *instance* given a *database name*.
        (No any special headers for this request)

        :param name: the database name which is given in the url
        :type name: str
        :rtype: json - the response of the request
        :raises: HTTPError - when the requested database name does not exist or if in case of an internal error 

        """
        response = requests.get(config.get('postgrest', 'instance_url') + "?name=eq." + name)
        if response.ok:
            data = response.json()
            if data:
                self.write({'response' : data})
                self.set_status(OK)
            else: 
                logging.error("Instance not found for name: " + name)
                raise tornado.web.HTTPError(NOT_FOUND)
        else:
            logging.error("Instance not found for name: " + name)
            raise tornado.web.HTTPError(NOT_FOUND)

    @http_basic_auth
    def post(self, id):
        """
        The *POST* method inserts a new instance into the database wih all the
        information that is needed for the creation of it.

        In the request body we specify all the information of the *instance*
        table along with the *attribute* and *volume* tables. All the 
        information is sent to a stored procedure in PostgreSQL which will
        insert the data in the related tables.
        
        .. note::
            
            * It's possible to insert more than one *hosts* or *volumes* in one instance.
            * The database names have to be unique
            * If any of the 3 insertions (in *instance*, *attribute*, *volume* table) is not successful then an *Exception* is raised and the private function :func:`__delete_instance__` is used in order to delete what may has been created.  
            * Also, the creation is not successful 

                * if the client is not authorized or
                * if there is any internal error
                * if the format of the request body is not right or if there is no *database name* field

        :param id: this argument is not used, however it has to exist for compatibility with the rest of endpoints
        :type id: str
        :raises: HTTPError - in case of an internal error
        :request body:  json

                       - for *instance*: json
                       - for *attribute*: json
                       - for *volume*: list of jsons

        """
        logging.debug(self.request.body)
        instance = {'in_json': json.loads(self.request.body)}
        
        # Insert the instance in database using PostgREST
        response = requests.post(config.get('postgrest', 'insert_instance_url'), json=instance, headers={'Prefer': 'return=representation'})
        if response.ok:
            logging.info("Created instance " + instance["in_json"]["name"])
            logging.debug(response.text)
            self.write(response.text)
            self.set_status(CREATED)
        else:
            logging.error("Error creating the instance: " + response.text)
            raise tornado.web.HTTPError(response.status_code)
            
            
            
    @http_basic_auth
    def put(self, id):
        """
        The *PUT* method updates an instance into the database wih all the information that is needed.

        In the request body we specify all the information of the *instance*
        table along with the *attribute* and *volume* tables. 

        The procedure of this method is the following:

        * We extract and separate the information of each table. 
        * We get the *id* of the row from the given (unique) database from the url.
        * If it exists, we delete if any information with that *id* exists in the tables.
        * After that, we insert the information to the related table along with the instance *id*. 
        * In case of more than one attributes we insert each one separetely.  
        * Finally, we update the *instance* table's row (which include the given database id) with the new given information.

        :param id: the database id which is given in the url
        :type id: str
        :raises: HTTPError - when the *request body* format is not right or in case of internall error

        """
        logging.debug(self.request.body)
        instance = {'iid': id, 'in_json': json.loads(self.request.body)}
        
        # Update the instance in database using PostgREST
        response = requests.post(config.get('postgrest', 'update_instance_url'), json=instance, headers={'Prefer': 'return=representation'})
        if response.ok:
            logging.info("Update instance: " + id)
            logging.debug(response.text)
            self.set_status(OK)
        else:
            logging.error("Error updating the instance: " + response.text)
            raise tornado.web.HTTPError(response.status_code)
            
            
            
    @http_basic_auth
    def delete(self, id):
        """
        The *DELETE* method deletes an instance by *database id*.
        
        In order to delete an instance we have to delete all the related information of the specified database id in *instance*, *attribute* and *volume* tables (:func:`__delete_instance__`).

        :param id: the database id which is given in the url
        :type id: str
        :raises: HTTPError - when the given database id cannot be found

        """
        logging.debug(self.request.body)
        if id.isdigit():
            instance = {'id': id}
        else:
            instance = {'instance_name': id}

        # Delete the instance in database using PostgREST
        response = requests.post(config.get('postgrest', 'delete_instance_url'), json=instance, headers={'Prefer': 'return=representation'})
        if response.ok:
            logging.info("Delete instance %s" % (id) )
            logging.debug(response.text)
            self.set_status(NO_CONTENT)
        else:
            logging.error("Error deleting the instance: " + response.text)
            raise tornado.web.HTTPError(response.status_code)

class Instance_filter(tornado.web.RequestHandler):
    """
    This is the handler of **/api/v1/instance** endpoint.

    The request methods implemented for this endpoint are:

    * :func:`get`

    """

    get_instances_url = config.get('postgrest', 'get_instances_url')

    def get(self, *args):

        """
        The *GET* method returns a list of e_groups owning resources

        :rtype: json -- the response of the request
        :raises: HTTPError - if there is an internal error or if the response is empty
        """
        auth_header = self.request.headers.get('auth')
        logging.debug("Auth header : %s" % (auth_header))
        if auth_header is None:
            raise tornado.web.HTTPError(BAD_REQUEST, "No 'auth' header found.")

        try:
            auth = json.loads(auth_header)
        except:
            raise tornado.web.HTTPError(BAD_REQUEST, "Error parsing JSON 'auth' header.")

        logging.debug("RPC Url : %s" % (self.get_instances_url))
    
        response = requests.post(self.get_instances_url, json=auth,
                headers={'Prefer': 'return=representation'})

        if response.ok:
            self.write(response.text)
            self.set_status(OK)
        else:
            logging.error("Response: %s" % (response.text))
            raise tornado.web.HTTPError(response.status_code)


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

from dbod.api.base import *
from dbod.config import config

class Attribute(tornado.web.RequestHandler):

    """
    This is the handler of **/<class>/<name>/attribute/<attribute_name>** endpoint.

    Things that are given for the development of this endpoint:

    * We request indirectly a `Postgres <https://www.postgresql.org/>`_ database through `PostgREST <http://postgrest.com/>`_ which returns a response in JSON format
    * The database's tables/views that are used for this endpoint are 

        * *attribute*

            +--+------------+-------------------------+------------+
            |id| instance_id|           name          |  value     |
            +==+============+=========================+============+
            |24|     42     |port                     | 5432       |
            +--+------------+-------------------------+------------+
            |25|     42     |buffer_pool_size         | 1G         |
            +--+------------+-------------------------+------------+

        \* *(instance)id == (attribute/volume)instance_id*
        
        \*\* the id s are autoincremented (type serial)

      All of them provide the appropriate information for the creation/update/deletion of an instance.
  
    The request methods implemented for this endpoint are:

    * :func:`get`
    * :func:`post` - (creation/addition of attributes)
    * :func:`put` - (update of existing attributes)
    * :func:`delete` - (deletion of attributes)
    
    .. note::

      You need to provide a <*username*> and a <*password*> or to provide
      manually the *Authorization* header in order to alter the database's
      content and specifically for :func:`post`, :func:`put` and :func:`delete`
      methods 

    """


    def get(self, **args):
        """
        The *GET* method returns an attribute referred to an *instance*.
        The parameter <attribute name> is optional. If it's not set the method will return all the attributes referred to the instance.
        (No any special headers for this request)

        :param inst_name: the database name which is given in the url
        :type inst_name: str
        :param attr_name: the attribute name to return
        :type attr_name: str
        :rtype: json - the response of the request
        :raises: HTTPError - when the requested database name does not exist or if in case of an internal error 

        """
        entity_id = args.get('entity')
        attribute_n = args.get('attribute_name')
        class_n = args.get('class')

        response = requests.get(config.get('postgrest', class_n + '_attributes_url') + "?" + class_n + "_id=eq." + entity_id)
        if response.ok:
            data = response.json()
            if data:
                if attribute_n:
                    if attribute_n in data[0]["attributes"]:
                        self.write(data[0]["attributes"][attribute_n])
                    else:
                        logging.error("Attribute " + attribute_n + " not found for " + class_n + " " + entity_id + ": " + response.text)
                        raise tornado.web.HTTPError(NOT_FOUND)
                else:
                    self.write(data[0]["attributes"])
                self.set_status(OK)
            else:
                logging.error("Attributes not found for " + class_n + ": " + entity_id)
                raise tornado.web.HTTPError(NOT_FOUND)

    @http_basic_auth
    def post(self, **args):
        """
        The *POST* method inserts a new attribute into the database for the specified instance.

        In the request body we specify all the information of the *attribute*
        table.
        
        .. note::
            
            * It's possible to insert more than one *attributes* in the same request. 
            * The attribute names are unique for each instance.
            * The creation is not successful 

                * if the client is not authorized or
                * if there is any internal error
                * if the format of the request body is not right or if there is no *database name* field

        :param name: the name of the database to insert the attributes
        :type name: str
        :raises: HTTPError - in case of an internal error
        :request body:  json

        """
        entity_id = args.get('entity')
        class_n = args.get('class')
        
        logging.debug(self.request.body)
        in_json = json.loads(self.request.body)
        attribute = {'id': entity_id, 'in_json': in_json}

        # Insert the instance in database using PostREST
        response = requests.post(config.get('postgrest', 'insert_' + class_n + '_attribute_url'), json=attribute, headers={'Prefer': 'return=representation'})
        if response.ok:
            logging.info("Created attribute " + json.dumps(in_json) + " for " + class_n + " " + entity_id)
            logging.debug(response.text)
            self.set_status(CREATED)
        else:
            logging.error("Error creating the attribute for " + class_n + " " + entity_id + ": " + response.text)
            raise tornado.web.HTTPError(response.status_code)
            
    @http_basic_auth
    def put(self, **args):
        """
        The *PUT* method updates an attribute into the database wih all the information that is needed.
        The name of the instance and the attribute are set in the URL. The new value of the attribute must be sent in the *request body*.

        :param instance: the database name which is given in the url
        :type instance: str
        :param attribute: the attribute name which is given in the url
        :type attribute: str
        :raises: HTTPError - when the *request body* format is not right or in case of internall error

        """
        
        entity_id = args.get('entity')
        attribute_n = args.get('attribute_name')
        class_n = args.get('class')
        
        logging.debug(self.request.body)
        in_json = {'id': entity_id, 'in_json': {attribute_n: self.request.body}}

        response = requests.post(config.get('postgrest', 'update_' + class_n + '_attribute_url'), json=in_json, headers={'Prefer': 'return=representation'})
        if response.ok:
            logging.info("Updated " + class_n + " attribute: " + attribute_n)
            self.set_status(NO_CONTENT)
        else:
            logging.error("Error updating the " + class_n + " " + entity_id + " attribute: " + response.text)
            raise tornado.web.HTTPError(response.status_code)

    @http_basic_auth
    def delete(self, **args):
        """
        The *DELETE* method deletes an attribute by *instance name* and *attribute name*.
        
        :param instance: the database name which is given in the url
        :type instance: str
        :param attribute: the attribute name which is given in the url
        :type attribute: str
        :raises: HTTPError - when the given database name cannot be found

        """
        entity_id = args.get('entity')
        attribute_n = args.get('attribute_name')
        class_n = args.get('class')
        
        json = {class_n + '_id': entity_id, 'attribute_name': attribute_n}
        
        # Delete the attribute in database using PostREST
        response = requests.post(config.get('postgrest', 'delete_' + class_n + '_attribute_url'), json=json, headers={'Prefer': 'return=representation'})
        if response.ok:
            logging.info("Delete " + class_n + " attribute: " + attribute_n)
            logging.debug(response.text)
            self.set_status(CREATED)
        else:
            logging.error("Error deleting the " + class_n + " " + entity_id + " attribute: " + response.text)
            raise tornado.web.HTTPError(response.status_code)

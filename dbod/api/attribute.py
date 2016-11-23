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
        The *GET* method returns an attributes referred to an *instance*.
        The parameter <attribute name> is optional. If it's not set the method will return all the attributes referred to the instance.
        (No any special headers for this request)

        :param inst_name: the database name which is given in the url
        :type inst_name: str
        :param attr_name: the attribute name to return
        :type attr_name: str
        :rtype: json - the response of the request
        :raises: HTTPError - when the requested database name does not exist or if in case of an internal error 

        """
        instance_n = args.get('instance')
        attribute_n = args.get('attribute_name')
        class_n = args.get('class')
        entid = get_instance_id_by_name(instance_n)
        if entid:
            if attribute_n:
                response = requests.get(config.get('postgrest', 'attribute_url') + "?select=value&instance_id=eq." + str(entid) + "&name=eq." + attribute_n)
                if response.ok:
                    data = response.json()
                    if data:
                        self.write(data[0]["value"])
                        self.set_status(OK)
                    else:
                        logging.error("Attribute '" + attribute_n + "' not found for instance: " + instance_n)
                        raise tornado.web.HTTPError(NOT_FOUND)
            else:
                filter = json.loads('{"inst_id": ' + str(entid) + '}')
                response = requests.post(config.get('postgrest', 'get_attributes_url'), json=filter)
                if response.ok:
                    data = response.json()
                    if data:
                        self.write(data[0]["get_attributes"])
                        self.set_status(OK)
                    else:
                        logging.error("Attributes not found for instance: " + instance_n)
                        raise tornado.web.HTTPError(NOT_FOUND)
        else:
            logging.error("Instance not found: " + instance_n)
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
        logging.debug(self.request.body)
        if not self.request.body:
            logging.error("The request contains no valid data")
            raise tornado.web.HTTPError(BAD_REQUEST)
            
        attributes = json.loads(self.request.body)
        instance_n = args.get('instance')
        entid = get_instance_id_by_name(instance_n)
        if attributes:
            if entid:
                insert_attributes = []
                for attribute in attributes:
                    insert_attr = {'instance_id': entid, 'name': attribute, 'value': attributes[attribute]}
                    logging.debug("Inserting attribute: " + json.dumps(insert_attr))
                    insert_attributes.append(insert_attr)
                
                response = requests.post(config.get('postgrest', 'attribute_url'), json=insert_attributes)
                if response.ok:
                    self.set_status(CREATED)
                else:
                    logging.error("Error inserting attributes: " + response.text)
                    raise tornado.web.HTTPError(response.status_code)
            else:
                logging.error("Instance not found: " + instance_n)
                raise tornado.web.HTTPError(NOT_FOUND)
        else:
            logging.error("The request contains no valid data")
            raise tornado.web.HTTPError(BAD_REQUEST)
            
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
        logging.debug(self.request.body)
        if not self.request.body:
            logging.error("The request contains no valid data")
            raise tornado.web.HTTPError(BAD_REQUEST)
            
        new_value = self.request.body
        instance_n = args.get('instance')
        attribute_n = args.get('attribute')
        entid = get_instance_id_by_name(instance_n)
        if not entid:
            logging.error("Instance '" + instance_n + "' doest not exist.")
            raise tornado.web.HTTPError(NOT_FOUND)
            
        body = json.loads('{"value":"' + new_value + '"}')
        response = requests.patch(config.get('postgrest', 'attribute_url') + "?instance_id=eq." + str(entid) + "&name=eq." + attribute_n, json=body)
        if response.ok:
            self.set_status(NO_CONTENT)
        else:
            logging.error("Error editing the attribute: " + response.text)
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
        instance_n = args.get('instance')
        attribute_n = args.get('attribute')
        
        if not instance_n:
            logging.error("No instance specified")
            raise tornado.web.HTTPError(BAD_REQUEST)
        if not attribute_n:
            logging.error("No attribute specified")
            raise tornado.web.HTTPError(BAD_REQUEST)
        
        entid = get_instance_id_by_name(instance_n)
        if entid:
            response = requests.delete(config.get('postgrest', 'attribute_url') + "?instance_id=eq." + str(entid) + "&name=eq." + attribute_n)
            self.set_status(response.status_code)
        else:
            logging.error("Instance not found: " + instance_n)
            raise tornado.web.HTTPError(NOT_FOUND)
            

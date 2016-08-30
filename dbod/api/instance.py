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
        response = requests.get(config.get('postgrest', 'instance_url') + "?db_name=eq." + name)
        if response.ok:
            data = response.json()
            if data:
                self.write({'response' : data})
                self.set_status(OK)
            else: 
                logging.error("Instance metadata not found: " + name)
                raise tornado.web.HTTPError(NOT_FOUND)
        else:
            logging.error("Entity metadata not found: " + name)
            raise tornado.web.HTTPError(NOT_FOUND)

    @http_basic_auth
    def post(self, name):
        """
        The *POST* method inserts a new instance into the database wih all the
        information that is needed for the creation of it.

        In the request body we specify all the information of the *instance*
        table along with the *attribute* and *volume* tables. We extract and
        separate the information of each table. After inserting the information
        in the *instance* table we use its *id* to relate the specific instance
        with the *attribute* and *volume* table.
        
        .. note::
            
            
            * It's possible to insert more than one *hosts* or *volumes* in one instance.
            * The database names have to be unique
            * If any of the 3 insertions (in *instance*, *attribute*, *volume* table) is not successful then an *Exception* is raised and the private function :func:`__delete_instance__` is used in order to delete what may has been created.  
            * Also, the creation is not successful 

                * if the client is not authorized or
                * if there is any internal error
                * if the format of the request body is not right or if there is no *database name* field

        :param name: the new database name which is given in the url or any other string
        :type name: str
        :raises: HTTPError - in case of an internal error
        :request body:  json

                       - for *instance*: json
                       - for *attribute*: json
                       - for *volume*: list of jsons

        """
        logging.debug(self.request.body)
        instance = json.loads(self.request.body)
        
        attributes = None
        volumes = None
        entid = None
        # Get the attributes
        if "attributes" in instance:
            attributes = instance["attributes"]
            del instance["attributes"]
        
        # Get the hosts
        if "hosts" in instance:
            hosts = instance["hosts"][0]
            if len(instance["hosts"]) > 1:
                for i in range(1, len(instance["hosts"])):
                    hosts = hosts + "," + instance["hosts"][i]
            instance["host"] = hosts
            del instance["hosts"]
        
        # Get the volumes
        if "volumes" in instance:
            volumes = instance["volumes"]
            del instance["volumes"]
        
        # Insert the instance in database using PostREST
        response = requests.post(config.get('postgrest', 'instance_url'), json=instance, headers={'Prefer': 'return=representation'})
        if response.ok:
            entid = json.loads(response.text)["id"]
            logging.info("Created instance " + instance["db_name"])
            logging.debug(response.text)
            self.set_status(CREATED)
        else:
            logging.error("Error creating the instance: " + response.text)
            raise tornado.web.HTTPError(response.status_code)
        
        # Add instance id to volumes
        if volumes:
            for volume in volumes:
                volume["instance_id"] = entid

            # Insert the volumes in database using PostREST
            logging.debug(volumes)
            response = requests.post(config.get('postgrest', 'volume_url'), json=volumes)
            if response.ok:
                logging.debug("Inserting volumes: " + json.dumps(volumes))
                self.set_status(CREATED)
            else:
                logging.error("Error creating the volumes: " + response.text)
                self.__delete_instance__(entid)
                raise tornado.web.HTTPError(response.status_code)
                
        # Insert the attributes
        if attributes:
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
                self.__delete_instance__(entid)
                raise tornado.web.HTTPError(response.status_code)
            
    @http_basic_auth
    def put(self, name):
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
        * Finally, we update the *instance* table's row (which include the given database name) with the new given information.

        :param name: the database name which is given in the url
        :type name: str
        :raises: HTTPError - when the *request body* format is not right or in case of internall error

        """
        logging.debug(self.request.body)
        instance = json.loads(self.request.body)
        entid = self.__get_instance_id__(name)
        if not entid:
            logging.error("Instance '" + name + "' doest not exist.")
            raise tornado.web.HTTPError(NOT_FOUND)
        
        # Check if the volumes are changed
        if "volumes" in instance:
            volumes = instance["volumes"]
            for volume in volumes:
                volume["instance_id"] = entid
            del instance["volumes"]
            
            # Delete current volumes
            response = requests.delete(config.get('postgrest', 'volume_url') + "?instance_id=eq." + str(entid))
            logging.debug("Volumes to insert: " + json.dumps(volumes))
            if response.ok or response.status_code == 404:
                if len(volumes) > 0:
                    response = requests.post(config.get('postgrest', 'volume_url'), json=volumes)
                    if response.ok:
                        self.set_status(NO_CONTENT)
                    else:
                        logging.error("Error adding volumes: " + response.text)
                        raise tornado.web.HTTPError(response.status_code)
            else:
                logging.error("Error deleting old volumes: " + response.text)
                raise tornado.web.HTTPError(response.status_code)
                
        # Check if the attributes are changed
        if "attributes" in instance:
            attributes = instance["attributes"]
            response = requests.delete(config.get('postgrest', 'attribute_url') + "?instance_id=eq." + str(entid))
            if response.ok or response.status_code == 404:
                if len(attributes) > 0:
                    # Insert the attributes
                    insert_attributes = []
                    for attribute in attributes:
                        insert_attr = {'instance_id': entid, 'name': attribute, 'value': attributes[attribute]}
                        logging.debug("Inserting attribute: " + json.dumps(insert_attr))
                        insert_attributes.append(insert_attr)
                        
                    response = requests.post(config.get('postgrest', 'attribute_url'), json=insert_attributes)
                    if response.ok:
                        self.set_status(NO_CONTENT)
                    else:
                        logging.error("Error inserting attributes: " + response.text)
                        raise tornado.web.HTTPError(response.status_code)
            else:
                logging.error("Error deleting attributes: " + response.text)
                raise tornado.web.HTTPError(response.status_code)
            del instance["attributes"]
        
        if instance:
            # Check if the hosts are changed
            if "hosts" in instance:
                hosts = instance["hosts"][0]
                if len(instance["hosts"]) > 1:
                    for i in range(1, len(instance["hosts"])):
                        hosts = hosts + "," + instance["hosts"][i]
                instance["host"] = hosts
                del instance["hosts"]
        
            response = requests.patch(config.get('postgrest', 'instance_url') + "?db_name=eq." + name, json=instance)
            if response.ok:
                self.set_status(NO_CONTENT)
            else:
                logging.error("Error editing the instance: " + response.text)
                raise tornado.web.HTTPError(response.status_code)
        else:
            self.set_status(NO_CONTENT)
            
    @http_basic_auth
    def delete(self, name):
        """
        The *DELETE* method deletes an instance by *database name*.
        
        In order to delete an instance we have to delete all the related information of the specified database name in *instance*, *attribute* and *volume* tables (:func:`__delete_instance__`). To achieve that we have to first find the *id* of the given database name (:func:__get_instance_id__).

        :param name: the database name which is given in the url
        :type name: str
        :raises: HTTPError - when the given database name cannot be found

        """
        entid = self.__get_instance_id__(name)
        if entid:
            logging.debug("Deleting instance id: " + str(entid))
            self.__delete_instance__(entid)
            self.set_status(204)
        else:
            logging.error("Instance not found: " + name)
            raise tornado.web.HTTPError(NOT_FOUND)
            
    def __get_instance_id__(self, name):
        """
        This is a private function which is used by :func:`put` and :func:`delete` methods.
        Returns the instance *id* given the database name in order to be able to operate on the instance related tables. It returns *None* if the specified database name does not exist in the *instance* table or in case of internal error.

        :param name: the database name from which we want to get the *id*
        :type name: str
        :rtype: str or None

        """
        response = requests.get(config.get('postgrest', 'instance_url') + "?db_name=eq." + name)
        if response.ok:
            data = response.json()
            if data:
                return data[0]["id"]
            else:
                return None
        else:
            return None
            
    def __delete_instance__(self, inst_id):
        """
        This is a private function that is used by :func:`put` and :func:`delete` methods.
        It deletes all the related information of an instance from the *instance*, *attribute* and *volume* table given the database's *id*
        
        :param inst_id: the id of the instance we want to delete
        :type inst_id: str

        """
        requests.delete(config.get('postgrest', 'attribute_url') + "?instance_id=eq." + str(inst_id))
        requests.delete(config.get('postgrest', 'volume_url') + "?instance_id=eq." + str(inst_id))
        requests.delete(config.get('postgrest', 'instance_url') + "?id=eq." + str(inst_id))
        


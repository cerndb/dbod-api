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
    def get(self, name):
        """Returns an instance by db_name"""
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

    def post(self, name):
        """Inserts a new instance in the database"""
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
                logging.error("Error inserting the port attribute: " + response.text)
                self.__delete_instance__(entid)
                raise tornado.web.HTTPError(response.status_code)
            
    def put(self, name):
        """Updates an instance"""
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
            
    def delete(self, name):
        """Deletes an instance by name"""
        entid = self.__get_instance_id__(name)
        if entid:
            logging.debug("Deleting instance id: " + str(entid))
            self.__delete_instance__(entid)
            self.set_status(204)
        else:
            logging.error("Instance not found: " + name)
            raise tornado.web.HTTPError(NOT_FOUND)
            
    def __get_instance_id__(self, name):
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
        requests.delete(config.get('postgrest', 'attribute_url') + "?instance_id=eq." + str(inst_id))
        requests.delete(config.get('postgrest', 'volume_url') + "?instance_id=eq." + str(inst_id))
        requests.delete(config.get('postgrest', 'instance_url') + "?id=eq." + str(inst_id))
        


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

from dbod.api.base import *
from dbod.config import config

class Entity(tornado.web.RequestHandler):
    def post(self, instance):
        """Inserts a new instance in the database"""
        entity = json.loads(self.request.body)
        
        # Get the port
        port = entity["port"]
        del entity["port"]
        
        # Get the volumes
        volumes = entity["volumes"]
        del entity["volumes"]
        
        # Insert the entity in database using PostREST
        response = requests.post("http://localhost:3000/instance", json=entity, headers={'Prefer': 'return=representation'})
        if response.ok:
            entid = json.loads(response.text)["id"]
            logging.debug("Created entity with id: " + str(entid))
        
            # Add entity id to volumes
            for volume in volumes:
                volume["instance_id"] = entid

            # Insert the volumes in database using PostREST
            response = requests.post("http://localhost:3000/volume", json=volumes)
            if response.ok:
                response = requests.post("http://localhost:3000/attribute", json={'instance_id': entid, 'name': 'port', 'value': port})
                if response.ok:
                    self.set_status(CREATED)
                else:
                    logging.error("Error inserting the port attribute: " + response.text)
                    self.__delete_instance__(entid)
                    raise tornado.web.HTTPError(response.status_code)
            else:
                logging.error("Error creating the volumes: " + response.text)
                self.__delete_instance__(entid)
                raise tornado.web.HTTPError(response.status_code)
        else:
            logging.error("Error creating the entity: " + response.text)
            raise tornado.web.HTTPError(response.status_code)
            
    def put(self, instance):
        """Updates an instance"""
        entity = json.loads(self.request.body)
        logging.debug(entity)
        response = requests.patch("http://localhost:3000/instance?db_name=eq." + instance, json=entity)
        if response.ok:
            self.set_status(response.status_code)
        else:
            logging.error("Instance not found: " + instance)
            raise tornado.web.HTTPError(response.status_code)
            
    def delete(self, instance):
        """Deletes an instance by name"""
        response = requests.get("http://localhost:3000/instance?db_name=eq." + instance)
        if response.ok:
            entid = json.loads(response.text)[0]["id"]
            logging.debug("Deleting instance id: " + str(entid))
            __delete_instance__(entid)
            self.set_status(response.status_code)
        else:
            logging.error("Instance not found: " + instance)
            raise tornado.web.HTTPError(response.status_code)
            
    def __delete_instance__(self, inst_id):
        requests.delete("http://localhost:3000/attribute?instance_id=eq." + str(inst_id))
        requests.delete("http://localhost:3000/volume?instance_id=eq." + str(inst_id))
        requests.delete("http://localhost:3000/instance?id=eq." + str(inst_id))
        


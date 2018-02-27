#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2015, CERN
# This software is distributed under the terms of the GNU General Public
# Licence version 3 (GPL Version 3), copied verbatim in the file "LICENSE".
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as Intergovernmental Organization
# or submit itself to any jurisdiction.

"""
Volume module, which includes all the classes related with Volume endpoints.
"""

import tornado.web
import logging
import requests
import json

from apiato.api.base import *
from apiato.config import config

class Volume(tornado.web.RequestHandler):
    """
    This is the handler of **/volume/<name>** endpoint.
    This endpoint takes 1 arguments:
    * *<name>* - the name of a *instance*
    Things that are given for the development of this endpoint:
    * We request indirectly a `Postgres <https://www.postgresql.org/>`_ database through `PostgREST <http://postgrest.com/>`_ which returns a response in JSON format
    * The database's table/view that is used for this endpoint is called *Volume* and provides metadata about a Volume and its attributes.
    * Here is an example of this table:
    --ToDO
    The request method implemented for this endpoint is just the :func:`get`.
    """
    def get(self, name):
        """Returns the volume information

        (No any special headers for this request)
        :param name: the isntance name which is given in the url
        :type name: str
        :rtype: json - the response of the request
        :raises: HTTPError - when the given instance name does not exist or in case of an internal error
        """
        response = requests.get(config.get('postgrest', 'volume_url') + "?name=eq." + name)
        if response.ok:
            data = response.json()
            if data:
                self.write({'response' : data})
                self.set_status(OK)
            else:
                logging.error("Volume metadata not found: " + name)
                raise tornado.web.HTTPError(NOT_FOUND)
        else:
            logging.error("Entity volume not found: " + name)
            raise tornado.web.HTTPError(NOT_FOUND)



    @http_basic_auth
    def post(self, id):
        """
        The *POST* method inserts a new volume into the database with all the
        information that is needed for the creation of it.
        In the request body we specify all the information of the *volume*
        table along with the *attribute* table. We extract and
        separate the information of each table.
        .. note::
            * It's possible to insert more than one *attribute* in one Volume.

            * Also, the creation is not successful
                * if the client is not authorized or
                * if there is any internal error
                * if the format of the request body is not right or if there is no *database name* field
        :param id: the new Volume name which is given in the url or any other string
        :type id: str
        :raises: HTTPError - in case of an internal error
        :request body:  json
                       - for *Volume*: json
                       - for *Volume attribute*: json
        """
        logging.debug(self.request.body)
        volume = {'in_json': json.loads(self.request.body)}

        # Insert the instance in database using PostREST
        response = requests.post(config.get('postgrest', 'insert_volume_url'), json=volume, headers={'Prefer': 'return=representation'})
        if response.ok:
            logging.info("Created volume " + id)
            logging.debug(response.text)
            self.set_status(CREATED)
        else:
            logging.error("Error creating the volume: " + response.text)
            raise tornado.web.HTTPError(response.status_code)




    @http_basic_auth
    def put(self, id):
        """
        The *PUT* method updates a volume with all the information that is needed.
        The procedure of this method is the following:
        :param id: the volume id which is given in the url
        :type id: str
        :raises: HTTPError - when the *request body* format is not right or in case of internall error
        """
        logging.debug(self.request.body)
        volume = {'id': id, 'in_json': json.loads(self.request.body)}
        response = requests.post(config.get('postgrest', 'update_volume_url'), json=volume, headers={'Prefer': 'return=representation'})
        if response.ok:
            logging.info("Update volume: " + id)
            logging.debug(response.text)
            self.set_status(CREATED)
        else:
            logging.error("Error updating the volume: " + response.text)
            raise tornado.web.HTTPError(response.status_code)


    @http_basic_auth
    def delete(self, id):
        """
        The *DELETE* method deletes a volume by *id*.
        In order to delete a volume we have to delete all the related information of the specified *attribute* tables.
        :param id: the database name which is given in the url
        :type id: str
        :raises: HTTPError - when the given database name cannot be found
        """
        logging.debug(self.request.body)
        volume = {'id': id}

        # Insert the instance in database using PostREST
        response = requests.post(config.get('postgrest', 'delete_volume_url'), json=volume, headers={'Prefer': 'return=representation'})
        if response.ok:
            logging.info("Delete volume " + volume["id"])
            logging.debug(response.text)
            self.set_status(NO_CONTENT)
        else:
            logging.error("Error delete the volume: " + response.text)
            raise tornado.web.HTTPError(response.status_code)
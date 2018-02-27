#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2015, CERN
# This software is distributed under the terms of the GNU General Public
# Licence version 3 (GPL Version 3), copied verbatim in the file "LICENSE".
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as Intergovernmental Organization
# or submit itself to any jurisdiction.

"""
cluster module, which includes all the classes related with cluster endpoints.
"""

import tornado.web
import logging
import requests
import json

from apiato.api.base import *
from apiato.config import config

class Cluster(tornado.web.RequestHandler):
    """
    This is the handler of **/cluster/<name>** endpoint.
    This endpoint takes 1 arguments:
    * *<name>* - the name of a *cluster*
    Things that are given for the development of this endpoint:
    * We request indirectly a `Postgres <https://www.postgresql.org/>`_ database through `PostgREST <http://postgrest.com/>`_ which returns a response in JSON format
    * The database's table/view that is used for this endpoint is called *cluster* and provides metadata about a cluster and its instances.
    * Here is an example of this table:
    --ToDO
    The request method implemented for this endpoint is just the :func:`get`.
    """
    def get(self, name):
        """Returns the cluster information
        he *GET* method returns a *cluster* given a *name*.
        (No any special headers for this request)
        :param name: the database name which is given in the url
        :type name: str
        :rtype: json - the response of the request
        :raises: HTTPError - when the given cluster name does not exist or in case of an internal error
        """
        response = requests.get(config.get('postgrest', 'cluster_url') + "?name=eq." + name)
        if response.ok:
            data = response.json()
            if data:
                self.write({'response' : data})
                self.set_status(OK)
            else:
                logging.error("Cluster metadata not found: " + name)
                raise tornado.web.HTTPError(NOT_FOUND)
        else:
            logging.error("Entity metadata not found: " + name)
            raise tornado.web.HTTPError(NOT_FOUND)



    @http_basic_auth
    def post(self, id):
        """
        The *POST* method inserts a new cluster into the database with all the
        information that is needed for the creation of it.
        In the request body we specify all the information of the *cluster*
        table along with the *attribute* table. We extract and
        separate the information of each table.
        .. note::
            * It's possible to insert more than one *attribute* in one cluster.
            * The cluster names have to be unique
            * Also, the creation is not successful
                * if the client is not authorized or
                * if there is any internal error
                * if the format of the request body is not right or if there is no *database name* field
        :param id: the new cluster name which is given in the url or any other string
        :type id: str
        :raises: HTTPError - in case of an internal error
        :request body:  json
                       - for *cluster*: json
                       - for *cluster attribute*: json
        """
        logging.debug(self.request.body)
        cluster = {'in_json': json.loads(self.request.body)}

        # Insert the instance in database using PostREST
        response = requests.post(config.get('postgrest', 'insert_cluster_url'), json=cluster, headers={'Prefer': 'return=representation'})
        if response.ok:
            logging.info("Created cluster " + cluster["in_json"]["name"])
            logging.debug(response.text)
            self.set_status(CREATED)
        else:
            logging.error("Error creating the cluster: " + response.text)
            raise tornado.web.HTTPError(response.status_code)




    @http_basic_auth
    def put(self, id):
        """
        The *PUT* method updates a cluster with all the information that is needed.
        The procedure of this method is the following:
        :param name: the cluster name which is given in the url
        :type name: str
        :raises: HTTPError - when the *request body* format is not right or in case of internall error
        """
        logging.debug(self.request.body)
        cluster = {'cid': id, 'in_json': json.loads(self.request.body)}
        response = requests.post(config.get('postgrest', 'update_cluster_url'), json=cluster, headers={'Prefer': 'return=representation'})
        if response.ok:
            logging.info("Update Cluster: " + id)
            logging.debug(response.text)
            self.set_status(OK)
        else:
            logging.error("Error updating the cluster: " + response.text)
            raise tornado.web.HTTPError(response.status_code)


    @http_basic_auth
    def delete(self, id):
        """
        The *DELETE* method deletes a cluster by *name*.
        In order to delete a cluster we have to delete all the related information of the specified database name in *cluster*, *attribute* and *instance* tables.
        :param id: the database name which is given in the url
        :type id: str
        :raises: HTTPError - when the given database name cannot be found
        """
        logging.debug(self.request.body)
        cluster = {'cid': id}

        # Insert the instance in database using PostREST
        response = requests.post(config.get('postgrest', 'delete_cluster_url'), json=cluster, headers={'Prefer': 'return=representation'})
        if response.ok:
            logging.info("Delete cluster: " + id)
            logging.debug(response.text)
            self.set_status(NO_CONTENT)
        else:
            logging.error("Error delete the cluster: " + response.text)
            raise tornado.web.HTTPError(response.status_code)


class Cluster_filter(tornado.web.RequestHandler):
    """
    This is the handler of **/api/v1/cluster** endpoint.

    The request methods implemented for this endpoint are:

    * :func:`get`

    """

    get_clusters_url = config.get('postgrest', 'get_clusters_url')

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

        logging.debug("RPC Url : %s" % (self.get_clusters_url))

        response = requests.post(self.get_clusters_url, json=auth,
                headers={'Prefer': 'return=representation'})

        if response.ok:
            self.write(response.text)
            self.set_status(OK)
        else:
            logging.error("Response: %s" % (response.text))
            raise tornado.web.HTTPError(response.status_code)

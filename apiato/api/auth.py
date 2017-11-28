#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2017, CERN
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

class Resources(tornado.web.RequestHandler):
    """
    This is the handler of **/auth/resources** endpoint.

    Things that are given for the development of this endpoint:

    * We request indirectly a `Postgres <https://www.postgresql.org/>`_ database through `PostgREST <http://postgrest.com/>`_ which returns a response in JSON format
    * The database's view that is used for this endpoint is called *api.e_groups* and provides a list of the e_groups owning instances.
    
    The request methods implemented for this endpoint are:

    * :func:`get`

    """

    url = config.get('postgrest', 'egroups_url')

    def get(self, *args):

        """
        The *GET* method returns a list of e_groups owning resources

        :rtype: json -- the response of the request
        :raises: HTTPError - if there is an internal error or if the response is empty
        """

        composed_url = self.url
        try:
            logging.debug('Request body: %s' % (self.request.body))
            body = json.loads(self.request.body)
            username = body.get("username")
            user_egroups = set(body.get("groups"))
        except KeyError, ValueError:
            raise tornado.web.HTTPError(BAD_REQUEST)
        
        resources = {}
        
        # Computing group intersection
        logging.debug('User e_groups %s' % user_egroups)

        # Verifying Admin role
        if config.get('auth', 'admin_group') in list(user_egroups):
            resources["admin"] = True

        logging.debug("Requesting system e_groups" + composed_url)
        response = requests.get(composed_url)
        system_egroups = None
        data = response.json()
        if response.ok and data:
            logging.debug("response: " + json.dumps(data))
            system_egroups = data[0].get("e_groups")
        else:
            logging.error("Error fetching list of system recognized e_groups: " + response.text)
            raise tornado.web.HTTPError(response.status_code)
        
        intersect = user_egroups.intersection(system_egroups)
        if bool(intersect):
            resources["groups"] = list(intersect)
        
        # Fetching list of owned instances
        logging.debug('Username: %s' % (username) )
        logging.debug("Requesting user owned instances: " + config.get('postgrest', 'user_instances_url'))
        rbody = {'owner': username , 'groups': resources.get('groups')}
        response = requests.post(config.get('postgrest','user_instances_url'),
            json=rbody,
            headers={'Prefer': 'return=representation'}
            )
        if response.ok:
            data = response.json()
            logging.debug("User instances response: " + json.dumps(data))
            resources["instances"] = data[0].get("get_user_instances")
        else:
            logging.debug(response)
            logging.info("No instances directly owned by user")
        
        # Fetching list of owned clusters
        logging.debug('Username: %s' % (username) )
        logging.debug("Requesting user owned clusters: " + config.get('postgrest', 'user_clusters_url'))
        rbody = {'owner': username , 'groups': resources.get('groups')}
        response = requests.post(config.get('postgrest','user_clusters_url'),
            json=rbody,
            headers={'Prefer': 'return=representation'}
            )
        if response.ok:
            data = response.json()
            logging.debug("User clusters response: " + json.dumps(data))
            resources["clusters"] = data[0].get("get_user_clusters")
        else:
            logging.debug(response)
            logging.info("No instances directly owned by user")

        if bool(resources):
            self.write(json.dumps(resources))
            self.set_status(OK)
        else:
            raise tornado.web.HTTPError(NOT_FOUND)




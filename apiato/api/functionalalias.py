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
from sys import exc_info
import requests
import tornado.web
import tornado.escape
from apiato.api.base import *
from apiato.config import config

class FunctionalAlias(tornado.web.RequestHandler):

    """
    This is the handler of **/instance/alias/<database name>** endpoint.

    Things that are given for the development of this endpoint:

    * We request indirectly a `Postgres <https://www.postgresql.org/>`_ database through `PostgREST <http://postgrest.com/>`_ which returns a response in JSON format
    * The database's table that is used for this endpoint is called *functional_aliases* and provides information for the functional alias association with an instance.
    * The columns of this table are like that:

    +------------+------------+----------------------+
    |  dns_name  |  db_name   |         alias        |
    +============+============+======================+
    | dbod-dns42 | dbod-db42  | dbod-alias42.cern.ch |
    +------------+------------+----------------------+

        * The *dns_name* is used internally. They point to a list of virtual IP addresses and each bound to a host
        * The *db_name* is the name of the database instance
        * The *alias* is the alias given in order the database to be accessed with that name

    * There is a pool of *dns_names* in this table and the other 2 columns are *NULL* in the begining

    The request methods implemented for this endpoint are:

    * :func:`get`
    * :func:`post`
    * :func:`delete` 

    .. note::

      You need to provide a <*username*> and a <*password*> to use
      :func:`post` and :func:`delete` methods or to provide manually the *Authorization* header.

    """

    url = config.get('postgrest', 'functional_alias_url')

    def get(self, db_name, *args):
        """
        The *GET* method returns the database name's *alias* and *dns name*.
        (No any special headers for this request)

        :param db_name: the database name which is given in the url
        :type db_name: str
        :rtype: json -- the response of the request
        :raises: HTTPError - when the requested database name does not exist or if there is an internal error 
        
        """
        logging.debug('Arguments:' + str(self.request.arguments))
        composed_url = self.url + '?db_name=eq.' + db_name + '&select=dns_name,alias'
        logging.info('Requesting ' + composed_url)
        response = requests.get(composed_url)
        data = response.json()
        if response.ok and data:
            logging.debug("response: " + json.dumps(data))
            self.write({'response' : data})
            self.set_status(OK)
        elif response.ok:
            logging.warning("Functional alias not found for instance: " + db_name)
            raise tornado.web.HTTPError(NOT_FOUND)
        else:
            logging.error("Error fetching functional alias: " + response.text)
            raise tornado.web.HTTPError(response.status_code)

    @http_basic_auth
    def post(self, db_name, *args):
        """
        The *POST* method inserts a new *database name* and its *alias* into the database. It
        adds the functional alias association for an instance.

        The *dns name* is chosen automatically from a pool; so, in the background this method 
        actually updates the *database name* and *alias* fields, which were *NULL* in the 
        begining.

        .. note::

            This method is not successful:

            * if the *database name* already exists
            * if there are no any *dns names* available
            * if the format of the *request body* is not right
            * if headers have to be specified
            * if the client does not have the right authorization header 
           
        :param db_name: the new database name which is given in the url
        :type db_name: str
        :raises: HTTPError - when the *url* or the *request body* format or the *headers* are not right
        :request body: alias=<alias> - the alias to be inserted for the given *database name* which is given in the *body* of the request

        """

        logging.debug('Arguments:' + str(self.request.arguments))
        try:
            alias = self.get_argument('alias')
            logging.debug("alias: %s" % (alias))
            
            dns_name = self._next_dnsname()

            if dns_name:
                logging.debug("dns_name picked: " + str(dns_name))
                headers = {'Prefer': 'return=representation'}
                insert_data = {"db_name": db_name, 
                               "alias": alias}
                logging.debug("Data to insert: " + str(insert_data))

                composed_url = self.url + '?dns_name=eq.' + dns_name
                logging.debug('Requesting insertion: ' + composed_url)
                
                response = requests.patch(composed_url, json=insert_data, headers=headers)
            
                if response.ok:
                    logging.info('Data inserted in the functional_aliases table')
                    logging.debug(response.text)
                    self.set_status(CREATED)
                else:
                    logging.error("Error inserting the functional alias: " + response.text)
                    self.set_status(response.status_code)
                        
            else:
                logging.error("No dns_name available in the functional_aliases table")
                self.set_status(SERVICE_UNAVAILABLE)
        except:
            logging.error("Argument not recognized or not defined.")
            logging.error("Try adding header 'Content-Type:application/x-www-form-urlencoded'")
            logging.error("The right format should be: alias=<alias>")
            raise tornado.web.HTTPError(BAD_REQUEST)


    @http_basic_auth
    def delete(self, db_name, *args):
        """
        The *DELETE* method deletes or else asssigns to *NULL* the *database name* and 
        *alias* fields. It removes the functional alias association for an instance.

        .. note::
            
            * If the *database name* doesn't exist it doesn't do anything
            * You have to be authorized to use this method
        
        :param db_name: the new database name which is given in the url
        :type db_name: str
        :raises: HTTPError - when the deletion is not successful

        """

        logging.debug('Arguments:' + str(self.request.arguments))

        dns_name = self._get_dns(db_name)
        logging.debug(dns_name)
        if dns_name:
            headers = {'Prefer': 'return=representation', 'Content-Type': 'application/json'}
            composed_url = self.url + '?dns_name=eq.' + dns_name
            logging.debug('Requesting deletion: ' + composed_url)
            delete_data = '{"db_name": null, "alias": null}'
            logging.debug("dns_name to be remained: " + dns_name)
            response = requests.patch(composed_url, json=json.loads(delete_data), headers=headers)

            if response.ok:
                logging.info("Delete success of: " + dns_name)
                logging.debug(response.text)
                self.set_status(NO_CONTENT)
            else:
                logging.error("Unsuccessful deletion")
                raise tornado.web.HTTPError(response.status_code)

        else:
            logging.info("db_name not found. Nothing to do")

    def _next_dnsname(self):
        """
        This is a private function which is used by :func:`post` method.
        Returns the next dnsname which can be used for a newly created instance.  
        If there is no available *dns name* in the pool or if there is any internal error it returns *None*.

        :rtype: str or None

        """
        #LIMIT is not working in postgrest but it uses some headers for that as well
        headers = {'Range-Unit': 'items', 'Range': '0-0'}
        # select the next available dns_name with db_name and alias assigned to NULL
        query_select = '?select=dns_name&order=dns_name.asc&'
        query_filter = 'db_name=is.null&alias=is.null&dns_name=isnot.null'
        composed_url = self.url + query_select + query_filter
        try:
            response_dns = requests.get(composed_url, headers=headers)
            if response_dns.ok:
                response_dns_dict = json.loads(response_dns.text)[0]
                return response_dns_dict['dns_name']
            else:
                return None
        except:
            error_msg = exc_info()[0]
            logging.error(error_msg)
            return None

    def _get_dns(self, db_name):
        """
        This is a private function which is used by :func:`delete` mehtod.
        Returns the *dns name* which is needed in order to set the *db_name* and *alias* to *NULL* (deletion). If the given *database name* which is passed as an argument does not exist then it returns None. 

        :param db_name: the new database name which is given in the url
        :type db_name: str
        :raises: IndexError - when the database name does not exist
        :rtype: str or None

        """
        composed_url = self.url + '?db_name=eq.' + db_name + '&select=dns_name'
        response = requests.get(composed_url)
        if response.ok:
            try:
                dns_name_dict = json.loads(response.text)[0]
                return dns_name_dict['dns_name']
            except IndexError:
                self.set_status(BAD_REQUEST)
                return None
        else:
            self.set_status(SERVICE_UNAVAILABLE) 
            return None

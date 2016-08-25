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
from dbod.api.base import *
from dbod.config import config

class FunctionalAlias(tornado.web.RequestHandler):

    """This is the handler of **/instance/alias/<database name>** endpoint.

    The request methods implemented for this endpoint are

    * :func:`get`
    * :func:`post`
    * :func:`delete` 

    .. note::

      You need to provide a <*username*> and a <*password*> to use
      :func:`post` and :func:`delete` methods.
    """
    url = config.get('postgrest', 'functional_alias_url')

    def get(self, db_name, *args):

        """The *GET* method returns the database name's *alias* and *dns name*.
        (No any special headers for this request)

        :param db_name: the database name which is given in the url
        :type db_name: str
        :returns: json -- the response of the request
        :raises: HTTPError - when the requested database name does not exist
    
        .. http:get:: /api/v1/instance/alias/(db_name)

        **Example request**:
            
        ``curl -i http://<domain>:<port>/api/v1/instance/alias/dbod_42``

        .. sourcecode:: http

            GET /api/v1/instance/dbod_db42 HTTP/1.1
            Host: <domain>
            Accept: */*

        **Example response**:

        .. sourcecode:: http

           HTTP/1.1 200 OK
           Content-Type: application/json; charset=UTF-8
           Server: TornadoServer/4.2

            {
                "response": [{
                                "dns_name": dbod_dns42, 
                                "alias": dbod_alias42.cern.ch
                            }]
            }
        """
        logging.debug('Arguments:' + str(self.request.arguments))
        composed_url = self.url + '?db_name=eq.' + db_name + '&select=dns_name,alias'
        logging.info('Requesting ' + composed_url)
        response = requests.get(composed_url)
        data = response.json()
        if response.ok and data:
            logging.debug("response: " + json.dumps(data))
            self.write({'response' : data})
        elif response.ok:
            logging.warning("Functional alias not found for instance: " + db_name)
            raise tornado.web.HTTPError(NOT_FOUND)
        else:
            logging.error("Error fetching functional alias: " + response.text)
            raise tornado.web.HTTPError(response.status_code)

    @http_basic_auth
    def post(self, db_name, *args):

        """The *POST* method inserts a new *database name* and its *alias* into the database. It
        adds the functional alias association for an instance.

        The *dns name* is chosen automatically from a pool; so, in the background this method 
        actually updates the *database name* and *alias* fields, which were *NULL* in the 
        begining.

        .. note::

            This method is not successful

            * if the *database name* already exists
            * if there are no any *dns names* available
            * if the format of the *request body* is not right
            * if headers have to be specified
            * if the client does not have the right authorization header 
           
        :param db_name: the new database name which is given in the url
        :type db_name: str
        :raises: HTTPError - when the *url* or the *request body* format or the *headers* are not right
        :request body: alias=<alias> - the alias to be inserted for the given *database name* which is given in the *body* of the request

        .. http:post:: /api/v1/instance/alias/(db_name)

        **Example request**:
            
        ``curl -i -u <username> -d 'alias=alias42'  -X POST http://<domain>:<port>/api/v1/instance/alias/dbod_42``

        ``Enter host password for user '<username>':``

        .. sourcecode:: http

            POST /api/v1/instance/alias/dbod_42 HTTP/1.1    
            Host: <domain>
            Authorization: Basic <authorization hash>
            Accept: */*
            Content-Type: application/x-www-form-urlencoded

        **Example response**:

        .. sourcecode:: http

           HTTP/1.1 201 Created
           Content-Type: text/html; charset=UTF-8
        """

        def next_dnsname():
            """Returns the next dnsname which can be used for a newly created
        instance, if any"""
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

        logging.debug('Arguments:' + str(self.request.arguments))
        try:
            alias = self.get_argument('alias')
            logging.debug("alias: %s" % (alias))
            
            dns_name = next_dnsname()

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
        """The *DELETE* method deletes or else asssigns to *NULL* the *database name* and 
        *alias* fields. It removes the functional alias association for an instance.

        .. note::
            
            * If the *database name* doesn't exist it doesn't do anything
            * You have to be authorized to use this method
        
        :param db_name: the new database name which is given in the url
        :type db_name: str
        :raises: HTTPError - when the deletion is not successful
        
        .. http:delete:: /api/v1/instance/alias/(db_name)

        **Example request**:
        
        ``curl -i -u <username> -X DELETE http://<domain>:<port>/api/v1/instance/alias/dbod_42``

        ``Enter host password for user '<username>':``

        .. sourcecode:: http
            
            DELETE /api/v1/instance/alias/dbod_42 HTTP/1.1
            Host: <domain>
            Authorization: Basic <authorization hash>
            Accept: */*

        **Example response**:

        .. sourcecode:: http

           HTTP/1.1 204 Created
           Content-Type: text/html; charset=UTF-8
        """

        def get_dns(db_name):
            """Get the dns_name given the db_name"""
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

        logging.debug('Arguments:' + str(self.request.arguments))

        dns_name = get_dns(db_name)
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

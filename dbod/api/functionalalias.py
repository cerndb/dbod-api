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

import logging
import json
from ast import literal_eval
from sys import exc_info
import requests
import tornado.web
import tornado.escape
from dbod.api.base import NOT_FOUND, BAD_REQUEST
from dbod.config import config

class FunctionalAliasHandler(tornado.web.RequestHandler):
    '''The handler for the instance/alias/<endpoint>'''
    url = config.get('postgrest', 'functional_alias_url')
    if not url:
        logging.error("Internal instance/alias endpoint not configured")
        raise tornado.web.HTTPError(NOT_FOUND)

    def data_received(self, *arg, **kwargs):
        '''Abstract method which handles streamed request data.'''
        #No need for implementation
        pass

    def get(self, db_name, *args):
        '''Returns db_name's alias and dns name'''
        #self.set_header('Content-Type', 'application/json')
        
        logging.debug(args)
        logging.debug('Arguments:' + str(self.request.arguments))
        composed_url = self.url + '?db_name=eq.' + db_name + '&select=dns_name,alias'
        logging.debug('Requesting ' + composed_url)
        response = requests.get(composed_url)
        if response.ok:
            data = response.json()
            if data:
                self.write({'response' : data})
                self.set_status(response.status_code)
            else:
                logging.error("Functional alias not found")
                raise tornado.web.HTTPError(NOT_FOUND)
        else:
            logging.error("Error fetching functional alias of: " + db_name)
            raise tornado.web.HTTPError(response.status_code)


    def post(self, *args):
        '''Updates a row with db_name and the alias. The dns_name is already there.'''

        def next_dnsname():
            '''Returns the next dnsname which can be used for a newly created
        instance, if any'''
            
            #self.set_header('Content-Type', 'application/json')
            #LIMIT is not working in postgrest but it uses some headers for that as well
            headers = {'Range-Unit': 'items', 'Range': '0-0'}
            # select the next available dns_name with db_name and alias assigned to NULL
            query_select = '?select=dns_name&order=dns_name.asc&'
            query_filter = 'db_name=is.null&alias=is.null&dns_name=isnot.null'
            composed_url = self.url + query_select + query_filter
            try:
                response_dns = requests.get(composed_url, headers=headers)
                response_dns_dict = literal_eval(response_dns.text)[0]
                if response_dns.ok:
                    return response_dns_dict['dns_name']
                else:
                    return None
            except:
                error_msg = exc_info()[0]
                logging.error(error_msg)
                return None
            

        def check_if_exists(column, value):
            '''It checks if the inserted data already exists in the functional_aliases table'''
            query = '?%s=eq.%s&select=%s' %(column, value, column)
            composed_url = self.url + query
            response = requests.get(composed_url)
            if response.ok and literal_eval(response.text):
                logging.error("A(n) %s with the value of %s already exists in the functional_aliases table" %(column,value))
                return True
            else:
                
                return False
        #self.set_header("Content-Type", 'application/json')
        self.set_header('Prefer', 'return=representation')
        logging.debug(args)
        logging.debug('Arguments:' + str(self.request.arguments))
        try:
            functional_alias = json.loads(self.get_argument('functional_alias'))
            logging.debug(str(len(functional_alias)) + " Argument(s) given:")
            logging.debug(functional_alias)
        except:
            logging.error("Argument not recognized or not defined.")
            logging.error("Try adding header 'Content-Type:application/x-www-form-urlencoded'")
            logging.error("The right format should be: functional_alias={'<db_name>':'<alias>'}")
            raise tornado.web.HTTPError(NOT_FOUND)

        dns_name = next_dnsname()
        logging.info("dns_name picked: " + str(dns_name))

        if dns_name:
            logging.debug("dns_name picked: " + str(dns_name))
            headers = {'Prefer': 'return=representation'}
            db_name = str(functional_alias.keys()[0])
            alias = str(functional_alias.values()[0])
            insert_data = {"db_name": db_name, 
                           "alias": alias}
            logging.debug("Data to insert: " + str(insert_data))

            #if not check_if_exists('db_name', db_name) and  not check_if_exists('alias', alias):
            composed_url = self.url + '?dns_name=eq.' + dns_name
            logging.debug('Requesting insertion: ' + composed_url)
            
            response = requests.patch(composed_url, json=insert_data, headers=headers)
        
            if response.ok:
                data = response.json()
                #if data:
                logging.info('Success. Data inserted in the functional_aliases table:')
                logging.info(data)
                self.set_status(response.status_code)
                #else:
                #    logging.error("Empty data")
                #    raise tornado.web.HTTPError(response.status_code)  
            else:
                logging.error("Unsuccessful insertion")
                self.set_status(response.status_code)
                    
        else:
            logging.error("No dns_name available in the functional_aliases table")
            raise tornado.web.HTTPError(BAD_REQUEST)

    def delete(self, db_name, *args):
        '''Deletes or else asssigns to NULL the db_name and alias fields.'''
        """Removes the functional alias association for an instance.
           If the functional alias doesn't exist it doesn't do anything"""

        def get_dns(db_name):
            '''Get the dns_name given the db_name'''
            composed_url = self.url + '?db_name=eq.' + db_name + '&select=dns_name'
            response = requests.get(composed_url)
            if response.ok:
                try:
                    dns_name_dict = literal_eval(response.text)[0]
                    return dns_name_dict['dns_name']
                except IndexError:
                    return None
            else: 
                return None


        logging.debug(args)
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
                data = response.json()
                logging.info("Delete success of: " + str(data))
                self.set_status(response.status_code)
            else:
                logging.error("Unsuccessful deletion")
                raise tornado.web.HTTPError(response.status_code)

        else:
            logging.info("db_name not found. Nothing to do")
            self.set_status(BAD_REQUEST)

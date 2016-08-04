#!/usr/bin/env python
'''Testing functional alias endpoint'''
# -*- coding: utf-8 -*-

# Copyright (C) 2015, CERN
# This software is distributed under the terms of the GNU General Public
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as Intergovernmental Organization
# or submit itself to any jurisdiction.

import json
import unittest
from timeout_decorator import timeout
import tornado.web

from mock import patch
from mock import MagicMock
from tornado.testing import AsyncHTTPTestCase
import requests
from dbod.api.api import handlers

class FunctionalAliasTest(AsyncHTTPTestCase, unittest.TestCase):
    '''Class for testing functional alias with nosetest'''
    #headers = {'Content-Type': 'application/x-www-form-urlencoded', 
    #           'Prefer': 'return=representation',
    #           'Accept': 'text/json'}
    db_name_test = "dbod_42"
    alias_test = "dbod-dbod-42.cern.ch"

    def get_app(self):
        print 'Getting the app'
        return tornado.web.Application(handlers)

    @timeout(5)
    def test_get_single_alias_by_name(self):
        '''test for getting the right data'''
        print 'test_get_single_alias_by_name'
        db_name = 'dbod_01'
        response = self.fetch("/api/v1/instance/alias/%s" %(db_name))
        data = json.loads(response.body)["response"]
        self.assertEquals(response.code, 200)
        #self.assertEquals(json.loads(response.headers)['Content-Type'], 'application/json')
        self.assertEquals(len(data), 1)
        self.assertEquals(data[0]["alias"], "dbod-dbod-01.cern.ch")
        self.assertTrue(data[0]["dns_name"] != None)
        self.assertEquals(response.headers['Content-Type'], 'application/json; charset=UTF-8')

    @timeout(5)
    def test_get_invalid_dbname(self):
        '''test when the db_name does not exist'''
        print 'test_get_invalid_dbname'
        response = self.fetch("/api/v1/instance/alias/%s" %(self.db_name_test))
        data = response.body
        self.assertEquals(response.code, 404)
        self.assertEquals(len(data), 69)
        self.assertEquals(response.headers['Content-Type'], 'text/html; charset=UTF-8')

    @timeout(5)
    @patch('dbod.api.functionalalias.requests.get')
    def test_get_bad_response(self, mock_get):
        '''test when the get response code is not 200. Server/api error'''
        print 'test_get_bad_response'
        status_code_test = 503
        mock_get.return_value = MagicMock(spec=requests.models.Response, 
                                          ok=False,
                                          status_code=status_code_test)
        db_name = 'dbod_01'
        response = self.fetch("/api/v1/instance/alias/%s" %(db_name))
        self.assertEquals(response.code, status_code_test)
        self.assertEquals(response.headers['Content-Type'], 'text/html; charset=UTF-8')

    @timeout(5)
    def test_novalid_db(self):
        '''test when the given db does not exist'''
        print 'test_novalid_db'
        response = self.fetch("/api/v1/instance/alias/some_db")
        self.assertEquals(response.code, 404)


    @timeout(5)
    def test_post_valid_request(self):
        '''test when the arguments are valid and dns_name is available'''
        print 'test_post_valid_request'
        body = 'functional_alias={"%s": "%s"}' %(self.db_name_test, self.alias_test)
        response = self.fetch("/api/v1/instance/alias/", 
                              method="POST", 
                              body=body)  
        self.assertEquals(response.code, 200)
        # confirm you get back the right data
        response = self.fetch("/api/v1/instance/alias/%s" %(self.db_name_test))
        data = json.loads(response.body)["response"]
        self.assertEquals(len(data), 1)
        self.assertEquals(data[0]["alias"], self.alias_test)
        self.assertTrue(data[0]["dns_name"] != None)
        # delete what has been created
        self.fetch("/api/v1/instance/alias/%s" %(self.db_name_test), 
                   method="DELETE")

    @timeout(5)
    def test_post_duplicate(self):
        '''test when there is a request to insert a db_name which already exists'''
        print 'test_post_duplicate'
        body = 'functional_alias={"dbod_01": "dbod-dbod-01.cern.ch"}'
        response = self.fetch("/api/v1/instance/alias/", 
                              method="POST", 
                              body=body)
        self.assertEquals(response.code, 409)    

    @timeout(5)
    def test_post_no_dns(self):
        '''test when there are no any dns available'''
        print 'test_post_no_dns'
        body = 'functional_alias={"%s": "%s"}' %(self.db_name_test, self.alias_test)
        self.fetch("/api/v1/instance/alias/", 
                   method="POST", 
                   body=body)
        body = 'functional_alias={"%s": "%s"}' %(self.db_name_test, self.alias_test)
        response = self.fetch("/api/v1/instance/alias/", 
                              method="POST", 
                              body=body)
        self.assertEquals(response.code, 400)
        # delete what has been created
        self.fetch("/api/v1/instance/alias/%s" %(self.db_name_test), 
                   method="DELETE")

    @timeout(5)
    def test_post_no_valid_argument(self):
        '''test if the provided argument is valid'''
        print 'test_post_no_valid_argument'
        body = 'something={"%s": "%s"}' %(self.db_name_test, self.alias_test)
        response = self.fetch("/api/v1/instance/alias/", 
                              method="POST", 
                              body=body)
        self.assertEquals(response.code, 404)

    @timeout(5)
    def test_post_bad_argument(self):
        '''test if the provided argument is valid'''
        print 'test_post_bad_argument'
        body = 'functional_alias={%s: %s}' %(self.db_name_test, self.alias_test)
        response = self.fetch("/api/v1/instance/alias/", 
                              method="POST", 
                              body=body)
        self.assertEquals(response.code, 404)
    
    @timeout(5)
    @patch('dbod.api.functionalalias.requests.get')
    def test_post_nextdns_failure(self, mock_get):
        '''test when there is a server error when getting an available dns_name'''
        status_code_test = 503
        mock_get.return_value = MagicMock(spec=requests.models.Response, 
                                          ok=False,
                                          status_code=status_code_test)
        
        body = 'functional_alias={"%s": "%s"}' %(self.db_name_test, self.alias_test)
        response = self.fetch("/api/v1/instance/alias/", 
                              method="POST", 
                              body=body)  
        # tornado will still raise a Bad Request -- to be improved 
        self.assertEquals(response.code, 400)
        # delete what has maybe been created
        self.fetch("/api/v1/instance/alias/%s" %(self.db_name_test), 
                   method="DELETE")   

    @timeout(5)
    def test_delete_valid_request(self):
        '''test when there is a valid request to delete a previous inserted db_name'''
        print 'test_delete_valid_request'
        # create entity to be deleted
        body = 'functional_alias={"%s": "%s"}' %(self.db_name_test, self.alias_test)
        response = self.fetch("/api/v1/instance/alias/", 
                              method="POST", 
                              body=body)
        response = self.fetch("/api/v1/instance/alias/%s" %(self.db_name_test), 
                              method="DELETE")
        self.assertEquals(response.code, 200)


    def test_delete_invalid_dbname(self):
        '''test when the given db_name to be deleted does not exist'''
        print 'test_delete_invalid_dbname'
        response = self.fetch("/api/v1/instance/alias/%s" %(self.db_name_test), 
                              method="DELETE")
        self.assertEquals(response.code, 400)

    @timeout(5)
    @patch('dbod.api.functionalalias.requests.get')
    def test_delete_getdns_failure(self, mock_get):
        '''test an unsuccessful get of the dns_name'''
        print 'test_delete_getdns_failure'
        status_code_test = 503
        mock_get.return_value = MagicMock(spec=requests.models.Response,
                                          ok=False,
                                          status_code=status_code_test)
        response = self.fetch("/api/v1/instance/alias/%s" %('dbod_01'),
                              method="DELETE")
        # tornado will still give Bad Request error message -- to be improved
        self.assertEquals(response.code, 400)

    @timeout(5)
    @patch('dbod.api.functionalalias.requests.patch')
    def test_delete_nosuccess_delete(self, mock_get):
        '''test an unsuccessful deletion'''
        print 'test_delete_nosuccess_delete'
        status_code_test = 503
        mock_get.return_value = MagicMock(spec=requests.models.Response,
                                          ok=False,
                                          status_code=status_code_test) 
        response = self.fetch("/api/v1/instance/alias/%s" %('dbod_01'),
                              method="DELETE")
        self.assertEquals(response.code, status_code_test)


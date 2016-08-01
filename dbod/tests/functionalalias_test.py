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
from timeout_decorator import timeout
import tornado.web

from tornado.testing import AsyncHTTPTestCase

from dbod.api.api import handlers

class FunctionalAliasTest(AsyncHTTPTestCase):
    '''Class for testing functional alias with nosetest'''
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 
               'Prefer': 'return=representation',
               'Accept': 'text/json'}

    def get_app(self):
        return tornado.web.Application(handlers)

    @timeout(5)
    def test_get_single_alias_by_name(self):
        '''test for getting the right data'''
        db_name_test = 'dbod_01'
        response = self.fetch("/api/v1/entity/alias/%s" %(db_name_test))
        data = json.loads(response.body)["response"]
        self.assertEquals(response.code, 200)
        self.assertEquals(len(data), 1)
        self.assertEquals(data[0]["alias"], "dbod-dbod-01.cern.ch")
        self.assertTrue(data[0]["dns_name"] != None)

    @timeout(5)
    def test_novalid_db(self):
        '''test when the given db does not exist'''
        response = self.fetch("/api/v1/entity/alias/some_db")
        self.assertEquals(response.code, 404)

    @timeout(5)
    def test_invalid_endpoint(self):
        '''test when the given endpoint does not exist'''
        response = self.fetch("/api/v1/entity/something/some_db")
        self.assertEquals(response.code, 404)


    @timeout(5)
    def test_post_valid_request(self):
        '''test when the arguments are valid and dns_name is available'''
        body = 'functional_alias={"dbod_42": "dbod-dbod-42.cern.ch"}'
        response = self.fetch("/api/v1/entity/alias/", 
                              method="POST", 
                              body=body, 
                              headers=self.headers)
        self.assertEquals(response.code, 200)
        self.fetch("/api/v1/entity/alias/dbod_42", 
                   method="DELETE")

    @timeout(5)
    def test_post_duplicate(self):
        '''test when there is a request to insert a db_name which already exists'''
        body = 'functional_alias={"dbod_01": "dbod-dbod-01.cern.ch"}'
        response = self.fetch("/api/v1/entity/alias/", 
                              method="POST", 
                              body=body, 
                              headers=self.headers)
        self.assertEquals(response.code, 409)    

    @timeout(5)
    def test_post_no_dns(self):
        '''test when there are no any dns available'''
        body = 'functional_alias={"dbod_42": "dbod-dbod-42.cern.ch"}'
        self.fetch("/api/v1/entity/alias/", 
                   method="POST", 
                   body=body, 
                   headers=self.headers)
        body = 'functional_alias={"dbod_42": "dbod-dbod-42.cern.ch"}'
        response = self.fetch("/api/v1/entity/alias/", 
                              method="POST", 
                              body=body, 
                              headers=self.headers)
        self.assertEquals(response.code, 400)
        self.fetch("/api/v1/entity/alias/dbod_42", 
                   method="DELETE")

    @timeout(5)
    def test_post_no_valid_argument(self):
        ''' test if the provided argument is valid'''
        body = 'something={"dbod_42": "dbod-dbod-42.cern.ch"}'
        response = self.fetch("/api/v1/entity/alias/", 
                              method="POST", 
                              body=body, 
                              headers=self.headers)
        self.assertEquals(response.code, 404)

    @timeout(5)
    def test_post_no_valid_headers(self):
        ''' test if the provided argument is valid'''
        body = 'something={"dbod_42": "dbod-dbod-42.cern.ch"}'
        response = self.fetch("/api/v1/entity/alias/", 
                              method="POST", 
                              body=body)
        self.assertEquals(response.code, 404)

    def test_post_bad_argument(self):
        ''' test if the provided argument is valid'''
        body = 'functional_alias={dbod_42: dbod-dbod-42.cern.ch}'
        response = self.fetch("/api/v1/entity/alias/", 
                              method="POST", 
                              body=body, 
                              headers=self.headers)
        self.assertEquals(response.code, 404)

    @timeout(5)
    def test_delete_valid_request(self):
        '''test when there is a valid request to delete a previous inserted db_name'''
        body = 'functional_alias={"dbod_42": "dbod-dbod-42.cern.ch"}'
        response = self.fetch("/api/v1/entity/alias/", 
                              method="POST", 
                              body=body, 
                              headers=self.headers)
        response = self.fetch("/api/v1/entity/alias/dbod_42", 
                              method="DELETE")
        self.assertEquals(response.code, 200)


    def test_delete_invalid_dbname(self):
        '''test when the given db_name does not exist'''
        response = self.fetch("/api/v1/entity/alias/dbod_42", 
                              method="DELETE")
        self.assertEquals(response.code, 400)

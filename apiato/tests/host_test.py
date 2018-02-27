# Copyright (C) 2015, CERN
# This software is distributed under the terms of the GNU General Public
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as Intergovernmental Organization
# or submit itself to any jurisdiction.

import unittest
from types import *
import json
import logging
import sys
import requests

import base64
import tornado.web

from mock import patch
from mock import MagicMock
from tornado.testing import AsyncHTTPTestCase
from timeout_decorator import timeout

from apiato.api.api import handlers
from apiato.config import config
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

class HostTest(AsyncHTTPTestCase, unittest.TestCase):
    """Class for testing Host endpoint with nosetest"""
    
    authentication = "basic " + \
                     base64.b64encode(config.get('api', 'user') + \
                     ":" + config.get('api', 'pass'))

    def get_app(self):
        return tornado.web.Application(handlers)

    @timeout(5)
    @patch('apiato.api.host.requests.get')
    @patch('apiato.api.host.json.dumps')
    @patch('apiato.api.host.Host.write')
    def test_get_valid_name(self, mock_write, mock_json, mock_get):
        """ test a successful get method with a valid given name"""
        print "test_get_valid_name"
        status_code_test = 200
        response_output = [{u'memory': 512}]
        mock_get.return_value = MagicMock(spec=requests.models.Response,
                                          ok=True,
                                          status_code=status_code_test,
                                          content=response_output)
        #mock_get.json.return_value.content = response_output
        #mock_json.return_value = MagicMock(content=[{"memory": 512}])
        response = self.fetch("/api/v1/host/names/host42")
        self.assertEquals(response.code, status_code_test)
    
    def empty_json(*args,**kwargs):
        class MockResponse:
            
            def __init__(self, ok, status_code, json_data):
                self.status_code_test = status_code
                self.ok = ok
                self.json_data = json_data

            def json(self):
                return self.json_data
        return MockResponse(True,200,[])


    @timeout(5)
    @patch('apiato.api.host.requests.get', side_effect=empty_json)
    def test_get_empty(self, mock_get):
        """test when the response of the request is empty"""
        print "test_get_empty"

        response = self.fetch("/api/v1/host/names/host42")
        self.assertEquals(response.code, 404)
    
    @timeout(5)
    @patch('apiato.api.host.requests.get')
    def test_get_notexist(self, mock_get):
        """test when the given name does not exist"""
        print "test_get_notexist"
        
        status_code_test_error = 502
        response_output = [{u'memory': 512}]
        mock_get.return_value = MagicMock(spec=requests.models.Response,
                                          ok=False,
                                          status_code=status_code_test_error,
                                          content=response_output)
        response = self.fetch("/api/v1/host/names/host42")
        self.assertEquals(response.code, status_code_test_error)
    
    @timeout(5)
    @patch('apiato.api.host.requests.post')
    def test_post_valid(self, mock_post):
        """test when the post request is valid"""
        print "test_post_valid"

        status_code_test = 201
        memory_test = '512'
        body_test = 'memory=' + memory_test
        mock_post.return_value = MagicMock(spec=requests.models.Response,
                                          ok=True,
                                          status_code=status_code_test)

        response = self.fetch("/api/v1/host/names/host42", 
                              method="POST", 
                              headers={'Authorization': self.authentication},
                              body=body_test)  
        self.assertEquals(response.code, status_code_test)
   
    @timeout(5)
    @patch('apiato.api.host.requests.post')
    def test_post_duplicate(self, mock_post):
        """test when the post request tries to insert a duplicate entry"""
        print "test_post_duplicate"

        status_code_test_error = 409
        memory_test = '512'
        body_test = 'memory=' + memory_test
        mock_post.return_value = MagicMock(spec=requests.models.Response,
                                          ok=False,
                                          status_code=status_code_test_error)

        response = self.fetch("/api/v1/host/names/host42", 
                              method="POST", 
                              headers={'Authorization': self.authentication},
                              body=body_test)  
        self.assertEquals(response.code, status_code_test_error)

    @timeout(5)
    @patch('apiato.api.host.requests.post')
    def test_post_wrongargument(self, mock_post):
        """test when the argument in the body of post request is wrong"""
        print "test_post_duplicate"

        status_code_test_error = 400
        memory_test = '512'
        body_test = 'something=' + memory_test
        mock_post.return_value = MagicMock(spec=requests.models.Response,
                                           status_code=status_code_test_error)

        response = self.fetch("/api/v1/host/names/host42", 
                              method="POST", 
                              headers={'Authorization': self.authentication},
                              body=body_test)  
        self.assertEquals(response.code, status_code_test_error)
    
    @timeout(5)
    @patch('apiato.api.host.requests.post')
    def test_post_badargument(self, mock_post):
        """test when the value of the argument of post request is string"""
        print "test_post_badargument"

        status_code_test_error = 400
        memory_test = 'forty-two'
        body_test = 'memory=' + memory_test
        mock_post.return_value = MagicMock(spec=requests.models.Response,
                                           status_code=status_code_test_error)

        response = self.fetch("/api/v1/host/names/host42", 
                              method="POST", 
                              headers={'Authorization': self.authentication},
                              body=body_test)  
        self.assertEquals(response.code, status_code_test_error)

    @timeout(5)
    @patch('apiato.api.host.requests.patch')
    def test_put_valid(self, mock_patch):
        """test when the put request is valid"""
        print "test_put_valid"

        status_code_test = 200
        memory_test = '42'
        body_test = 'memory=' + memory_test
        mock_patch.return_value = MagicMock(spec=requests.models.Response,
                                          ok=True,
                                          status_code=status_code_test)

        response = self.fetch("/api/v1/host/names/host42", 
                              method="PUT", 
                              headers={'Authorization': self.authentication,
                                       'Content-Type': 'application/x-www-form-urlencoded'},
                              body=body_test)  
        self.assertEquals(response.code, status_code_test)

    @timeout(5)
    @patch('apiato.api.host.requests.patch')
    def test_put_notexist(self, mock_patch):
        """test when the name to update with put request does not exist"""
        print "test_put_notexist"

        status_code_test_error = 404
        memory_test = '512'
        body_test = 'memory=' + memory_test
        mock_patch.return_value = MagicMock(spec=requests.models.Response,
                                          ok=False,
                                          status_code=status_code_test_error)

        response = self.fetch("/api/v1/host/names/host42", 
                              method="PUT", 
                              headers={'Authorization': self.authentication,
                                       'Content-Type': 'application/x-www-form-urlencoded'},
                              body=body_test)  
        self.assertEquals(response.code, status_code_test_error)


    @timeout(5)
    @patch('apiato.api.host.requests.patch')
    def test_put_wrongargument(self, mock_patch):
        """test when the argument in the body of put request is wrong"""
        print "test_put_wrongargument"

        status_code_test_error = 400
        memory_test = '42'
        body_test = 'something=' + memory_test
        mock_patch.return_value = MagicMock(spec=requests.models.Response,
                                          status_code=status_code_test_error)

        response = self.fetch("/api/v1/host/names/host42", 
                              method="PUT", 
                              headers={'Authorization': self.authentication,
                                       'Content-Type': 'application/x-www-form-urlencoded'},
                              body=body_test)  
        self.assertEquals(response.code, status_code_test_error)
    
    @timeout(5)
    @patch('apiato.api.host.requests.patch')
    def test_put_badargument(self, mock_patch):
        """test when the value of the argument of put request is string"""
        print "test_put_badargument"

        status_code_test_error = 400
        memory_test = 'forty-two'
        body_test = 'memory=' + memory_test
        mock_patch.return_value = MagicMock(spec=requests.models.Response,
                                          status_code=status_code_test_error)

        response = self.fetch("/api/v1/host/names/host42", 
                              method="PUT", 
                              headers={'Authorization': self.authentication,
                                       'Content-Type': 'application/x-www-form-urlencoded'},
                              body=body_test)  
        self.assertEquals(response.code, status_code_test_error)
    
    @timeout(5)
    @patch('apiato.api.host.requests.delete')
    def test_delete_valid(self, mock_delete):
        """test when the delete request is valid"""
        print "test_delete_valid"

        status_code_test = 204
        memory_test = '512'
        body_test = 'memory=' + memory_test
        mock_delete.return_value = MagicMock(spec=requests.models.Response,
                                             ok=True,
                                             status_code=status_code_test)

        response = self.fetch("/api/v1/host/names/host42", 
                              method="DELETE", 
                              headers={'Authorization': self.authentication})  
        self.assertEquals(response.code, status_code_test)

    @timeout(5)
    @patch('apiato.api.host.requests.delete')
    def test_delete_notexist(self, mock_delete):
        """test when the name to delete with delete request does not exist"""
        print "test_delete_notexist"

        status_code_test_error = 404
        memory_test = '512'
        body_test = 'memory=' + memory_test
        mock_delete.return_value = MagicMock(spec=requests.models.Response,
                                          ok=False,
                                          status_code=status_code_test_error)

        response = self.fetch("/api/v1/host/names/host42", 
                              method="DELETE", 
                              headers={'Authorization': self.authentication})
        self.assertEquals(response.code, status_code_test_error)


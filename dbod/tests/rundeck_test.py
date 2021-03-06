# Copyright (C) 2015, CERN
# This software is distributed under the terms of the GNU General Public
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as Intergovernmental Organization
# or submit itself to any jurisdiction.

import unittest
import logging

import base64
import tornado.web
import requests

from sys import stdout
from mock import patch
from mock import MagicMock
from tornado.testing import AsyncHTTPTestCase
from timeout_decorator import timeout

from dbod.api.api import handlers
from dbod.config import config
logging.basicConfig(stream=stdout, level=logging.DEBUG)

class RundeckTest(AsyncHTTPTestCase, unittest.TestCase):
    """Class for testing Rundeck execution with nosetest"""
    
    authentication = "basic " + \
                     base64.b64encode(config.get('api', 'user') + \
                     ":" + config.get('api', 'pass'))

    def get_app(self):
        return tornado.web.Application(handlers)

    @patch('dbod.api.rundeck.requests.get')
    def test_get_success(self, mock_get):
        """test when get method is successful"""
        print "test_get_success"
        status_code_test = 200
        response_text = '[{"db_name":"dbod42","hostname":"dbod42.cern.ch","port":"5500","username":"dbod","db_type":"MYSQL","category":"TEST","tags":"MYSQL,TEST"}, \
        {"db_name":"dbod24","hostname":"dbod24.cern.ch","port":"6603","username":"dbod","db_type":"PG","category":"PROD","tags":"PG,PROD"}]'

        mock_get.return_value = MagicMock(spec=requests.models.Response,
                                          ok=True,
                                          status_code=status_code_test,
                                          text=response_text)

        response = self.fetch("/api/v1/rundeck/resources.xml")
        
        self.assertEquals(response.code, 200)

    @patch('dbod.api.rundeck.requests.get')
    def test_get_nosuccess(self, mock_get):
        """test when get method is not successful """
        print "test_get_nosuccess"
        status_code_test_error = 502

        mock_get.return_value = MagicMock(spec=requests.models.Response,
                                          ok=False,
                                          status_code=status_code_test_error)

        response = self.fetch("/api/v1/rundeck/resources.xml")
        self.assertEquals(response.code, 404)
    
    @timeout(10)
    @patch('dbod.api.rundeck.requests.get')
    @patch('dbod.api.rundeck.requests.post')
    def test_post_job_success(self, mock_post, mock_get):
        """test an execution of a registered job of an existing instance"""
        print "test_post_existing_instance"
        status_code_test = 200
        response_output_running = '{"execCompleted": false, "execState": "running"}'
        response_output_success = '{"execCompleted": true, "execState": "succeeded", "log": "[snapscript_24,snapscript_42]"}'
        response_run = '{"id":42}'

        mock_get.side_effect = [MagicMock(spec=requests.models.Response,
                                           ok=True,
                                           status_code=status_code_test,
                                           text=response_output_running),
                                MagicMock(spec=requests.models.Response,
                                           ok=True,
                                           status_code=status_code_test,
                                           text=response_output_success)]
        mock_post.return_value = MagicMock(spec=requests.models.Response,
                                           ok=True,
                                           status_code=status_code_test,
                                           text=response_run)

        response = self.fetch("/api/v1/rundeck/job/get-snapshots/instance42",
                             method="POST",
                             headers={'Authorization': self.authentication},
                             body='')
        self.assertEquals(response.code, 200)
        
    @patch('dbod.api.rundeck.requests.get')
    @patch('dbod.api.rundeck.requests.post')
    def test_post_job_nosuccess(self, mock_post, mock_get):
        """test when the job execution is not successful"""
        print "test_post_job_nosuccess"
        status_code_test = 200
        response_run = '{"id":42}'
        response_output = '{"execCompleted": true, "execState": "failed", "log": "[snapscript_24,snapscript_42]"}'

        mock_get.return_value = MagicMock(spec=requests.models.Response,
                                           ok=True,
                                           status_code=status_code_test,
                                           text=response_output)
        mock_post.return_value = MagicMock(spec=requests.models.Response,
                                          ok=True,
                                          status_code=status_code_test,
                                          text=response_run)
        
        response = self.fetch("/api/v1/rundeck/job/get-snapshots/instance42",
                               method="POST",
                               headers={'Authorization': self.authentication},
                               body='')
        self.assertEquals(response.code, 502)
    
    @patch('dbod.api.rundeck.requests.get')
    @patch('dbod.api.rundeck.requests.post')
    def test_post_jobstatus_error(self, mock_post, mock_get):
        """test when the the get request of the job from rundeck status is not successful"""
        print "test_post_jobstatus_error"
        status_code_test = 200
        status_code_test_error = 500
        response_run = '{"id":42}'
        response_output = '{"execCompleted": true, "execState": "succeeded", "log": "[snapscript_24,snapscript_42]"}'

        mock_get.return_value = MagicMock(spec=requests.models.Response,
                                          ok=False,
                                          status_code=status_code_test_error,
                                          text=response_output)
        mock_post.return_value = MagicMock(spec=requests.models.Response,
                                           ok=True,
                                           status_code=status_code_test,
                                           text=response_run)
        
        response = self.fetch("/api/v1/rundeck/job/get-snapshots/instance42",
                               method="POST",
                               headers={'Authorization': self.authentication},
                               body='')
        self.assertEquals(response.code, status_code_test_error)

    @patch('dbod.api.rundeck.requests.get')
    @patch('dbod.api.rundeck.requests.post')
    def test_post_jobrun_error(self, mock_post, mock_get):
        """test when the the post request of the job to rundeck is not successful"""
        print "test_post_jobrun_error"
        status_code_test = 200
        status_code_test_error = 400
        response_run = '{"id":42}'

        mock_get.return_value = MagicMock(spec=requests.models.Response,
                                          status_code=status_code_test)
        mock_post.return_value = MagicMock(spec=requests.models.Response,
                                           ok=False,
                                           status_code=status_code_test_error,
                                           text=response_run)
        
        response = self.fetch("/api/v1/rundeck/job/get-snapshots/instance42",
                               method="POST",
                               headers={'Authorization': self.authentication},
                               body='')

        self.assertEquals(response.code, status_code_test_error)   
 

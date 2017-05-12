#!/usr/bin/env python
"""Testing Kubernetes Clusters endpoint"""
# -*- coding: utf-8 -*-

# Copyright (C) 2015, CERN
# This software is distributed under the terms of the GNU General Public
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as Intergovernmental Organization
# or submit itself to any jurisdiction.

import json
import unittest
import base64
import requests
import tornado.web

from mock import patch
from mock import MagicMock
from tornado.testing import AsyncHTTPTestCase
from timeout_decorator import timeout

from dbod.api.api import handlers
from dbod.config import config

class KubernetesClustersTest(AsyncHTTPTestCase, unittest.TestCase):

    authentication = "basic " + \
                     base64.b64encode(config.get('api', 'user') + \
                     ":" + config.get('api', 'pass'))

    testJson = {
      "kind": "Deployment",
      "spec": {
	"template": {
	  "spec": {
	    "containers": [
	      {
		"image": "jaysot/mysql",
		"imagePullPolicy": "Always",
		"volumeMounts": [
		  {
		    "mountPath": "/ORA/dbs03/TEST",
		    "name": "volume-data"
		  },
		  {
		    "mountPath": "/ORA/dbs02/TEST",
		    "name": "volume-bin"
		  },
		  {
		    "mountPath": "/docker-entrypoint-initdb.d",
		    "name": "secret-init"
		  },
		  {
		    "mountPath": "/etc/mysql/conf.d",
		    "name": "secret-conf"
		  }
		],
		"ports": [
		  {
		    "containerPort": 5500,
		    "name": "p0"
		  }
		],
		"name": "mysql-contenador"
	      }
	    ],
	    "volumes": [
	      {
		"cinder": {
		  "volumeID": "7f50317e-9e5d-453b-889b-2d82c0340dcc" ,
		  "fsType": "ext4"
		},
		"name": "volume-data"
	      },
	      {
		"cinder": {
		  "volumeID": "6c40f35a-1cbc-4133-b0f3-f76160ffecdf",
		  "fsType": "ext4"
		},
		"name": "volume-bin"
	      },
	      {
		"secret": {
		  "secretName": "init-test"
		},
		"name": "secret-init"
	      },
	      {
		"secret": {
		  "secretName": "mysql-conf"
		},
		"name": "secret-conf"
	      }
	    ]
	  },
	  "metadata": {
	    "labels": {
	      "app": "test-app"
	    }
	  }
	},
	"replicas": 1
      },
      "apiVersion": "extensions/v1beta1",
      "metadata": {
	"name": "test-depl"
      }
    }

    headers = {'X-Subject-Token':'Token'}
    gfunc_return = ({'api_address': 'kube_base_url', 'projects':[{'id':'projID', 'name':'projName'}], 'volumes':[{'name':'sth'}]},200)
    return_data = [{u'KubeData': 'KubeConf'}]
    blistdir = ['config', 'ca.pem', 'key.pem', 'cert.pem']
    app_type = 'mysql'
    app_name = 'mysqltest1'
    klistdir1 = ['init.sql', 'templates']
    klistdir2 = [app_type + '-cnf.template', app_type + '-depl.json.template',
                 app_type + '-secret.json.template', app_type + '-secret.yaml.template',
                 app_type + '-svc.json.template']

    def get_app(self):
        return tornado.web.Application(handlers)

    @patch('dbod.api.kubernetes.KubernetesClusters.write')
    @patch('dbod.api.kubernetes.json.dumps')
    @patch('dbod.api.kubernetes.requests.get')
    @patch('dbod.api.kubernetes.get_function')
    @patch('dbod.api.base.requests.post')
    @patch('dbod.api.base.check_output', return_value='valid run')
    def test_get_clusters(self, mock_cmd, mock_post, mock_gfunc, mock_get, mock_json, mock_write):
        print 'test_get_clusters'
        test_status_code = 200
        #mock_listdir.return_value = self.blistdir
        mock_post.return_value = MagicMock(spec=requests.models.Response,
                                           ok=True,
                                           headers=self.headers
                                           )
        mock_gfunc.return_value = self.gfunc_return
        mock_get.return_value = MagicMock(spec=requests.models.Response,
                                          ok=True,
                                          status_code=test_status_code,
                                          content=self.return_data
                                          )
        response = self.fetch("/api/v1/beta/kubernetes/k8s-test2/namespaces/default/deployments/" + self.app_name, method="GET")
        self.assertEquals(response.code, test_status_code)

    @patch('dbod.api.kubernetes.KubernetesClusters.write')
    @patch('dbod.api.kubernetes.json.dumps')
    @patch('dbod.api.kubernetes.requests.post')
    @patch('dbod.api.kubernetes.KubernetesClusters.postjson', side_effect=['','','id1','id2'])
    @patch('dbod.api.kubernetes.KubernetesClusters.check_ifexists', side_effect=[False, False])
    @patch('dbod.api.kubernetes.get_function')
    @patch('dbod.api.base.requests.post')
    @patch('dbod.api.base.check_output', return_value='valid run')
    def test_post_clusters(self, mock_cmd, mock_bpost, mock_gfunc, mock_check, mock_postjson, mock_kpost, mock_json, mock_write):
        print 'test_post_clusters'
        body=json.dumps(self.testJson)
        #mock_blistdir.return_value = self.blistdir
        mock_bpost.return_value = MagicMock(spec=requests.models.Response,
                                           ok=True,
                                           headers=self.headers
                                           )
        mock_gfunc.return_value = self.gfunc_return
        mock_bpost.return_value = MagicMock(spec=requests.models.Response,
                                           ok=True,
                                           status_code=200,
                                           content=self.return_data
                                           )
        #mock_kpath.isdir.side_effect = [True, True, False]
        #mock_klistdir.side_effect = [self.klistdir1, self.klistdir2]

        response = self.fetch("/api/v1/kubernetes/k8s-test/namespaces/default/deployments?app_type=" +
                               self.app_type + "&vol_type=cinder&app_name=" + self.app_name,
                               method="POST",
                               headers={'Authorization': self.authentication},
                               body=str(body))
        self.assertEquals(response.code, 200)

    '''
    def test_delete_clusters(self):
        response = self.fetch("/api/v1/beta/kubernetes/k8s-test/namespaces/default/deployments/mysql-depl",
                              method="DELETE",
                              headers={'Authorization': self.authentication})
        print response.body, response.code
    '''



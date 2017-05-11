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


    def get_app(self):
        return tornado.web.Application(handlers)

    @patch('dbod.api.kubernetes.KubernetesClusters.write')
    @patch('dbod.api.kubernetes.json.dumps')
    @patch('dbod.api.kubernetes.requests.get')
    @patch('dbod.api.kubernetes.get_function')
    @patch('dbod.api.base.requests.post')
    @patch('dbod.api.base.check_output', return_value='valid run')
    @patch('dbod.api.base.mkdir', return_value=True)
    @patch('dbod.api.base.listdir')
    @patch('dbod.api.base.path', return_value=True)
    @patch('dbod.api.base.json.load')
    @patch('dbod.api.base.open')
    def test_get_clusters(self, mock_open, mock_load, mock_path, mock_listdir, mock_mdir, mock_cmd, mock_post, mock_gfunc, mock_get, mock_json, mock_write):
        print 'test_get_clusters'
        mock_listdir.return_value = ['config', 'ca.pem', 'key.pem', 'cert.pem']
        mock_post.return_value = MagicMock(spec=requests.models.Response,
                                           ok=True,
                                           headers={'X-Subject-Token':'Token'}
                                           )
        mock_gfunc.return_value = {'api_address': 'kube_base_url'},200
        mock_get.return_value = MagicMock(spec=requests.models.Response,
                                          ok=True,
                                          status_code=200,
                                          content=[{u'KubeData': 'KubeConf'}]
                                          )
        response = self.fetch("/api/v1/beta/kubernetes/k8s-test2/namespaces/default/deployments/mysql-depl", method="GET")
        self.assertEquals(response.code, 200)

    @patch('dbod.api.kubernetes.KubernetesClusters.write')
    @patch('dbod.api.kubernetes.json.dumps')
    @patch('dbod.api.kubernetes.requests.post')
    @patch('dbod.api.kubernetes.KubernetesClusters.postjson', side_effect=['','','id1','id2'])
    @patch('dbod.api.kubernetes.KubernetesClusters.check_ifexists', side_effect=[False, False])
    @patch('dbod.api.kubernetes.KubernetesClusters.template_write')
    @patch('dbod.api.kubernetes.mkdir', return_value=True)
    @patch('dbod.api.kubernetes.path', return_value=False)
    @patch('dbod.api.kubernetes.get_function')
    @patch('dbod.api.base.requests.post')
    @patch('dbod.api.base.check_output', return_value='valid run')
    @patch('dbod.api.base.mkdir', return_value=True)
    @patch('dbod.api.base.listdir')
    @patch('dbod.api.base.path', return_value=True)
    @patch('dbod.api.base.json.load')
    @patch('dbod.api.base.open')
    def test_post_clusters(self, mock_open, mock_load, mock_bpath, mock_listdir, mock_bmdir, mock_cmd, mock_bpost, mock_gfunc, mock_kpath, mock_kmdir, mock_templwrite, mock_check, mock_postjson, mock_kpost, mock_json, mock_write):
        body=json.dumps(self.testJson)
        mock_listdir.return_value = ['config', 'ca.pem', 'key.pem', 'cert.pem']
        mock_bpost.return_value = MagicMock(spec=requests.models.Response,
                                           ok=True,
                                           headers={'X-Subject-Token':'Token'}
                                           )
        mock_gfunc.return_value = {'api_address': 'kube_base_url', 'projects':[{'id':'projID', 'name':'projName'}], 'volumes':[{'name':'sth'}]},200
        mock_bpost.return_value = MagicMock(spec=requests.models.Response,
                                           ok=True,
                                           status_code=200,
                                           content=[{u'KubeData': 'KubeConf'}]
                                           )



        response = self.fetch("/api/v1/kubernetes/k8s-test2/namespaces/default/deployments?app_type=mysql&vol_type=cinder&app_name=mysqltest2",
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



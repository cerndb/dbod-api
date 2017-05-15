/api/v1/(beta)/kubernetes/<cluster>/<resource>/<name>/<subresource>/<subname>
=============================================================================


.. http:get:: /api/v1/beta/kubernetes/<cluster>/<resource>/<name>/<subresource>/(<subname>)

  Returns a json with the metadata of the requested deployment

  **Example request**

  ``curl -i -X GET https://<server>:<port>/api/v1/beta/kubernetes/k8s-test/namespaces/default/deployments/mysqltest1``

  **Example response**

  .. sourcecode:: http

      HTTP/1.1 200 OK
      Date: Mon, 01 May 2017 08:47:39 GMT
      Content-Length: 2176
      Etag: "2ca9a6bcf08e97f38da307f92940a70e46d2f48e"
      Content-Type: application/json; charset=UTF-8
      Server: TornadoServer/4.2

  .. sourcecode:: python

      {
	"response": {
	  "status": {
	    "observedGeneration": 1,
	    "updatedReplicas": 1,
	    "availableReplicas": 1,
	    "conditions": [
	      {
		"status": "True",
		"lastUpdateTime": "2017-05-03T14:07:39Z",
		"lastTransitionTime": "2017-05-03T14:07:39Z",
		"reason": "MinimumReplicasAvailable",
		"message": "Deployment has minimum availability.",
		"type": "Available"
	      }
	    ],
	    "replicas": 1
	  },
	  "kind": "Deployment",
	  "spec": {
	    "strategy": {
	      "rollingUpdate": {
		"maxSurge": 1,
		"maxUnavailable": 1
	      },
	      "type": "RollingUpdate"
	    },
	    "selector": {
	      "matchLabels": {
		"app": "mysqltest1-app"
	      }
	    },
	    "template": {
	      "spec": {
		"dnsPolicy": "ClusterFirst",
		"securityContext": {},
		"terminationGracePeriodSeconds": 30,
		"restartPolicy": "Always",
		"volumes": [
		  {
		    "nfs": {
		      "path": "/ORA/dbs03/MYSQLTEST1",
		      "server": "dbnash5142"
		    },
		    "name": "volume-data"
		  },
		  {
		    "nfs": {
		      "path": "/ORA/dbs02/MYSQLTEST1",
		      "server": "dbnash5142"
		    },
		    "name": "volume-bin"
		  },
		  {
		    "secret": {
		      "defaultMode": 420,
		      "secretName": "mysqltest1-secret-init.sql"
		    },
		    "name": "secret-init"
		  },
		  {
		    "secret": {
		      "defaultMode": 420,
		      "secretName": "mysqltest1-secret-mysql.cnf"
		    },
		    "name": "secret-conf"
		  }
		],
		"imagePullSecrets": [
		  {
		    "name": "gitlab-registry"
		  }
		],
		"containers": [
		  {
		    "terminationMessagePath": "/dev/termination-log",
		    "name": "contenedor-mysqltest1",
		    "image": "gitlab-registry.cern.ch/db/dbod-mysql:5.7.17",
		    "volumeMounts": [
		      {
			"mountPath": "/ORA/dbs03/MYSQLTEST1",
			"name": "volume-data"
		      },
		      {
			"mountPath": "/ORA/dbs02/MYSQLTEST1",
			"name": "volume-data"
		      },
		      {
			"mountPath": "/ORA/dbs02/MYSQLTEST1",
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
		    "imagePullPolicy": "Always",
		    "ports": [
		      {
			"protocol": "TCP",
			"name": "p0",
			"containerPort": 5500
		      }
		    ],
		    "resources": {}
		  }
		]
	      },
	      "metadata": {
		"labels": {
		  "app": "mysqltest1-app"
		},
		"creationTimestamp": null
	      }
	    },
	    "replicas": 1
	  },
	  "apiVersion": "extensions/v1beta1",
	  "metadata": {
	    "name": "mysqltest1-depl",
	    "generation": 1,
	    "labels": {
	      "app": "mysqltest1-app"
	    },
	    "namespace": "default",
	    "resourceVersion": "3929981",
	    "creationTimestamp": "2017-05-03T14:07:39Z",
	    "annotations": {
	      "deployment.kubernetes.io/revision": "1"
	    },
	    "selfLink": "/apis/extensions/v1beta1/namespaces/default/deployments/mysqltest1-depl",
	    "uid": "dddee035-3009-11e7-aa99-02163e00d45e"
	  }
	}
      }

  :query cluster: Magnum cluster
  :query resource: The resource you request for from Kubernetes, usually *namespaces*
  :queey name: The name of the resource, usually *default*
  :query subresource: The Kubernetes (sub)resource in the resource above, e.g. *deployments*
  :query subname: The name of the subresource
  :resheader Content-Type: application/json; charset=UTF-8
  :statuscode 200: No error
  :statuscode 404: Resource not found

.. http:post:: /api/v1/beta/kubernetes/<cluster>/<resource>/<name>/<subresource>?app_type=<app_type mysql/postgres>&app_name=<name>&vol_type=<volume_type cinder/nfs>&server_data=<nfsDataServer>&server_bin=<nfsBinlogServer>&path_data=<nfsDataPath>&path_bin=<nfsBinlogsPath>

  **Example request**:

  ``curl -i -u '<user>:<password>'-X POST nopcfound:5444/api/v1/beta/kubernetes/k8s-test/namespaces/default/deployments?app_type=mysql&app_name=mysqltest1&vol_type=nfs&server_data=dbnash5142&server_bin=dbnash5142&path_data=/ORA/dbs03/MYSQLTEST1&path_bin=/ORA/dbs02/MYSQLTEST1``

  **Example response**:

  .. sourcecode:: http

      HTTP/1.1 200 OK
      Date: Mon, 01 May 2017 08:47:39 GMT
      Content-Length: 2176
      Etag: "2ca9a6bcf08e97f38da307f92940a70e46d2f48e"
      Content-Type: application/json; charset=UTF-8
      Server: TornadoServer/4.2

  .. sourcecode:: python

      {
	"response": [
	  {
	    "Secretconf": "/api/v1/namespaces/default/secrets/test2-secret-mysql.cnf"
	  },
	  {
	    "Secretinit": "/api/v1/namespaces/default/secrets/test2-secret-init.sql"
	  },
	  {
	    "Service": {
	      "status": {
		"loadBalancer": {}
	      },
	      "kind": "Service",
	      "spec": {
		"clusterIP": "10.254.193.204",
		"sessionAffinity": "None",
		"type": "NodePort",
		"ports": [
		  {
		    "targetPort": 5500,
		    "protocol": "TCP",
		    "name": "p0",
		    "nodePort": 30695,
		    "port": 5500
		  }
		],
		"selector": {
		  "app": "test2-app"
		}
	      },
	      "apiVersion": "v1",
	      "metadata": {
		"name": "test2-svc",
		"namespace": "default",
		"resourceVersion": "3937796",
		"creationTimestamp": "2017-05-15T09:56:22Z",
		"selfLink": "/api/v1/namespaces/default/services/test2-svc",
		"uid": "c04732f1-3954-11e7-aa99-02163e00d45e"
	      }
	    }
	  },
	  {
	    "Deployment": {
	      "status": {},
	      "kind": "Deployment",
	      "spec": {
		"strategy": {
		  "rollingUpdate": {
		    "maxSurge": 1,
		    "maxUnavailable": 1
		  },
		  "type": "RollingUpdate"
		},
		"selector": {
		  "matchLabels": {
		    "app": "test2-app"
		  }
		},
		"template": {
		  "spec": {
		    "dnsPolicy": "ClusterFirst",
		    "securityContext": {},
		    "terminationGracePeriodSeconds": 30,
		    "restartPolicy": "Always",
		    "volumes": [
		      {
			"nfs": {
			  "path": "/ORA/dbs03/MYSQLTEST1",
			  "server": "dbnash5142"
			},
			"name": "volume-data"
		      },
		      {
			"nfs": {
			  "path": "/ORA/dbs02/MYSQLTEST1",
			  "server": "dbnash5142"
			},
			"name": "volume-bin"
		      },
		      {
			"secret": {
			  "defaultMode": 420,
			  "secretName": "test2-secret-init.sql"
			},
			"name": "secret-init"
		      },
		      {
			"secret": {
			  "defaultMode": 420,
			  "secretName": "test2-secret-mysql.cnf"
			},
			"name": "secret-conf"
		      }
		    ],
		    "imagePullSecrets": [
		      {
			"name": "gitlab-registry"
		      }
		    ],
		    "containers": [
		      {
			"terminationMessagePath": "/dev/termination-log",
			"name": "contenedor-test2",
			"image": "gitlab-registry.cern.ch/db/dbod-mysql:5.7.17",
			"volumeMounts": [
			  {
			    "mountPath": "/ORA/dbs03/TEST2",
			    "name": "volume-data"
			  },
			  {
			    "mountPath": "/ORA/dbs02/TEST2",
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
			"imagePullPolicy": "Always",
			"ports": [
			  {
			    "protocol": "TCP",
			    "name": "p0",
			    "containerPort": 5500
			  }
			],
			"resources": {}
		      }
		    ]
		  },
		  "metadata": {
		    "labels": {
		      "app": "test2-app"
		    },
		    "creationTimestamp": null
		  }
	      },
	      "apiVersion": "extensions/v1beta1",
	      "metadata": {
		"name": "test2-depl",
		"generation": 1,
		"labels": {
		  "app": "test2-app"
		},
		"namespace": "default",
		"resourceVersion": "3937798",
		"creationTimestamp": "2017-05-15T09:56:22Z",
		"selfLink": "/apis/extensions/v1beta1/namespaces/default/deployments/test2-depl",
		"uid": "c04f73fa-3954-11e7-aa99-02163e00d45e"
	      }
	    }
	  }
	]
      }

  :query cluster: Magnum cluster
  :query resource: The resource you request for from Kubernetes, usually *namespaces*
  :queey name: The name of the resource, usually *default*
  :query subresource: The Kubernetes (sub)resource in the resource above, e.g. *deployments*
  :query subname: The name of the subresource
  :resheader Content-Type: application/json; charset=UTF-8
  :statuscode 202: No error
  :statuscode 404: Resource not found


.. http:delete:: /api/v1/beta/kubernetes/<cluster>/<resource>/<name>/<subresource>/<subname>(?app_type=<mysql/postgres>(&delete_volumes=<True/False>&delete_service=<True/False>&force=<True/False>)) 

  **Example request**

  ``curl -i -X DELETE https://<server>:<port>/api/v1/beta/kubernetes/k8s-test/namespaces/default/deployments/mysqltest1&delete_service=True&delete_volumes=True``

  **Example response**

  .. sourcecode:: http

      HTTP/1.1 200 OK
      Date: Mon, 01 May 2017 08:47:39 GMT
      Content-Length: 2176
      Etag: "2ca9a6bcf08e97f38da307f92940a70e46d2f48e"
      Content-Type: application/json; charset=UTF-8
      Server: TornadoServer/4.2

  :query cluster: Magnum cluster
  :query resource: The resource you request for from Kubernetes, usually *namespaces*
  :queey name: The name of the resource, usually *default*
  :query subresource: The Kubernetes (sub)resource in the resource above, e.g. *deployments*
  :query subname: The name of the subresource
  :resheader Content-Type: application/json; charset=UTF-8
  :statuscode 202: No error
  :statuscode 404: Resource not found


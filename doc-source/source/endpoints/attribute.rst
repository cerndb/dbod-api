/api/v1/attribute
===================

.. http:get:: /api/v1/instance/(db_name)

	System information about a certain database. Includes ownership, access control 
	version, server, etc.

   **Example request**:

   ``curl -i -X GET https://<server>:<port>/api/v1/instance/<db_name>``

   **Example response**:

   .. sourcecode:: http


		HTTP/1.1 200 OK
		Content-Length: 394
		Content-Type: application/json; charset=UTF-8
		Date: Fri, 26 Aug 2016 13:55:10 GMT
		Etag: "bda41ea73ac1ee679651da8304653ab832eab1b1"
		Server: TornadoServer/4.2

		{
			"response": [
				{
					"class": "TEST",
					"creation_date": "2014-08-26",
					"db_name": "pinocho",
					"db_size": 200,
					"db_type": "MYSQL",
					"description": "MySQL Test database",
					"e_group": "admin_egroup",
					"expiry_date": null,
					"host": "server01",
					"id": 22,
					"master": null,
					"no_connections": 100,
					"project": "DBOD",
					"slave": null,
					"state": "RUNNING",
					"status": "1",
					"username": "username",
					"version": "5.6.17"
				}
			]
		}

   :query db_name: Instance name
   :resheader Content-Type: application/json; charset=UTF-8
   :statuscode 200: No error
   :statuscode 404: Instance not found in system

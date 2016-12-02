/api/v1/fim
===================

.. http:get:: /api/v1/fim/(db_name)

	FIM information about a certain instance. Includes owner contact information
    and affiliation

   **Example request**:

   ``curl -i -X GET https://<server>:<port>/api/v1/fim/<db_name>``

   **Example response**:

   .. sourcecode:: http


		HTTP/1.1 200 OK
		Content-Length: 394
		Content-Type: application/json; charset=UTF-8
		Date: Fri, 26 Aug 2016 13:55:10 GMT
		Etag: "bda41ea73ac1ee679651da8304653ab832eab1b1"
		Server: TornadoServer/4.2

		{
			"response": 
				{
					"owner_name": "foo",
                    ...
				}
		}

   :query instance: Instance name
   :resheader Content-Type: application/json; charset=UTF-8
   :statuscode 200: No error
   :statuscode 404: Instance not found in system

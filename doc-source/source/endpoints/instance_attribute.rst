/api/v1/instance/<name>/attribute/<attribute_name>
==================================================

.. http:get:: /api/v1/instance/(instance_name)/attribute/(attribute_name)

    Returns the value of an instance attribute or, if the attribute_name is empty,
    a full list of the instance attributes.

   **Example request**:

   ``curl -i -X GET https://<server>:<port>/api/v1/instance/<instance_name>/attribute/(attribute_name?)``

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
                "attribute1": "value1",
                "attribute2": "value2"
            }
		}

   :query instance_name: Instance name
   :query attribute_name: Attribute name
   :resheader Content-Type: application/json; charset=UTF-8
   :statuscode 200: No error
   :statuscode 404: Instance not found in system

.. http:delete:: /api/v1/instance/(instance_name)/attribute/(attribute_name)

    Returns the value of an instance attribute or, if the attribute_name is empty,
    a full list of the instance attributes.

   **Example request**:

   ``curl -i -X DELETE https://<server>:<port>/api/v1/instance/<instance_name>/attribute/<attribute_name>``

   **Example response**:

   .. sourcecode:: http


		HTTP/1.1 200 OK
		Content-Length: 394
		Content-Type: application/json; charset=UTF-8
		Date: Fri, 26 Aug 2016 13:55:10 GMT
		Etag: "bda41ea73ac1ee679651da8304653ab832eab1b1"
		Server: TornadoServer/4.2

   :query instance_name: Instance name
   :query attribute_name: Attribute name
   :resheader Content-Type: application/json; charset=UTF-8
   :statuscode 200: No error
   :statuscode 404: Instance or attribute not found in system

.. http:put:: /api/v1/instance/(instance_name)/attribute/(attribute_name)

    Returns the value of an instance attribute or, if the attribute_name is empty,
    a full list of the instance attributes.

   **Example request**:

   ``curl -i -X PUT https://<server>:<port>/api/v1/instance/<instance_name>/attribute/<attribute_name>``

   **Example response**:

   .. sourcecode:: http


		HTTP/1.1 200 OK
		Content-Length: 394
		Content-Type: application/json; charset=UTF-8
		Date: Fri, 26 Aug 2016 13:55:10 GMT
		Etag: "bda41ea73ac1ee679651da8304653ab832eab1b1"
		Server: TornadoServer/4.2

   :query instance_name: Instance name
   :resheader Content-Type: application/json; charset=UTF-8
   :statuscode 204: No error
   :statuscode 404: Instance or attribute not found in system

.. http:post:: /api/v1/instance/(instance_name)/attribute/(attribute_name)

    Returns the value of an instance attribute or, if the attribute_name is empty,
    a full list of the instance attributes.

   **Example request**:

   ``curl -i -H "Content-Type: application/json" -X POST -d '{"attr":"value"}' https://<server>:<port>/api/v1/instance/<instance_name>/attribute/<attribute_name>``

   :query instance_name: Instance name
   :resheader Content-Type: application/json; charset=UTF-8
   :statuscode 201: No error
   :statuscode 404: Instance not found in system

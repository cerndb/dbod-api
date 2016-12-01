/api/v1/host
===================

.. http:get:: /api/v1/host/names/<name>

	Returns a json with the memory assigned to each host.

   **Example request**:

   ``curl -i -X GET https://<server>:<port>/api/v1/host/names/<name>``

   **Example response**:

   .. sourcecode:: http


                HTTP/1.1 200 OK
                Date: Thu, 01 Dec 2016 17:22:06 GMT
                Content-Length: 30
                Etag: "ffd3be949a2dd4b26086119241118ae42ef05432"
                Content-Type: application/json; charset=UTF-8
                Server: TornadoServer/4.2

   .. sourcecode:: python 
		{
			"response": [
				{
					"memory": 42
				}
			]
		}

   :query name: Host name
   :resheader Content-Type: application/json; charset=UTF-8
   :statuscode 200: No error
   :statuscode 404: Name (host) not found in system
   :statuscode 500: Backend error (api or postgrest or database)


.. http:post:: /api/v1/instance/host/names/<name>

    **Example request**:
  
    ``curl -k -i -X POST -u <usernmae>:<password> https://<domain>:<port>/api/v1/host/names/<new_name>?memory=<memory_in_MB(int)>``
    or
    ``curl -k -i -X POST -u <usernmae>:<password> -H 'Content-Type: application/x-www-form-urlencoded' https://<domain>:<port>/api/v1/host/names/<new_name> -d 'memory=<memory_in_MB(int)>'`` 
    
    **Example response**:

    .. sourcecode:: http

                HTTP/1.1 201 Created
                Date: Thu, 01 Dec 2016 17:35:07 GMT
                Content-Length: 0
                Content-Type: text/html; charset=UTF-8
                Server: TornadoServer/4.2


    :query name: Host name
    :reqheader Accept: application/json
    :resheader Content-Type: application/json
    :resheader Charset: UTF-8
    :statuscode 201: Host mapping successfuly created
    :statuscode 400: Error when the format or the argument is not correct
    :statuscode 409: Error when inserting duplicate names
    :statuscode 500: Backend error (api or postgrest or database)

      
.. http:put:: /api/v1/instance/alias/<db_name>

    **Example request**:

    ``curl -k -i -X PUT -u <usernmae>:<password> https://<domain>:<port>/api/v1/host/names/<existing_name>?memory=<memory_in_MB(int)>``
    or
    ``curl -k -i -X PUT -u <usernmae>:<password> -H 'Content-Type: application/x-www-form-urlencoded' https://<domain>:<port>/api/v1/host/names/<existing_name> -d 'memory=<memory_in_MB(int)>'``


    **Example response**:

    .. sourcecode:: http

                HTTP/1.1 200 OK
                Date: Thu, 01 Dec 2016 17:25:44 GMT
                Content-Length: 0
                Content-Type: text/html; charset=UTF-8
                Server: TornadoServer/4.2

    :query name: Host name
    :reqheader Accept: application/json
    :resheader Content-Type: application/json
    :resheader Charset: UTF-8
    :statuscode 200: Host mapping successfuly updated
    :statuscode 400: Format or argument error 
    :statuscode 404: Error for non existent name
    :statuscode 500: Backend error (api or postgrest or database)


.. http:delete:: /api/v1/instance/host/names/<name>

    **Example request**:
  
    ``curl -k -i -X DELETE -u <usernmae>:<password> https://<domain>:<port>/api/v1/host/names/<new_name>``
    
    **Example response**:

    .. sourcecode:: http

                HTTP/1.1 200 OK
                Date: Thu, 01 Dec 2016 17:37:07 GMT
                Content-Length: 0
                Content-Type: text/html; charset=UTF-8
                Server: TornadoServer/4.2


    :query name: Host name
    :reqheader Accept: application/json
    :resheader Content-Type: application/json
    :resheader Charset: UTF-8
    :statuscode 200: Host mapping successfuly deleted
    :statuscode 404: Error for non existent name
    :statuscode 500: Backend error (api or postgrest or database)


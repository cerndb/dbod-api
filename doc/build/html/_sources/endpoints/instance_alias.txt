/api/v1/instance/alias
=======================

        
.. http:get:: /api/v1/instance/alias/<db_name>
    
    **Example request**:

    ``curl -X GET -i https://<domain>:<port>/api/v1/instance/alias/<db_name>``

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Date: Fri, 26 Aug 2016 08:37:53 GMT
        Content-Length: 67
        Etag: "36bdee6a05ae3420c4faf5811dc7d9aff181b1d0"
        Content-Type: application/json; charset=UTF-8
        Server: TornadoServer/4.2

    .. sourcecode:: python

        {
            "response": [{
                            "dns_name": dns_name_42, 
                            "alias": ip_alias,
                        }]
        }

    :query db_name: instance name
    :reqheader Accept: application/json
    :resheader Content-Type: application/json
    :resheader Charset: UTF-8
    :statuscode 200: no error
    :statuscode 404: there's no instance with that name

    
.. http:delete:: /api/v1/instance/alias/<db_name>

    **Example request**:

    ``curl -X DELETE -i https://<domain>:<port>/api/v1/instance/alias/<db_name>``

    **Example response**:

    .. sourcecode:: http

    	HTTP/1.1 204 No Content
		Date: Fri, 26 Aug 2016 13:44:34 GMT
		Content-Length: 0
		Content-Type: text/html; charset=UTF-8
		Server: TornadoServer/4.2
    
    :query db_name: instance name
    :reqheader Accept: application/json
    :resheader Content-Type: application/json
    :resheader Charset: UTF-8
    :statuscode 204: Alias association successfuly deleted
    :statuscode 400: Trying to delete a non existing mapping


.. http:post:: /api/v1/instance/alias/<db_name>
    
    **Example request**:

    ``curl -X POST -i https://<domain>:<port>/api/v1/instance/alias/<db_name??alias=<ip-alias>``

    **Example response**:

    .. sourcecode:: http

		HTTP/1.1 201 Created
		Date: Fri, 26 Aug 2016 13:43:46 GMT
		Content-Length: 0
		Content-Type: text/html; charset=UTF-8
		Server: TornadoServer/4.2



    :query db_name: instance name
    :reqheader Accept: application/json
    :resheader Content-Type: application/json
    :resheader Charset: UTF-8
    :statuscode 201: Alias mapping successfuly created
    :statuscode 404: Error creating alias

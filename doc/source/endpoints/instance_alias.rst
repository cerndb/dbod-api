/api/v1/instance/alias
=======================

.. http:get:: /api/v1/instance/alias/(db_name)

    **Example request**:

    ``curl -X GET -i https://<domain>:<port>/api/v1/instance/alias/dbod_42``

    .. sourcecode:: http

        GET /api/v1/instance/dbod_db42 HTTP/1.1
        Host: <domain>
        Accept: */*

    **Example response**:

    ``curl -X GET -i https://<domain>:<port>/api/v1/instance/alias/dbod_42``

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
                            "dns_name": dbod_dns42, 
                            "alias": dbod_alias42.cern.ch
                        }]
        }

    :query db_name: instance name
    :reqheader Accept: application/json
    :resheader Content-Type: application/json
    :resheader Charset: UTF-8
    :statuscode 200: no error
    :statuscode 404: there's no instance with that name

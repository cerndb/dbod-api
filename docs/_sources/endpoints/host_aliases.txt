/api/v1/host/aliases
=======================

.. http:get:: /api/v1/host/aliases/<hostname>

    Returns a list of IP aliases assigned to the host specified by <hostname>

    **Example response**:

    ``curl -X GET -i https://<domain>:<port>/api/v1/host/aliases/test_server``

    .. sourcecode:: http

		HTTP/1.1 200 OK
		Content-Length: 194
		Content-Type: application/json; charset=UTF-8
		Date: Fri, 26 Aug 2016 10:07:49 GMT
		Etag: "bda4f8b8eed1db692dcf4a0f95563544e16ef249"
		Server: TornadoServer/4.2


    .. sourcecode:: python

		{
			"response": [
				{
					"aliases": [
						"dbod-test2.domain",
						"dbod-test1.domain",
					],
					"host": "test_server"
				}
			]
		}


    :query hostname: server name
    :resheader Content-Type: application/json
    :resheader Charset: UTF-8
    :statuscode 200: no error
    :statuscode 404: host not registered in the system (or no instances hosted)

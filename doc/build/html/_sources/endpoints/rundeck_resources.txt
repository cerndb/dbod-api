/api/v1/rundeck/resources.xml
=============================

.. http:get:: /api/v1/instance/alias/(db_name)

	This URI returns an XML document ready to be used as a source of information
	for the node list on a Rundeck setup.

    **Example request**:

    ``curl -X GET -i https://<domain>:<port>/api/v1/rundeck/resources.xml``

    .. sourcecode:: http

		HTTP/1.1 200 OK
		Date: Fri, 26 Aug 2016 09:45:42 GMT
		Content-Length: 52661
		Etag: "5d553d39cf0f3422569d19549627c8e9c615732e"
		Content-Type: text/xml
		Server: TornadoServer/4.2

    .. sourcecode:: xml 

        <?xml version="1.0" encoding="UTF-8"?>
        <project>
            <node name="db1" hostname="dbod-db1.domain" ... />
            <node name="db2" hostname="dbod-db2.domain" ... />
        </project>    

    :resheader Content-Type: text/xml

/
===================

.. http:get:: /

   Returns the list of endpoints currently being served by the API Server

   **Example response**:

   .. sourcecode:: http

      GET / HTTP/1.1
      Host: example.com
      Accept: applicaHTTP/1.1 200 OK
	Date: Fri, 26 Aug 2016 09:39:58 GMT
	Content-Length: 486
	Etag: "b4b039b348035550c569a378d2d0e8ab4f9dd0cf"
	Content-Type: text/html
	Server: TornadoServer/4.2

	Please use :
		<p>http://hostname:port/api/v1/instance/NAME</p>
		<p>http://hostname:port/api/v1/instance/alias/NAME</p>
		<p>http://hostname:port/api/v1/host/aliases/HOSTNAME</p>
		<p>http://hostname:port/api/v1/metadata/instance/NAME</p>
		<p>http://hostname:port/api/v1/metadata/host/HOSTNAME</p>
		<p>http://hostname:port/api/v1/rundeck/resources.xml</p>
		<p>http://hostname:port/api/v1/rundeck/job/JOB/NODE</p>
                <p>http://hostname:port/api/v1/(beta/)kubernetes/cluster/resource/name/subresource/subname<p>

   :resheader Content-Type: text/html 

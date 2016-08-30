/api/v1/rundeck/job
===================

.. http:post:: /api/v1/rundeck/job/(job-name)/(instance)

    Executes the Rundeck job specified by (job-name) on the target (instance).
    
    The followin example covers the execution of a job named ``get-snapshots``
    which returns the list of snapshots from a certain instance which could be
    used to launch a restore.

   **Example request**:

    ``curl -i -u $AUTH -X POST https://<server>:5443/api/v1/rundeck/job/get-snapshots/pinocho``

   **Example response**:

   .. sourcecode:: http

	HTTP/1.1 200 OK
	Date: Fri, 26 Aug 2016 14:55:45 GMT
	Content-Length: 5258
	Content-Type: application/json; charset=UTF-8
	Server: TornadoServer/4.2

	{ "response": 
	  { 
		"execState": "succeeded", 
		"hasFailedNodes": false, 
		"lastModified": "1472223348000", 
		"completed": true, 
		"totalSize": 5260,
		"execCompleted": true, 
		"percentLoaded": 99.88593155893535, 
		"offset": "5254", 
		"entries": [
		  {
			"absolute_time": "2016-08-26T14:55:47Z", 
			"node": "pinocho", 
			"log": "['snapscript_13072015_171321_133_5617','snapscript_09072015_170607_131_5617', 'snapscript_13072015_171233_132_561']",
			"level": "NORMAL", 
			"command": null,
			"user": "dbod", 
			"time": "16:55:47", 
			"stepctx": "1"}], 
			"id": "143", 
			"execDuration": 3000
		
	  }
	}
 

   :resheader Content-Type: application/json; charset=UTF-8
   :statuscode 200: No error executing job. Check log for details
   :statuscode 502: Job not found in Rundeck

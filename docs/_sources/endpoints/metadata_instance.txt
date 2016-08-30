/api/v1/metadata/instance
=============================

.. http:get:: /api/v1/metadata/instance/(db_name)

    Returns the full set of information present in the system for a certain
    database instance.

   **Example request**:

   ``curl -i -X GET https://<server>:<port>/api/v1/metadata/instance/<db_name>``

   **Example response**:

   .. sourcecode:: http

        HTTP/1.1 200 OK
        Content-Length: 954
        Content-Type: application/json; charset=UTF-8
        Date: Fri, 26 Aug 2016 14:05:13 GMT
        Etag: "f3181702286fb653c98cf885923ce61779343020"
        Server: TornadoServer/4.2

        {
            "response": [
                {
                    "attributes": {
                        "buffer_pool_size": "1G",
                        "port": "5500"
                    },
                    "basedir": "/usr/local/mysql/mysql-5.6.17",
                    "bindir": "/usr/local/mysql/mysql-5.6.17/bin",
                    "class": "TEST",
                    "datadir": "/ORA/dbs03/<DB_NAME>/mysql",
                    "db_name": "pinocho",
                    "db_type": "MYSQL",
                    "hosts": [
                        "db-50019"
                    ],
                    "id": 22,
                    "logdir": "/ORA/dbs02/<DB_NAME>/mysql",
                    "port": "5500",
                    "socket": "/var/lib/mysql/mysql.sock.<db_name>.5500",
                    "username": "username",
                    "version": "5.6.17",
                    "volumes": [
                        {
                            "file_mode": "0755",
                            "group": "mysql",
                            "id": 57,
                            "instance_id": 22,
                            "mount_options": "rw,bg,hard,nointr,tcp,vers=3,noatime,timeo=600,rsize=65536,wsize=65536",
                            "mounting_path": "/ORA/dbs02/<DB_NAME>",
                            "owner": "mysql",
                            "server": "nasserver01"
                        },
                        {
                            "file_mode": "0755",
                            "group": "mysql",
                            "id": 58,
                            "instance_id": 22,
                            "mount_options": "rw,bg,hard,nointr,tcp,vers=3,noatime,timeo=600,rsize=65536,wsize=65536",
                            "mounting_path": "/ORA/dbs03/<DB_NAME>",
                            "owner": "mysql",
                            "server": "nasserver02"
                        }
                    ]
                }
            ]
        }


   :query db_name: Instance name
   :resheader Content-Type: application/json; charset=UTF-8
   :statuscode 200: No error
   :statuscode 404: Instance not found in system

/api/v1/host/<name>/metadata
============================

.. http:get:: /api/v1/metadata/host/(hostname)

    Returns a list with the metadata entries of all the databases hosted in a
    certain server

   **Example request**:

   ``curl -i -X GET https://<server>:<port>/api/v1/metadata/host/<hostname>``

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
                    "datadir": "/ORA/dbs03/PINOCHO/mysql",
                    "db_name": "pinocho",
                    "db_type": "MYSQL",
                    "hosts": [
                        "db-50019"
                    ],
                    "id": 22,
                    "logdir": "/ORA/dbs02/PINOCHO/mysql",
                    "port": "5500",
                    "socket": "/var/lib/mysql/mysql.sock.pinocho.5500",
                    "username": "username",
                    "version": "5.6.17",
                    "volumes": [
                        {
                            "file_mode": "0755",
                            "group": "mysql",
                            "id": 57,
                            "instance_id": 22,
                            "mount_options": "rw,bg,hard,nointr,tcp,vers=3,noatime,timeo=600,rsize=65536,wsize=65536",
                            "mounting_path": "/ORA/dbs02/PINOCHO",
                            "owner": "mysql",
                            "server": "nasserver01"
                        },
                        {
                            "file_mode": "0755",
                            "group": "mysql",
                            "id": 58,
                            "instance_id": 22,
                            "mount_options": "rw,bg,hard,nointr,tcp,vers=3,noatime,timeo=600,rsize=65536,wsize=65536",
                            "mounting_path": "/ORA/dbs03/PINOCHO",
                            "owner": "mysql",
                            "server": "nasserver02"
                        }
                    ]
                }
                {
                    "attributes": {
                        "buffer_pool_size": "1G",
                        "port": "5501"
                    },
                    "basedir": "/usr/local/mysql/mysql-5.6.17",
                    "bindir": "/usr/local/mysql/mysql-5.6.17/bin",
                    "class": "TEST",
                    "datadir": "/ORA/dbs03/PINOCHO2/mysql",
                    "db_name": "pinocho2",
                    "db_type": "MYSQL",
                    "hosts": [
                        "hostname2"
                    ],
                    "id": 280,
                    "logdir": "/ORA/dbs02/PINOCHO2/mysql",
                    "port": "5501",
                    "socket": "/var/lib/mysql/mysql.sock.pinocho2.5501",
                    "username": "username2",
                    "version": "5.6.17",
                    "volumes": [
                        {
                            "file_mode": "0755",
                            "group": "mysql",
                            "id": 71,
                            "instance_id": 280,
                            "mount_options": "rw,bg,hard,nointr,tcp,vers=3,noatime,timeo=600,rsize=65536,wsize=65536",
                            "mounting_path": "/ORA/dbs02/PINOCHO2",
                            "owner": "mysql",
                            "server": "nasserver03"
                        },
                        {
                            "file_mode": "0755",
                            "group": "mysql",
                            "id": 72,
                            "instance_id": 280,
                            "mount_options": "rw,bg,hard,nointr,tcp,vers=3,noatime,timeo=600,rsize=65536,wsize=65536",
                            "mounting_path": "/ORA/dbs03/PINOCHO2",
                            "owner": "mysql",
                            "server": "nasserver04"
                        }
                    ]
                }
            ]
        }


   :query hostname: Server name
   :resheader Content-Type: application/json; charset=UTF-8
   :statuscode 200: No error
   :statuscode 404: Server not found in system

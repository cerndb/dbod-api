-------------------------------
-- Test values
-------------------------------
INSERT INTO apiato.volume_type (type, description)
    VALUES ('NETAPP', 'NETAPP volume type'),
           ('CEPTH',  'CEPTH volume type');

INSERT INTO apiato.instance_type (type, description)
VALUES ('ZOOKEEPER', 'Zookeeper instance type'),
       ('MYSQL'    , 'MySQL database type'),
       ('PG'       , 'PostgreSQL database type');

-- Insert test data for hosts
INSERT INTO apiato.host (name, memory)
VALUES ('host01', 12),
       ('host02', 24),
       ('host03', 64),
       ('host04', 256);

INSERT INTO apiato.cluster (owner, name, e_group, category, creation_date, expiry_date, instance_type_id, project, description, version, master_cluster_id, state, status)
VALUES ('user05','cluster01','testgroupZ','DEV',now(),NULL,1,'NILE','Test zookeeper cluster 1', '3.4.9',NULL,'RUNNING','ACTIVE');


-- Insert test data for instances
INSERT INTO apiato.instance (owner, name, e_group, category, creation_date, instance_type_id, size, no_connections, project, description, version, master_instance_id, slave_instance_id, host_id, state, status, cluster_id)
VALUES ('user01', 'dbod01', 'testgroupA', 'TEST', now(), 2 , 100 , 100 , 'API' , 'Test instance 1'      , '5.6.17', NULL, NULL, 1, 'RUNNING', 'ACTIVE',     NULL),
       ('user01', 'dbod02', 'testgroupB', 'PROD', now(), 3 , 50  , 500 , 'API' , 'Test instance 2'      , '9.4.4' , NULL, NULL, 3, 'RUNNING', 'ACTIVE',     NULL),
       ('user02', 'dbod03', 'testgroupB', 'TEST', now(), 2 , 100 , 200 , 'WEB' , 'Expired instance 1'   , '5.5'   , NULL, NULL, 1, 'RUNNING', 'NON-ACTIVE', NULL),
       ('user03', 'dbod04', 'testgroupA', 'PROD', now(), 3 , 250 , 10  , 'LCC' , 'Test instance 3'      , '9.4.5' , NULL, NULL, 1, 'RUNNING', 'ACTIVE',     NULL),
       ('user04', 'dbod05', 'testgroupC', 'TEST', now(), 2 , 300 , 200 , 'WEB' , 'Test instance 4'      , '5.6.17', NULL, NULL, 1, 'RUNNING', 'ACTIVE',     NULL),
       ('user04', 'dbod06', 'testgroupC', 'TEST', now(), 2 , 300 , 200 , 'WEB' , 'Test instance 4'      , '5.6.17', NULL, NULL, 1, 'RUNNING', 'ACTIVE',     NULL),
       ('user05', 'node01', 'testgroupZ', 'DEV' , now(), 1 , NULL, NULL, 'NILE', 'Test zookeeper inst 1', '3.4.9' , NULL, NULL, 4, 'RUNNING', 'ACTIVE',     1),
       ('user05', 'node02', 'testgroupZ', 'DEV' , now(), 1 , NULL, NULL, 'NILE', 'Test zookeeper inst 2', '3.4.9' , NULL, NULL, 4, 'RUNNING', 'ACTIVE',     1);

-- Insert test data for volumes
INSERT INTO apiato.volume (instance_id, volume_type_id, file_mode, owner, "group", server, mount_options, mounting_path)
VALUES (1, 1, '0755', 'TSM', 'ownergroup', 'NAS-server', 'rw,bg,hard', '/MNT/data1'),
       (1, 1, '0755', 'TSM', 'ownergroup', 'NAS-server', 'rw', '/MNT/bin'),
       (2, 1, '0755', 'TSM', 'ownergroup', 'NAS-server', 'rw,bg,hard', '/MNT/data2'),
       (4, 1, '0755', 'TSM', 'ownergroup', 'NAS-server', 'rw,bg,hard,tcp', '/MNT/data4'),
       (5, 1, '0755', 'TSM', 'ownergroup', 'NAS-server', 'rw,bg,hard', '/MNT/data5'),
       (5, 1, '0755', 'TSM', 'ownergroup', 'NAS-server', 'rw', '/MNT/bin'),
       (6, 1, '0755', 'TSM', 'ownergroup', 'NAS-server', 'rw', '/MNT/zk'),
       (7, 1, '0755', 'TSM', 'ownergroup', 'NAS-server', 'rw', '/MNT/zk'),
       (7, 2, '0755', 'TSM', 'ownergroup', 'NAS-server', 'rw,bg,hard', '/MNT/data01');

-- Insert test data for attributes
INSERT INTO apiato.instance_attribute (instance_id, name, value)
VALUES (1, 'port', '5501'),
       (2, 'port', '6603'),
       (3, 'port', '5510'),
       (4, 'port', '6601'),
       (5, 'port', '5500'),
       (6, 'port', '2181'),
       (7, 'port', '2181');

-- Insert test data for cluster attributes
INSERT INTO apiato.cluster_attribute (cluster_id, name, value)
    VALUES (1, 'service','zookeeper'),
           (1, 'user'   ,'zookeeper');

INSERT INTO apiato.volume_attribute (volume_id, name, value)
VALUES (8, 'ro', 'TRUE'),
       (8, 'fw', 'TRUE'),
       (9, 'ro', 'FALSE');

-- Insert test data for functional aliases
INSERT INTO apiato.functional_alias (dns_name, instance_id, alias)
VALUES ('db-dbod-dns01', 1   , 'dbod-dbod-01.cern.ch'),
       ('db-dbod-dns02', 2   , 'dbod-dbod-02.cern.ch'),
       ('db-dbod-dns03', 3   , 'dbod-dbod-03.cern.ch'),
       ('db-dbod-dns04', 4   , 'dbod-dbod-04.cern.ch'),
       ('db-dbod-dns05', NULL, NULL);
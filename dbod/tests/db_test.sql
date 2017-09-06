
-- Insert test data for volumes
INSERT INTO public.volume_type (type, description)
VALUES ('NETAPP', 'NETAPP volume type'),
       ('CEPTH',  'CEPTH volume type');

INSERT INTO public.volume (instance_id, volume_type_id, file_mode, owner, "group", server, mount_options, mounting_path)
VALUES (1, 1, '0755', 'TSM', 'ownergroup', 'NAS-server', 'rw,bg,hard', '/MNT/data1'),
       (1, 1, '0755', 'TSM', 'ownergroup', 'NAS-server', 'rw', '/MNT/bin'),
       (2, 1, '0755', 'TSM', 'ownergroup', 'NAS-server', 'rw,bg,hard', '/MNT/data2'),
       (4, 1, '0755', 'TSM', 'ownergroup', 'NAS-server', 'rw,bg,hard,tcp', '/MNT/data4'),
       (5, 1, '0755', 'TSM', 'ownergroup', 'NAS-server', 'rw,bg,hard', '/MNT/data5'),
       (5, 1, '0755', 'TSM', 'ownergroup', 'NAS-server', 'rw', '/MNT/bin'),
       (6, 1, '0755', 'TSM', 'ownergroup', 'NAS-server', 'rw', '/MNT/zk'),
       (7, 1, '0755', 'TSM', 'ownergroup', 'NAS-server', 'rw', '/MNT/zk'),
       (7, 2, '0755', 'TSM', 'ownergroup', 'NAS-server', 'rw,bg,hard', '/MNT/data01');

INSERT INTO public.volume_attribute (volume_id, name, value)
VALUES (8, 'ro', 'TRUE'),
       (8, 'fw', 'TRUE'),
       (9, 'ro', 'FALSE');
       
-- Insert test data for hosts
INSERT INTO public.host (name, memory)
VALUES ('host01', 12),
       ('host02', 24),
       ('host03', 64),
       ('host04', 256);

-- Insert test data for instances
INSERT INTO public.instance (owner, name, e_group, category, creation_date, type_id, size, no_connections, project, description, version, master_id, slave_id, host_id, state, status, cluster_id)
VALUES (1, 'user01', 'dbod01', 'testgroupA', 'TEST', now(), 2 , 100 , 100 , 'API' , 'Test instance 1'      , '5.6.17', NULL, NULL, 1, 'RUNNING', 'ACTIVE',     NULL),
       (2, 'user01', 'dbod02', 'testgroupB', 'PROD', now(), 3 , 50  , 500 , 'API' , 'Test instance 2'      , '9.4.4' , NULL, NULL, 3, 'RUNNING', 'ACTIVE',     NULL),
       (3, 'user02', 'dbod03', 'testgroupB', 'TEST', now(), 2 , 100 , 200 , 'WEB' , 'Expired instance 1'   , '5.5'   , NULL, NULL, 1, 'RUNNING', 'NON-ACTIVE', NULL),
       (4, 'user03', 'dbod04', 'testgroupA', 'PROD', now(), 3 , 250 , 10  , 'LCC' , 'Test instance 3'      , '9.4.5' , NULL, NULL, 1, 'RUNNING', 'ACTIVE',     NULL),
       (5, 'user04', 'dbod05', 'testgroupC', 'TEST', now(), 2 , 300 , 200 , 'WEB' , 'Test instance 4'      , '5.6.17', NULL, NULL, 1, 'RUNNING', 'ACTIVE',     NULL),
       (6, 'user04', 'dbod06', 'testgroupC', 'TEST', now(), 2 , 300 , 200 , 'WEB' , 'Test instance 4'      , '5.6.17', NULL, NULL, 1, 'RUNNING', 'ACTIVE',     NULL),
       (7, 'user05', 'node01', 'testgroupZ', 'DEV' , now(), 1 , NULL, NULL, 'NILE', 'Test zookeeper inst 1', '3.4.9' , NULL, NULL, 4, 'RUNNING', 'ACTIVE',     1),
       (8, 'user05', 'node02', 'testgroupZ', 'DEV' , now(), 1 , NULL, NULL, 'NILE', 'Test zookeeper inst 2', '3.4.9' , NULL, NULL, 4, 'RUNNING', 'ACTIVE',     1);

-- Insert test data for attributes
INSERT INTO public.instance_attribute (instance_id, name, value)
VALUES (1, 'port', '5501'),
       (2, 'port', '6603'),
       (3, 'port', '5510'),
       (4, 'port', '6601'),
       (5, 'port', '5500');

-- Insert test data for database aliases
INSERT INTO public.functional_aliases (dns_name, db_name, alias)
VALUES ('db-dbod-dns01','dbod01','dbod-dbod-01.cern.ch'),
       ('db-dbod-dns02','dbod02','dbod-dbod-02.cern.ch'),
       ('db-dbod-dns03','dbod03','dbod-dbod-03.cern.ch'),
       ('db-dbod-dns04','dbod04','dbod-dbod-04.cern.ch'),
       ('db-dbod-dns05', NULL, NULL);

-- Insert test data from clusters
INSERT INTO public.cluster (owner, name, e_group, category, creation_date, expiry_date, type_id, project, description, version, master_id, state, status)
VALUES ('user05','cluster01','testgroupZ','DEV',now(),NULL,1,'NILE','Test zookeeper cluster 1', '3.4.9',NULL,'RUNNING','ACTIVE');

-- Insert test data for cluster attributes
INSERT INTO public.cluster_attribute (cluster_id, name, value)
VALUES (1, 'service','zookeeper'),
       (1, 'user'   ,'zookeeper');
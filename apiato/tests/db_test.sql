-- Copyright (C) 2015, CERN
-- This software is distributed under the terms of the GNU General Public
-- Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".
-- In applying this license, CERN does not waive the privileges and immunities
-- granted to it by virtue of its status as Intergovernmental Organization
-- or submit itself to any jurisdiction.

------------------------------
-- DATA TO RUN TESTS
------------------------------

-- Clean all the tables!
TRUNCATE TABLE public.volume_attribute CASCADE;
TRUNCATE TABLE public.instance_attribute CASCADE;
TRUNCATE TABLE public.cluster_attribute CASCADE;
TRUNCATE TABLE public.cluster CASCADE;
TRUNCATE TABLE public.volume CASCADE;
TRUNCATE TABLE public.job CASCADE;
TRUNCATE TABLE public.instance CASCADE;
TRUNCATE TABLE public.host CASCADE;
TRUNCATE TABLE public.functional_aliases CASCADE;
TRUNCATE TABLE public.fim_data CASCADE;

ALTER SEQUENCE volume_id_seq RESTART WITH 1;
ALTER SEQUENCE volume_attribute_id_seq RESTART WITH 1;
ALTER SEQUENCE host_id_seq RESTART WITH 1;
ALTER SEQUENCE instance_id_seq RESTART WITH 1;
ALTER SEQUENCE instance_attribute_id_seq RESTART WITH 1;
ALTER SEQUENCE cluster_id_seq RESTART WITH 1;
ALTER SEQUENCE cluster_attribute_id_seq RESTART WITH 1;
ALTER SEQUENCE job_id_seq RESTART WITH 1;

-- Insert test data for hosts
INSERT INTO public.host (id, name, memory)
VALUES (1, 'host01', 12),
       (2, 'host02', 24),
       (3, 'host03', 64),
       (4, 'host04', 256);
SELECT setval('host_id_seq', (SELECT MAX(id) from public.host));

-- Insert test data from clusters
INSERT INTO public.cluster (id, owner, name, egroup, category, creation_date, expiry_date, type_id, project, description, version, master_id, state, status)
VALUES (1, 'user05','cluster01','testgroupZ','DEV',now(),NULL,1,'NILE','Test zookeeper cluster 1', '3.4.9',NULL,'RUNNING','ACTIVE');
SELECT setval('cluster_id_seq', (SELECT MAX(id) from public.cluster));

-- Insert test data for cluster attributes
INSERT INTO public.cluster_attribute (id, cluster_id, name, value)
VALUES (1, 1, 'service','zookeeper'),
       (2, 1, 'user'   ,'zookeeper');
SELECT setval('cluster_attribute_id_seq', (SELECT MAX(id) from public.cluster_attribute));

-- Insert test data for instances
INSERT INTO public.instance (id, owner, name, egroup, category, creation_date, type_id, size, project, description, version, master_id, slave_id, host_id, state, status, cluster_id)
VALUES (1, 'user01', 'apiato01', 'testgroupA', 'TEST', now(), 2 , 100 , 'API' , 'Test instance 1'      , '5.6.17', NULL, NULL, 1, 'RUNNING', 'ACTIVE',     NULL),
       (2, 'user01', 'apiato02', 'testgroupB', 'PROD', now(), 3 , 50  , 'API' , 'Test instance 2'      , '9.4.4' , NULL, NULL, 3, 'RUNNING', 'ACTIVE',     NULL),
       (3, 'user02', 'apiato03', 'testgroupB', 'TEST', now(), 2 , 100 , 'WEB' , 'Expired instance 1'   , '5.5'   , NULL, NULL, 1, 'RUNNING', 'NON_ACTIVE', NULL),
       (4, 'user03', 'apiato04', 'testgroupA', 'PROD', now(), 3 , 250 , 'LCC' , 'Test instance 3'      , '9.4.5' , NULL, NULL, 1, 'RUNNING', 'ACTIVE',     NULL),
       (5, 'user04', 'apiato05', 'testgroupC', 'TEST', now(), 2 , 300 , 'WEB' , 'Test instance 4'      , '5.6.17', NULL, NULL, 1, 'RUNNING', 'ACTIVE',     NULL),
       (6, 'user04', 'apiato06', 'testgroupC', 'TEST', now(), 2 , 300 , 'WEB' , 'Test instance 4'      , '5.6.17', NULL, NULL, 1, 'RUNNING', 'ACTIVE',     NULL),
       (7, 'user05', 'node01',   'testgroupZ', 'DEV' , now(), 1 , NULL, 'NILE', 'Test zookeeper inst 1', '3.4.9' , NULL, NULL, 4, 'RUNNING', 'ACTIVE',     1),
       (8, 'user05', 'node02',   'testgroupZ', 'DEV' , now(), 1 , NULL, 'NILE', 'Test zookeeper inst 2', '3.4.9' , NULL, NULL, 4, 'RUNNING', 'ACTIVE',     1);
SELECT setval('instance_id_seq', (SELECT MAX(id) from public.instance));

-- Insert test data for attributes
INSERT INTO public.instance_attribute (instance_id, name, value)
VALUES (1, 'port', '5501'),
       (2, 'port', '6603'),
       (3, 'port', '5510'),
       (4, 'port', '6601'),
       (5, 'port', '5500');
SELECT setval('instance_attribute_id_seq', (SELECT MAX(id) from public.instance_attribute));

-- Insert test data for volumes
INSERT INTO public.volume (id, instance_id, type_id, file_mode, owner, "group", server, mount_options, mounting_path)
VALUES (1, 1, 1, '0755', 'TSM', 'ownergroup', 'NAS-server', 'rw,bg,hard', '/MNT/data1'),
       (2, 1, 1, '0755', 'TSM', 'ownergroup', 'NAS-server', 'rw', '/MNT/bin'),
       (3, 2, 1, '0755', 'TSM', 'ownergroup', 'NAS-server', 'rw,bg,hard', '/MNT/data2'),
       (4, 4, 1, '0755', 'TSM', 'ownergroup', 'NAS-server', 'rw,bg,hard,tcp', '/MNT/data4'),
       (5, 5, 1, '0755', 'TSM', 'ownergroup', 'NAS-server', 'rw,bg,hard', '/MNT/data5'),
       (6, 5, 1, '0755', 'TSM', 'ownergroup', 'NAS-server', 'rw', '/MNT/bin'),
       (7, 6, 1, '0755', 'TSM', 'ownergroup', 'NAS-server', 'rw', '/MNT/zk'),
       (8, 7, 1, '0755', 'TSM', 'ownergroup', 'NAS-server', 'rw', '/MNT/zk'),
       (9, 7, 2, '0755', 'TSM', 'ownergroup', 'NAS-server', 'rw,bg,hard', '/MNT/data01');
SELECT setval('volume_id_seq', (SELECT MAX(id) from public.volume));

INSERT INTO public.volume_attribute (id, volume_id, name, value)
VALUES (1, 8, 'ro', 'TRUE'),
       (2, 8, 'fw', 'TRUE'),
       (3, 9, 'ro', 'FALSE');
SELECT setval('volume_attribute_id_seq', (SELECT MAX(id) from public.volume_attribute));

-- Insert test data for database aliases
INSERT INTO public.functional_aliases (dns_name, db_name, alias)
VALUES ('db-apiato-dns01','apiato01','apiato-apiato-01.cern.ch'),
       ('db-apiato-dns02','apiato02','apiato-apiato-02.cern.ch'),
       ('db-apiato-dns03','apiato03','apiato-apiato-03.cern.ch'),
       ('db-apiato-dns04','apiato04','apiato-apiato-04.cern.ch'),
       ('db-apiato-dns05', NULL, NULL);

-- Insert test data for jobs
INSERT INTO public.job (id, instance_id, command_name, creation_date, completion_date, requester, admin_action, state, email_sent)
VALUES (1,1,'CLEANUP','01-AUG-17','01-AUG-17','user01','2','FINISHED_FAIL',NULL),
       (2,1,'BACKUP' ,'02-AUG-17','02-AUG-17','user01','2','PENDING'      ,NULL),
       (3,1,'CLEANUP','03-AUG-17','03-AUG-17','user01','2','FINISHED_OK'  ,NULL),
       (4,1,'BACKUP' ,'04-AUG-17','04-AUG-17','user01','2','FINISHED_OK'  ,NULL),
       (5,1,'CLEANUP','05-AUG-17','05-AUG-17','user01','2','FINISHED_OK'  ,NULL),
       (6,2,'CLEANUP','10-AUG-17','10-AUG-17','user02','2','FINISHED_OK'  ,NULL);
SELECT setval('job_id_seq', (SELECT MAX(id) from public.job));

-- Insert test data for job logs
INSERT INTO public.job_log (id, log)
VALUES (1,'
Thu Aug 01 10:51:44 CEST 2017 : RunTime.CleanUpOlderThanDays: on </DATA/database/apiato01/logs> removed older than <30>.
Thu Aug 01 10:51:44 CEST 2017 : RunTime.RunStr running find /DATA/database/apiato01/logs   -name \*  -mtime +30 -exec rm -rf {} \;
Thu Aug 01 10:51:45 CEST 2017 : RunTime.CleanUpOlderThanDays: done.
Thu Aug 01 10:51:45 CEST 2017 : Main: Starting
Thu Aug 01 10:51:47 CEST 2017 : RunTime.RunStr running hostname'),
       (2,'
Thu Aug 02 10:51:44 CEST 2017 : RunTime.CleanUpOlderThanDays: on </DATA/database/apiato01/logs> removed older than <30>.
Thu Aug 02 10:51:44 CEST 2017 : RunTime.RunStr running find /DATA/database/apiato01/logs   -name \*  -mtime +30 -exec rm -rf {} \;
Thu Aug 02 10:51:45 CEST 2017 : RunTime.CleanUpOlderThanDays: done.
Thu Aug 02 10:51:45 CEST 2017 : Main: Starting
Thu Aug 02 10:51:47 CEST 2017 : RunTime.RunStr running hostname'),
       (3,'
Thu Aug 03 10:51:44 CEST 2017 : RunTime.CleanUpOlderThanDays: on </DATA/database/apiato01/logs> removed older than <30>.
Thu Aug 03 10:51:44 CEST 2017 : RunTime.RunStr running find /DATA/database/apiato01/logs   -name \*  -mtime +30 -exec rm -rf {} \;
Thu Aug 03 10:51:45 CEST 2017 : RunTime.CleanUpOlderThanDays: done.
Thu Aug 03 10:51:45 CEST 2017 : Main: Starting
Thu Aug 03 10:51:47 CEST 2017 : RunTime.RunStr running hostname'),
       (4,'
Thu Aug 04 10:51:44 CEST 2017 : RunTime.CleanUpOlderThanDays: on </DATA/database/apiato01/logs> removed older than <30>.
Thu Aug 04 10:51:44 CEST 2017 : RunTime.RunStr running find /DATA/database/apiato01/logs   -name \*  -mtime +30 -exec rm -rf {} \;
Thu Aug 04 10:51:45 CEST 2017 : RunTime.CleanUpOlderThanDays: done.
Thu Aug 04 10:51:45 CEST 2017 : Main: Starting
Thu Aug 04 10:51:47 CEST 2017 : RunTime.RunStr running hostname'),
       (5,'
Thu Aug 05 10:51:44 CEST 2017 : RunTime.CleanUpOlderThanDays: on </DATA/database/apiato01/logs> removed older than <30>.
Thu Aug 05 10:51:44 CEST 2017 : RunTime.RunStr running find /DATA/database/apiato01/logs   -name \*  -mtime +30 -exec rm -rf {} \;
Thu Aug 05 10:51:45 CEST 2017 : RunTime.CleanUpOlderThanDays: done.
Thu Aug 05 10:51:45 CEST 2017 : Main: Starting
Thu Aug 05 10:51:47 CEST 2017 : RunTime.RunStr running hostname'),
       (6,'
Thu Aug 10 10:48:08 CEST 2017 : Main: Starting
Thu Aug 10 10:48:09 CEST 2017 : RunTime.RunStr running hostname
Thu Aug 10 10:48:13 CEST 2017 : RunTime_Zapi.GetVolInfoCmode : working with volume: </DATA/database/apiato02>
Thu Aug 10 10:48:13 CEST 2017 : RunTime_Zapi.GetVolInfoCmode: query looks like: 
 <volume-get-iter>
	<max-records>10</max-records>
	<query>
		<volume-attributes>
			<volume-id-attributes>
				<junction-path>/DATA/database/apiato02</junction-path>
			</volume-id-attributes>
		</volume-attributes>
	</query>
	<desired-attributes>
		<volume-autosize-attributes></volume-autosize-attributes>
		<volume-id-attributes></volume-id-attributes>
		<volume-space-attributes></volume-space-attributes>
		<volume-state-attributes></volume-state-attributes>
	</desired-attributes>
</volume-get-iter>
Thu Aug 10 10:49:02 CEST 2017 : Main: presnap actions completed successfully.
Thu Aug 10 10:49:02 CEST 2017 : Main: Master status:
 File	Position	Binlog_Do_DB	Binlog_Ignore_DB	Executed_Gtid_Set
 binlog.001940	120			

Thu Aug 10 10:49:02 CEST 2017 : RunTime::GetVersionDB: version <5617>.
Thu Aug 10 10:49:06 CEST 2017 : RunTime_Zapi::SnapCreate: Created!!
Thu Aug 10 10:49:06 CEST 2017 : Main: Success creating snapshot: <snapscript_553> on volume: <apiato02>.!
Thu Aug 10 10:49:06 CEST 2017 : Main: postnap actions completed successfully.
Thu Aug 10 10:49:06 CEST 2017 : Main: mysql_snapshot is over.
Thu Aug 10 10:49:06 CEST 2017 : mysql_snapshot.Main: State: [0]');

INSERT INTO public.fim_data (internal_id, instance_name, description, owner_account_type, owner_first_name, owner_last_name, owner_login, owner_mail, owner_phone1, owner_phone2, owner_portable_phone, owner_department, owner_group, owner_section)
VALUES ('abc1', 'apiato01', 'Test database 01', 'Personal', 'Alice', 'Lastname', 'user01', 'alice@cern.ch', '77550', NULL, NULL, 'ITC', 'DBC', 'EEC'),
       ('bcd2', 'apiato02', 'Test database 02', 'Personal', 'Alice', 'Lastname', 'user01', 'alice@cern.ch', '77550', NULL, NULL, 'ITC', 'DBC', 'EEC'),
       ('cde3', 'apiato04', 'Test database 02', 'System', 'Account', 'Services', 'user03', 'accounts@cern.ch', '88000', NULL, NULL, 'ACC', 'SSE', NULL);


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
INSERT INTO public.instance (id, owner, name, e_group, category, creation_date, type_id, size, no_connections, project, description, version, master_id, slave_id, host_id, state, status, cluster_id)
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
       
-- Insert test data for jobs
INSERT INTO api.job 
VALUES (1,1,'user01','dbod01','CLEANUP','MYSQL','01-AUG-17','01-AUG-17','user01','2','FINISHED_FAIL','
Thu Aug 01 10:51:44 CEST 2017 : RunTime.CleanUpOlderThanDays: on </DATA/database/dbod01/logs> removed older than <30>.
Thu Aug 01 10:51:44 CEST 2017 : RunTime.RunStr running find /DATA/database/dbod01/logs   -name \*  -mtime +30 -exec rm -rf {} \;
Thu Aug 01 10:51:45 CEST 2017 : RunTime.CleanUpOlderThanDays: done.
Thu Aug 01 10:51:45 CEST 2017 : Main: Starting
Thu Aug 01 10:51:47 CEST 2017 : RunTime.RunStr running hostname',NULL,NULL),
       (2,1,'user01','dbod01','BACKUP','MYSQL','02-AUG-17','02-AUG-17','user01','2','PENDING','
Thu Aug 02 10:51:44 CEST 2017 : RunTime.CleanUpOlderThanDays: on </DATA/database/dbod01/logs> removed older than <30>.
Thu Aug 02 10:51:44 CEST 2017 : RunTime.RunStr running find /DATA/database/dbod01/logs   -name \*  -mtime +30 -exec rm -rf {} \;
Thu Aug 02 10:51:45 CEST 2017 : RunTime.CleanUpOlderThanDays: done.
Thu Aug 02 10:51:45 CEST 2017 : Main: Starting
Thu Aug 02 10:51:47 CEST 2017 : RunTime.RunStr running hostname',NULL,NULL),
       (3,1,'user01','dbod01','CLEANUP','MYSQL','03-AUG-17','03-AUG-17','user01','2','FINISHED_OK','
Thu Aug 03 10:51:44 CEST 2017 : RunTime.CleanUpOlderThanDays: on </DATA/database/dbod01/logs> removed older than <30>.
Thu Aug 03 10:51:44 CEST 2017 : RunTime.RunStr running find /DATA/database/dbod01/logs   -name \*  -mtime +30 -exec rm -rf {} \;
Thu Aug 03 10:51:45 CEST 2017 : RunTime.CleanUpOlderThanDays: done.
Thu Aug 03 10:51:45 CEST 2017 : Main: Starting
Thu Aug 03 10:51:47 CEST 2017 : RunTime.RunStr running hostname',NULL,NULL),
       (4,1,'user01','dbod01','BACKUP','MYSQL','04-AUG-17','04-AUG-17','user01','2','FINISHED_OK','
Thu Aug 04 10:51:44 CEST 2017 : RunTime.CleanUpOlderThanDays: on </DATA/database/dbod01/logs> removed older than <30>.
Thu Aug 04 10:51:44 CEST 2017 : RunTime.RunStr running find /DATA/database/dbod01/logs   -name \*  -mtime +30 -exec rm -rf {} \;
Thu Aug 04 10:51:45 CEST 2017 : RunTime.CleanUpOlderThanDays: done.
Thu Aug 04 10:51:45 CEST 2017 : Main: Starting
Thu Aug 04 10:51:47 CEST 2017 : RunTime.RunStr running hostname',NULL,NULL),
       (5,1,'user01','dbod01','CLEANUP','MYSQL','05-AUG-17','05-AUG-17','user01','2','FINISHED_OK','
Thu Aug 05 10:51:44 CEST 2017 : RunTime.CleanUpOlderThanDays: on </DATA/database/dbod01/logs> removed older than <30>.
Thu Aug 05 10:51:44 CEST 2017 : RunTime.RunStr running find /DATA/database/dbod01/logs   -name \*  -mtime +30 -exec rm -rf {} \;
Thu Aug 05 10:51:45 CEST 2017 : RunTime.CleanUpOlderThanDays: done.
Thu Aug 05 10:51:45 CEST 2017 : Main: Starting
Thu Aug 05 10:51:47 CEST 2017 : RunTime.RunStr running hostname',NULL,NULL),
       (6,2,'user02','dbod02','CLEANUP','MYSQL','10-AUG-17','10-AUG-17','user02','2','FINISHED_OK','
Thu Aug 10 10:48:08 CEST 2017 : Main: Starting
Thu Aug 10 10:48:09 CEST 2017 : RunTime.RunStr running hostname
Thu Aug 10 10:48:13 CEST 2017 : RunTime_Zapi.GetVolInfoCmode : working with volume: </DATA/database/dbod02>
Thu Aug 10 10:48:13 CEST 2017 : RunTime_Zapi.GetVolInfoCmode: query looks like: 
 <volume-get-iter>
	<max-records>10</max-records>
	<query>
		<volume-attributes>
			<volume-id-attributes>
				<junction-path>/DATA/database/dbod02</junction-path>
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
Thu Aug 10 10:49:06 CEST 2017 : Main: Success creating snapshot: <snapscript_553> on volume: <dbod02>.!
Thu Aug 10 10:49:06 CEST 2017 : Main: postnap actions completed successfully.
Thu Aug 10 10:49:06 CEST 2017 : Main: mysql_snapshot is over.
Thu Aug 10 10:49:06 CEST 2017 : mysql_snapshot.Main: State: [0]',NULL,NULL);

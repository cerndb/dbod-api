INSERT INTO api.job VALUES (1,1,'user01','dbod01','CLEANUP','MYSQL','01-AUG-17','01-AUG-17','user01','2','FINISHED_FAIL','
Thu Aug 01 10:51:44 CEST 2017 : RunTime.CleanUpOlderThanDays: on </DATA/database/dbod01/logs> removed older than <30>.
Thu Aug 01 10:51:44 CEST 2017 : RunTime.RunStr running find /DATA/database/dbod01/logs   -name \*  -mtime +30 -exec rm -rf {} \;
Thu Aug 01 10:51:45 CEST 2017 : RunTime.CleanUpOlderThanDays: done.
Thu Aug 01 10:51:45 CEST 2017 : Main: Starting
Thu Aug 01 10:51:47 CEST 2017 : RunTime.RunStr running hostname
',NULL,NULL);
INSERT INTO api.job VALUES (2,1,'user01','dbod01','BACKUP','MYSQL','02-AUG-17','02-AUG-17','user01','2','PENDING','
Thu Aug 02 10:51:44 CEST 2017 : RunTime.CleanUpOlderThanDays: on </DATA/database/dbod01/logs> removed older than <30>.
Thu Aug 02 10:51:44 CEST 2017 : RunTime.RunStr running find /DATA/database/dbod01/logs   -name \*  -mtime +30 -exec rm -rf {} \;
Thu Aug 02 10:51:45 CEST 2017 : RunTime.CleanUpOlderThanDays: done.
Thu Aug 02 10:51:45 CEST 2017 : Main: Starting
Thu Aug 02 10:51:47 CEST 2017 : RunTime.RunStr running hostname
',NULL,NULL);
INSERT INTO api.job VALUES (3,1,'user01','dbod01','CLEANUP','MYSQL','03-AUG-17','03-AUG-17','user01','2','FINISHED_OK','
Thu Aug 03 10:51:44 CEST 2017 : RunTime.CleanUpOlderThanDays: on </DATA/database/dbod01/logs> removed older than <30>.
Thu Aug 03 10:51:44 CEST 2017 : RunTime.RunStr running find /DATA/database/dbod01/logs   -name \*  -mtime +30 -exec rm -rf {} \;
Thu Aug 03 10:51:45 CEST 2017 : RunTime.CleanUpOlderThanDays: done.
Thu Aug 03 10:51:45 CEST 2017 : Main: Starting
Thu Aug 03 10:51:47 CEST 2017 : RunTime.RunStr running hostname
',NULL,NULL);
INSERT INTO api.job VALUES (4,1,'user01','dbod01','BACKUP','MYSQL','04-AUG-17','04-AUG-17','user01','2','FINISHED_OK','
Thu Aug 04 10:51:44 CEST 2017 : RunTime.CleanUpOlderThanDays: on </DATA/database/dbod01/logs> removed older than <30>.
Thu Aug 04 10:51:44 CEST 2017 : RunTime.RunStr running find /DATA/database/dbod01/logs   -name \*  -mtime +30 -exec rm -rf {} \;
Thu Aug 04 10:51:45 CEST 2017 : RunTime.CleanUpOlderThanDays: done.
Thu Aug 04 10:51:45 CEST 2017 : Main: Starting
Thu Aug 04 10:51:47 CEST 2017 : RunTime.RunStr running hostname
',NULL,NULL);
INSERT INTO api.job VALUES (5,1,'user01','dbod01','CLEANUP','MYSQL','05-AUG-17','05-AUG-17','user01','2','FINISHED_OK','
Thu Aug 05 10:51:44 CEST 2017 : RunTime.CleanUpOlderThanDays: on </DATA/database/dbod01/logs> removed older than <30>.
Thu Aug 05 10:51:44 CEST 2017 : RunTime.RunStr running find /DATA/database/dbod01/logs   -name \*  -mtime +30 -exec rm -rf {} \;
Thu Aug 05 10:51:45 CEST 2017 : RunTime.CleanUpOlderThanDays: done.
Thu Aug 05 10:51:45 CEST 2017 : Main: Starting
Thu Aug 05 10:51:47 CEST 2017 : RunTime.RunStr running hostname
',NULL,NULL);
INSERT INTO api.job VALUES (6,2,'user02','dbod02','CLEANUP','MYSQL','10-AUG-17','10-AUG-17','user02','2','FINISHED_OK','
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
Thu Aug 10 10:49:06 CEST 2017 : mysql_snapshot.Main: State: [0]
',NULL,NULL);
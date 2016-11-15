INSERT INTO apiato.instance_type (type, description)
    VALUES ('zookeeper','zookeeper instance type');

INSERT INTO apiato.host (name, memory)
    VALUES ('nile-zookeeper-sec-dev-1','2');

INSERT INTO apiato.host (name, memory)
    VALUES ('nile-zookeeper-sec-dev-2','2');

INSERT INTO apiato.host (name, memory)
   VALUES ('nile-zookeeper-sec-dev-3','2');

INSERT INTO apiato.cluster (owner, name, e_group, category, creation_date, expiry_date, instance_type_id, project, description, version, master_cluster_id, state, status)
  VALUES ('zookeeper','cluster_nile-zookeeper-sec-dev-1','it-db-nile-admins','DEV',CURRENT_TIMESTAMP,NULL,1,'Nile development','Secured Zookeeper cluster for NILE dev', NULL,NULL,'RUNNING','ACTIVE');

INSERT INTO apiato.instance (owner, name, e_group, category, creation_date, expiry_date, instance_type_id, project, description, version, master_instance_id, host_id, state, status, cluster_id)
  VALUES ('zookeeper','node_nile-zookeeper-sec-dev-1','it-db-nile-admins','DEV',CURRENT_TIMESTAMP,NULL,1,'Nile development','Secured Zookeeper cluster node for NILE dev', NULL, NULL, 1,'RUNNING','ACTIVE',1);

INSERT INTO apiato.instance (owner, name, e_group, category, creation_date, expiry_date, instance_type_id, project, description, version, master_instance_id, host_id, state, status, cluster_id)
  VALUES ('zookeeper','node_nile-zookeeper-sec-dev-2','it-db-nile-admins','DEV',CURRENT_TIMESTAMP,NULL,1,'Nile development','Secured Zookeeper cluster node for NILE dev', NULL, NULL, 2,'RUNNING','ACTIVE',1);

INSERT INTO apiato.instance (owner, name, e_group, category, creation_date, expiry_date, instance_type_id, project, description, version, master_instance_id, host_id, state, status, cluster_id)
  VALUES ('zookeeper','node_nile-zookeeper-sec-dev-3','it-db-nile-admins','DEV',CURRENT_TIMESTAMP,NULL,1,'Nile development','Secured Zookeeper cluster node for NILE dev', NULL, NULL, 3,'RUNNING','ACTIVE',1);

INSERT INTO apiato.cluster_attribute (cluster_id, name, value)
    VALUES (1,'use_sasl_auth','true');

INSERT INTO apiato.cluster_attribute (cluster_id, name, value)
    VALUES (1,'service','zookeeper');

INSERT INTO apiato.cluster_attribute (cluster_id, name, value)
    VALUES (1,'path','/etc/zookeeper/conf/');

INSERT INTO apiato.cluster_attribute (cluster_id, name, value)
    VALUES (1,'user','zookeeper');

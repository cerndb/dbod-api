DROP SCHEMA apiato CASCADE;
DROP SCHEMA apiato_ro CASCADE;
CREATE SCHEMA IF NOT EXISTS apiato;
CREATE SCHEMA IF NOT EXISTS apiato_ro;

------------------------------------------
-- TYPES
------------------------------------------
CREATE TYPE apiato.instance_state AS ENUM (
  'RUNNING',
  'MAINTENANCE',
  'AWATING-APPROVAL',
  'JOB-PENDING'
);

CREATE TYPE apiato.instance_status AS ENUM (
  'ACTIVE',
  'NON-ACTIVE'
);

CREATE TYPE apiato.instance_category AS ENUM (
  'PROD',
  'DEV',
  'TEST',
  'QA',
  'REF'
);

CREATE TYPE apiato.job_state AS ENUM (
  'FINISHED_FAIL',
  'FINISHED_OK'
);

------------------------------------------
-- LOV TABLES
------------------------------------------

--INSTANCE_TYPE
CREATE TABLE apiato.instance_type (
  instance_type_id serial,
  type             varchar(64) UNIQUE NOT NULL,
  description      varchar(1024),
  CONSTRAINT instance_type_pkey PRIMARY KEY (instance_type_id)
);

--VOLUME_TYPE
CREATE TABLE apiato.volume_type (
  volume_type_id   serial,
  type             varchar(64) UNIQUE NOT NULL,
  description      varchar(1024),
  CONSTRAINT volume_type_pkey PRIMARY KEY (volume_type_id)
);

------------------------------------------
-- TABLES
------------------------------------------
-- CLUSTER
CREATE TABLE apiato.cluster (
  cluster_id           serial,
  owner                varchar(32) NOT NULL,
  name                 varchar(128) UNIQUE NOT NULL,
  e_group              varchar(256),
  category             apiato.instance_category NOT NULL,
  creation_date        date NOT NULL,
  expiry_date          date,
  instance_type_id     int NOT NULL,
  project              varchar(128),
  description          varchar(1024),
  version              varchar(128),
  master_cluster_id    int,
  state                apiato.instance_state NOT NULL,
  status               apiato.instance_status NOT NULL,
  CONSTRAINT cluster_pkey               PRIMARY KEY (cluster_id),
  CONSTRAINT cluster_master_fk          FOREIGN KEY (master_cluster_id) REFERENCES apiato.cluster (cluster_id),
  CONSTRAINT cluster_instance_type_fk   FOREIGN KEY (instance_type_id)   REFERENCES apiato.instance_type (instance_type_id)
);
--FK INDEXES for CLUSTER table
CREATE INDEX cluster_master_idx ON apiato.cluster (master_cluster_id);
CREATE INDEX cluster_type_idx   ON apiato.cluster (instance_type_id);

-- HOST
CREATE TABLE apiato.host (
  host_id  serial,
  name     varchar(63) UNIQUE NOT NULL,
  memory   integer NOT NULL,
  CONSTRAINT host_pkey PRIMARY KEY (host_id)
);

-- INSTANCES
CREATE TABLE apiato.instance (
    instance_id          serial,
    owner                varchar(32) NOT NULL,
    name                 varchar(128) UNIQUE NOT NULL,
    e_group              varchar(256),
    category             apiato.instance_category NOT NULL,
    creation_date        date NOT NULL,
    expiry_date          date,
    instance_type_id     int NOT NULL,
    size                 int,
    no_connections       int,
    project              varchar(128),
    description          varchar(1024),
    version              varchar(128),
    master_instance_id   int,
    slave_instance_id    int,
    host_id              int,
    state                apiato.instance_state NOT NULL,
    status               apiato.instance_status NOT NULL,
    cluster_id           int,
    CONSTRAINT instance_pkey               PRIMARY KEY (instance_id),
    CONSTRAINT instance_master_fk          FOREIGN KEY (master_instance_id) REFERENCES apiato.instance (instance_id),
    CONSTRAINT instance_slave_fk           FOREIGN KEY (slave_instance_id)  REFERENCES apiato.instance (instance_id),
    CONSTRAINT instance_host_fk            FOREIGN KEY (host_id)            REFERENCES apiato.host     (host_id),
    CONSTRAINT instance_instance_type_fk   FOREIGN KEY (instance_type_id)   REFERENCES apiato.instance_type (instance_type_id),
    CONSTRAINT instance_cluster_fk         FOREIGN KEY (cluster_id)         REFERENCES apiato.cluster (cluster_id) ON DELETE CASCADE
);
--FK INDEXES for INSTANCE table
CREATE INDEX instance_host_idx      ON apiato.instance (host_id);
CREATE INDEX instance_master_idx    ON apiato.instance (master_instance_id);
CREATE INDEX instance_slave_idx     ON apiato.instance (slave_instance_id);
CREATE INDEX instance_type_idx      ON apiato.instance (instance_type_id);
CREATE INDEX instance_cluster_idx   ON apiato.cluster  (cluster_id);


-- INSTANCE_ATTRIBUTES
CREATE TABLE apiato.instance_attribute (
  attribute_id serial,
  instance_id  integer NOT NULL,
  name         varchar(32) NOT NULL,
  value        varchar(250) NOT NULL,
  CONSTRAINT instance_attribute_pkey        PRIMARY KEY (attribute_id),
  CONSTRAINT instance_attribute_instance_fk FOREIGN KEY (instance_id) REFERENCES apiato.instance (instance_id) ON DELETE CASCADE,
  UNIQUE (instance_id, name)
);
CREATE INDEX instance_attribute_instance_idx ON apiato.instance_attribute (instance_id);



-- CLUSTER_ATTRIBUTES
CREATE TABLE apiato.cluster_attribute (
  attribute_id serial,
  cluster_id   integer NOT NULL,
  name         varchar(32) NOT NULL,
  value        varchar(250) NOT NULL,
  CONSTRAINT cluster_attribute_pkey        PRIMARY KEY (attribute_id),
  CONSTRAINT cluster_attribute_cluster_fk FOREIGN KEY (cluster_id) REFERENCES apiato.cluster (cluster_id) ON DELETE CASCADE,
  UNIQUE (cluster_id, name)
);
CREATE INDEX cluster_attribute_cluster_idx ON apiato.cluster_attribute (cluster_id);

-- JOBS
CREATE TABLE apiato.job (
    job_id          serial,
    instance_id     int NOT NULL,
    name            varchar(64) NOT NULL,
    creation_date   date NOT NULL,
    completion_date date,
    requester       varchar(32) NOT NULL,
    admin_action    int NOT NULL,
    state           apiato.job_state NOT NULL,
    log             text,
    result          varchar(2048),
    email_sent      date,
    CONSTRAINT job_pkey        PRIMARY KEY (job_id),
    CONSTRAINT job_instance_fk FOREIGN KEY (instance_id) REFERENCES apiato.instance (instance_id)

);
CREATE INDEX job_instance_idx ON apiato.job (instance_id);


-- VOLUME
CREATE TABLE apiato.volume (
  volume_id       serial,
  instance_id     integer NOT NULL,
  file_mode       char(4) NOT NULL,
  owner           varchar(32) NOT NULL,
  "group"         varchar(32) NOT NULL,
  server          varchar(63) NOT NULL,
  mount_options   varchar(256) NOT NULL,
  mounting_path   varchar(256) NOT NULL,
  volume_type_id  int NOT NULL,
  CONSTRAINT volume_pkey           PRIMARY KEY (volume_id),
  CONSTRAINT volume_instance_fk    FOREIGN KEY (instance_id)    REFERENCES apiato.instance (instance_id),
  CONSTRAINT volume_volume_type_fk FOREIGN KEY (volume_type_id) REFERENCES apiato.volume_type (volume_type_id)
);
CREATE INDEX volume_instance_idx    ON apiato.volume (instance_id);
CREATE INDEX volume_volume_type_idx ON apiato.volume (volume_type_id);


-- VOLUME_ATTRIBUTE
CREATE TABLE apiato.volume_attribute (
  attribute_id serial,
  volume_id    integer NOT NULL,
  name         varchar(32) NOT NULL,
  value        varchar(250) NOT NULL,
  CONSTRAINT volume_attribute_pkey       PRIMARY KEY (attribute_id),
  CONSTRAINT volume_attribute_volume_fk  FOREIGN KEY (volume_id) REFERENCES apiato.volume (volume_id),
  UNIQUE (volume_id, name)
);
CREATE INDEX volume_attribute_volume_idx ON apiato.volume_attribute (volume_id);


-- Functional aliases table
CREATE TABLE apiato.functional_alias
(
  functional_alias_id serial,
  dns_name            character varying(256) UNIQUE NOT NULL,
  instance_id         int,
  alias               character varying(256),
  CONSTRAINT functional_alias_pkey        PRIMARY KEY (functional_alias_id),
  CONSTRAINT functional_alias_instance_fk FOREIGN KEY (instance_id)    REFERENCES apiato.instance (instance_id)
);
CREATE INDEX functional_alias_instance_idx ON apiato.functional_alias (instance_id);

------------------------------
-- FUNCTIONS
------------------------------

-- Get hosts function
CREATE OR REPLACE FUNCTION apiato.get_hosts(host_ids INTEGER[])
RETURNS VARCHAR[] AS $$
DECLARE
  hosts VARCHAR := '';
BEGIN
  SELECT ARRAY (SELECT name FROM host WHERE host_id = ANY(host_ids)) INTO hosts;
  RETURN hosts;
END
$$ LANGUAGE plpgsql;


-- Get volumes function
CREATE OR REPLACE FUNCTION apiato.get_volumes(pid INTEGER)
RETURNS JSON[] AS $$
DECLARE
  volumes JSON[];
BEGIN
  SELECT ARRAY (SELECT row_to_json(t) FROM (SELECT * FROM apiato.volume WHERE instance_id = pid) t) INTO volumes;
  return volumes;
END
$$ LANGUAGE plpgsql;

-- Get instance attribute function
CREATE OR REPLACE FUNCTION apiato.get_instance_attribute(attr_name VARCHAR, inst_id INTEGER)
RETURNS VARCHAR AS $$
DECLARE
  res VARCHAR;
BEGIN
  SELECT value FROM apiato.instance_attribute A WHERE A.instance_id = inst_id AND A.name = attr_name INTO res;
  return res;
END
$$ LANGUAGE plpgsql;

-- Get instance attribute function
CREATE OR REPLACE FUNCTION apiato.get_volume_attribute(attr_name VARCHAR, vol_id INTEGER)
  RETURNS VARCHAR AS $$
DECLARE
  res VARCHAR;
BEGIN
  SELECT value FROM apiato.volume_attribute A WHERE A.instance_id = vol_id AND A.name = attr_name INTO res;
  return res;
END
$$ LANGUAGE plpgsql;

-- Get instance attribute function
CREATE OR REPLACE FUNCTION apiato.get_cluster_attribute(attr_name VARCHAR, clus_id INTEGER)
  RETURNS VARCHAR AS $$
DECLARE
  res VARCHAR;
BEGIN
  SELECT value FROM apiato.cluster_attribute A WHERE A.cluster_id = clus_id AND A.name = attr_name INTO res;
  return res;
END
$$ LANGUAGE plpgsql;

-- Get attributes function
CREATE OR REPLACE FUNCTION apiato.get_instance_attributes(inst_id INTEGER)
  RETURNS JSON AS $$
DECLARE
  attributes JSON;
BEGIN
  SELECT json_object(j.body::text[]) FROM
    (SELECT '{' || string_agg( buf, ',' ) || '}' body
     FROM
       (SELECT  name::text || ', ' || value::text buf
        FROM apiato.instance_attribute
        WHERE instance_id = inst_id) t) j INTO attributes;
  return attributes;
END
$$ LANGUAGE plpgsql;

-- Get attributes function
CREATE OR REPLACE FUNCTION apiato.get_volume_attributes(vol_id INTEGER)
  RETURNS JSON AS $$
DECLARE
  attributes JSON;
BEGIN
  SELECT json_object(j.body::text[]) FROM
    (SELECT '{' || string_agg( buf, ',' ) || '}' body
     FROM
       (SELECT  name::text || ', ' || value::text buf
        FROM apiato.volume_attribute
        WHERE instance_id = vol_id) t) j INTO attributes;
  return attributes;
END
$$ LANGUAGE plpgsql;

-- Get attributes function
CREATE OR REPLACE FUNCTION apiato.get_cluster_attributes(clus_id INTEGER)
  RETURNS JSON AS $$
DECLARE
  attributes JSON;
BEGIN
  SELECT json_object(j.body::text[]) FROM
    (SELECT '{' || string_agg( buf, ',' ) || '}' body
     FROM
       (SELECT  name::text || ', ' || value::text buf
        FROM apiato.cluster_attribute
        WHERE cluster_id = clus_id) t) j INTO attributes;
  return attributes;
END
$$ LANGUAGE plpgsql;

-- Get attributes function
CREATE OR REPLACE FUNCTION apiato.get_cluster_instances(clus_id INTEGER)
RETURNS JSON[] AS $$
DECLARE
  instances JSON[];
BEGIN
  SELECT ARRAY (SELECT row_to_json(t) FROM (SELECT * FROM apiato_ro.metadata WHERE cluster_id = clus_id) t) INTO instances;
  return instances;
END
$$ LANGUAGE plpgsql;


------------------------------
-- VIEWS
------------------------------

--Host
CREATE OR REPLACE VIEW apiato_ro.host AS
SELECT host.host_id AS id,
       host.name,
       host.memory
FROM apiato.host;

-- Instance View
CREATE OR REPLACE VIEW apiato_ro.instance AS
SELECT instance.instance_id AS id,
       instance.owner AS username,
       instance.name,
       instance.e_group,
       instance.category "class",
       instance.creation_date,
       instance.expiry_date,
       instance_type.type AS type,
       instance.project,
       instance.description,
       instance_master.name AS master,
       instance_slave.name AS slave,
       host.name AS host,
       instance.state,
       instance.status
FROM apiato.instance
  LEFT JOIN apiato.instance AS instance_master ON apiato.instance.instance_id = instance_master.instance_id
  LEFT JOIN apiato.instance AS instance_slave ON apiato.instance.instance_id = instance_slave.instance_id
  JOIN apiato.instance_type ON apiato.instance.instance_type_id = apiato.instance_type.instance_type_id
  JOIN apiato.host ON apiato.instance.host_id = apiato.host.host_id;


CREATE OR REPLACE VIEW apiato_ro.cluster_attributes AS
SELECT
      apiato.cluster.cluster_id,
      apiato.get_cluster_attributes(apiato.cluster.cluster_id) as attributes
FROM apiato.cluster;

CREATE OR REPLACE VIEW apiato_ro.instance_attributes AS
SELECT
      apiato.instance.instance_id,
      apiato.get_instance_attributes(apiato.instance.instance_id) as attributes
FROM apiato.instance;

CREATE OR REPLACE VIEW apiato_ro.volume_attributes AS
SELECT
      apiato.volume.volume_id,
      apiato.get_volume_attributes(apiato.volume.volume_id) as attributes
FROM apiato.volume;

-- Volume View
CREATE OR REPLACE VIEW apiato_ro.volume AS
SELECT volume.volume_id AS id,
       volume.instance_id,
       apiato.volume_type.type AS type,
       volume.server,
       volume.mounting_path
FROM apiato.volume
  JOIN apiato.volume_type ON apiato.volume.volume_type_id = apiato.volume_type.volume_type_id;

-- Metadata View
CREATE OR REPLACE VIEW apiato_ro.metadata AS
  SELECT
    instance.instance_id AS id,
    instance.owner AS username,
    instance.name AS db_name,
    instance.category "class",
    instance_type.type AS type,
    instance.version,
    string_to_array(host.name::text, ','::text) as hosts,
    apiato.get_instance_attributes(apiato.instance.instance_id) attributes,
    apiato.get_instance_attribute('port', apiato.instance.instance_id ) port,
    get_volumes volumes,
    instance.cluster_id
  FROM apiato.instance
    JOIN apiato.instance_type ON apiato.instance.instance_type_id = apiato.instance_type.instance_type_id
    LEFT JOIN apiato.host ON apiato.instance.host_id = apiato.host.host_id,
    apiato.get_volumes(apiato.instance.instance_id);


-- cluster View
CREATE OR REPLACE VIEW apiato_ro.cluster AS
  SELECT
    cluster.cluster_id AS id,
    cluster.owner AS username,
    cluster.name AS name,
    cluster.e_group,
    cluster.project,
    cluster.description,
    cluster.category "class",
    instance_type.type AS type,
    cluster.version,
    cluster_master.name AS master_name,
    get_cluster_instances as instances,
    apiato.get_cluster_attributes(apiato.cluster.cluster_id) as attributes,
    apiato.get_cluster_attribute('port', apiato.cluster.cluster_id ) port
  FROM apiato.cluster
    JOIN apiato.instance_type ON apiato.cluster.instance_type_id = apiato.instance_type.instance_type_id
    LEFT JOIN apiato.cluster AS cluster_master ON apiato.cluster.cluster_id = cluster_master.master_cluster_id,
      apiato.get_cluster_instances(apiato.cluster.cluster_id);


-- Functional Aliases View
CREATE OR REPLACE VIEW apiato_ro.functional_alias AS
  SELECT functional_alias.functional_alias_id AS id,
         apiato.instance.instance_id,
         functional_alias.dns_name,
         apiato.instance.name AS name,
         functional_alias.alias
  FROM apiato.functional_alias
  LEFT JOIN apiato.instance ON apiato.functional_alias.instance_id = apiato.instance.instance_id ;

-- Rundeck instances View
CREATE OR REPLACE VIEW apiato_ro.rundeck_instance AS
  SELECT apiato.instance.name AS db_name,
         apiato.functional_alias.alias AS hostname,
         apiato.get_instance_attribute('port', apiato.instance.instance_id) AS port,
         'dbod'::CHAR(4) AS username,
         apiato.instance_type.type AS db_type,
         apiato.instance.category AS category,
         apiato.instance_type.type || ',' || category AS tags
  FROM apiato.instance
    JOIN apiato.functional_alias ON apiato.instance.instance_id = apiato.functional_alias.instance_id
    JOIN apiato.instance_type ON apiato.instance.instance_type_id = apiato.instance_type.instance_type_id;

-- Host aliases View
CREATE OR REPLACE VIEW apiato_ro.host_alias AS
  SELECT host.name AS host,
         array_agg('dbod-' || regexp_replace(apiato.instance.name, '_', '-', 'g') || '.cern.ch') AS aliases
  FROM apiato.instance
    JOIN apiato.host ON apiato.instance.host_id = apiato.host.host_id
  GROUP BY host;


-------------------------------
-- Test values
-------------------------------
INSERT INTO apiato.volume_type (type, description)
    VALUES ('NETAPP', 'NETAPP volume type');

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
       (6, 1, '0755', 'TSM', 'ownergroup', 'NAS-server', 'rw', '/MNT/zk');

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

-- Insert test data for functional aliases
INSERT INTO apiato.functional_alias (dns_name, instance_id, alias)
VALUES ('db-dbod-dns01', 1   , 'dbod-dbod-01.cern.ch'),
       ('db-dbod-dns02', 2   , 'dbod-dbod-02.cern.ch'),
       ('db-dbod-dns03', 3   , 'dbod-dbod-03.cern.ch'),
       ('db-dbod-dns04', 4   , 'dbod-dbod-04.cern.ch'),
       ('db-dbod-dns05', NULL, NULL);


--------------------------------
-- INSERT PROCEDURES
--------------------------------
--Clusters
CREATE OR REPLACE FUNCTION apiato_ro.insert_cluster(in_json JSON) RETURNS INTEGER AS $$
DECLARE
  cluster_id      int;
  cluster_json    json;
  attributes_json json;
BEGIN
  --Get the new cluster_id to be used in the insertion
   SELECT nextval(pg_get_serial_sequence('apiato.cluster', 'cluster_id')) INTO cluster_id;
   cluster_json := in_json::jsonb || ('{ "cluster_id" :' || cluster_id || '}')::jsonb;

   INSERT INTO apiato.cluster SELECT * FROM json_populate_record(null::apiato.cluster,cluster_json);

   --Inserting Attributes
   attributes_json := cluster_json::json->'attributes';
   PERFORM apiato_ro.insert_cluster_attributes((json_array_elements(attributes_json)::jsonb || ('{ "cluster_id" :' || cluster_id || '}')::jsonb)::json);

  RETURN cluster_id;
END
$$ LANGUAGE plpgsql;


--Cluster Attributes
CREATE OR REPLACE FUNCTION apiato_ro.insert_cluster_attributes(in_json JSON) RETURNS INTEGER AS $$
DECLARE
  attribute_id    int;
  cluster_id      int;
  attributes_json json;
BEGIN

   --Get the new cluster_id to be used in the insertion
   SELECT nextval(pg_get_serial_sequence('apiato.cluster_attribute', 'attribute_id')) INTO attribute_id;
   attributes_json := in_json::jsonb || ('{ "attribute_id" :' || attribute_id || '}')::jsonb;

   INSERT INTO apiato.cluster_attribute SELECT * FROM json_populate_record(null::apiato.cluster_attribute,attributes_json);

  RETURN attribute_id;
END
$$ LANGUAGE plpgsql;

--Instance Attributes
CREATE OR REPLACE FUNCTION apiato_ro.insert_instance_attributes(in_json JSON) RETURNS INTEGER AS $$
DECLARE
  attribute_id    int;
  instance_id      int;
  attributes_json json;
BEGIN

   --Get the new cluster_id to be used in the insertion
   SELECT nextval(pg_get_serial_sequence('apiato.instance_attribute', 'attribute_id')) INTO attribute_id;
   attributes_json := in_json::jsonb || ('{ "attribute_id" :' || attribute_id || '}')::jsonb;

   INSERT INTO apiato.instance_attribute SELECT * FROM json_populate_record(null::apiato.instance_attribute,attributes_json);

  RETURN attribute_id;
END
$$ LANGUAGE plpgsql;

--Functional Alias
CREATE OR REPLACE FUNCTION apiato_ro.insert_functional_alias(in_json JSON) RETURNS bool AS $$
DECLARE
   success     bool;
  in_dns_name  VARCHAR ;
BEGIN

    SELECT apiato_ro.functional_alias.dns_name INTO in_dns_name
     FROM apiato_ro.functional_alias
    WHERE apiato_ro.functional_alias.name IS NULL
      AND apiato_ro.functional_alias.alias IS NULL
  ORDER BY apiato_ro.functional_alias.dns_name ASC LIMIT 1;

    UPDATE apiato.functional_alias
      SET instance_id=(in_json->>'instance_id')::int, alias = in_json->>'alias'
    WHERE apiato.functional_alias.dns_name = in_dns_name
      AND (in_json->>'instance_id')::int NOT IN (SELECT a.instance_id FROM apiato.functional_alias a WHERE a.instance_id IS NOT NULL)
      RETURNING TRUE INTO success;

    RETURN success;
END
$$ LANGUAGE plpgsql;

--Volume Attributes
CREATE OR REPLACE FUNCTION apiato_ro.insert_volume_attributes(in_json JSON) RETURNS INTEGER AS $$
DECLARE
  attribute_id     int;
  instance_id      int;
  attributes_json json;
BEGIN
   --Get the new attribute_id to be used in the insertion
   SELECT nextval(pg_get_serial_sequence('apiato.volume_attribute', 'attribute_id')) INTO attribute_id;
   attributes_json := in_json::jsonb || ('{ "attribute_id" :' || attribute_id || '}')::jsonb;

   INSERT INTO apiato.volume_attribute SELECT * FROM json_populate_record(null::apiato.volume_attribute, attributes_json);

  RETURN attribute_id;
END
$$ LANGUAGE plpgsql;

--Volume
CREATE OR REPLACE FUNCTION apiato_ro.insert_volume(in_json JSON) RETURNS INTEGER AS $$
DECLARE
  volume_id       int;
  volume_json     json;
  attributes_json json;
BEGIN
  --Get the new volume_id to be used in the insertion
   SELECT nextval(pg_get_serial_sequence('apiato.volume', 'volume_id')) INTO volume_id;
   volume_json := in_json::jsonb || ('{ "volume_id" :' || volume_id || '}')::jsonb;

   INSERT INTO apiato.volume SELECT * FROM json_populate_record(null::apiato.volume, volume_json);

   --Inserting Attributes
   attributes_json := volume_json::json->'attributes';
   PERFORM apiato_ro.insert_volume_attributes((json_array_elements(attributes_json)::jsonb || ('{ "volume_id" :' || volume_id || '}')::jsonb)::json);

  RETURN volume_id;
END
$$ LANGUAGE plpgsql;

--Instance
CREATE OR REPLACE FUNCTION apiato_ro.insert_instance(in_json JSON) RETURNS INTEGER AS $$
DECLARE
  instance_id     int;
  instance_json   json;
  volumes_json    json;
  attributes_json json;
BEGIN
  --Get the new instance_id to be used in the insertion
   SELECT nextval(pg_get_serial_sequence('apiato.instance', 'instance_id')) INTO instance_id;
   instance_json := in_json::jsonb || ('{ "instance_id" :' || instance_id || '}')::jsonb;

   INSERT INTO apiato.instance SELECT * FROM json_populate_record(null::apiato.instance, instance_json);

   --Inserting Attributes
   attributes_json := instance_json::json->'attributes';
   PERFORM apiato_ro.insert_instance_attributes((json_array_elements(attributes_json)::jsonb || ('{ "instance_id" :' || instance_id || '}')::jsonb)::json);
   
   --Inserting Volumes
   volumes_json := instance_json::json->'volumes';
   PERFORM apiato_ro.insert_volume((json_array_elements(volumes_json)::jsonb || ('{ "instance_id" :' || instance_id || '}')::jsonb)::json);

  RETURN instance_id;
END
$$ LANGUAGE plpgsql;


--Cluster Attributes
CREATE OR REPLACE FUNCTION apiato_ro.insert_host(in_json JSON) RETURNS INTEGER AS $$
DECLARE
  host_id    int;
  host_json  json;
BEGIN

   --Get the new cluster_id to be used in the insertion
   SELECT nextval(pg_get_serial_sequence('apiato.host', 'host_id')) INTO host_id;
   host_json := in_json::jsonb || ('{ "host_id" :' || host_id || '}')::jsonb;

   INSERT INTO apiato.host SELECT * FROM json_populate_record(null::apiato.host,host_json);

  RETURN host_id;
END
$$ LANGUAGE plpgsql;

-----------------------------------
--DELETE PROCEDURES
-----------------------------------
--Clusters
CREATE OR REPLACE FUNCTION apiato_ro.delete_cluster(id INT) RETURNS bool AS $$
DECLARE
 success bool;
BEGIN

   DELETE FROM apiato.cluster WHERE cluster_id = id RETURNING TRUE INTO success;

RETURN success;
END
$$ LANGUAGE plpgsql;

--Hosts
CREATE OR REPLACE FUNCTION apiato_ro.delete_host(id INT) RETURNS bool AS $$
DECLARE
 success bool;
BEGIN

   DELETE FROM apiato.host WHERE host_id = id RETURNING TRUE INTO success;

RETURN success;
END
$$ LANGUAGE plpgsql;


--Functional alias
CREATE OR REPLACE FUNCTION apiato_ro.delete_functional_alias(id INT) RETURNS bool AS $$
DECLARE
 success bool;
BEGIN

   UPDATE apiato.functional_alias SET instance_id = NULL, alias=NULL WHERE functional_alias_id = id RETURNING TRUE INTO success;

RETURN success;
END
$$ LANGUAGE plpgsql;


--Instance
CREATE OR REPLACE FUNCTION apiato_ro.delete_instance(id int) RETURNS bool AS $$
DECLARE
 success bool;
BEGIN

   EXECUTE format(' DELETE FROM apiato.instance WHERE instance_id = $1 RETURNING TRUE') USING id INTO success;

RETURN success;
END
$$ LANGUAGE plpgsql;


--Volume
CREATE OR REPLACE FUNCTION apiato_ro.delete_volume(id int) RETURNS bool AS $$
DECLARE
 success bool;
BEGIN

   EXECUTE format(' DELETE FROM apiato.volume WHERE volume_id = $1 RETURNING TRUE') USING id INTO success;

RETURN success;
END
$$ LANGUAGE plpgsql;


-----------------------------------
--UPDATE PROCEDURES
-----------------------------------
--Clusters
CREATE OR REPLACE FUNCTION apiato_ro.update_cluster(in_json JSON) RETURNS bool AS $$
DECLARE
 success bool;
BEGIN

   UPDATE apiato.cluster
    SET owner             = (CASE WHEN src.in_json::jsonb ? 'owner' THEN src.owner ELSE apiato.cluster.owner END),
        name              = (CASE WHEN src.in_json::jsonb ? 'name' THEN src.name ELSE apiato.cluster.name END),
        e_group           = (CASE WHEN src.in_json::jsonb ? 'e_group' THEN src.e_group ELSE apiato.cluster.e_group END),
        category          = (CASE WHEN src.in_json::jsonb ? 'category' THEN src.category ELSE apiato.cluster.category END),
        creation_date     = (CASE WHEN src.in_json::jsonb ? 'creation_date' THEN src.creation_date ELSE apiato.cluster.creation_date END),
        expiry_date       = (CASE WHEN src.in_json::jsonb ? 'expiry_date' THEN src.expiry_date ELSE apiato.cluster.expiry_date END),
        instance_type_id  = (CASE WHEN src.in_json::jsonb ? 'instance_type_id' THEN src.instance_type_id ELSE apiato.cluster.instance_type_id END),
        project           = (CASE WHEN src.in_json::jsonb ? 'project' THEN src.project ELSE apiato.cluster.project END),
        description       = (CASE WHEN src.in_json::jsonb ? 'description' THEN src.description ELSE apiato.cluster.description END),
        version           = (CASE WHEN src.in_json::jsonb ? 'version' THEN src.version ELSE apiato.cluster.version END),
        master_cluster_id = (CASE WHEN src.in_json::jsonb ? 'master_cluster_id' THEN src.master_cluster_id ELSE apiato.cluster.master_cluster_id END),
        state             = (CASE WHEN src.in_json::jsonb ? 'state' THEN src.state ELSE apiato.cluster.state END),
        status            = (CASE WHEN src.in_json::jsonb ? 'status' THEN src.status ELSE apiato.cluster.status END),
     FROM (SELECT * FROM json_populate_record(null::apiato.cluster,in_json)
           CROSS JOIN (SELECT in_json AS source_json) src
    WHERE apiato.cluster.cluster_id = src.cluster_id;

RETURN success;
END
$$ LANGUAGE plpgsql;


--Functional Alias
CREATE OR REPLACE FUNCTION apiato_ro.update_functional_alias(in_json JSON) RETURNS bool AS $$
DECLARE
 success bool;
BEGIN

   UPDATE apiato.functional_alias
    SET name   = (CASE WHEN src.in_json::jsonb ? 'instance_id' THEN src.instance_id ELSE apiato.functional_alias.instance_id END),
        memory = (CASE WHEN src.in_json::jsonb ? 'alias' THEN src.alias ELSE apiato.functional_alias.alias END)
     FROM (SELECT * FROM json_populate_record(null::apiato.functional_alias,in_json)
           CROSS JOIN (SELECT in_json AS source_json) src
    WHERE apiato.functional_alias.functional_alias_id = src.functional_alias_id;

RETURN TRUE;
END
$$ LANGUAGE plpgsql;


--Instance
CREATE OR REPLACE FUNCTION apiato_ro.update_instance(in_json JSON) RETURNS bool AS $$
DECLARE
 success bool;
BEGIN

   UPDATE apiato.instance
    SET owner             = (CASE WHEN src.in_json::jsonb ? 'owner' THEN src.owner ELSE apiato.instance.owner END),
        name              = (CASE WHEN src.in_json::jsonb ? 'name' THEN src.name ELSE apiato.instance.name END),
        e_group           = (CASE WHEN src.in_json::jsonb ? 'e_group' THEN src.e_group ELSE apiato.instance.e_group END),
        category          = (CASE WHEN src.in_json::jsonb ? 'category' THEN src.category ELSE apiato.instance.category END),
        creation_date     = (CASE WHEN src.in_json::jsonb ? 'creation_date' THEN src.creation_date ELSE apiato.instance.creation_date END),
        expiry_date       = (CASE WHEN src.in_json::jsonb ? 'expiry_date' THEN src.expiry_date ELSE apiato.instance.expiry_date END),
        instance_type_id  = (CASE WHEN src.in_json::jsonb ? 'instance_type_id' THEN src.instance_type_id ELSE apiato.instance.instance_type_id END),
        project           = (CASE WHEN src.in_json::jsonb ? 'project' THEN src.project ELSE apiato.instance.project END),
        description       = (CASE WHEN src.in_json::jsonb ? 'description' THEN src.description ELSE apiato.instance.description END),
        version           = (CASE WHEN src.in_json::jsonb ? 'version' THEN src.version ELSE apiato.instance.version END),
        master_instance_id = (CASE WHEN src.in_json::jsonb ? 'master_instance_id' THEN src.master_instance_id ELSE apiato.instance.master_instance_id END),
        slave_instance_id = (CASE WHEN src.in_json::jsonb ? 'slave_instance_id' THEN src.slave_instance_id ELSE apiato.instance.slave_instance_id END),
        host_id           = (CASE WHEN src.in_json::jsonb ? 'host_id' THEN src.host_id ELSE apiato.instance.host_id END),
        state             = (CASE WHEN src.in_json::jsonb ? 'state' THEN src.state ELSE apiato.instance.state END),
        status            = (CASE WHEN src.in_json::jsonb ? 'status' THEN src.status ELSE apiato.instance.status END),
        cluster_id        = (CASE WHEN src.in_json::jsonb ? 'cluster_id' THEN src.cluster_id ELSE apiato.instance.cluster_id END)
     FROM (SELECT * FROM json_populate_record(null::apiato.instance,in_json)
           CROSS JOIN (SELECT in_json AS source_json) src
    WHERE apiato.instance.instance_id = src.instance_id;

RETURN success;
END
$$ LANGUAGE plpgsql;


--Instance attribute
CREATE OR REPLACE FUNCTION apiato_ro.update_instance_attribute(in_json JSON) RETURNS bool AS $$
DECLARE
 success bool;
BEGIN

   UPDATE apiato.instance_attribute
    SET value = src.name
     FROM (SELECT * FROM json_populate_record(null::apiato.instance_attribute, in_json)
           CROSS JOIN (SELECT in_json AS source_json) src
    WHERE apiato.instance_attribute.instance_id = src.instance_id AND apiato.instance_attribute.name = src.name;

RETURN success;
END
$$ LANGUAGE plpgsql;

--Hosts
CREATE OR REPLACE FUNCTION apiato_ro.update_host(in_json JSON) RETURNS bool AS $$
DECLARE
 success bool;
BEGIN

  UPDATE apiato.host
    SET name   = (CASE WHEN src.in_json::jsonb ? 'name' THEN src.name ELSE apiato.host.name END),
        memory = (CASE WHEN src.in_json::jsonb ? 'memory' THEN src.memory ELSE apiato.host.memory END)
     FROM (SELECT * FROM json_populate_record(null::apiato.host,in_json)
           CROSS JOIN (SELECT in_json) AS source_json) src
    WHERE apiato.host.host_id = src.host_id;

RETURN TRUE;
END
$$ LANGUAGE plpgsql;
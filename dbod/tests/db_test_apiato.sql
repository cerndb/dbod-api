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
    CONSTRAINT instance_cluster_fk         FOREIGN KEY (cluster_id)         REFERENCES apiato.cluster (cluster_id)
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
  CONSTRAINT instance_attribute_instance_fk FOREIGN KEY (instance_id) REFERENCES apiato.instance (instance_id),
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
  CONSTRAINT cluster_attribute_cluster_fk FOREIGN KEY (cluster_id) REFERENCES apiato.cluster (cluster_id),
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
  function_alias_id serial,
  dns_name          character varying(256) UNIQUE NOT NULL,
  instance_id       int UNIQUE,
  alias             character varying(256),
  CONSTRAINT functional_alias_pkey        PRIMARY KEY (function_alias_id),
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

-- Instance Attribute View
CREATE OR REPLACE VIEW apiato_ro.instance_attribute AS
SELECT instance_attribute.attribute_id AS id,
       instance_attribute.instance_id,
       instance_attribute.name,
       instance_attribute.value
FROM apiato.instance_attribute;

--Volume Attribute View
CREATE OR REPLACE VIEW apiato_ro.volume_attribute AS
SELECT volume_attribute.attribute_id AS id,
       volume_attribute.volume_id,
       volume_attribute.name,
       volume_attribute.value
FROM apiato.volume_attribute;

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


-- Metadata View
CREATE OR REPLACE VIEW apiato_ro.cluster AS
  SELECT
    cluster.cluster_id AS id,
    cluster.owner AS username,
    cluster.name AS name,
    cluster.category "class",
    instance_type.type AS type,
    cluster.version,
    get_cluster_instances as instances,
    apiato.get_cluster_attributes(apiato.cluster.cluster_id) as attributes,
    apiato.get_cluster_attribute('port', apiato.cluster.cluster_id ) port
  FROM apiato.cluster
    JOIN apiato.instance_type ON apiato.cluster.instance_type_id = apiato.instance_type.instance_type_id,
    apiato.get_cluster_instances(apiato.cluster.cluster_id);


-- Functional Aliases View
CREATE OR REPLACE VIEW apiato_ro.functional_aliases AS
  SELECT functional_aliases.dns_name,
    functional_aliases.name as db_name,
    functional_aliases.alias
  FROM apiato.functional_alias
    LEFT JOIN apiato.instance ON apiato.functional_alias.instance_id = apiato.functional_alias.instance_id;




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
INSERT INTO public.functional_aliases (dns_name, instance_id, alias)
VALUES ('db-dbod-dns01', 1   , 'dbod-dbod-01.cern.ch'),
       ('db-dbod-dns02', 2   , 'dbod-dbod-02.cern.ch'),
       ('db-dbod-dns03', 3   , 'dbod-dbod-03.cern.ch'),
       ('db-dbod-dns04', 4   , 'dbod-dbod-04.cern.ch'),
       ('db-dbod-dns05', NULL, NULL);
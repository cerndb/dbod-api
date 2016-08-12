-- SCHEMA CREATION
CREATE SCHEMA IF NOT EXISTS public;
CREATE SCHEMA IF NOT EXISTS api;
CREATE SCHEMA IF NOT EXISTS fdw;

------------------------------
-- CLEANUP
------------------------------

DROP VIEW IF EXISTS api.host_aliases;
DROP VIEW IF EXISTS api.rundeck_instances;
DROP VIEW IF EXISTS api.metadata;
DROP VIEW IF EXISTS api.functional_aliases;
DROP VIEW IF EXISTS api.host;
DROP VIEW IF EXISTS api.volume;
DROP VIEW IF EXISTS api.attribute;
DROP VIEW IF EXISTS api.instance;

DROP FUNCTION IF EXISTS public.get_directories(inst_name VARCHAR, type VARCHAR, version VARCHAR, port VARCHAR);
DROP FUNCTION IF EXISTS public.get_attribute(attr_name VARCHAR, inst_id INTEGER);
DROP FUNCTION IF EXISTS public.get_volumes(pid INTEGER);
DROP FUNCTION IF EXISTS public.get_hosts(host_ids INTEGER[]);

DROP TABLE IF EXISTS public.functional_aliases;
DROP TABLE IF EXISTS public.attribute;
DROP TABLE IF EXISTS public.host;
DROP TABLE IF EXISTS public.volume;

DROP VIEW IF EXISTS public.job_stats;
DROP VIEW IF EXISTS public.command_stats;
DROP VIEW IF EXISTS public.dod_instances;
DROP VIEW IF EXISTS public.dod_command_definition;
DROP VIEW IF EXISTS public.dod_command_params;
DROP VIEW IF EXISTS public.dod_instance_changes;
DROP VIEW IF EXISTS public.dod_jobs;
DROP VIEW IF EXISTS public.dod_upgrades;

DROP FOREIGN TABLE IF EXISTS fdw.dod_command_definition;
DROP FOREIGN TABLE IF EXISTS fdw.dod_command_params;
DROP FOREIGN TABLE IF EXISTS fdw.dod_instance_changes;
DROP FOREIGN TABLE IF EXISTS fdw.dod_instances;
DROP FOREIGN TABLE IF EXISTS fdw.dod_jobs;
DROP FOREIGN TABLE IF EXISTS fdw.dod_upgrades;

------------------------------
-- CREATION OF FOREIGN TABLES
------------------------------

-- DOD_COMMAND_DEFINITION
CREATE FOREIGN TABLE fdw.dod_command_definition (
    command_name varchar(64) NOT NULL,
    type varchar(64) NOT NULL,
    exec varchar(2048),
    category varchar(20)
)
SERVER oradb
OPTIONS (
    schema 'DBONDEMAND_TEST',
    table 'DOD_COMMAND_DEFINITION'
);
ALTER FOREIGN TABLE fdw.dod_command_definition ALTER COLUMN command_name OPTIONS (
    key 'true'
);
ALTER FOREIGN TABLE fdw.dod_command_definition ALTER COLUMN type OPTIONS (
    key 'true'
);
ALTER FOREIGN TABLE fdw.dod_command_definition ALTER COLUMN category OPTIONS (
    key 'true'
);

-- DOD_COMMAND_PARAMS
CREATE FOREIGN TABLE fdw.dod_command_params (
    username varchar(32) NOT NULL,
    db_name varchar(128) NOT NULL,
    command_name varchar(64) NOT NULL,
    type varchar(64) NOT NULL,
    creation_date date NOT NULL,
    name varchar(64) NOT NULL,
    value text,
    category varchar(20)
)
SERVER oradb
OPTIONS (
    schema 'DBONDEMAND_TEST',
    table 'DOD_COMMAND_PARAMS'
);
ALTER FOREIGN TABLE fdw.dod_command_params ALTER COLUMN db_name OPTIONS (
    key 'true'
);

-- DOD_INSTANCE_CHANGES
CREATE FOREIGN TABLE fdw.dod_instance_changes (
    username varchar(32) NOT NULL,
    db_name varchar(128) NOT NULL,
    attribute varchar(32) NOT NULL,
    change_date date NOT NULL,
    requester varchar(32) NOT NULL,
    old_value varchar(1024),
    new_value varchar(1024)
)
SERVER oradb
OPTIONS (
    schema 'DBONDEMAND_TEST',
    table 'DOD_INSTANCE_CHANGES'
);
ALTER FOREIGN TABLE fdw.dod_instance_changes ALTER COLUMN db_name OPTIONS (
    key 'true'
);

-- DOD_INSTANCES
CREATE FOREIGN TABLE fdw.dod_instances (
    username varchar(32) NOT NULL,
    db_name varchar(128) NOT NULL,
    e_group varchar(256),
    category varchar(32) NOT NULL,
    creation_date date NOT NULL,
    expiry_date date,
    db_type varchar(32) NOT NULL,
    db_size int NOT NULL,
    no_connections int,
    project varchar(128),
    description varchar(1024),
    version varchar(128),
    master varchar(32),
    slave varchar(32),
    host varchar(128),
    state varchar(32),
    status varchar(32),
    id int
)
SERVER oradb
OPTIONS (
    schema 'DBONDEMAND_TEST',
    table 'DOD_INSTANCES'
);
ALTER FOREIGN TABLE fdw.dod_instances ALTER COLUMN db_name OPTIONS (
    key 'true'
);

-- DOD_JOBS
CREATE FOREIGN TABLE fdw.dod_jobs (
    username varchar(32) NOT NULL,
    db_name varchar(128) NOT NULL,
    command_name varchar(64) NOT NULL,
    type varchar(64) NOT NULL,
    creation_date date NOT NULL,
    completion_date date,
    requester varchar(32) NOT NULL,
    admin_action int NOT NULL,
    state varchar(32) NOT NULL,
    log text,
    result varchar(2048),
    email_sent date,
    category varchar(20)
)
SERVER oradb
OPTIONS (
    schema 'DBONDEMAND_TEST',
    table 'DOD_JOBS'
);
ALTER FOREIGN TABLE fdw.dod_jobs ALTER COLUMN db_name OPTIONS (
    key 'true'
);

-- DOD_UPGRADES
CREATE FOREIGN TABLE fdw.dod_upgrades (
    db_type varchar(32) NOT NULL,
    category varchar(32) NOT NULL,
    version_from varchar(128) NOT NULL,
    version_to varchar(128) NOT NULL
)
SERVER oradb
OPTIONS (
    schema 'DBONDEMAND_TEST',
    table 'DOD_UPGRADES'
);
ALTER FOREIGN TABLE fdw.dod_upgrades ALTER COLUMN db_type OPTIONS (
    key 'true'
);
ALTER FOREIGN TABLE fdw.dod_upgrades ALTER COLUMN category OPTIONS (
    key 'true'
);
ALTER FOREIGN TABLE fdw.dod_upgrades ALTER COLUMN version_from OPTIONS (
    key 'true'
);

------------------------------------
-- VIEWS FOR BACKWARD COMPATIBILITY
------------------------------------

CREATE OR REPLACE VIEW public.dod_instances AS
SELECT * FROM fdw.dod_instances;

CREATE OR REPLACE VIEW public.dod_command_definition AS
SELECT * FROM fdw.dod_command_definition;

CREATE OR REPLACE VIEW public.dod_command_params AS
SELECT * FROM fdw.dod_command_params;

CREATE OR REPLACE VIEW public.dod_instance_changes AS
SELECT * FROM fdw.dod_instance_changes;

CREATE OR REPLACE VIEW public.dod_jobs AS
SELECT * FROM fdw.dod_jobs;

CREATE OR REPLACE VIEW public.dod_upgrades AS
SELECT * FROM fdw.dod_upgrades;

-- Job stats view
CREATE OR REPLACE VIEW public.job_stats AS 
SELECT db_name, command_name, COUNT(*) as COUNT, ROUND(AVG(completion_date - creation_date) * 24*60*60) AS mean_duration
FROM dod_jobs GROUP BY command_name, db_name;

-- Command stats view
CREATE OR REPLACE VIEW public.command_stats AS
SELECT command_name, COUNT(*) AS COUNT, ROUND(AVG(completion_date - creation_date) * 24*60*60) AS mean_duration
FROM dod_jobs GROUP BY command_name;


---------------------------------
-- TABLES FOR NEW DATA FROM LDAP
---------------------------------

-- Volume table
CREATE TABLE public.volume (
    id serial,
    instance_id integer NOT NULL,
    file_mode char(4) NOT NULL,
    owner varchar(32) NOT NULL,
    vgroup varchar(32) NOT NULL,
    server varchar(63) NOT NULL,
    mount_options varchar(256) NOT NULL,
    mounting_path varchar(256) NOT NULL
);

-- Host table
CREATE TABLE public.host (
    id serial,
    name varchar(63) NOT NULL,
    memory integer NOT NULL
);

-- Attribute table
CREATE TABLE public.attribute (
    id serial,
    instance_id integer NOT NULL,
    name varchar(32) NOT NULL,
    value varchar(250) NOT NULL
);

-- Functional aliases table
CREATE TABLE public.functional_aliases
(
  dns_name character varying(256) NOT NULL,
  db_name character varying(8),
  alias character varying(256),
  CONSTRAINT functional_aliases_pkey PRIMARY KEY (dns_name)
);

------------------------------
-- FUNCTIONS
------------------------------

-- Get hosts function
CREATE OR REPLACE FUNCTION public.get_hosts(host_ids INTEGER[])
RETURNS VARCHAR[] AS $$
DECLARE
  hosts VARCHAR := '';
BEGIN
  SELECT ARRAY (SELECT name FROM host WHERE id = ANY(host_ids)) INTO hosts;
  RETURN hosts;
END
$$ LANGUAGE plpgsql;

-- Get volumes function
CREATE OR REPLACE FUNCTION public.get_volumes(pid INTEGER)
RETURNS JSON[] AS $$
DECLARE
  volumes JSON[];
BEGIN
  SELECT ARRAY (SELECT row_to_json(t) FROM (SELECT * FROM public.volume WHERE instance_id = pid) t) INTO volumes;
  return volumes;
END
$$ LANGUAGE plpgsql;

-- Get attribute function
CREATE OR REPLACE FUNCTION public.get_attribute(attr_name VARCHAR, inst_id INTEGER)
RETURNS VARCHAR AS $$
DECLARE
  res VARCHAR;
BEGIN
  SELECT value FROM public.attribute A WHERE A.instance_id = inst_id AND A.name = attr_name INTO res;
  return res;
END
$$ LANGUAGE plpgsql;

-- Get directories function
CREATE OR REPLACE FUNCTION public.get_directories(inst_name VARCHAR, type VARCHAR, version VARCHAR, port VARCHAR)
RETURNS TABLE (basedir VARCHAR, bindir VARCHAR, datadir VARCHAR, logdir VARCHAR, socket VARCHAR) AS $$
BEGIN
  IF type = 'MYSQL' THEN
    RETURN QUERY SELECT 
      ('/usr/local/mysql/mysql-' || version)::VARCHAR basedir, 
      ('/usr/local/mysql/mysql-' || version || '/bin')::VARCHAR bindir, 
      ('/ORA/dbs03/' || upper(inst_name) || '/mysql')::VARCHAR datadir, 
      ('/ORA/dbs02/' || upper(inst_name) || '/mysql')::VARCHAR logdir, 
      ('/var/lib/mysql/mysql.sock.' || lower(inst_name) || '.' || port)::VARCHAR socket;
  ELSIF type = 'PG' THEN
    RETURN QUERY SELECT 
      ('/usr/local/pgsql/pgsql-' || version)::VARCHAR basedir, 
      ('/usr/local/pgsql/pgsql-' || version || '/bin')::VARCHAR bindir, 
      ('/ORA/dbs03/' || upper(inst_name) || '/data')::VARCHAR datadir, 
      ('/ORA/dbs02/' || upper(inst_name) || '/pg_xlog')::VARCHAR logdir, 
      ('/var/lib/pgsql/')::VARCHAR socket;
  ELSIF type = 'InfluxDB' THEN
    RETURN QUERY SELECT 
      ('/usr/local/influxdb/influxdb-' || version)::VARCHAR basedir, 
      ('/usr/local/influxdb/influxdb-' || version || '/bin')::VARCHAR bindir, 
      ('/ORA/dbs03/' || upper(inst_name) || '/data')::VARCHAR datadir, 
      ('/ORA/dbs02/' || upper(inst_name) || '/pg_xlog')::VARCHAR logdir, 
      ('/tmp')::VARCHAR socket;
  ELSE
    RETURN QUERY SELECT 
      ('/#BASEDIR#/' || version)::VARCHAR basedir, 
      ('/#BASEDIR#/' || version || '/bin')::VARCHAR bindir, 
      ('/ORA/dbs03/' || upper(inst_name) || '/data')::VARCHAR datadir, 
      ('/ORA/dbs02/' || upper(inst_name) || '/pg_xlog')::VARCHAR logdir, 
      ('/tmp')::VARCHAR socket;
  END IF;
END
$$ LANGUAGE plpgsql;

------------------------------
-- VIEWS FOR DBOD-API
------------------------------

-- Instance View
CREATE OR REPLACE VIEW api.instance AS 
SELECT dod_instances.id,
       dod_instances.username,
       dod_instances.db_name,
       dod_instances.e_group,
       dod_instances.category,
       dod_instances.creation_date,
       dod_instances.expiry_date,
       dod_instances.db_type,
       dod_instances.db_size,
       dod_instances.no_connections,
       dod_instances.project,
       dod_instances.description,
       dod_instances.version,
       dod_instances.master,
       dod_instances.slave,
       dod_instances.host,
       dod_instances.state,
       dod_instances.status
FROM dod_instances;

-- Attribute View
CREATE OR REPLACE VIEW api.attribute AS 
SELECT attribute.id,
       attribute.instance_id,
       attribute.name,
       attribute.value
FROM attribute;

-- Volume View
CREATE OR REPLACE VIEW api.volume AS 
SELECT volume.id,
       volume.instance_id,
       volume.file_mode,
       volume.owner,
       volume.vgroup,
       volume.server,
       volume.mount_options,
       volume.mounting_path
FROM volume;

-- Host View
CREATE OR REPLACE VIEW api.host AS 
SELECT host.id,
       host.name,
       host.memory
FROM host;

-- Functional Aliases View
CREATE OR REPLACE VIEW api.functional_aliases AS 
SELECT functional_aliases.dns_name,
       functional_aliases.db_name,
       functional_aliases.alias
FROM public.functional_aliases;


-- Metadata View
CREATE OR REPLACE VIEW api.metadata AS
SELECT id, username, db_name, category, db_type, version, host, public.get_attribute('port', id) port, get_volumes volumes, d.*
FROM public.dod_instances, public.get_volumes(id), public.get_directories(db_name, db_type, version, public.get_attribute('port', id)) d;

-- Rundeck instances View
CREATE OR REPLACE VIEW api.rundeck_instances AS
SELECT public.dod_instances.db_name, 
       public.functional_aliases.alias hostname,
       public.get_attribute('port', public.dod_instances.id) port,
       'dbod'::CHAR username,
       public.dod_instances.db_type db_type,
       public.dod_instances.category category,
       db_type || ',' || category tags
FROM public.dod_instances JOIN public.functional_aliases ON
public.dod_instances.db_name = public.functional_aliases.db_name;

-- Host aliases View
CREATE OR REPLACE VIEW api.host_aliases AS
SELECT host, array_agg('dbod-' || db_name || '.cern.ch') aliases 
FROM fdw.dod_instances 
GROUP BY host;


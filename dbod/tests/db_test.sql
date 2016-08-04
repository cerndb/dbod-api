-- Copyright (C) 2015, CERN
-- This software is distributed under the terms of the GNU General Public
-- Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".
-- In applying this license, CERN does not waive the privileges and immunities
-- granted to it by virtue of its status as Intergovernmental Organization
-- or submit itself to any jurisdiction.

------------------------------------------------
-- Create the structure for the test database --
------------------------------------------------

CREATE SCHEMA IF NOT EXISTS public;

-- DOD_COMMAND_DEFINITION
CREATE TABLE public.dod_command_definition (
    command_name varchar(64) NOT NULL,
    type varchar(64) NOT NULL,
    exec varchar(2048),
    category varchar(20),
    PRIMARY KEY (command_name, type, category)
);

-- DOD_COMMAND_PARAMS
CREATE TABLE public.dod_command_params (
    username varchar(32) NOT NULL,
    db_name varchar(128) NOT NULL,
    command_name varchar(64) NOT NULL,
    type varchar(64) NOT NULL,
    creation_date date NOT NULL,
    name varchar(64) NOT NULL,
    value text,
    category varchar(20),
    PRIMARY KEY (username, db_name, command_name, type, creation_date, name)
);

-- DOD_INSTANCE_CHANGES
CREATE TABLE public.dod_instance_changes (
    username varchar(32) NOT NULL,
    db_name varchar(128) NOT NULL,
    attribute varchar(32) NOT NULL,
    change_date date NOT NULL,
    requester varchar(32) NOT NULL,
    old_value varchar(1024),
    new_value varchar(1024),
    PRIMARY KEY (username, db_name, attribute, change_date)
);

-- DOD_INSTANCES
CREATE TABLE public.dod_instances (
    id serial,
    username varchar(32) NOT NULL,
    db_name varchar(128) NOT NULL,
    e_group varchar(256),
    category varchar(32) NOT NULL,
    creation_date date NOT NULL,
    expiry_date date,
    db_type varchar(32) NOT NULL,
    db_size int,
    no_connections int,
    project varchar(128),
    description varchar(1024),
    version varchar(128),
    master varchar(32),
    slave varchar(32),
    host varchar(128),
    state varchar(32),
    status varchar(32),
    CONSTRAINT dod_instances_pkey PRIMARY KEY (id),
    CONSTRAINT dod_instances_dbname UNIQUE (db_name)
);

-- DOD_JOBS
CREATE TABLE public.dod_jobs (
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
    category varchar(20),
    PRIMARY KEY (username, db_name, command_name, type, creation_date)
);

-- DOD_UPGRADES
CREATE TABLE public.dod_upgrades (
    db_type varchar(32) NOT NULL,
    category varchar(32) NOT NULL,
    version_from varchar(128) NOT NULL,
    version_to varchar(128) NOT NULL,
    PRIMARY KEY (db_type, category, version_from)
);

-- VOLUME
CREATE TABLE public.volume (
    id serial,
    instance_id integer NOT NULL,
    file_mode char(4) NOT NULL,
    owner varchar(32) NOT NULL,
    vgroup varchar(32) NOT NULL,
    server varchar(63) NOT NULL,
    mount_options varchar(256) NOT NULL,
    mounting_path varchar(256) NOT NULL,
    PRIMARY KEY (id)
);

-- HOST
CREATE TABLE public.host (
    id serial,
    name varchar(63) NOT NULL,
    memory integer NOT NULL,
    PRIMARY KEY (id)
);

-- ATTRIBUTE
CREATE TABLE public.attribute (
    id serial,
    instance_id integer NOT NULL,
    name varchar(32) NOT NULL,
    value varchar(250) NOT NULL,
    PRIMARY KEY (id)
);

-- FUNCTIONAL ALIASES
CREATE TABLE public.functional_aliases (
    dns_name character varying(256) NOT NULL,
    db_name character varying(8),
    alias character varying(256),
    CONSTRAINT functional_aliases_pkey PRIMARY KEY (dns_name),
    CONSTRAINT db_name_con UNIQUE (db_name)
);

-- Insert test data for instances
INSERT INTO public.dod_instances (username, db_name, e_group, category, creation_date, expiry_date, db_type, db_size, no_connections, project, description, version, master, slave, host, state, status)
VALUES ('user01', 'dbod01', 'testgroupA', 'TEST', now(), NULL, 'MYSQL', 100, 100, 'API', 'Test instance 1', '5.6.17', NULL, NULL, 'host01', 'RUNNING', 1),
       ('user01', 'dbod02', 'testgroupB', 'PROD', now(), NULL, 'PG', 50, 500, 'API', 'Test instance 2', '9.4.4', NULL, NULL, 'host03', 'RUNNING', 1),
       ('user02', 'dbod03', 'testgroupB', 'TEST', now(), NULL, 'MYSQL', 100, 200, 'WEB', 'Expired instance 1', '5.5', NULL, NULL, 'host01', 'RUNNING', 0),
       ('user03', 'dbod04', 'testgroupA', 'PROD', now(), NULL, 'PG', 250, 10, 'LCC', 'Test instance 3', '9.4.5', NULL, NULL, 'host01', 'RUNNING', 1),
       ('user04', 'dbod05', 'testgroupC', 'TEST', now(), NULL, 'MYSQL', 300, 200, 'WEB', 'Test instance 4', '5.6.17', NULL, NULL, 'host01', 'RUNNING', 1);
       
-- Insert test data for volumes
INSERT INTO public.volume (instance_id, file_mode, owner, vgroup, server, mount_options, mounting_path)
VALUES (1, '0755', 'TSM', 'ownergroup', 'NAS-server', 'rw,bg,hard', '/MNT/data1'),
       (1, '0755', 'TSM', 'ownergroup', 'NAS-server', 'rw', '/MNT/bin'),
       (2, '0755', 'TSM', 'ownergroup', 'NAS-server', 'rw,bg,hard', '/MNT/data2'),
       (4, '0755', 'TSM', 'ownergroup', 'NAS-server', 'rw,bg,hard,tcp', '/MNT/data4'),
       (5, '0755', 'TSM', 'ownergroup', 'NAS-server', 'rw,bg,hard', '/MNT/data5'),
       (5, '0755', 'TSM', 'ownergroup', 'NAS-server', 'rw', '/MNT/bin');

-- Insert test data for attributes
INSERT INTO public.attribute (instance_id, name, value)
VALUES (1, 'port', '5501'),
       (2, 'port', '6603'),
       (3, 'port', '5510'),
       (4, 'port', '6601'),
       (5, 'port', '5500');
        
-- Insert test data for hosts
INSERT INTO public.host (name, memory)
VALUES ('host01', 12),
       ('host02', 24),
       ('host03', 64),
       ('host04', 256);
       
-- Insert test data for database aliases
INSERT INTO public.functional_aliases (dns_name, db_name, alias)
VALUES ('db-dbod-dns01','dbod_01','dbod-dbod-01.cern.ch'),
       ('db-dbod-dns02','dbod_02','dbod-dbod-02.cern.ch'),
       ('db-dbod-dns03','dbod_03','dbod-dbod-03.cern.ch'),
       ('db-dbod-dns04','dbod_04','dbod-dbod-04.cern.ch'),
       ('db-dbod-dns05', NULL, NULL);

-- Schema API
CREATE SCHEMA IF NOT EXISTS api;

-- Dod_instances view
CREATE OR REPLACE VIEW api.dod_instances AS
SELECT id, username, db_name, e_group, category, creation_date, expiry_date, db_type, db_size, no_connections, project, description, version, master, slave, host, state, status
FROM dod_instances;
       
-- Job stats view
CREATE OR REPLACE VIEW api.job_stats AS 
SELECT db_name, command_name, COUNT(*) as COUNT, ROUND(AVG(completion_date - creation_date) * 24*60*60) AS mean_duration
FROM dod_jobs GROUP BY command_name, db_name;

-- Command stats view
CREATE OR REPLACE VIEW api.command_stats AS
SELECT command_name, COUNT(*) AS COUNT, ROUND(AVG(completion_date - creation_date) * 24*60*60) AS mean_duration
FROM dod_jobs GROUP BY command_name;
       
-- Get hosts function
CREATE OR REPLACE FUNCTION get_hosts(host_ids INTEGER[])
RETURNS VARCHAR[] AS $$
DECLARE
  hosts VARCHAR := '';
BEGIN
  SELECT ARRAY (SELECT name FROM host WHERE id = ANY(host_ids)) INTO hosts;
  RETURN hosts;
END
$$ LANGUAGE plpgsql;

-- Get volumes function
CREATE OR REPLACE FUNCTION get_volumes(pid INTEGER)
RETURNS JSON[] AS $$
DECLARE
  volumes JSON[];
BEGIN
  SELECT ARRAY (SELECT row_to_json(t) FROM (SELECT * FROM public.volume WHERE instance_id = pid) t) INTO volumes;
  return volumes;
END
$$ LANGUAGE plpgsql;

-- Get port function
CREATE OR REPLACE FUNCTION get_attribute(attr_name VARCHAR, inst_id INTEGER)
RETURNS VARCHAR AS $$
DECLARE
  res VARCHAR;
BEGIN
  SELECT value FROM public.attribute A WHERE A.instance_id = inst_id AND A.name = attr_name INTO res;
  return res;
END
$$ LANGUAGE plpgsql;


-- Get directories function
CREATE OR REPLACE FUNCTION get_directories(inst_name VARCHAR, type VARCHAR, version VARCHAR, port VARCHAR)
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
      ('/usr/local/mysql/mysql-' || version || '/bin')::VARCHAR bindir, 
      ('/ORA/dbs03/' || upper(inst_name) || '/data')::VARCHAR datadir, 
      ('/ORA/dbs02/' || upper(inst_name) || '/pg_xlog')::VARCHAR logdir, 
      ('/var/lib/pgsql/')::VARCHAR socket;
  END IF;
END
$$ LANGUAGE plpgsql;
       
CREATE VIEW api.instance AS
SELECT * FROM public.dod_instances;

CREATE VIEW api.volume AS
SELECT * FROM public.volume;

CREATE VIEW api.attribute AS
SELECT * FROM public.attribute;

CREATE VIEW api.host AS
SELECT * FROM public.host;

-- Metadata View
CREATE OR REPLACE VIEW api.metadata AS
SELECT id, username, db_name, category, db_type, version, host, get_attribute('port', id) port, get_volumes volumes, d.*
FROM dod_instances, get_volumes(id), get_directories(db_name, db_type, version, get_attribute('port', id)) d;

-- Rundeck instances View
CREATE OR REPLACE VIEW api.rundeck_instances AS
SELECT public.dod_instances.db_name, 
       public.functional_aliases.alias hostname,
       public.get_attribute('port', public.dod_instances.id) port,
       'dbod' username,
       public.dod_instances.db_type db_type,
       public.dod_instances.category category,
       db_type || ',' || category tags
FROM public.dod_instances JOIN public.functional_aliases ON
public.dod_instances.db_name = public.functional_aliases.db_name;

-- Host aliases View
CREATE OR REPLACE VIEW api.host_aliases AS
SELECT host, string_agg('dbod-' || db_name || 'domain', E',') aliases 
FROM dod_instances 
GROUP BY host;

-- Functional aliases view
CREATE OR REPLACE VIEW api.functional_aliases AS
SELECT * 
FROM functional_aliases;

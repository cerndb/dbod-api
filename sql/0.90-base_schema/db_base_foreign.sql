-- Copyright (C) 2015, CERN
-- This software is distributed under the terms of the GNU General Public
-- Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".
-- In applying this license, CERN does not waive the privileges and immunities
-- granted to it by virtue of its status as Intergovernmental Organization
-- or submit itself to any jurisdiction.

------------------------------
-- CREATION OF FOREIGN TABLES
------------------------------

CREATE SCHEMA IF NOT EXISTS fdw;

-- DOD_COMMAND_DEFINITION
CREATE FOREIGN TABLE fdw.dod_command_definition (
    command_name varchar(64) NOT NULL,
    type varchar(64) NOT NULL,
    exec varchar(2048)
)
SERVER itcore_dbod
OPTIONS (
    schema 'DBONDEMAND',
    table 'DOD_COMMAND_DEFINITION'
);
ALTER FOREIGN TABLE fdw.dod_command_definition ALTER COLUMN command_name OPTIONS (
    key 'true'
);
ALTER FOREIGN TABLE fdw.dod_command_definition ALTER COLUMN type OPTIONS (
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
SERVER itcore_dbod
OPTIONS (
    schema 'DBONDEMAND',
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
SERVER itcore_dbod
OPTIONS (
    schema 'DBONDEMAND',
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
SERVER itcore_dbod
OPTIONS (
    schema 'DBONDEMAND',
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
    id int,
    instance_id int
)
SERVER itcore_dbod
OPTIONS (
    schema 'DBONDEMAND',
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
SERVER itcore_dbod
OPTIONS (
    schema 'DBONDEMAND',
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

-- FIM TABLE
CREATE FOREIGN TABLE fdw.fim_data (
    internal_id character varying(36) NOT NULL,
    instance_name character varying(64),
    description character varying(450),
    owner_account_type character varying(20),
    owner_first_name character varying(24),
    owner_last_name character varying(40),
    owner_login character varying(64),
    owner_mail character varying(128),
    owner_phone1 character varying(5),
    owner_phone2 character varying(5),
    owner_portable_phone character varying(7),
    owner_department character varying(3),
    owner_group character varying(3),
    owner_section character varying(3)
)
SERVER itcore_dbod
OPTIONS (
    schema 'FIM_ORA_MA',
    table 'DB_ON_DEMAND'
);
ALTER FOREIGN TABLE fdw.fim_data ALTER COLUMN internal_id OPTIONS (
    key 'true'
);

------------------------------------
-- LOCAL TABLES
------------------------------------

-- VOLUME
CREATE TABLE public.volume (
    id serial,
    instance_id integer NOT NULL,
    file_mode char(4) NOT NULL,
    owner varchar(32) NOT NULL,
    "group" varchar(32) NOT NULL,
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
    PRIMARY KEY (id),
    CONSTRAINT name_con UNIQUE (name)
);

-- ATTRIBUTE
CREATE TABLE public.attribute (
    id serial,
    instance_id integer NOT NULL,
    name varchar(32) NOT NULL,
    value varchar(250) NOT NULL,
    PRIMARY KEY (id),
    UNIQUE (instance_id, name)
);

-- FUNCTIONAL ALIASES
CREATE TABLE public.functional_aliases (
    dns_name character varying(256) NOT NULL,
    db_name character varying(8),
    alias character varying(256),
    CONSTRAINT functional_aliases_pkey PRIMARY KEY (dns_name),
    CONSTRAINT db_name_con UNIQUE (db_name)
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

CREATE OR REPLACE VIEW public.fim_data AS
SELECT * FROM fdw.fim_data;

-- Job stats view
CREATE OR REPLACE VIEW public.job_stats AS 
SELECT db_name, command_name, COUNT(*) as COUNT, ROUND(AVG(completion_date - creation_date) * 24*60*60) AS mean_duration
FROM dod_jobs GROUP BY command_name, db_name;

-- Command stats view
CREATE OR REPLACE VIEW public.command_stats AS
SELECT command_name, COUNT(*) AS COUNT, ROUND(AVG(completion_date - creation_date) * 24*60*60) AS mean_duration
FROM dod_jobs GROUP BY command_name;

------------------------------------------
-- TYPES
------------------------------------------
CREATE TYPE public.instance_state AS ENUM (
  'RUNNING',
  'MAINTENANCE',
  'AWATING-APPROVAL',
  'JOB-PENDING'
);

CREATE TYPE public.instance_status AS ENUM (
  'ACTIVE',
  'NON-ACTIVE'
);

CREATE TYPE public.instance_category AS ENUM (
  'PROD',
  'DEV',
  'TEST',
  'QA',
  'REF'
);

CREATE TYPE public.job_state AS ENUM (
  'FINISHED_FAIL',
  'FINISHED_OK'
);

--INSTANCE_TYPE
CREATE TABLE public.instance_type (
  id serial,
  type             varchar(64) UNIQUE NOT NULL,
  description      varchar(1024),
  CONSTRAINT instance_type_pkey PRIMARY KEY (id)
);

INSERT INTO public.instance_type (type, description)
VALUES ('ZOOKEEPER', 'Zookeeper instance type'),
       ('MYSQL'    , 'MySQL database type'),
       ('PG'       , 'PostgreSQL database type');
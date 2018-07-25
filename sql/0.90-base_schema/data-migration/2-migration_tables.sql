-- Copyright (C) 2017, CERN
-- This software is distributed under the terms of the GNU General Public
-- Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".
-- In applying this license, CERN does not waive the privileges and immunities
-- granted to it by virtue of its status as Intergovernmental Organization
-- or submit itself to any jurisdiction.


CREATE SCHEMA IF NOT EXISTS source;
CREATE SCHEMA IF NOT EXISTS fim;

-- COMMAND_DEFINITION
CREATE FOREIGN TABLE source.dod_command_definition (
    command_name varchar(64) NOT NULL,
    type varchar(64) NOT NULL,
    exec varchar(2048)
)
SERVER <pg_source>
OPTIONS (
    schema_name 'public',
    table_name 'dod_command_definition',
    updatable 'false'
);

-- COMMAND_PARAM
CREATE FOREIGN TABLE source.dod_command_params (
    username varchar(32) NOT NULL,
    db_name varchar(128) NOT NULL,
    command_name varchar(64) NOT NULL,
    type varchar(64) NOT NULL,
    creation_date timestamp NOT NULL,
    name varchar(64) NOT NULL,
    value text
)
SERVER <oracle_source>
OPTIONS (
    schema 'DBONDEMAND',
    table 'DOD_COMMAND_PARAMS',
    readonly 'true'
);

-- INSTANCE_CHANGE
CREATE FOREIGN TABLE source.dod_instance_changes (
    username varchar(32) NOT NULL,
    db_name varchar(128) NOT NULL,
    attribute varchar(32) NOT NULL,
    change_date timestamp NOT NULL,
    requester varchar(32) NOT NULL,
    old_value varchar(1024),
    new_value varchar(1024)
)
SERVER <oracle_source>
OPTIONS (
    schema 'DBONDEMAND',
    table 'DOD_INSTANCE_CHANGES',
    readonly 'true'
);

-- HOST
CREATE FOREIGN TABLE source.host (
    id serial,
    name varchar(63) NOT NULL,
    memory integer NOT NULL
)
SERVER <pg_source>
OPTIONS (
    schema_name 'public',
    table_name 'host',
    updatable 'false'
);

-- INSTANCE
CREATE FOREIGN TABLE source.dod_instances (
    username varchar(32) NOT NULL,
    db_name varchar(128) NOT NULL,
    e_group varchar(256),
    category varchar(32) NOT NULL,
    creation_date timestamp NOT NULL,
    expiry_date timestamp,
    db_type varchar(32) NOT NULL,
    db_size integer,
    no_connections integer,
    project varchar(128),
    description varchar(1024),
    state varchar(32) NOT NULL,
    status char(1) NOT NULL,
    version varchar(128),
    master varchar(32),
    slave varchar(32),
    host varchar(128),
    id serial
)
SERVER <oracle_source>
OPTIONS (
    schema 'DBONDEMAND',
    table 'DOD_INSTANCES',
    readonly 'true'
);

-- INSTANCE_ATTRIBUTE
CREATE FOREIGN TABLE source.attribute (
    id serial,
    instance_id integer NOT NULL,
    name varchar(32) NOT NULL,
    value varchar(250) NOT NULL
)
SERVER <pg_source>
OPTIONS (
    schema_name 'public',
    table_name 'attribute',
    updatable 'false'
);

-- JOB
CREATE FOREIGN TABLE source.dod_jobs (
    username varchar(32) NOT NULL,
    db_name varchar(128) NOT NULL,
    command_name varchar(64) NOT NULL,
    type varchar(64) NOT NULL,
    creation_date timestamp NOT NULL,
    completion_date timestamp,
    requester varchar(32) NOT NULL,
    admin_action int NOT NULL,
    state varchar(32) NOT NULL,
    log text,
    result varchar(2048),
    email_sent timestamp,
    id int NOT NULL,
    instance_id int NOT NULL
)
SERVER <oracle_source>
OPTIONS (
    schema 'DBONDEMAND',
    table 'DOD_JOBS',
    readonly 'true'
);

-- UPGRADE
CREATE FOREIGN TABLE source.dod_upgrades (
    db_type varchar(32) NOT NULL,
    category varchar(32) NOT NULL,
    version_from varchar(128) NOT NULL,
    version_to varchar(128) NOT NULL
)
SERVER <pg_source>
OPTIONS (
    schema_name 'public',
    table_name 'dod_upgrades',
    updatable 'false'
);

-- FIM_DATA
CREATE FOREIGN TABLE fim.db_on_demand (
    internal_id varchar(36) NOT NULL,
    instance_name varchar(64),
    description varchar(450),
    owner_account_type varchar(20),
    owner_first_name varchar(24),
    owner_last_name varchar(40),
    owner_login varchar(64),
    owner_mail varchar(128),
    owner_phone1 varchar(5),
    owner_phone2 varchar(5),
    owner_portable_phone varchar(7),
    owner_department varchar(3),
    owner_group varchar(3),
    owner_section varchar(3)
)
SERVER <oracle_source>
OPTIONS (
    schema 'FIM_ORA_MA',
    table 'DB_ON_DEMAND',
    readonly 'true'
);

-- VOLUME
CREATE FOREIGN TABLE source.volume (
    id serial,
    instance_id integer NOT NULL,
    file_mode char(4) NOT NULL,
    owner varchar(32) NOT NULL,
    "group" varchar(32) NOT NULL,
    server varchar(63) NOT NULL,
    mount_options varchar(256) NOT NULL,
    mounting_path varchar(256) NOT NULL
)
SERVER <pg_source>
OPTIONS (
    schema_name 'public',
    table_name 'volume',
    updatable 'false'
);

-- FUNCTIONAL ALIASES
CREATE FOREIGN TABLE source.functional_aliases (
    dns_name varchar(256) NOT NULL,
    db_name varchar(8),
    alias varchar(256)
)
SERVER <pg_source>
OPTIONS (
    schema_name 'public',
    table_name 'functional_aliases',
    updatable 'false'
);

-- RUNDECK EXECUTION TABLE
CREATE FOREIGN TABLE fim.rundeck_execution (
  id bigint NOT NULL,
  version bigint NOT NULL,
  abortedby character varying(255),
  arg_string text,
  cancelled boolean NOT NULL,
  date_completed timestamp without time zone,
  date_started timestamp without time zone,
  do_nodedispatch boolean,
  execution_type character varying(30),
  failed_node_list text,
  filter text,
  loglevel character varying(255),
  node_exclude text,
  node_exclude_name text,
  node_exclude_os_arch text,
  node_exclude_os_family text,
  node_exclude_os_name text,
  node_exclude_os_version text,
  node_exclude_precedence boolean,
  node_exclude_tags text,
  node_filter_editable boolean,
  node_include text,
  node_include_name text,
  node_include_os_arch text,
  node_include_os_family text,
  node_include_os_name text,
  node_include_os_version text,
  node_include_tags text,
  node_keepgoing boolean,
  node_rank_attribute character varying(255),
  node_rank_order_ascending boolean,
  node_threadcount integer,
  orchestrator_id bigint,
  outputfilepath text,
  project character varying(255) NOT NULL,
  retry text,
  retry_attempt integer,
  retry_delay character varying(255),
  retry_execution_id bigint,
  scheduled_execution_id bigint,
  server_nodeuuid character varying(36),
  status character varying(255),
  succeeded_node_list text,
  success_on_empty_node_filter boolean,
  timed_out boolean,
  timeout text,
  rduser character varying(255) NOT NULL,
  user_role_list text,
  will_retry boolean,
  workflow_id bigint,
  retry_original_id bigint
)
SERVER <rundeck_source>
OPTIONS (
    schema_name 'public',
    table_name 'execution',
    updatable 'false'
);

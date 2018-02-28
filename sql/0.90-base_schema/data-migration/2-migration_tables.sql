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


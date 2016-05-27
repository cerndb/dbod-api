-- Cleanup
DROP FOREIGN TABLE fo_dod_command_definition;
DROP FOREIGN TABLE fo_dod_command_params;
DROP FOREIGN TABLE fo_dod_instance_changes;
DROP FOREIGN TABLE fo_dod_instances;
DROP FOREIGN TABLE fo_dod_jobs;
DROP FOREIGN TABLE fo_dod_upgrades;

-- DOD_COMMAND_DEFINITION
CREATE FOREIGN TABLE fo_dod_command_definition (
    command_name varchar(64) NOT NULL,
    type varchar(64) NOT NULL,
    exec varchar(2048),
    category varchar(20)
)
SERVER dbodtest
OPTIONS (
    schema 'DBONDEMAND_TEST',
    "table" 'DOD_COMMAND_DEFINITION'
);
ALTER FOREIGN TABLE fo_dod_command_definition ALTER COLUMN command_name OPTIONS (
    key 'true'
);
ALTER FOREIGN TABLE fo_dod_command_definition ALTER COLUMN type OPTIONS (
    key 'true'
);
ALTER FOREIGN TABLE fo_dod_command_definition ALTER COLUMN category OPTIONS (
    key 'true'
);

-- DOD_COMMAND_PARAMS
CREATE FOREIGN TABLE fo_dod_command_params (
    username varchar(32) NOT NULL,
    db_name varchar(128) NOT NULL,
    command_name varchar(64) NOT NULL,
    type varchar(64) NOT NULL,
    creation_date date NOT NULL,
    name varchar(64) NOT NULL,
    value text,
    category varchar(20)
)
SERVER dbodtest
OPTIONS (
    schema 'DBONDEMAND_TEST',
    "table" 'DOD_COMMAND_PARAMS'
);
ALTER FOREIGN TABLE fo_dod_command_params ALTER COLUMN db_name OPTIONS (
    key 'true'
);

-- DOD_INSTANCE_CHANGES
CREATE FOREIGN TABLE fo_dod_instance_changes (
    username varchar(32) NOT NULL,
    db_name varchar(128) NOT NULL,
    attribute varchar(32) NOT NULL,
    change_date date NOT NULL,
    requester varchar(32) NOT NULL,
    old_value varchar(1024),
    new_value varchar(1024)
)
SERVER dbodtest
OPTIONS (
    schema 'DBONDEMAND_TEST',
    "table" 'DOD_INSTANCE_CHANGES'
);
ALTER FOREIGN TABLE fo_dod_instance_changes ALTER COLUMN db_name OPTIONS (
    key 'true'
);

-- DOD_INSTANCES
CREATE FOREIGN TABLE fo_dod_instances (
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
    id int,
)
SERVER dbodtest
OPTIONS (
    schema 'DBONDEMAND_TEST',
    "table" 'DOD_INSTANCES'
);
ALTER FOREIGN TABLE fo_dod_instances ALTER COLUMN db_name OPTIONS (
    key 'true'
);

-- DOD_JOBS
CREATE FOREIGN TABLE fo_dod_jobs (
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
SERVER dbodtest
OPTIONS (
    schema 'DBONDEMAND_TEST',
    "table" 'DOD_JOBS'
);
ALTER FOREIGN TABLE fo_dod_jobs ALTER COLUMN db_name OPTIONS (
    key 'true'
);

-- DOD_UPGRADES
CREATE FOREIGN TABLE fo_dod_upgrades (
    db_type varchar(32) NOT NULL,
    category varchar(32) NOT NULL,
    version_from varchar(128) NOT NULL,
    version_to varchar(128) NOT NULL
)
SERVER dbodtest
OPTIONS (
    schema 'DBONDEMAND_TEST',
    "table" 'DOD_UPGRADES'
);
ALTER FOREIGN TABLE fo_dod_upgrades ALTER COLUMN db_type OPTIONS (
    key 'true'
);
ALTER FOREIGN TABLE fo_dod_upgrades ALTER COLUMN category OPTIONS (
    key 'true'
);
ALTER FOREIGN TABLE fo_dod_upgrades ALTER COLUMN version_from OPTIONS (
    key 'true'
);

-- Views to ensure backward compatibility
CREATE OR REPLACE VIEW dod_instances AS
SELECT * FROM fo_dod_instances;

CREATE OR REPLACE VIEW dod_jobs AS
SELECT * FROM fo_dod_jobs;

CREATE OR REPLACE VIEW dod_upgrades AS
SELECT * FROM fo_dod_upgrades;

CREATE OR REPLACE VIEW dod_instance_changes AS
SELECT * FROM fo_dod_instance_changes;

CREATE OR REPLACE VIEW dod_command_params AS
SELECT * FROM fo_dod_command_params;

CREATE OR REPLACE VIEW dod_command_definition AS
SELECT * FROM fo_dod_command_definition;
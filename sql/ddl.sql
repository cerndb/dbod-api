CREATE FOREIGN TABLE fo_instance (
    id integer NOT NULL,
    username varchar(32) NOT NULL,
    db_name varchar(128) NOT NULL,
    host varchar(128) NOT NULL,  -- define as array: host integer ARRAY[4]
    e_group varchar(256),
    category varchar(32) NOT NULL,
    creation_date date NOT NULL,
    expiry_date date,
    db_type varchar(32) NOT NULL,
    version varchar(128),
    project varchar(128),
    description varchar(1024),
    state varchar(32) NOT NULL,
    status varchar(1) NOT NULL,
    master varchar(32),  -- references a host: master integer FK
    slave varchar(32)    -- references a host: master integer FK
)
SERVER dbodtest
OPTIONS (
    schema 'DBONDEMAND_TEST',
    "table" 'INSTANCE'
);
ALTER FOREIGN TABLE fo_instance ALTER COLUMN id OPTIONS (
    key 'true'
);

CREATE TYPE instance_category AS ENUM ('REF', 'DEV', 'PROD');
CREATE TYPE instance_type AS ENUM ('MYSQL', 'PGSQL', 'ORACLE', 'ORA');
CREATE TABLE instance (
    id integer NOT NULL,
    owner varchar(32) NOT NULL,
    name varchar(8) NOT NULL,
    host integer ARRAY[4] NOT NULL,
    port integer NOT NULL,
    egroup varchar(256),
    category instance_category NOT NULL,
    creation date NOT NULL,
    expiration date,
    type instance_type NOT NULL,
    version varchar(128),
    project varchar(128),
    description varchar(1024),
    state varchar(32) NOT NULL,
    status varchar(1) NOT NULL,
    master integer,  -- references a host: master integer FK
    slave integer,   -- references a host: master integer FK
    buffer varchar(16) NOT NULL DEFAULT '1G'
);

CREATE TABLE volume (
    id serial,
    instance_id integer NOT NULL,
    file_mode char(4) NOT NULL,
    owner varchar(32) NOT NULL,
    vgroup varchar(32) NOT NULL,
    server varchar(63) NOT NULL,
    mount_options varchar(256) NOT NULL,
    mounting_path varchar(256) NOT NULL
);

CREATE TABLE host (
    id serial,
    name varchar(63) NOT NULL,
    memory integer NOT NULL
);

CREATE TABLE attributes (
    id INTEGER NOT NULL,
    instance_id integer NOT NULL,
    name varchar(32) NOT NULL,
    value varchar(250) NOT NULL
);


CREATE FOREIGN TABLE upgrade (
    db_type varchar(32) NOT NULL,
    category varchar(32) NOT NULL,
    version_from varchar(128) NOT NULL,
    version_to varchar(128) NOT NULL
)
SERVER testdbod
OPTIONS (
    schema 'DBONDEMAND_TEST',
    "table" 'UPGRADE'
);
ALTER FOREIGN TABLE upgrade ALTER COLUMN db_type OPTIONS (
    key 'true'
);
ALTER FOREIGN TABLE upgrade ALTER COLUMN category OPTIONS (
    key 'true'
);
ALTER FOREIGN TABLE upgrade ALTER COLUMN version_from OPTIONS (
    key 'true'
);

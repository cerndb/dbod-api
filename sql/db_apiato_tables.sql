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
  CONSTRAINT volume_attribute_volume_fk  FOREIGN KEY (volume_id) REFERENCES apiato.volume (volume_id)  ON DELETE CASCADE,
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

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
-- Rename attribute table
ALTER TABLE public.attribute RENAME TO instance_attribute;

-- Redefinte attribute view
DROP VIEW IF EXISTS api.attribute;
CREATE VIEW api.instance_attribute AS
SELECT * FROM public.instance_attribute;

--- Redefine metadata view
-- Get volumes function
CREATE OR REPLACE FUNCTION api.get_volumes(pid INTEGER)
RETURNS JSON[] AS $$
DECLARE
  volumes JSON[];
BEGIN
  SELECT ARRAY (SELECT row_to_json(t) FROM (SELECT * FROM public.volume WHERE instance_id = pid) t) INTO volumes;
  return volumes;
END
$$ LANGUAGE plpgsql;

-- Get instance attribute function
CREATE OR REPLACE FUNCTION api.get_instance_attribute(attribute_name VARCHAR, iid INTEGER)
RETURNS VARCHAR AS $$
DECLARE
  res VARCHAR;
BEGIN
  SELECT name, value FROM public.instance_attribute A WHERE A.instance_id = iid AND A.name = attribute_name INTO res;
  return res;
END
$$ LANGUAGE plpgsql;

-- Get attributes function
CREATE OR REPLACE FUNCTION api.get_instance_attributes(inst_id INTEGER)
  RETURNS JSON AS $$
DECLARE
  attributes JSON;
BEGIN
  SELECT json_object(j.body::text[]) FROM
    (SELECT '{' || string_agg( buf, ',' ) || '}' body
     FROM
       (SELECT  name::text || ', ' || value::text buf
        FROM public.instance_attribute
        WHERE instance_id = inst_id) t) j INTO attributes;
  return attributes;
END
$$ LANGUAGE plpgsql;

-- Instance table

--- Requirements

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


DROP VIEW IF EXISTS public.instance CASCADE;
DROP TABLE IF EXISTS public.instance;

CREATE TABLE IF NOT EXISTS public.instance (
    id                   serial,
    owner                varchar(32) NOT NULL,
    name                 varchar(128) UNIQUE NOT NULL,
    e_group              varchar(256),
    category             public.instance_category NOT NULL,
    creation_date        date NOT NULL,
    expiry_date          date,
    type_id              int NOT NULL,
    size                 int,
    no_connections       int,
    project              varchar(128),
    description          varchar(1024),
    version              varchar(128),
    master_id            int,
    slave_id             int,
    host_id              int,
    state                public.instance_state NOT NULL,
    status               public.instance_status NOT NULL,
    cluster_id           int,
    CONSTRAINT instance_pkey               PRIMARY KEY (id),
    CONSTRAINT instance_master_fk          FOREIGN KEY (master_id) REFERENCES public.instance (id),
    CONSTRAINT instance_slave_fk           FOREIGN KEY (slave_id)  REFERENCES public.instance (id),
    CONSTRAINT instance_host_fk            FOREIGN KEY (host_id)   REFERENCES public.host     (id),
    CONSTRAINT instance_instance_type_fk   FOREIGN KEY (type_id)   REFERENCES public.instance_type (id)
);
--FK INDEXES for INSTANCE table
CREATE INDEX instance_host_idx      ON public.instance (host_id);
CREATE INDEX instance_master_idx    ON public.instance (master_id);
CREATE INDEX instance_slave_idx     ON public.instance (slave_id);
CREATE INDEX instance_type_idx      ON public.instance (type_id);

--- Add Volume related DB objects
\ir db_add_volume.sql
---

-- Metadata View
DROP VIEW IF EXISTS api.metadata;
CREATE OR REPLACE VIEW api.metadata AS
  SELECT
    instance.id AS id,
    instance.owner AS username,
    instance.name AS db_name,
    instance.category "class",
    instance_type.type AS type,
    instance.version,
    string_to_array(host.name::text, ','::text) as hosts,
    api.get_instance_attributes(public.instance.id) attributes,
    api.get_instance_attribute('port', public.instance.id ) port,
    api.get_volumes(public.instance.id) volumes,
    instance.cluster_id
  FROM public.instance
    JOIN public.instance_type ON public.instance.type_id = public.instance_type.id
    LEFT JOIN public.host ON public.instance.host_id = public.host.id,
    api.get_volumes(public.instance.id);


--- API Views
-- Volume View
DROP VIEW IF EXISTS api.volume;
CREATE OR REPLACE VIEW api.volume AS
SELECT volume.id AS id,
       volume.instance_id,
       volume.file_mode,
       volume.owner,
       volume."group",
       volume.mount_options,
       public.instance.name AS name,
       public.volume_type.type AS type,
       volume.server,
       volume.mounting_path,
       api.get_volume_attributes(public.volume.id) as attributes
FROM public.volume
  JOIN public.volume_type ON public.volume.volume_type_id = public.volume_type.id
  JOIN public.instance ON public.volume.instance_id = public.instance.id;

-- Instance View
DROP VIEW IF EXISTS api.instance;
CREATE OR REPLACE VIEW api.instance AS
SELECT instance.id AS id,
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
FROM public.instance
  LEFT JOIN public.instance AS instance_master ON public.instance.id = instance_master.id
  LEFT JOIN public.instance AS instance_slave ON public.instance.id = instance_slave.id
  JOIN public.instance_type ON public.instance.type_id = public.instance_type.id
  JOIN public.host ON public.instance.host_id = public.host.id;

-- Insert instance
CREATE OR REPLACE FUNCTION api.insert_instance(in_json JSON) RETURNS INTEGER AS $$
DECLARE
  instance_id     int;
  instance_json   json;
  volumes_json    json;
  attributes_json json;
BEGIN
  --Get the new instance_id to be used in the insertion
   SELECT nextval(pg_get_serial_sequence('public.instance', 'id')) INTO instance_id;
   instance_json := in_json::jsonb || ('{ "id" :' || instance_id || '}')::jsonb;

   INSERT INTO public.instance SELECT * FROM json_populate_record(null::public.instance, instance_json);

   --Inserting Attributes
   attributes_json := instance_json::json->'attributes';
   PERFORM api.insert_instance_attribute(instance_id, (json_array_elements(attributes_json)::jsonb)::json);

   --Inserting Volumes
   volumes_json := instance_json::json->'volumes';
   PERFORM api.insert_volume((json_array_elements(volumes_json)::jsonb || ('{ "instance_id" :' || instance_id || '}')::jsonb)::json);

  RETURN instance_id;
END
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION api.insert_instance(id int, in_json JSON) RETURNS INTEGER AS $$
DECLARE
  instance_json   json;
  volumes_json    json;
  attributes_json json;
BEGIN
  --Get the new instance_id to be used in the insertion
   instance_json := in_json::jsonb || ('{ "id" :' || id || '}')::jsonb;

   INSERT INTO public.instance SELECT * FROM json_populate_record(null::public.instance, instance_json);

   --Inserting Attributes
   attributes_json := instance_json::json->'attributes';
   PERFORM api.insert_instance_attribute(instance_id, (json_array_elements(attributes_json)::jsonb)::json);

   --Inserting Volumes
   volumes_json := instance_json::json->'volumes';
   PERFORM api.insert_volume((json_array_elements(volumes_json)::jsonb || ('{ "instance_id" :' || instance_id || '}')::jsonb)::json);

  RETURN instance_id;
END
$$ LANGUAGE plpgsql;

--- Attributes

-- Get instance attribute function
CREATE OR REPLACE FUNCTION api.get_instance_attribute(attribute_name VARCHAR, instance_name varchar)
RETURNS varchar AS $$
DECLARE
res varchar;
BEGIN
  SELECT value FROM api.instance_attribute A WHERE A.instance_id = 
    (SELECT ID from api.instance where name = instance_name) AND
    A.name = attribute_name
    INTO res;
  RETURN res;  
END
$$ LANGUAGE plpgsql;

-- Get attributes function
CREATE OR REPLACE FUNCTION api.get_instance_attributes(instance_name varchar)
  RETURNS JSON AS $$
DECLARE
  attributes JSON;
  inst_id integer;
BEGIN
  SELECT id from api.instance where name = instance_name INTO inst_id;
  SELECT json_object(j.body::text[]) FROM
    (SELECT '{' || string_agg( buf, ',' ) || '}' body
     FROM
       (SELECT  name::text || ', ' || value::text buf
        FROM api.instance_attribute
        WHERE instance_id = inst_id) t) j INTO attributes;
  return attributes;
END
$$ LANGUAGE plpgsql;

--Instance Attributes by ID
CREATE OR REPLACE FUNCTION api.insert_instance_attribute(iid int, in_json JSON) RETURNS INTEGER AS $$
BEGIN

  INSERT INTO public.instance_attribute(instance_id, name, value)
  SELECT * FROM 
  (SELECT iid as instance_id, j.key as name, j.value from
    (SELECT * from json_each(in_json)) as j) as input;
  RETURN iid;

END
$$ LANGUAGE plpgsql;

-- Instance Attribute by instance name
CREATE OR REPLACE FUNCTION api.insert_instance_attribute(instance_name varchar, in_json JSON) RETURNS INTEGER AS $$
DECLARE
 iid integer;
 res integer;
BEGIN

  SELECT id from api.instance where name = instance_name INTO iid;
  SELECT api.insert_instance_attribute(iid, in_json) into res;
  RETURN res;

END
$$ LANGUAGE plpgsql;

--Instance Attributes
CREATE OR REPLACE FUNCTION api.update_instance_attribute(id int, in_json JSON) RETURNS INTEGER AS $$
DECLARE
  attribute_id    int;
  attributes_json json;
  attr_name       varchar;
  attr_value      varchar;

BEGIN

  --Get the new cluster_id to be used in the insertion
  SELECT nextval(pg_get_serial_sequence('public.instance_attribute', 'id')) INTO attribute_id;
  attributes_json := in_json::jsonb || ('{ "id" :' || attribute_id || '}')::jsonb;

  --Tranform key value to table format
  SELECT json_object_keys(in_json) INTO attr_name;
  SELECT in_json->>attr_name INTO attr_value;
  attributes_json := attributes_json::jsonb ||  ('{ "name" : "' || attr_name || '"}')::jsonb || ('{ "value" : "' || attr_value || '"}')::jsonb || ('{ "instance_id" :' || id || '}')::jsonb;


  INSERT INTO public.instance_attribute SELECT * FROM json_populate_record(null::public.instance_attribute,attributes_json);

  RETURN attribute_id;
END
$$ LANGUAGE plpgsql;

--Instance Attributes
CREATE OR REPLACE FUNCTION api.update_instance_attribute(attribute_name varchar, attribute_value varchar, instance_name varchar) RETURNS INTEGER AS $$
DECLARE
  attribute_id integer;
  iid integer;
BEGIN

  SELECT id from api.instance where name = instance_name INTO iid;
  select id from public.instance_attribute where instance_id = iid and name = attribute_name into attribute_id;
  if attribute_id is null
  then
    RAISE EXCEPTION 'Attribute not found %', attribute_id using hint = 'Attribute not found';
  end if;
  update public.instance_attribute set value = attribute_value where id = attribute_id;
  RETURN attribute_id;
END
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION api.delete_instance_attribute(instance_name VARCHAR, attribute_name varchar) RETURNS bool AS $$
DECLARE
  instance_id integer;
  success bool;
BEGIN
  SELECT id from api.instance where name = instance_name INTO instance_id;
  EXECUTE format(' DELETE FROM public.instance_attribute WHERE instance_id = $1 AND name=$2 RETURNING TRUE') USING instance_id, attribute_name INTO success;

  RETURN success;
END
$$ LANGUAGE plpgsql;

-- Delete Instance
CREATE OR REPLACE FUNCTION api.delete_instance(id int) RETURNS bool AS $$
DECLARE
 success bool;
BEGIN

   EXECUTE format(' DELETE FROM public.instance WHERE id = $1 RETURNING TRUE') USING id INTO success;

RETURN success;
END
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION api.delete_instance(instance_name varchar) RETURNS bool AS $$
DECLARE
 success bool;
 instance_id integer;
BEGIN
  SELECT id from api.instance where name = instance_name INTO instance_id;
  EXECUTE format(' DELETE FROM public.instance WHERE id = $1 RETURNING TRUE') USING instance_id INTO success;

RETURN success;
END
$$ LANGUAGE plpgsql;

--Instance
CREATE OR REPLACE FUNCTION api.update_instance(iid int, in_json JSON) RETURNS bool AS $$
DECLARE
 success bool;
BEGIN

   UPDATE public.instance
    SET owner         = (CASE WHEN src.in_json::jsonb ? 'owner' THEN src.owner ELSE public.instance.owner END),
        name          = (CASE WHEN src.in_json::jsonb ? 'name' THEN src.name ELSE public.instance.name END),
        e_group       = (CASE WHEN src.in_json::jsonb ? 'e_group' THEN src.e_group ELSE public.instance.e_group END),
        category      = (CASE WHEN src.in_json::jsonb ? 'category' THEN src.category ELSE public.instance.category END),
        creation_date = (CASE WHEN src.in_json::jsonb ? 'creation_date' THEN src.creation_date ELSE public.instance.creation_date END),
        expiry_date   = (CASE WHEN src.in_json::jsonb ? 'expiry_date' THEN src.expiry_date ELSE public.instance.expiry_date END),
        type_id       = (CASE WHEN src.in_json::jsonb ? 'type_id' THEN src.type_id ELSE public.instance.type_id END),
        project       = (CASE WHEN src.in_json::jsonb ? 'project' THEN src.project ELSE public.instance.project END),
        description   = (CASE WHEN src.in_json::jsonb ? 'description' THEN src.description ELSE public.instance.description END),
        version       = (CASE WHEN src.in_json::jsonb ? 'version' THEN src.version ELSE public.instance.version END),
        master_id     = (CASE WHEN src.in_json::jsonb ? 'master_id' THEN src.master_id ELSE public.instance.master_id END),
        slave_id      = (CASE WHEN src.in_json::jsonb ? 'slave_id' THEN src.slave_id ELSE public.instance.slave_id END),
        host_id       = (CASE WHEN src.in_json::jsonb ? 'host_id' THEN src.host_id ELSE public.instance.host_id END),
        state         = (CASE WHEN src.in_json::jsonb ? 'state' THEN src.state ELSE public.instance.state END),
        status        = (CASE WHEN src.in_json::jsonb ? 'status' THEN src.status ELSE public.instance.status END),
        cluster_id    = (CASE WHEN src.in_json::jsonb ? 'cluster_id' THEN src.cluster_id ELSE public.instance.cluster_id END)
     FROM (SELECT * FROM json_populate_record(null::public.instance,in_json)
           CROSS JOIN (SELECT in_json) AS source_json) src
    WHERE public.instance.id = iid;

RETURN success;
END
$$ LANGUAGE plpgsql;


-- Test DATA

-- Insert test data for instances
INSERT INTO public.instance (owner, name, e_group, category, creation_date, type_id, size, no_connections, project, description, version, master_id, slave_id, host_id, state, status, cluster_id)
VALUES ('user01', 'dbod01', 'testgroupA', 'TEST', now(), 2 , 100 , 100 , 'API' , 'Test instance 1'      , '5.6.17', NULL, NULL, 1, 'RUNNING', 'ACTIVE',     NULL),
       ('user01', 'dbod02', 'testgroupB', 'PROD', now(), 3 , 50  , 500 , 'API' , 'Test instance 2'      , '9.4.4' , NULL, NULL, 3, 'RUNNING', 'ACTIVE',     NULL),
       ('user02', 'dbod03', 'testgroupB', 'TEST', now(), 2 , 100 , 200 , 'WEB' , 'Expired instance 1'   , '5.5'   , NULL, NULL, 1, 'RUNNING', 'NON-ACTIVE', NULL),
       ('user03', 'dbod04', 'testgroupA', 'PROD', now(), 3 , 250 , 10  , 'LCC' , 'Test instance 3'      , '9.4.5' , NULL, NULL, 1, 'RUNNING', 'ACTIVE',     NULL),
       ('user04', 'dbod05', 'testgroupC', 'TEST', now(), 2 , 300 , 200 , 'WEB' , 'Test instance 4'      , '5.6.17', NULL, NULL, 1, 'RUNNING', 'ACTIVE',     NULL),
       ('user04', 'dbod06', 'testgroupC', 'TEST', now(), 2 , 300 , 200 , 'WEB' , 'Test instance 4'      , '5.6.17', NULL, NULL, 1, 'RUNNING', 'ACTIVE',     NULL),
       ('user05', 'node01', 'testgroupZ', 'DEV' , now(), 1 , NULL, NULL, 'NILE', 'Test zookeeper inst 1', '3.4.9' , NULL, NULL, 4, 'RUNNING', 'ACTIVE',     1),
       ('user05', 'node02', 'testgroupZ', 'DEV' , now(), 1 , NULL, NULL, 'NILE', 'Test zookeeper inst 2', '3.4.9' , NULL, NULL, 4, 'RUNNING', 'ACTIVE',     1);


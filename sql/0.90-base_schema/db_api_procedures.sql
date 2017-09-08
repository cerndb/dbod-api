-- Copyright (C) 2015, CERN
-- This software is distributed under the terms of the GNU General Public
-- Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".
-- In applying this license, CERN does not waive the privileges and immunities
-- granted to it by virtue of its status as Intergovernmental Organization
-- or submit itself to any jurisdiction.

CREATE SCHEMA IF NOT EXISTS api;

------------------------------------------
-- FUNCTIONS USED BY API
------------------------------------------

-- Get cluster instances
CREATE OR REPLACE FUNCTION api.get_cluster_instances(clus_id integer)
  RETURNS json[] AS $$
DECLARE
  instances JSON[];
BEGIN
  SELECT ARRAY (SELECT row_to_json(t) FROM (SELECT * FROM api.metadata WHERE cluster_id = clus_id) t) INTO instances;
  return instances;
END
$$ LANGUAGE plpgsql;

-- Insert cluster
CREATE OR REPLACE FUNCTION api.insert_cluster(in_json json)
  RETURNS integer AS $$
DECLARE
  cluster_id      int;
  cluster_json    json;
  attributes_json json;
BEGIN
  --Get the new cluster_id to be used in the insertion
  SELECT nextval(pg_get_serial_sequence('public.cluster', 'id')) INTO cluster_id;
  cluster_json := in_json::jsonb || ('{ "id" :' || cluster_id || '}')::jsonb;

  INSERT INTO public.cluster SELECT * FROM json_populate_record(null::public.cluster,cluster_json);

  --Inserting Attributes
  attributes_json := cluster_json::json->'attributes';
  PERFORM api.insert_cluster_attribute(cluster_id,(json_array_elements(attributes_json)::jsonb)::json);

  RETURN cluster_id;
END
$$ LANGUAGE plpgsql;

-- Update cluster
CREATE OR REPLACE FUNCTION api.update_cluster(
  cid integer,
  in_json json)
  RETURNS boolean AS $$
DECLARE
 success bool;
BEGIN
   UPDATE public.cluster
    SET owner         = (CASE WHEN src.in_json::jsonb ? 'owner' THEN src.owner ELSE public.cluster.owner END),
        name          = (CASE WHEN src.in_json::jsonb ? 'name' THEN src.name ELSE public.cluster.name END),
        e_group       = (CASE WHEN src.in_json::jsonb ? 'e_group' THEN src.e_group ELSE public.cluster.e_group END),
        category      = (CASE WHEN src.in_json::jsonb ? 'category' THEN src.category ELSE public.cluster.category END),
        creation_date = (CASE WHEN src.in_json::jsonb ? 'creation_date' THEN src.creation_date ELSE public.cluster.creation_date END),
        expiry_date   = (CASE WHEN src.in_json::jsonb ? 'expiry_date' THEN src.expiry_date ELSE public.cluster.expiry_date END),
        type_id       = (CASE WHEN src.in_json::jsonb ? 'type_id' THEN src.type_id ELSE public.cluster.type_id END),
        project       = (CASE WHEN src.in_json::jsonb ? 'project' THEN src.project ELSE public.cluster.project END),
        description   = (CASE WHEN src.in_json::jsonb ? 'description' THEN src.description ELSE public.cluster.description END),
        version       = (CASE WHEN src.in_json::jsonb ? 'version' THEN src.version ELSE public.cluster.version END),
        master_id     = (CASE WHEN src.in_json::jsonb ? 'master_id' THEN src.master_id ELSE public.cluster.master_id END),
        state         = (CASE WHEN src.in_json::jsonb ? 'state' THEN src.state ELSE public.cluster.state END),
        status        = (CASE WHEN src.in_json::jsonb ? 'status' THEN src.status ELSE public.cluster.status END)
    FROM (SELECT * FROM json_populate_record(null::public.cluster,in_json)
        CROSS JOIN (SELECT in_json) AS source_json) src
    WHERE public.cluster.id = cid;
RETURN success;
END
$$ LANGUAGE plpgsql;

-- Delete cluster
CREATE OR REPLACE FUNCTION api.delete_cluster(cid integer)
  RETURNS boolean AS $$
DECLARE
  success bool;
BEGIN
  DELETE FROM public.cluster WHERE public.cluster.id = cid RETURNING TRUE INTO success;
RETURN success;
END
$$ LANGUAGE plpgsql;

-- Get cluster attribute by id
CREATE OR REPLACE FUNCTION api.get_cluster_attribute(
  attr_name character varying,
  clus_id integer)
  RETURNS character varying AS $$
DECLARE
  res VARCHAR;
BEGIN
  SELECT value FROM public.cluster_attribute A WHERE A.id = clus_id AND A.name = attr_name INTO res;
  return res;
END
$$ LANGUAGE plpgsql;

-- Get cluster attributes
CREATE OR REPLACE FUNCTION api.get_cluster_attributes(clus_id integer)
  RETURNS json AS $$
DECLARE
  attributes JSON;
BEGIN
  SELECT json_object(j.body::text[]) FROM
    (SELECT '{' || string_agg( buf, ',' ) || '}' body
     FROM
       (SELECT  name::text || ', ' || value::text buf
        FROM public.cluster_attribute
        WHERE cluster_id = clus_id) t) j INTO attributes;
  return attributes;
END
$$ LANGUAGE plpgsql;

-- Insert cluster attribute
CREATE OR REPLACE FUNCTION api.insert_cluster_attribute(
  id integer,
  in_json json)
  RETURNS integer AS $$
DECLARE
  attribute_id    int;
  cluster_id      int;
  attributes_json json;
  attr_name       varchar;
  attr_value      varchar;
BEGIN
  --Get the new cluster_id to be used in the insertion
  SELECT nextval(pg_get_serial_sequence('public.cluster_attribute', 'id')) INTO attribute_id;
  attributes_json := in_json::jsonb || ('{ "id" :' || attribute_id || '}')::jsonb;

  --Tranform key value to table format
  SELECT json_object_keys(in_json) INTO attr_name;
  SELECT in_json->>attr_name INTO attr_value;
  attributes_json := attributes_json::jsonb ||  ('{ "name" : "' || attr_name || '"}')::jsonb || ('{ "value" : "' || attr_value || '"}')::jsonb || ('{ "cluster_id" :' || id || '}')::jsonb;

  --Get the new attribute_id to be used in the insertion
  SELECT nextval(pg_get_serial_sequence('public.cluster_attribute', 'id')) INTO attribute_id;
  attributes_json := attributes_json::jsonb || ('{ "id" :' || attribute_id || '}')::jsonb;

  INSERT INTO public.cluster_attribute SELECT * FROM json_populate_record(null::public.cluster_attribute,attributes_json);
  RETURN attribute_id;
END
$$ LANGUAGE plpgsql;

-- Update cluster attribute
CREATE OR REPLACE FUNCTION api.update_cluster_attribute(
  id integer,
  in_json json)
  RETURNS boolean AS $$
DECLARE
  success bool;
  attr_name varchar;
  attr_value varchar;
BEGIN
  SELECT json_object_keys(in_json) INTO attr_name;
  SELECT in_json->>attr_name INTO attr_value;
   UPDATE public.cluster_attribute
    SET value = attr_value
    WHERE public.cluster_attribute.cluster_id = id AND public.cluster_attribute.name = attr_name;
RETURN TRUE;
END
$$ LANGUAGE plpgsql;

-- Delete cluster attribute
CREATE OR REPLACE FUNCTION api.delete_cluster_attribute(
    cluster_id integer,
    attribute_name character varying)
  RETURNS boolean AS $$
DECLARE
  success bool;
BEGIN
  EXECUTE format(' DELETE FROM public.cluster_attribute WHERE cluster_id = $1 AND name=$2 RETURNING TRUE') 
    USING cluster_id, attribute_name INTO success;
  RETURN success;
END
$$ LANGUAGE plpgsql;

-- Insert instance with known id
CREATE OR REPLACE FUNCTION api.insert_instance(
  id integer,
  in_json json)
  RETURNS integer AS $$
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

-- Insert instance without id
CREATE OR REPLACE FUNCTION api.insert_instance(in_json json)
  RETURNS integer AS $$
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

-- Update instance
CREATE OR REPLACE FUNCTION api.update_instance(
  iid integer,
  in_json json)
  RETURNS boolean AS $$
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

-- Delete instance by name
CREATE OR REPLACE FUNCTION api.delete_instance(instance_name character varying)
  RETURNS boolean AS $$
DECLARE
  success bool;
  instance_id integer;
BEGIN
  SELECT id from api.instance where name = instance_name INTO instance_id;
  EXECUTE format(' DELETE FROM public.instance WHERE id = $1 RETURNING TRUE') USING instance_id INTO success;
RETURN success;
END
$$ LANGUAGE plpgsql;

-- Delete instance by id
CREATE OR REPLACE FUNCTION api.delete_instance(id integer)
  RETURNS boolean AS $$
DECLARE
  success bool;
BEGIN
  EXECUTE format(' DELETE FROM public.instance WHERE id = $1 RETURNING TRUE') USING id INTO success;
RETURN success;
END
$$ LANGUAGE plpgsql;

-- Get instance attribute by id
CREATE OR REPLACE FUNCTION api.get_instance_attribute(
  attribute_name character varying,
  iid integer)
  RETURNS character varying AS $$
DECLARE
  res VARCHAR;
BEGIN
  SELECT name, value FROM public.instance_attribute A WHERE A.instance_id = iid AND A.name = attribute_name INTO res;
  return res;
END
$$ LANGUAGE plpgsql;

-- Get instance attribute by name
CREATE OR REPLACE FUNCTION api.get_instance_attribute(
  attribute_name character varying,
  instance_name character varying)
  RETURNS character varying AS $$
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

-- Get instance attributes by id
CREATE OR REPLACE FUNCTION api.get_instance_attributes(inst_id integer)
  RETURNS json AS $$
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

-- Get instance attributes by name
CREATE OR REPLACE FUNCTION api.get_instance_attributes(instance_name character varying)
  RETURNS json AS $$
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

-- Insert instance attribute by instance id
CREATE OR REPLACE FUNCTION api.insert_instance_attribute(
  iid integer,
  in_json json)
  RETURNS integer AS $$
BEGIN
  INSERT INTO public.instance_attribute(instance_id, name, value)
  SELECT * FROM 
  (SELECT iid as instance_id, j.key as name, j.value from
    (SELECT * from json_each(in_json)) as j) as input;
  RETURN iid;
END
$$ LANGUAGE plpgsql;

-- Insert instance attribute by instance name
CREATE OR REPLACE FUNCTION api.insert_instance_attribute(
  instance_name character varying,
  in_json json)
  RETURNS integer AS $$
DECLARE
 iid integer;
 res integer;
BEGIN

  SELECT id from api.instance where name = instance_name INTO iid;
  SELECT api.insert_instance_attribute(iid, in_json) into res;
  RETURN res;

END
$$ LANGUAGE plpgsql;

-- Update instance attribute by id
CREATE OR REPLACE FUNCTION api.update_instance_attribute(
  id integer,
  in_json json)
  RETURNS integer AS $$
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

-- Update instance attribute by name
CREATE OR REPLACE FUNCTION api.update_instance_attribute(
  attribute_name character varying,
  attribute_value character varying,
  instance_name character varying)
  RETURNS integer AS $$
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

-- Delete instance attribute
CREATE OR REPLACE FUNCTION api.delete_instance_attribute(
    instance_name character varying,
    attribute_name character varying)
  RETURNS boolean AS $$
DECLARE
  instance_id integer;
  success bool;
BEGIN
  SELECT id from api.instance where name = instance_name INTO instance_id;
  EXECUTE format(' DELETE FROM public.instance_attribute WHERE instance_id = $1 AND name=$2 RETURNING TRUE') USING instance_id, attribute_name INTO success;
  RETURN success;
END
$$ LANGUAGE plpgsql;

-- Get volumes for instance id
CREATE OR REPLACE FUNCTION api.get_volumes(pid integer)
  RETURNS json[] AS $$
DECLARE
  volumes JSON[];
BEGIN
  SELECT ARRAY (SELECT row_to_json(t) FROM (SELECT * FROM public.volume WHERE instance_id = pid) t) INTO volumes;
  return volumes;
END
$$ LANGUAGE plpgsql;

-- Insert volume
CREATE OR REPLACE FUNCTION api.insert_volume(in_json json)
  RETURNS integer AS $$
DECLARE
  volume_id       int;
  volume_json     json;
  attributes_json json;
BEGIN
  --Get the new volume_id to be used in the insertion
   SELECT nextval(pg_get_serial_sequence('public.volume', 'id')) INTO volume_id;
   volume_json := in_json::jsonb || ('{ "id" :' || volume_id || '}')::jsonb;

   INSERT INTO public.volume SELECT * FROM json_populate_record(null::public.volume, volume_json);

   --Inserting Attributes
   attributes_json := volume_json::json->'attributes';
   PERFORM api.insert_volume_attribute(volume_id,(json_array_elements(attributes_json)::jsonb)::json);

  RETURN volume_id;
END
$$ LANGUAGE plpgsql;

-- Delete volume
CREATE OR REPLACE FUNCTION api.delete_volume(id integer)
  RETURNS boolean AS $$
DECLARE
  success bool;
BEGIN
  EXECUTE format(' DELETE FROM public.volume WHERE id = $1 RETURNING TRUE') USING id INTO success;
RETURN success;
END
$$ LANGUAGE plpgsql;

-- Get volume attribute
CREATE OR REPLACE FUNCTION api.get_volume_attribute(
  attr_name character varying,
  vol_id integer)
  RETURNS character varying AS $$
DECLARE
  res VARCHAR;
BEGIN
  SELECT value FROM api.volume_attribute A WHERE A.instance_id = vol_id AND A.name = attr_name INTO res;
  return res;
END
$$ LANGUAGE plpgsql;

-- Get volume attributes
CREATE OR REPLACE FUNCTION api.get_volume_attributes(vol_id integer)
  RETURNS json AS $$
DECLARE
  attributes JSON;
BEGIN
  SELECT json_object(j.body::text[]) FROM
    (SELECT '{' || string_agg( buf, ',' ) || '}' body
     FROM
       (SELECT  name::text || ', ' || value::text buf
        FROM public.volume_attribute
        WHERE volume_id = vol_id) t) j INTO attributes;
  return attributes;
END
$$ LANGUAGE plpgsql;

-- Insert volume attribute
CREATE OR REPLACE FUNCTION api.insert_volume_attribute(
  id integer,
  in_json json)
  RETURNS integer AS $$
DECLARE
  attribute_id    int;
  attributes_json json;
  attr_name       varchar;
  attr_value      varchar;
BEGIN
  --Get the new volume_id to be used in the insertion
  SELECT nextval(pg_get_serial_sequence('public.volume_attribute', 'id')) INTO attribute_id;
  attributes_json := in_json::jsonb || ('{ "id" :' || attribute_id || '}')::jsonb;

  --Tranform key value to table format
  SELECT json_object_keys(in_json) INTO attr_name;
  SELECT in_json->>attr_name INTO attr_value;
  attributes_json := attributes_json::jsonb ||  ('{ "name" : "' || attr_name || '"}')::jsonb || ('{ "value" : "' || attr_value || '"}')::jsonb || ('{ "volume_id" :' || id || '}')::jsonb;

  INSERT INTO public.volume_attribute SELECT * FROM json_populate_record(null::public.volume_attribute,attributes_json);
  RETURN attribute_id;
END
$$ LANGUAGE plpgsql;

-- Update volume attribute
CREATE OR REPLACE FUNCTION api.update_volume_attribute(
  id integer,
  in_json json)
  RETURNS boolean AS $$
DECLARE
  success bool;
  attr_name varchar;
  attr_value varchar;
BEGIN
  SELECT json_object_keys(in_json) INTO attr_name;
  SELECT in_json->>attr_name INTO attr_value;
  UPDATE public.volume_attribute
  SET value = attr_value
  WHERE public.volume_attribute.volume_id = id AND public.volume_attribute.name = attr_name;

  RETURN TRUE;
END
$$ LANGUAGE plpgsql;

-- Delete volume attribute
CREATE OR REPLACE FUNCTION api.delete_volume_attribute(
  volume_id integer,
  attribute_name character varying)
  RETURNS boolean AS $$
DECLARE
  success bool;
BEGIN
  EXECUTE format(' DELETE FROM public.volume_attribute WHERE volume_id = $1 AND name=$2 RETURNING TRUE') USING volume_id, attribute_name INTO success;
  RETURN success;
END
$$ LANGUAGE plpgsql;

-- Get directories function
CREATE OR REPLACE FUNCTION api.get_directories(inst_name VARCHAR, type VARCHAR, version VARCHAR, port VARCHAR)
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
      ('/ORA/dbs03/' || upper(inst_name) )::VARCHAR datadir,
      ('/ORA/dbs02/' || upper(inst_name) )::VARCHAR logdir,
      ('/var/lib/pgsql/')::VARCHAR socket;
  ELSIF type = 'ORACLE' or type = 'ORA' THEN
    RETURN QUERY SELECT
      ('/ORA/dbs01/oracle/product/rdbms')::VARCHAR basedir, -- home
      ('/ORA/dbs01/oracle/product/rdbms')::VARCHAR bindir, -- home
      ('/ORA/dbs03/' || upper(inst_name) )::VARCHAR datadir,
      ('/ORA/dbs02/' || upper(inst_name) )::VARCHAR logdir,
      ('/ORA/dbs01/oracle/product/rdbms/network/admin')::VARCHAR socket; -- tnsnames
  END IF;
END
$$ LANGUAGE plpgsql;

-- Get owner information for the instance
CREATE OR REPLACE FUNCTION api.get_owner_data(db_name varchar)
  RETURNS json AS $$
DECLARE
  owner JSON;
BEGIN
  SELECT row_to_json(t) FROM (SELECT * FROM public.fim_data WHERE instance_name = db_name) t INTO owner;
  return owner;
END
$$ LANGUAGE plpgsql;
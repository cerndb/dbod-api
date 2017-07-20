--VOLUME_TYPE
CREATE TABLE IF NOT EXISTS public.volume_type (
  id   serial,
  type             varchar(64) UNIQUE NOT NULL,
  description      varchar(1024),
  CONSTRAINT volume_type_pkey PRIMARY KEY (id)
);

--- Tables
-- VOLUME_ATTRIBUTE
CREATE TABLE IF NOT EXISTS public.volume_attribute (
  id serial,
  volume_id    integer NOT NULL,
  name         varchar(32) NOT NULL,
  value        varchar(250) NOT NULL,
  CONSTRAINT volume_attribute_pkey       PRIMARY KEY (id),
  CONSTRAINT volume_attribute_volume_fk  FOREIGN KEY (volume_id) REFERENCES public.volume (id)  ON DELETE CASCADE,
  UNIQUE (volume_id, name)
);
CREATE INDEX IF NOT EXISTS volume_attribute_volume_idx ON public.volume_attribute (id);

-- Modify volume table
alter table public.volume add column if not exists volume_type_id int;

--- Procedures
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

-- Get volume attribute function
CREATE OR REPLACE FUNCTION api.get_volume_attribute(attr_name VARCHAR, vol_id INTEGER)
  RETURNS VARCHAR AS $$
DECLARE
  res VARCHAR;
BEGIN
  SELECT value FROM api.volume_attribute A WHERE A.instance_id = vol_id AND A.name = attr_name INTO res;
  return res;
END
$$ LANGUAGE plpgsql;

-- Get attributes function
CREATE OR REPLACE FUNCTION api.get_volume_attributes(vol_id INTEGER)
  RETURNS JSON AS $$
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

--Volume
CREATE OR REPLACE FUNCTION api.insert_volume(in_json JSON) RETURNS INTEGER AS $$
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

--Instance Attributes
CREATE OR REPLACE FUNCTION api.insert_volume_attribute(id int, in_json JSON) RETURNS INTEGER AS $$
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

CREATE OR REPLACE FUNCTION api.delete_volume(id int) RETURNS bool AS $$
DECLARE
 success bool;
BEGIN

   EXECUTE format(' DELETE FROM public.volume WHERE id = $1 RETURNING TRUE') USING id INTO success;

RETURN success;
END
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION api.delete_volume_attribute(volume_id int, attribute_name varchar) RETURNS bool AS $$
DECLARE
  success bool;
BEGIN

  EXECUTE format(' DELETE FROM public.volume_attribute WHERE volume_id = $1 AND name=$2 RETURNING TRUE') USING volume_id, attribute_name INTO success;

  RETURN success;
END
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION api.update_volume_attribute(id int, in_json JSON) RETURNS bool AS $$
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

--- Data
DELETE from volume_type where true;
INSERT INTO public.volume_type (type, description)
    VALUES ('NETAPP', 'NETAPP volume type'),
           ('CEPTH',  'CEPTH volume type');


DELETE from public.volume where true;
INSERT INTO public.volume (instance_id, volume_type_id, file_mode, owner, "group", server, mount_options, mounting_path)
VALUES (1, 1, '0755', 'TSM', 'ownergroup', 'NAS-server', 'rw,bg,hard', '/MNT/data1'),
       (1, 1, '0755', 'TSM', 'ownergroup', 'NAS-server', 'rw', '/MNT/bin'),
       (2, 1, '0755', 'TSM', 'ownergroup', 'NAS-server', 'rw,bg,hard', '/MNT/data2'),
       (4, 1, '0755', 'TSM', 'ownergroup', 'NAS-server', 'rw,bg,hard,tcp', '/MNT/data4'),
       (5, 1, '0755', 'TSM', 'ownergroup', 'NAS-server', 'rw,bg,hard', '/MNT/data5'),
       (5, 1, '0755', 'TSM', 'ownergroup', 'NAS-server', 'rw', '/MNT/bin'),
       (6, 1, '0755', 'TSM', 'ownergroup', 'NAS-server', 'rw', '/MNT/zk'),
       (7, 1, '0755', 'TSM', 'ownergroup', 'NAS-server', 'rw', '/MNT/zk'),
       (7, 2, '0755', 'TSM', 'ownergroup', 'NAS-server', 'rw,bg,hard', '/MNT/data01');


DELETE from public.volume_attribute where true;
INSERT INTO public.volume_attribute (volume_id, name, value)
VALUES (8, 'ro', 'TRUE'),
       (8, 'fw', 'TRUE'),
       (9, 'ro', 'FALSE');

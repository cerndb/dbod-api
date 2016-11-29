------------------------------
-- FUNCTIONS
------------------------------

-- Get hosts function
CREATE OR REPLACE FUNCTION apiato.get_hosts(host_ids INTEGER[])
RETURNS VARCHAR[] AS $$
DECLARE
  hosts VARCHAR := '';
BEGIN
  SELECT ARRAY (SELECT name FROM host WHERE host_id = ANY(host_ids)) INTO hosts;
  RETURN hosts;
END
$$ LANGUAGE plpgsql;


-- Get volumes function
CREATE OR REPLACE FUNCTION apiato.get_volumes(pid INTEGER)
RETURNS JSON[] AS $$
DECLARE
  volumes JSON[];
BEGIN
  SELECT ARRAY (SELECT row_to_json(t) FROM (SELECT * FROM apiato.volume WHERE instance_id = pid) t) INTO volumes;
  return volumes;
END
$$ LANGUAGE plpgsql;

-- Get instance attribute function
CREATE OR REPLACE FUNCTION apiato.get_instance_attribute(attr_name VARCHAR, inst_id INTEGER)
RETURNS VARCHAR AS $$
DECLARE
  res VARCHAR;
BEGIN
  SELECT value FROM apiato.instance_attribute A WHERE A.instance_id = inst_id AND A.name = attr_name INTO res;
  return res;
END
$$ LANGUAGE plpgsql;

-- Get instance attribute function
CREATE OR REPLACE FUNCTION apiato.get_volume_attribute(attr_name VARCHAR, vol_id INTEGER)
  RETURNS VARCHAR AS $$
DECLARE
  res VARCHAR;
BEGIN
  SELECT value FROM apiato.volume_attribute A WHERE A.instance_id = vol_id AND A.name = attr_name INTO res;
  return res;
END
$$ LANGUAGE plpgsql;

-- Get instance attribute function
CREATE OR REPLACE FUNCTION apiato.get_cluster_attribute(attr_name VARCHAR, clus_id INTEGER)
  RETURNS VARCHAR AS $$
DECLARE
  res VARCHAR;
BEGIN
  SELECT value FROM apiato.cluster_attribute A WHERE A.cluster_id = clus_id AND A.name = attr_name INTO res;
  return res;
END
$$ LANGUAGE plpgsql;

-- Get attributes function
CREATE OR REPLACE FUNCTION apiato.get_instance_attributes(inst_id INTEGER)
  RETURNS JSON AS $$
DECLARE
  attributes JSON;
BEGIN
  SELECT json_object(j.body::text[]) FROM
    (SELECT '{' || string_agg( buf, ',' ) || '}' body
     FROM
       (SELECT  name::text || ', ' || value::text buf
        FROM apiato.instance_attribute
        WHERE instance_id = inst_id) t) j INTO attributes;
  return attributes;
END
$$ LANGUAGE plpgsql;

-- Get attributes function
CREATE OR REPLACE FUNCTION apiato.get_volume_attributes(vol_id INTEGER)
  RETURNS JSON AS $$
DECLARE
  attributes JSON;
BEGIN
  SELECT json_object(j.body::text[]) FROM
    (SELECT '{' || string_agg( buf, ',' ) || '}' body
     FROM
       (SELECT  name::text || ', ' || value::text buf
        FROM apiato.volume_attribute
        WHERE volume_id = vol_id) t) j INTO attributes;
  return attributes;
END
$$ LANGUAGE plpgsql;

-- Get attributes function
CREATE OR REPLACE FUNCTION apiato.get_cluster_attributes(clus_id INTEGER)
  RETURNS JSON AS $$
DECLARE
  attributes JSON;
BEGIN
  SELECT json_object(j.body::text[]) FROM
    (SELECT '{' || string_agg( buf, ',' ) || '}' body
     FROM
       (SELECT  name::text || ', ' || value::text buf
        FROM apiato.cluster_attribute
        WHERE cluster_id = clus_id) t) j INTO attributes;
  return attributes;
END
$$ LANGUAGE plpgsql;

-- Get attributes function
CREATE OR REPLACE FUNCTION apiato.get_cluster_instances(clus_id INTEGER)
RETURNS JSON[] AS $$
DECLARE
  instances JSON[];
BEGIN
  SELECT ARRAY (SELECT row_to_json(t) FROM (SELECT * FROM apiato_ro.metadata WHERE cluster_id = clus_id) t) INTO instances;
  return instances;
END
$$ LANGUAGE plpgsql;



--------------------------------
-- INSERT PROCEDURES
--------------------------------
--Clusters
CREATE OR REPLACE FUNCTION apiato_ro.insert_cluster(in_json JSON) RETURNS INTEGER AS $$
DECLARE
  cluster_id      int;
  cluster_json    json;
  attributes_json json;
BEGIN
  --Get the new cluster_id to be used in the insertion
   SELECT nextval(pg_get_serial_sequence('apiato.cluster', 'cluster_id')) INTO cluster_id;
   cluster_json := in_json::jsonb || ('{ "cluster_id" :' || cluster_id || '}')::jsonb;

   INSERT INTO apiato.cluster SELECT * FROM json_populate_record(null::apiato.cluster,cluster_json);

   --Inserting Attributes
   attributes_json := cluster_json::json->'attributes';
   PERFORM apiato_ro.insert_cluster_attributes(cluster_id,(json_array_elements(attributes_json)::jsonb)::json);

  RETURN cluster_id;
END
$$ LANGUAGE plpgsql;


--Cluster Attributes
CREATE OR REPLACE FUNCTION apiato_ro.insert_cluster_attribute(id int, in_json JSON) RETURNS INTEGER AS $$
DECLARE
  attribute_id    int;
  cluster_id      int;
  attributes_json json;
  attr_name       varchar;
  attr_value      varchar;

BEGIN

  --Get the new cluster_id to be used in the insertion
  SELECT nextval(pg_get_serial_sequence('apiato.cluster_attribute', 'attribute_id')) INTO attribute_id;
  attributes_json := in_json::jsonb || ('{ "attribute_id" :' || attribute_id || '}')::jsonb;

  --Tranform key value to table format
  SELECT json_object_keys(in_json) INTO attr_name;
  SELECT in_json->>attr_name INTO attr_value;
  attributes_json := attributes_json::jsonb ||  ('{ "name" : "' || attr_name || '"}')::jsonb || ('{ "value" : "' || attr_value || '"}')::jsonb || ('{ "cluster_id" :' || id || '}')::jsonb;

  --Get the new cluster_id to be used in the insertion
   SELECT nextval(pg_get_serial_sequence('apiato.cluster_attribute', 'attribute_id')) INTO attribute_id;
   attributes_json := attributes_json::jsonb || ('{ "attribute_id" :' || attribute_id || '}')::jsonb;


   INSERT INTO apiato.cluster_attribute SELECT * FROM json_populate_record(null::apiato.cluster_attribute,attributes_json);

  RETURN attribute_id;
END
$$ LANGUAGE plpgsql;

--Instance Attributes
CREATE OR REPLACE FUNCTION apiato_ro.insert_instance_attributes(in_json JSON) RETURNS INTEGER AS $$
DECLARE
  attribute_id    int;
  instance_id      int;
  attributes_json json;
BEGIN

   --Get the new cluster_id to be used in the insertion
   SELECT nextval(pg_get_serial_sequence('apiato.instance_attribute', 'attribute_id')) INTO attribute_id;
   attributes_json := in_json::jsonb || ('{ "attribute_id" :' || attribute_id || '}')::jsonb;

   INSERT INTO apiato.instance_attribute SELECT * FROM json_populate_record(null::apiato.instance_attribute,attributes_json);

  RETURN attribute_id;
END
$$ LANGUAGE plpgsql;

--Functional Alias
CREATE OR REPLACE FUNCTION apiato_ro.insert_functional_alias(in_json JSON) RETURNS bool AS $$
DECLARE
   success     bool;
  in_dns_name  VARCHAR ;
BEGIN

    SELECT apiato_ro.functional_alias.dns_name INTO in_dns_name
     FROM apiato_ro.functional_alias
    WHERE apiato_ro.functional_alias.name IS NULL
      AND apiato_ro.functional_alias.alias IS NULL
  ORDER BY apiato_ro.functional_alias.dns_name ASC LIMIT 1;

    UPDATE apiato.functional_alias
      SET instance_id=(in_json->>'instance_id')::int, alias = in_json->>'alias'
    WHERE apiato.functional_alias.dns_name = in_dns_name
      AND (in_json->>'instance_id')::int NOT IN (SELECT a.instance_id FROM apiato.functional_alias a WHERE a.instance_id IS NOT NULL)
      RETURNING TRUE INTO success;

    RETURN success;
END
$$ LANGUAGE plpgsql;



--Volume
CREATE OR REPLACE FUNCTION apiato_ro.insert_volume(in_json JSON) RETURNS INTEGER AS $$
DECLARE
  volume_id       int;
  volume_json     json;
  attributes_json json;
BEGIN
  --Get the new volume_id to be used in the insertion
   SELECT nextval(pg_get_serial_sequence('apiato.volume', 'volume_id')) INTO volume_id;
   volume_json := in_json::jsonb || ('{ "volume_id" :' || volume_id || '}')::jsonb;

   INSERT INTO apiato.volume SELECT * FROM json_populate_record(null::apiato.volume, volume_json);

   --Inserting Attributes
   attributes_json := volume_json::json->'attributes';
   PERFORM apiato_ro.insert_volume_attribute(volume_id,(json_array_elements(attributes_json)::jsonb)::json);

  RETURN volume_id;
END
$$ LANGUAGE plpgsql;

--Instance Attributes
CREATE OR REPLACE FUNCTION apiato_ro.insert_volume_attribute(id int, in_json JSON) RETURNS INTEGER AS $$
DECLARE
  attribute_id    int;
  attributes_json json;
  attr_name       varchar;
  attr_value      varchar;

BEGIN

  --Get the new cluster_id to be used in the insertion
  SELECT nextval(pg_get_serial_sequence('apiato.volume_attribute', 'attribute_id')) INTO attribute_id;
  attributes_json := in_json::jsonb || ('{ "attribute_id" :' || attribute_id || '}')::jsonb;

  --Tranform key value to table format
  SELECT json_object_keys(in_json) INTO attr_name;
  SELECT in_json->>attr_name INTO attr_value;
  attributes_json := attributes_json::jsonb ||  ('{ "name" : "' || attr_name || '"}')::jsonb || ('{ "value" : "' || attr_value || '"}')::jsonb || ('{ "volume_id" :' || id || '}')::jsonb;


  INSERT INTO apiato.volume_attribute SELECT * FROM json_populate_record(null::apiato.volume_attribute,attributes_json);

  RETURN attribute_id;
END
$$ LANGUAGE plpgsql;


--Instance
CREATE OR REPLACE FUNCTION apiato_ro.insert_instance(in_json JSON) RETURNS INTEGER AS $$
DECLARE
  instance_id     int;
  instance_json   json;
  volumes_json    json;
  attributes_json json;
BEGIN
  --Get the new instance_id to be used in the insertion
   SELECT nextval(pg_get_serial_sequence('apiato.instance', 'instance_id')) INTO instance_id;
   instance_json := in_json::jsonb || ('{ "instance_id" :' || instance_id || '}')::jsonb;

   INSERT INTO apiato.instance SELECT * FROM json_populate_record(null::apiato.instance, instance_json);

   --Inserting Attributes
   attributes_json := instance_json::json->'attributes';
   PERFORM apiato_ro.insert_instance_attributes((json_array_elements(attributes_json)::jsonb)::json);

   --Inserting Volumes
   volumes_json := instance_json::json->'volumes';
   PERFORM apiato_ro.insert_volume((json_array_elements(volumes_json)::jsonb || ('{ "instance_id" :' || instance_id || '}')::jsonb)::json);

  RETURN instance_id;
END
$$ LANGUAGE plpgsql;

--Instance Attributes
CREATE OR REPLACE FUNCTION apiato_ro.insert_instance_attribute(id int, in_json JSON) RETURNS INTEGER AS $$
DECLARE
  attribute_id    int;
  attributes_json json;
  attr_name       varchar;
  attr_value      varchar;

BEGIN

  --Get the new cluster_id to be used in the insertion
  SELECT nextval(pg_get_serial_sequence('apiato.instance_attribute', 'attribute_id')) INTO attribute_id;
  attributes_json := in_json::jsonb || ('{ "attribute_id" :' || attribute_id || '}')::jsonb;

  --Tranform key value to table format
  SELECT json_object_keys(in_json) INTO attr_name;
  SELECT in_json->>attr_name INTO attr_value;
  attributes_json := attributes_json::jsonb ||  ('{ "name" : "' || attr_name || '"}')::jsonb || ('{ "value" : "' || attr_value || '"}')::jsonb || ('{ "instance_id" :' || id || '}')::jsonb;


  INSERT INTO apiato.instance_attribute SELECT * FROM json_populate_record(null::apiato.isntance_attribute,attributes_json);

  RETURN attribute_id;
END
$$ LANGUAGE plpgsql;


--Cluster Attributes
CREATE OR REPLACE FUNCTION apiato_ro.insert_host(in_json JSON) RETURNS INTEGER AS $$
DECLARE
  host_id    int;
  host_json  json;
BEGIN

   --Get the new cluster_id to be used in the insertion
   SELECT nextval(pg_get_serial_sequence('apiato.host', 'host_id')) INTO host_id;
   host_json := in_json::jsonb || ('{ "host_id" :' || host_id || '}')::jsonb;

   INSERT INTO apiato.host SELECT * FROM json_populate_record(null::apiato.host,host_json);

  RETURN host_id;
END
$$ LANGUAGE plpgsql;

-----------------------------------
--DELETE PROCEDURES
-----------------------------------
--Clusters
CREATE OR REPLACE FUNCTION apiato_ro.delete_cluster(id INT) RETURNS bool AS $$
DECLARE
 success bool;
BEGIN

   DELETE FROM apiato.cluster WHERE cluster_id = id RETURNING TRUE INTO success;

RETURN success;
END
$$ LANGUAGE plpgsql;

--Hosts
CREATE OR REPLACE FUNCTION apiato_ro.delete_host(id INT) RETURNS bool AS $$
DECLARE
 success bool;
BEGIN

   DELETE FROM apiato.host WHERE host_id = id RETURNING TRUE INTO success;

RETURN success;
END
$$ LANGUAGE plpgsql;


--Functional alias
CREATE OR REPLACE FUNCTION apiato_ro.delete_functional_alias(id INT) RETURNS bool AS $$
DECLARE
 success bool;
BEGIN

   UPDATE apiato.functional_alias SET instance_id = NULL, alias=NULL WHERE functional_alias_id = id RETURNING TRUE INTO success;

RETURN success;
END
$$ LANGUAGE plpgsql;


--Instance
CREATE OR REPLACE FUNCTION apiato_ro.delete_instance(id int) RETURNS bool AS $$
DECLARE
 success bool;
BEGIN

   EXECUTE format(' DELETE FROM apiato.instance WHERE instance_id = $1 RETURNING TRUE') USING id INTO success;

RETURN success;
END
$$ LANGUAGE plpgsql;


--Volume
CREATE OR REPLACE FUNCTION apiato_ro.delete_volume(id int) RETURNS bool AS $$
DECLARE
 success bool;
BEGIN

   EXECUTE format(' DELETE FROM apiato.volume WHERE volume_id = $1 RETURNING TRUE') USING id INTO success;

RETURN success;
END
$$ LANGUAGE plpgsql;

--cluster attribute
CREATE OR REPLACE FUNCTION apiato_ro.delete_cluster_attribute(cluster_id int, attribute_name varchar) RETURNS bool AS $$
DECLARE
  success bool;
BEGIN

  EXECUTE format(' DELETE FROM apiato.cluster_attribute WHERE cluster_id = $1 AND name=$2 RETURNING TRUE') USING cluster_id, attribute_name INTO success;

  RETURN success;
END
$$ LANGUAGE plpgsql;


--cluster attribute
CREATE OR REPLACE FUNCTION apiato_ro.delete_instance_attribute(instance_id int, attribute_name varchar) RETURNS bool AS $$
DECLARE
  success bool;
BEGIN

  EXECUTE format(' DELETE FROM apiato.instance_attribute WHERE instance_id = $1 AND name=$2 RETURNING TRUE') USING instance_id, attribute_name INTO success;

  RETURN success;
END
$$ LANGUAGE plpgsql;


--cluster attribute
CREATE OR REPLACE FUNCTION apiato_ro.delete_volume_attribute(volume_id int, attribute_name varchar) RETURNS bool AS $$
DECLARE
  success bool;
BEGIN

  EXECUTE format(' DELETE FROM apiato.volume_attribute WHERE volume_id = $1 AND name=$2 RETURNING TRUE') USING volume_id, attribute_name INTO success;

  RETURN success;
END
$$ LANGUAGE plpgsql;

-----------------------------------
--UPDATE PROCEDURES
-----------------------------------
--Clusters
CREATE OR REPLACE FUNCTION apiato_ro.update_cluster(id INT, in_json JSON) RETURNS bool AS $$
DECLARE
 success bool;
BEGIN

   UPDATE apiato.cluster
    SET owner             = (CASE WHEN src.in_json::jsonb ? 'owner' THEN src.owner ELSE apiato.cluster.owner END),
        name              = (CASE WHEN src.in_json::jsonb ? 'name' THEN src.name ELSE apiato.cluster.name END),
        e_group           = (CASE WHEN src.in_json::jsonb ? 'e_group' THEN src.e_group ELSE apiato.cluster.e_group END),
        category          = (CASE WHEN src.in_json::jsonb ? 'category' THEN src.category ELSE apiato.cluster.category END),
        creation_date     = (CASE WHEN src.in_json::jsonb ? 'creation_date' THEN src.creation_date ELSE apiato.cluster.creation_date END),
        expiry_date       = (CASE WHEN src.in_json::jsonb ? 'expiry_date' THEN src.expiry_date ELSE apiato.cluster.expiry_date END),
        instance_type_id  = (CASE WHEN src.in_json::jsonb ? 'instance_type_id' THEN src.instance_type_id ELSE apiato.cluster.instance_type_id END),
        project           = (CASE WHEN src.in_json::jsonb ? 'project' THEN src.project ELSE apiato.cluster.project END),
        description       = (CASE WHEN src.in_json::jsonb ? 'description' THEN src.description ELSE apiato.cluster.description END),
        version           = (CASE WHEN src.in_json::jsonb ? 'version' THEN src.version ELSE apiato.cluster.version END),
        master_cluster_id = (CASE WHEN src.in_json::jsonb ? 'master_cluster_id' THEN src.master_cluster_id ELSE apiato.cluster.master_cluster_id END),
        state             = (CASE WHEN src.in_json::jsonb ? 'state' THEN src.state ELSE apiato.cluster.state END),
        status            = (CASE WHEN src.in_json::jsonb ? 'status' THEN src.status ELSE apiato.cluster.status END)
     FROM (SELECT * FROM json_populate_record(null::apiato.cluster,in_json)
           CROSS JOIN (SELECT in_json) AS source_json) src
    WHERE apiato.cluster.cluster_id = id;

RETURN success;
END
$$ LANGUAGE plpgsql;


--Functional Alias
CREATE OR REPLACE FUNCTION apiato_ro.update_functional_alias(in_json JSON) RETURNS bool AS $$
DECLARE
 success bool;
BEGIN

   UPDATE apiato.functional_alias
    SET name   = (CASE WHEN src.in_json::jsonb ? 'instance_id' THEN src.instance_id ELSE apiato.functional_alias.instance_id END),
        memory = (CASE WHEN src.in_json::jsonb ? 'alias' THEN src.alias ELSE apiato.functional_alias.alias END)
     FROM (SELECT * FROM json_populate_record(null::apiato.functional_alias,in_json)
           CROSS JOIN (SELECT in_json) AS source_json) src
    WHERE apiato.functional_alias.functional_alias_id = src.functional_alias_id;

RETURN TRUE;
END
$$ LANGUAGE plpgsql;


--Instance
CREATE OR REPLACE FUNCTION apiato_ro.update_instance(in_json JSON) RETURNS bool AS $$
DECLARE
 success bool;
BEGIN

   UPDATE apiato.instance
    SET owner              = (CASE WHEN src.in_json::jsonb ? 'owner' THEN src.owner ELSE apiato.instance.owner END),
        name               = (CASE WHEN src.in_json::jsonb ? 'name' THEN src.name ELSE apiato.instance.name END),
        e_group            = (CASE WHEN src.in_json::jsonb ? 'e_group' THEN src.e_group ELSE apiato.instance.e_group END),
        category           = (CASE WHEN src.in_json::jsonb ? 'category' THEN src.category ELSE apiato.instance.category END),
        creation_date      = (CASE WHEN src.in_json::jsonb ? 'creation_date' THEN src.creation_date ELSE apiato.instance.creation_date END),
        expiry_date        = (CASE WHEN src.in_json::jsonb ? 'expiry_date' THEN src.expiry_date ELSE apiato.instance.expiry_date END),
        instance_type_id   = (CASE WHEN src.in_json::jsonb ? 'instance_type_id' THEN src.instance_type_id ELSE apiato.instance.instance_type_id END),
        project            = (CASE WHEN src.in_json::jsonb ? 'project' THEN src.project ELSE apiato.instance.project END),
        description        = (CASE WHEN src.in_json::jsonb ? 'description' THEN src.description ELSE apiato.instance.description END),
        version            = (CASE WHEN src.in_json::jsonb ? 'version' THEN src.version ELSE apiato.instance.version END),
        master_instance_id = (CASE WHEN src.in_json::jsonb ? 'master_instance_id' THEN src.master_instance_id ELSE apiato.instance.master_instance_id END),
        slave_instance_id  = (CASE WHEN src.in_json::jsonb ? 'slave_instance_id' THEN src.slave_instance_id ELSE apiato.instance.slave_instance_id END),
        host_id            = (CASE WHEN src.in_json::jsonb ? 'host_id' THEN src.host_id ELSE apiato.instance.host_id END),
        state              = (CASE WHEN src.in_json::jsonb ? 'state' THEN src.state ELSE apiato.instance.state END),
        status             = (CASE WHEN src.in_json::jsonb ? 'status' THEN src.status ELSE apiato.instance.status END),
        cluster_id         = (CASE WHEN src.in_json::jsonb ? 'cluster_id' THEN src.cluster_id ELSE apiato.instance.cluster_id END)
     FROM (SELECT * FROM json_populate_record(null::apiato.instance,in_json)
           CROSS JOIN (SELECT in_json) AS source_json) src
    WHERE apiato.instance.instance_id = src.instance_id;

RETURN success;
END
$$ LANGUAGE plpgsql;


--Cluster attribute
CREATE OR REPLACE FUNCTION apiato_ro.update_cluster_attribute(id int, in_json JSON) RETURNS bool AS $$
DECLARE
  success bool;
  attr_name varchar;
  attr_value varchar;
BEGIN
  SELECT json_object_keys(in_json) INTO attr_name;
  SELECT in_json->>attr_name INTO attr_value;
   UPDATE apiato.cluster_attribute
    SET value = attr_value
    WHERE apiato.cluster_attribute.cluster_id = id AND apiato.cluster_attribute.name = attr_name;

RETURN TRUE;
END
$$ LANGUAGE plpgsql;



--instance attribute
CREATE OR REPLACE FUNCTION apiato_ro.update_instance_attribute(id int, in_json JSON) RETURNS bool AS $$
DECLARE
  success bool;
  attr_name varchar;
  attr_value varchar;
BEGIN
  SELECT json_object_keys(in_json) INTO attr_name;
  SELECT in_json->>attr_name INTO attr_value;
  UPDATE apiato.instance_attribute
  SET value = attr_value
  WHERE apiato.isntance_attribute.instance_id = id AND apiato.instance_attribute.name = attr_name;

  RETURN TRUE;
END
$$ LANGUAGE plpgsql;


--Volume attribute
CREATE OR REPLACE FUNCTION apiato_ro.update_volume_attribute(id int, in_json JSON) RETURNS bool AS $$
DECLARE
  success bool;
  attr_name varchar;
  attr_value varchar;
BEGIN
  SELECT json_object_keys(in_json) INTO attr_name;
  SELECT in_json->>attr_name INTO attr_value;
  UPDATE apiato.instance_attribute
  SET value = attr_value
  WHERE apiato.volume_attribute.volume_id = id AND apiato.volume_attribute.name = attr_name;

  RETURN TRUE;
END
$$ LANGUAGE plpgsql;

--Hosts
CREATE OR REPLACE FUNCTION apiato_ro.update_host(id INT, in_json JSON) RETURNS bool AS $$
DECLARE
 success bool;
BEGIN

  UPDATE apiato.host
    SET name   = (CASE WHEN src.in_json::jsonb ? 'name' THEN src.name ELSE apiato.host.name END),
        memory = (CASE WHEN src.in_json::jsonb ? 'memory' THEN src.memory ELSE apiato.host.memory END)
     FROM (SELECT * FROM json_populate_record(null::apiato.host,in_json)
           CROSS JOIN (SELECT in_json) AS source_json) src
    WHERE apiato.host.host_id = id;

RETURN TRUE;
END
$$ LANGUAGE plpgsql;

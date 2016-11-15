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
        WHERE instance_id = vol_id) t) j INTO attributes;
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
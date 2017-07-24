--- TABLES
-- CLUSTER
CREATE TABLE public.cluster (
  id           serial,
  owner                varchar(32) NOT NULL,
  name                 varchar(128) UNIQUE NOT NULL,
  e_group              varchar(256),
  category             public.instance_category NOT NULL,
  creation_date        date NOT NULL,
  expiry_date          date,
  type_id              int NOT NULL,
  project              varchar(128),
  description          varchar(1024),
  version              varchar(128),
  master_id            int,
  state                public.instance_state NOT NULL,
  status               public.instance_status NOT NULL,
  CONSTRAINT cluster_pkey               PRIMARY KEY (id),
  CONSTRAINT cluster_master_fk          FOREIGN KEY (master_id) REFERENCES public.cluster (id),
  CONSTRAINT cluster_instance_type_fk   FOREIGN KEY (type_id)   REFERENCES public.instance_type (id)
);
--FK INDEXES for CLUSTER table
CREATE INDEX cluster_master_idx ON public.cluster (master_id);
CREATE INDEX cluster_type_idx   ON public.cluster (type_id);

-- CLUSTER_ATTRIBUTES
CREATE TABLE public.cluster_attribute (
  id serial,
  cluster_id   integer NOT NULL,
  name         varchar(32) NOT NULL,
  value        varchar(250) NOT NULL,
  CONSTRAINT cluster_attribute_pkey        PRIMARY KEY (id),
  CONSTRAINT cluster_attribute_cluster_fk FOREIGN KEY (cluster_id) REFERENCES public.cluster (id) ON DELETE CASCADE,
  UNIQUE (cluster_id, name)
);
CREATE INDEX cluster_attribute_cluster_idx ON public.cluster_attribute (cluster_id);

--- PROCEDURES
-- Get instance attribute function
CREATE OR REPLACE FUNCTION api.get_cluster_attribute(attr_name VARCHAR, clus_id INTEGER)
  RETURNS VARCHAR AS $$
DECLARE
  res VARCHAR;
BEGIN
  SELECT value FROM public.cluster_attribute A WHERE A.id = clus_id AND A.name = attr_name INTO res;
  return res;
END
$$ LANGUAGE plpgsql;

-- Get attributes function
CREATE OR REPLACE FUNCTION api.get_cluster_attributes(clus_id INTEGER)
  RETURNS JSON AS $$
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

-- Get cluster instances
CREATE OR REPLACE FUNCTION api.get_cluster_instances(clus_id INTEGER)
RETURNS JSON[] AS $$
DECLARE
  instances JSON[];
BEGIN
  SELECT ARRAY (SELECT row_to_json(t) FROM (SELECT * FROM api.metadata WHERE cluster_id = clus_id) t) INTO instances;
  return instances;
END
$$ LANGUAGE plpgsql;

--- VIEWS
CREATE OR REPLACE VIEW api.cluster_attributes AS
SELECT
      public.cluster.id,
      api.get_cluster_attributes(public.cluster.id) as attributes
FROM public.cluster;

CREATE OR REPLACE VIEW api.cluster AS
  SELECT
    cluster.id AS id,
    cluster.owner AS username,
    cluster.name AS name,
    cluster.e_group,
    cluster.project,
    cluster.description,
    cluster.category "class",
    instance_type.type AS type,
    cluster.version,
    cluster_master.name AS master_name,
    api.get_cluster_instances(public.cluster.id) as instances,
    api.get_cluster_attributes(public.cluster.id) as attributes,
    api.get_cluster_attribute('port', public.cluster.id ) port
  FROM public.cluster
    JOIN public.instance_type ON public.cluster.type_id = public.instance_type.id
    LEFT JOIN public.cluster AS cluster_master ON public.cluster.id = cluster_master.master_id,
    api.get_cluster_instances(public.cluster.id);

--- Insert Procedures
--Clusters
CREATE OR REPLACE FUNCTION api.insert_cluster(in_json JSON) RETURNS INTEGER AS $$
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


--Cluster Attributes
CREATE OR REPLACE FUNCTION api.insert_cluster_attribute(id int, in_json JSON) RETURNS INTEGER AS $$
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

-----------------------------------
--UPDATE PROCEDURES
-----------------------------------
--Clusters
CREATE OR REPLACE FUNCTION api.update_cluster(cid INT, in_json JSON) RETURNS bool AS $$
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

--Cluster attribute
CREATE OR REPLACE FUNCTION api.update_cluster_attribute(id int, in_json JSON) RETURNS bool AS $$
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

--- DELETE 
--Clusters
CREATE OR REPLACE FUNCTION api.delete_cluster(cid INT) RETURNS bool AS $$
DECLARE
 success bool;
BEGIN

   DELETE FROM public.cluster WHERE public.cluster.id = cid RETURNING TRUE INTO success;

RETURN success;
END
$$ LANGUAGE plpgsql;

--cluster attribute
CREATE OR REPLACE FUNCTION api.delete_cluster_attribute(cluster_id int, attribute_name varchar) RETURNS bool AS $$
DECLARE
  success bool;
BEGIN

  EXECUTE format(' DELETE FROM public.cluster_attribute WHERE cluster_id = $1 AND name=$2 RETURNING TRUE') 
    USING cluster_id, attribute_name INTO success;

  RETURN success;
END
$$ LANGUAGE plpgsql;


--- DATA


INSERT INTO public.cluster (owner, name, e_group, category, creation_date, expiry_date, type_id, project, description, version, master_id, state, status)
VALUES ('user05','cluster01','testgroupZ','DEV',now(),NULL,1,'NILE','Test zookeeper cluster 1', '3.4.9',NULL,'RUNNING','ACTIVE');

-- Insert test data for cluster attributes
INSERT INTO public.cluster_attribute (cluster_id, name, value)
    VALUES (1, 'service','zookeeper'),
           (1, 'user'   ,'zookeeper');

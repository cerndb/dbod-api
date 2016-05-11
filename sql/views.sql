
-- Drop view and function to be able to insert it again
DROP VIEW api.test_metadata;
DROP FUNCTION get_hosts(INTEGER[]);
DROP FUNCTION get_volumes(INTEGER);

-- Get hosts function
CREATE OR REPLACE FUNCTION get_hosts(host_ids INTEGER[])
RETURNS VARCHAR[] AS $$
DECLARE
  hosts VARCHAR := '';
BEGIN
  SELECT ARRAY (SELECT name FROM host WHERE id = ANY(host_ids)) INTO hosts;
  RETURN hosts;
END
$$ LANGUAGE plpgsql;

-- Get volumes function
CREATE OR REPLACE FUNCTION get_volumes(pid INTEGER)
RETURNS JSON[] AS $$
DECLARE
  volumes JSON[];
BEGIN
  SELECT ARRAY (SELECT row_to_json(t) FROM (SELECT * FROM VOLUME WHERE instance_id = pid) t) INTO volumes;
  return volumes;
END
$$ LANGUAGE plpgsql;


-- DOD_INSTANCES View
CREATE VIEW DOD_INSTANCES AS
SELECT USERNAME, DB_NAME, E_GROUP, CATEGORY, CREATION_DATE, EXPIRY_DATE, DB_TYPE, 0 DB_SIZE, 0 NO_CONNECTIONS, PROJECT, DESCRIPTION, VERSION, MASTER, SLAVE, HOST, STATE, STATUS
FROM fo_instance;

-- TEST_METADATA View
CREATE VIEW api.test_metadata AS
SELECT id, owner, name, category, type, version, get_hosts(host) hosts, get_volumes volumes
FROM instance, get_volumes(id);


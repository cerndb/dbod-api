
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

-- Get directories function
CREATE OR REPLACE FUNCTION get_directories(inst_name VARCHAR, type VARCHAR, version VARCHAR, port VARCHAR)
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
      ('/usr/local/mysql/mysql-' || version || '/bin')::VARCHAR bindir, 
      ('/ORA/dbs03/' || upper(inst_name) || '/data')::VARCHAR datadir, 
      ('/ORA/dbs02/' || upper(inst_name) || '/pg_xlog')::VARCHAR logdir, 
      ('/var/lib/pgsql/')::VARCHAR socket;
  END IF;
END
$$ LANGUAGE plpgsql;


-- DOD_INSTANCES View
CREATE VIEW DOD_INSTANCES AS
SELECT USERNAME, DB_NAME, E_GROUP, CATEGORY, CREATION_DATE, EXPIRY_DATE, DB_TYPE, 0 DB_SIZE, 0 NO_CONNECTIONS, PROJECT, DESCRIPTION, VERSION, MASTER, SLAVE, HOST, STATE, STATUS
FROM fo_instance;

-- TEST_METADATA View
CREATE OR REPLACE VIEW api.test_metadata AS
SELECT id, username, db_name, category, db_type, version, host, get_volumes volumes, 
'/usr/local/mysql/mysql-' || version basedir,
'/ORA/dbs03/' || db_name || '/mysql' datadir,
'/ORA/dbs02/' || db_name || '/mysql' logdir
FROM fo_instance, get_volumes(id);

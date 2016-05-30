
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
  SELECT ARRAY (SELECT row_to_json(t) FROM (SELECT * FROM public.volume WHERE instance_id = pid) t) INTO volumes;
  return volumes;
END
$$ LANGUAGE plpgsql;

-- Get port function
CREATE OR REPLACE FUNCTION get_attribute(name VARCHAR, instance_id INTEGER)
RETURNS VARCHAR AS $$
DECLARE
  res VARCHAR;
BEGIN
  SELECT value FROM public.attribute A WHERE A.instance_id = instance_id AND A.name = name INTO res;
  return res;
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


-- TEST_METADATA View
CREATE OR REPLACE VIEW api.test_metadata AS
SELECT id, username, db_name, category, db_type, version, host, get_volumes volumes, d.*
FROM fo_instance, get_volumes(id), get_directories(db_name, db_type, version, '5500') d;

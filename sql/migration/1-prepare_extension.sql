
-- DESTROY EVERYTHING
DROP SCHEMA public CASCADE;
DROP SCHEMA fim CASCADE;
DROP SCHEMA source CASCADE;
----------------------------

CREATE SCHEMA IF NOT EXISTS public;

CREATE EXTENSION postgres_fdw;

CREATE SERVER <pg_source> FOREIGN DATA WRAPPER postgres_fdw 
    OPTIONS (host '<pg_source>', dbname 'dbod', port '3000');
GRANT USAGE ON FOREIGN SERVER <pg_source> TO admin;

CREATE USER MAPPING FOR admin SERVER <pg_source>
    OPTIONS (user 'admin', password 'admin');
    
CREATE EXTENSION oracle_fdw;

CREATE SERVER <oracle_source> FOREIGN DATA WRAPPER oracle_fdw
    OPTIONS (dbserver '<oracle_source>');
GRANT USAGE ON FOREIGN SERVER <oracle_source> TO admin;

CREATE USER MAPPING FOR admin SERVER <oracle_source>
    OPTIONS (user 'admin', password 'admin');
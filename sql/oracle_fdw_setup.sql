-- Run as administrator
CREATE EXTENSION oracle_fdw;

CREATE SERVER <server_name> FOREIGN DATA WRAPPER oracle_fdw
    OPTIONS (dbserver '<server_name>');
GRANT USAGE ON FOREIGN SERVER <server_name> TO <dbuser>;

CREATE USER MAPPING FOR <dbuser> SERVER <server_name>
    OPTIONS (user '<oracle_username>', password '<oracle_password>');
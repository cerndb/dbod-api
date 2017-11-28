-- Copyright (C) 2017, CERN
-- This software is distributed under the terms of the GNU General Public
-- Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".
-- In applying this license, CERN does not waive the privileges and immunities
-- granted to it by virtue of its status as Intergovernmental Organization
-- or submit itself to any jurisdiction.

-- This script MUST be run as ADMINISTRATOR

-- Destroy schemas from previous migration (if any)
DROP SCHEMA fim CASCADE;
DROP SCHEMA source CASCADE;
----------------------------

CREATE EXTENSION postgres_fdw;

CREATE SERVER <pg_source> FOREIGN DATA WRAPPER postgres_fdw 
    OPTIONS (host '<pg_source>', dbname 'apiato', port '3000');
GRANT USAGE ON FOREIGN SERVER <pg_source> TO admin;

CREATE USER MAPPING FOR admin SERVER <pg_source>
    OPTIONS (user 'admin', password 'admin');
    
CREATE EXTENSION oracle_fdw;

CREATE SERVER <oracle_source> FOREIGN DATA WRAPPER oracle_fdw
    OPTIONS (dbserver '<oracle_source>');
GRANT USAGE ON FOREIGN SERVER <oracle_source> TO admin;

CREATE USER MAPPING FOR admin SERVER <oracle_source>
    OPTIONS (user 'admin', password 'admin');
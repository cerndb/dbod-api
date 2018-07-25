-- Copyright (C) 2017, CERN
-- This software is distributed under the terms of the GNU General Public
-- Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".
-- In applying this license, CERN does not waive the privileges and immunities
-- granted to it by virtue of its status as Intergovernmental Organization
-- or submit itself to any jurisdiction.

-- This optional view connects the FIM Table from Oracle to the current schema.
DROP TABLE IF EXISTS public.fim_data;
DROP VIEW IF EXISTS api.fim_data;

CREATE VIEW public.fim_data AS 
  SELECT * FROM fim.db_on_demand;
    
CREATE VIEW api.fim_data AS 
  SELECT * FROM fim.db_on_demand;


-- This optional view connects the JOBS Table from Oracle to the current schema.
DROP TABLE IF EXISTS public.job_log;
DROP VIEW IF EXISTS api.job_log;

CREATE VIEW public.job_log AS 
  SELECT id, log
  FROM source.dod_jobs;
    
CREATE VIEW api.job_log AS 
  SELECT id, log
  FROM source.dod_jobs;
  
-- This optional view connects the JOBS Table from Oracle to the current schema.
DROP TABLE IF EXISTS public.rundeck;
DROP VIEW IF EXISTS api.rundeck;

CREATE VIEW public.rundeck AS
  SELECT id, date_started, date_completed, execution_type, project, status
  FROM fim.rundeck_execution;
  
CREATE VIEW api.rundeck AS
  SELECT id, date_started, date_completed, execution_type, project, status
  FROM fim.rundeck_execution;
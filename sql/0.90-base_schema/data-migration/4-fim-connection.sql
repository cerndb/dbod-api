-- Copyright (C) 2017, CERN
-- This software is distributed under the terms of the GNU General Public
-- Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".
-- In applying this license, CERN does not waive the privileges and immunities
-- granted to it by virtue of its status as Intergovernmental Organization
-- or submit itself to any jurisdiction.

-- This optional file connects the FIM Table from Oracle to the current schema.

DROP TABLE public.fim_data;

CREATE VIEW public.fim_data AS 
    SELECT * FROM fim.db_on_demand;
    
CREATE VIEW api.fim_data AS 
    SELECT * FROM fim.db_on_demand;



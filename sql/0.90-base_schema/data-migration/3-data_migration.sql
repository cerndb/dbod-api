-- Copyright (C) 2017, CERN
-- This software is distributed under the terms of the GNU General Public
-- Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".
-- In applying this license, CERN does not waive the privileges and immunities
-- granted to it by virtue of its status as Intergovernmental Organization
-- or submit itself to any jurisdiction.

TRUNCATE TABLE public.command_definition CASCADE;
TRUNCATE TABLE public.command_param CASCADE;
TRUNCATE TABLE public.host CASCADE;
TRUNCATE TABLE public.instance CASCADE;
TRUNCATE TABLE public.instance_attribute CASCADE;
TRUNCATE TABLE public.functional_aliases CASCADE;
TRUNCATE TABLE public.volume CASCADE;
TRUNCATE TABLE public.upgrade CASCADE;
TRUNCATE TABLE public.job CASCADE;
TRUNCATE TABLE public.instance_change CASCADE;

-- Insert hosts
INSERT INTO public.host (name, memory)
SELECT DISTINCT(host), 0
FROM source.dod_instances;

-- Migrate instances
INSERT INTO public.instance (id, owner, name, egroup, category, creation_date, expiry_date, type_id, size, project, description, version, master_id, slave_id, host_id, state, status, cluster_id)
SELECT dod_instance.id, username, db_name, e_group, category::instance_category, creation_date, 
       expiry_date, t.id type_id, db_size, project, dod_instance.description, version, NULL, NULL, 
       host.id host_id, 
       state::instance_state, 
       CASE WHEN dod_instance.status='1' THEN 'ACTIVE'::instance_status
            ELSE 'NON_ACTIVE'::instance_status
       END status, NULL
FROM source.dod_instances dod_instance
INNER JOIN public.host host ON dod_instance.host = host.name
INNER JOIN public.instance_type t ON dod_instance.db_type = t.type;

-- Add master_id to slave instances
UPDATE public.instance
SET master_id=query.id
FROM (SELECT d.id, d.db_name
      FROM source.dod_instances s, source.dod_instances d
      WHERE s.master = d.db_name) AS query, source.dod_instances
WHERE public.instance.id = source.dod_instances.id AND query.db_name = source.dod_instances.master;

-- Add slave_id to master instances
UPDATE public.instance
SET slave_id=query.id
FROM (SELECT d.id, d.db_name
      FROM source.dod_instances s, source.dod_instances d
      WHERE s.slave = d.db_name) AS query, source.dod_instances
WHERE public.instance.id = source.dod_instances.id AND query.db_name = source.dod_instances.slave;

-- Migrate instance attributes (workaround using GROUP BY because there are duplicates)
INSERT INTO public.instance_attribute(id, instance_id, name, value)
SELECT min(id), instance_id, name, max(value)
FROM source.attribute s
WHERE s.instance_id IN (SELECT id FROM public.instance)
GROUP BY instance_id, name;

-- Migrate instance changes
INSERT INTO public.instance_change (instance_id, attribute, change_date, requester, old_value, new_value)
SELECT instance.id instance_id, attribute, change_date, requester, old_value, new_value
FROM source.dod_instance_changes changes
INNER JOIN public.instance instance ON instance.name = changes.db_name;

-- Migrate functional aliases
INSERT INTO public.functional_aliases (dns_name, db_name, alias)
SELECT dns_name, db_name, alias
FROM source.functional_aliases;

-- Migrate volumes
INSERT INTO public.volume (id, instance_id, file_mode, owner, "group", server, mount_options, mounting_path, type_id)
SELECT id, instance_id, file_mode, owner, "group", server, mount_options, mounting_path, 1
FROM source.volume v
WHERE v.instance_id IN (SELECT id FROM public.instance);

-- Migrate upgrades
INSERT INTO public.upgrade (db_type, category, version_from, version_to)
SELECT db_type, category, version_from, version_to
FROM source.dod_upgrades;

-- Migrate command definitions
INSERT INTO public.command_definition (command_name, type, exec)
SELECT command_name, type, exec
FROM source.dod_command_definition;

-- Migrate jobs
INSERT INTO public.job (id, instance_id, command_name, creation_date, completion_date, requester, admin_action, state, email_sent)
SELECT j.id, i.id, j.command_name, j.creation_date, j.completion_date, j.requester, j.admin_action, j.state, j.email_sent
FROM source.dod_jobs j, source.dod_instances i
WHERE j.db_name = i.db_name;

-- Migrate command params
INSERT INTO public.command_param (job_id, name, value)
SELECT job.id, name, value
FROM source.dod_command_params param
INNER JOIN source.dod_jobs job ON param.username = job.username AND param.db_name = job.db_name AND param.command_name = job.command_name AND param.type = job.type AND param.creation_date = job.creation_date;

-- Make sure all the sequences are properly set, as manual inserts were done
SELECT setval('instance_id_seq', (SELECT MAX(id) from public.instance));
SELECT setval('instance_attribute_id_seq', (SELECT MAX(id) from public.instance_attribute));
SELECT setval('volume_id_seq', (SELECT MAX(id) from public.volume));
-- Copyright (C) 2017, CERN
-- This software is distributed under the terms of the GNU General Public
-- Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".
-- In applying this license, CERN does not waive the privileges and immunities
-- granted to it by virtue of its status as Intergovernmental Organization
-- or submit itself to any jurisdiction.


-- Migrate command definitions
INSERT INTO public.command_definition (command_name, type, exec, category)
SELECT command_name, type, exec, ''
FROM source.dod_command_definition;

-- Migrate command params
INSERT INTO public.command_param (username, db_name, command_name, type, creation_date, name, value, category)
SELECT username, db_name, command_name, type, creation_date, name, value, ''
FROM source.dod_command_params;

-- Insert hosts
INSERT INTO public.host (name, memory)
SELECT DISTINCT(host), 0
FROM source.dod_instances;

-- Migrate instances
INSERT INTO public.instance (owner, name, e_group, category, creation_date, expiry_date, type_id, size, no_connections, project, description, state, status, version, master_id, slave_id, host_id, id)
SELECT username, db_name, e_group, category::instance_category, creation_date, 
       expiry_date, t.id type_id, db_size, no_connections, project, i.description, 
       state::instance_state, 
       CASE WHEN i.status='1' THEN 'ACTIVE'::instance_status
            ELSE 'NON_ACTIVE'::instance_status
       END status, 
       version, NULL, NULL, h.id host_id, i.id
FROM source.dod_instances i
INNER JOIN public.host h ON i.host = h.name
INNER JOIN public.instance_type t ON i.db_type = t.type;

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
FROM source.attribute
GROUP BY instance_id, name;

-- Migrate functional aliases
INSERT INTO public.functional_aliases (dns_name, db_name, alias)
SELECT dns_name, db_name, alias
FROM source.functional_aliases;

-- Migrate volumes
INSERT INTO public.volume (id, instance_id, file_mode, owner, "group", server, mount_options, mounting_path, volume_type_id)
SELECT id, instance_id, file_mode, owner, "group", server, mount_options, mounting_path, 1
FROM source.volume;

-- Migrate upgrades
INSERT INTO public.upgrade (db_type, category, version_from, version_to)
SELECT db_type, category, version_from, version_to
FROM source.dod_upgrades;

-- Migrate jobs
INSERT INTO public.job (username, db_name, command_name, type, creation_date, completion_date, requester, admin_action, state, log, result, email_sent, category, instance_id)
SELECT j.username, j.db_name, j.command_name, j.type, j.creation_date, j.completion_date, j.requester, j.admin_action, j.state, j.log, j.result, j.email_sent, j.category, i.id
FROM source.dod_jobs j, source.dod_instances i
WHERE j.db_name = i.db_name;

-- Migrate instance changes
INSERT INTO public.instance_change (username, db_name, attribute, change_date, requester, old_value, new_value)
SELECT username, db_name, attribute, change_date, requester, old_value, new_value
FROM source.dod_instance_changes;


-- Make sure all the sequences are properly set, as manual inserts were done
SELECT setval('instance_id_seq', (SELECT MAX(id) from public.instance));
SELECT setval('instance_attribute_id_seq', (SELECT MAX(id) from public.instance_attribute));
SELECT setval('volume_id_seq', (SELECT MAX(id) from public.volume));
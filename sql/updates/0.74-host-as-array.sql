-- Update to change the type of "host" to an Array.
-- The name of the field "host" will be changed to "hosts".
DROP VIEW api.metadata;
CREATE OR REPLACE VIEW api.metadata AS
SELECT id, username, db_name, category, db_type, version, string_to_array(dod_instances.host, '') AS hosts, public.get_attribute('port', id) port, get_volumes volumes, d.*
FROM public.dod_instances, public.get_volumes(id), public.get_directories(db_name, db_type, version, public.get_attribute('port', id)) d;
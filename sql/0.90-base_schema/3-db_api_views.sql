-- Copyright (C) 2017, CERN
-- This software is distributed under the terms of the GNU General Public
-- Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".
-- In applying this license, CERN does not waive the privileges and immunities
-- granted to it by virtue of its status as Intergovernmental Organization
-- or submit itself to any jurisdiction.

------------------------------
-- CREATION OF VIEWS
------------------------------

-- Clusters
CREATE OR REPLACE VIEW api.cluster AS 
  SELECT cluster.id,
    cluster.owner,
    cluster.name,
    cluster.egroup,
    cluster.category,
    cluster.creation_date,
    cluster.expiry_date,
    cluster.type_id,
    instance_type.type,
    cluster.project,
    cluster.description,
    cluster.version,
    cluster.master_id,
    cluster_master.name AS master,
    api.get_cluster_instances(cluster.id) AS instances,
    api.get_cluster_attributes(cluster.id) AS attributes
  FROM cluster
    JOIN instance_type ON cluster.type_id = instance_type.id
    LEFT JOIN cluster cluster_master ON cluster.id = cluster_master.master_id,
    LATERAL api.get_cluster_instances(cluster.id) get_cluster_instances(get_cluster_instances);

-- Cluster attributes
CREATE OR REPLACE VIEW api.cluster_attributes AS 
  SELECT cluster.id,
    api.get_cluster_attributes(cluster.id) AS attributes
  FROM cluster;

-- Instances
CREATE OR REPLACE VIEW api.instance AS 
  SELECT instance.id,
    instance.owner,
    instance.name,
    instance.egroup,
    instance.category,
    instance.creation_date,
    instance.expiry_date,
    instance.type_id,
    instance_type.type,
    instance.size,
    instance.project,
    instance.description,
    instance.version,
    instance.master_id,
    instance_master.name AS master,
    instance.slave_id,
    instance_slave.name AS slave,
    instance.host_id,
    host.name AS host,
    instance.state,
    instance.status,
    instance.cluster_id,
    cluster.name AS cluster,
    api.get_instance_attributes(instance.id) AS attributes,
    api.get_owner_data(instance.name) AS user
  FROM instance
    LEFT JOIN instance instance_master ON instance.id = instance_master.id
    LEFT JOIN instance instance_slave ON instance.id = instance_slave.id
    LEFT JOIN cluster ON instance.cluster_id = cluster.id
    JOIN instance_type ON instance.type_id = instance_type.id
    JOIN host ON instance.host_id = host.id;

-- Instance attributes
CREATE OR REPLACE VIEW api.instance_attribute AS 
  SELECT instance_attribute.id,
    instance_attribute.instance_id,
    instance_attribute.name,
    instance_attribute.value
  FROM instance_attribute;

-- Jobs
CREATE OR REPLACE VIEW api.job AS 
  SELECT job.id,
    job.instance_id,
    job.command_name,
    job.creation_date,
    job.completion_date,
    job.requester,
    job.admin_action,
    job.state,
    job.email_sent
  FROM job;
  
-- Volumes
CREATE OR REPLACE VIEW api.volume AS 
  SELECT volume.id,
    volume.instance_id,
    instance.name AS instance,
    volume.file_mode,
    volume.owner,
    volume."group",
    volume.server,
    volume.mount_options,
    volume.mounting_path,
    volume.type_id,
    volume_type.type,
    api.get_volume_attributes(volume.id) AS attributes
  FROM volume
    JOIN volume_type ON volume.type_id = volume_type.id
    JOIN instance ON volume.instance_id = instance.id;

-- Hosts
CREATE OR REPLACE VIEW api.host AS 
  SELECT host.id,
    host.name,
    host.memory
  FROM host;

-- Host aliases
CREATE OR REPLACE VIEW api.host_aliases AS 
  SELECT instance.host_id,
    host.name, 
    string_agg(('dbod-'::text || instance.name::text) || '.cern.ch'::text, ','::text) AS aliases
  FROM instance
  JOIN host ON instance.host_id = host.id
  GROUP BY instance.host_id, host.name;

-- Functional aliases
CREATE OR REPLACE VIEW api.functional_aliases AS 
  SELECT functional_aliases.dns_name,
    functional_aliases.db_name,
    functional_aliases.alias
  FROM functional_aliases;

-- Metadata
CREATE OR REPLACE VIEW api.metadata AS 
  SELECT instance.id,
    instance.owner AS username,
    instance.owner AS owner,
    instance.name AS db_name,
    instance.name AS name,
    instance.category AS class,
    instance.category AS category,
    instance_type.type,
    instance.version,
    instance.creation_date,
    instance.expiry_date,
    instance.egroup,
    instance.project,
    string_to_array(host.name::text, ','::text) AS hosts,
    host.name AS host,
    api.get_instance_attributes(instance.id) AS attributes,
    api.get_instance_attribute('port'::varchar, instance.id) AS port,
    api.get_volumes(instance.id) AS volumes,
    api.get_owner_data(instance.name) AS user,
    d.basedir,
    d.bindir,
    d.datadir,
    d.logdir,
    d.socket,
    instance.cluster_id,
    cluster.name AS cluster,
    instance.state,
    instance.status,
    instance.description
  FROM instance
    JOIN instance_type ON instance.type_id = instance_type.id
    LEFT JOIN cluster ON instance.cluster_id = cluster.id
    LEFT JOIN host ON instance.host_id = host.id,
    LATERAL api.get_volumes(instance.id) get_volumes(get_volumes),
    LATERAL api.get_owner_data(instance.name) get_owner_data(get_owner_data),
    LATERAL api.get_directories(instance.name, instance_type.type, instance.version, api.get_instance_attribute('port'::varchar, instance.id)) d(basedir, bindir, datadir, logdir, socket);

-- Rundeck instances
CREATE OR REPLACE VIEW api.rundeck_instances AS 
  SELECT instance.name,
    functional_aliases.alias AS hostname,
    api.get_instance_attribute('port'::character varying, instance.id) AS port,
    'apiato'::varchar AS username,
    instance.type_id,
    instance.category,
    (instance.type_id::text || ','::text) || instance.category::text AS tags
  FROM instance
    JOIN functional_aliases ON instance.name::text = functional_aliases.db_name::text;

-- Instance types
CREATE OR REPLACE VIEW api.instance_type AS
  SELECT * FROM public.instance_type;

-- Volume types
CREATE OR REPLACE VIEW api.volume_type AS
  SELECT * FROM public.volume_type;
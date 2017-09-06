-- Copyright (C) 2015, CERN
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
    cluster.owner AS username,
    cluster.name,
    cluster.e_group,
    cluster.project,
    cluster.description,
    cluster.category AS class,
    instance_type.type,
    cluster.version,
    cluster_master.name AS master_name,
    api.get_cluster_instances(cluster.id) AS instances,
    api.get_cluster_attributes(cluster.id) AS attributes,
    api.get_cluster_attribute('port'::character varying, cluster.id) AS port
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
    instance.owner AS username,
    instance.name,
    instance.e_group,
    instance.category AS class,
    instance.creation_date,
    instance.expiry_date,
    instance_type.type,
    instance.project,
    instance.description,
    instance_master.name AS master,
    instance_slave.name AS slave,
    host.name AS host,
    instance.state,
    instance.status
  FROM instance
    LEFT JOIN instance instance_master ON instance.id = instance_master.id
    LEFT JOIN instance instance_slave ON instance.id = instance_slave.id
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
    job.username,
    job.db_name,
    job.command_name,
    job.type,
    job.creation_date,
    job.completion_date,
    job.requester,
    job.admin_action,
    job.state,
    job.log,
    job.result,
    job.email_sent,
    job.category
  FROM job;

-- Volumes
CREATE OR REPLACE VIEW api.volume AS 
  SELECT volume.id,
    volume.instance_id,
    volume.file_mode,
    volume.owner,
    volume."group",
    volume.mount_options,
    instance.name,
    volume_type.type,
    volume.server,
    volume.mounting_path,
    api.get_volume_attributes(volume.id) AS attributes
  FROM volume
    JOIN volume_type ON volume.volume_type_id = volume_type.id
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
    string_agg(('dbod-'::text || instance.name::text) || 'domain'::text, ','::text) AS aliases
  FROM instance
  GROUP BY instance.host_id;

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
    instance.name AS db_name,
    instance.category AS class,
    instance_type.type,
    instance.version,
    string_to_array(host.name::text, ','::text) AS hosts,
    api.get_instance_attributes(instance.id) AS attributes,
    api.get_instance_attribute('port'::character varying, instance.id) AS port,
    api.get_volumes(instance.id) AS volumes,
    instance.cluster_id
  FROM instance
    JOIN instance_type ON instance.type_id = instance_type.id
    LEFT JOIN host ON instance.host_id = host.id,
    LATERAL api.get_volumes(instance.id) get_volumes(get_volumes);

-- Rundeck instances
CREATE OR REPLACE VIEW api.rundeck_instances AS 
  SELECT instance.name,
    functional_aliases.alias AS hostname,
    api.get_instance_attribute('port'::character varying, instance.id) AS port,
    'dbod'::character(1) AS username,
    instance.type_id,
    instance.category,
    (instance.type_id::text || ','::text) || instance.category::text AS tags
  FROM instance
    JOIN functional_aliases ON instance.name::text = functional_aliases.db_name::text;
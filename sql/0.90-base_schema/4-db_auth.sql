-- Copyright (C) 2017, CERN
-- This software is distributed under the terms of the GNU General Public
-- Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".
-- In applying this license, CERN does not waive the privileges and immunities
-- granted to it by virtue of its status as Intergovernmental Organization
-- or submit itself to any jurisdiction.

------------------------------
-- CREATION OF AUTH FUNCTIONS
------------------------------

-- Get all the clusters for the user
CREATE OR REPLACE FUNCTION api.get_clusters(
  owner character varying,
  groups json,
  admin boolean)
  RETURNS SETOF api.cluster AS $$
#variable_conflict use_variable
BEGIN
  IF admin THEN
    return query 
    select * from api.cluster;
  ELSE
    return query 
    select * from api.cluster 
    where api.cluster.egroup in
      (select value from json_array_elements_text(groups))
      or api.cluster.owner = owner;
  END IF;
END
$$ LANGUAGE plpgsql;

-- Get all the instances for the user
CREATE OR REPLACE FUNCTION api.get_instances(
  owner character varying,
  groups json,
  admin boolean)
  RETURNS SETOF api.instance AS $$
#variable_conflict use_variable
BEGIN
  IF admin THEN
    return query 
    select * from api.instance;
  ELSE
    return query 
    select * from api.instance 
    where api.instance.egroup in
      (select value from json_array_elements_text(groups))
      or api.instance.owner = owner;
  END IF;
END
$$ LANGUAGE plpgsql;

-- Get all the jobs for the user
CREATE OR REPLACE FUNCTION api.get_jobs(
  owner character varying,
  groups json,
  admin boolean)
  RETURNS SETOF api.job AS $$
#variable_conflict use_variable
BEGIN
  IF admin THEN
    return query
    select * from api.job;
  ELSE
    return query
    select * from api.job
    where instance_id in
      (select id from api.instance 
      where api.instance.egroup in
        (select value from json_array_elements_text(groups))
        or api.instance.owner = owner);
  END IF;
END
$$ LANGUAGE plpgsql;

-- List all the clusters for the user
CREATE OR REPLACE FUNCTION api.get_user_clusters(
  owner character varying,
  groups json,
  admin boolean)
  RETURNS character varying[] AS $$
#variable_conflict use_variable
DECLARE 
res varchar[];
BEGIN
  IF admin THEN
    select array_agg(name) from api.cluster
    into res;
    return res;
  ELSE
    select array_agg(name) from api.cluster 
    where api.cluster.egroup in
      (select value from json_array_elements_text(groups))
      or api.cluster.owner = owner
    into res;
    return res;
  END IF;
END
$$ LANGUAGE plpgsql;

-- List all the instances for the user
CREATE OR REPLACE FUNCTION api.get_user_instances(
  owner character varying,
  groups json,
  admin boolean)
  RETURNS character varying[] AS $$
#variable_conflict use_variable
DECLARE
res varchar[];
BEGIN
  IF admin THEN
    select array_agg(name) from api.instance
    into res;
    return res;
  ELSE
    select array_agg(name) from api.instance 
    where api.instance.egroup in
      (select value from json_array_elements_text(groups))
      or api.instance.owner = owner
    into res;
    return res;
  END IF;
END
$$ LANGUAGE plpgsql;

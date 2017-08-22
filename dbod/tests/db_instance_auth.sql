-- Filtering functions for instance and cluster views
drop function if exists api.get_instances(owner varchar, groups json); 
create or replace function api.get_instances(owner varchar, groups json)
returns setof api.instance as $$
begin

  return query 
  select * from api.instance 
  where api.instance.e_group in
    (select value from json_array_elements_text(groups))
    or api.instance.username = owner;

end
$$ language plpgsql;

drop function if exists api.get_cluster(owner varchar, groups json); 
create or replace function api.get_clusters(owner varchar, groups json)
returns setof api.cluster as $$
begin

  return query 
  select * from api.cluster 
  where api.cluster.e_group in
    (select value from json_array_elements_text(groups))
    or api.cluster.username = owner;

end
$$ language plpgsql;

drop function if exists api.get_job(owner varchar, groups json); 
create or replace function api.get_jobs(owner varchar, groups json)
returns setof api.job as $$
begin

  return query
  select * from api.job
  where instance_id in
    (select id from api.instance 
    where api.instance.e_group in
      (select value from json_array_elements_text(groups))
      or api.instance.username = owner);

end
$$ language plpgsql;
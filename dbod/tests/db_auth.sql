-- e-groups view
drop view if exists api.e_groups;
create view api.e_groups as 
select array_agg(e_group) e_groups from (select distinct e_group from api.instance) as e; 

drop function if exists api.get_user_instances(owner varchar, groups json); 
create or replace function api.get_user_instances(owner varchar, groups json)
returns varchar[] as $$
declare
res varchar[];
begin

  select array_agg(name) from api.instance 
  where api.instance.e_group in
    (select value from json_array_elements_text(groups))
    or api.instance.username = owner
  into res;

  return res;

end
$$ language plpgsql;

drop function if exists api.get_user_clusters(owner varchar, groups json); 
create or replace function api.get_user_clusters(owner varchar, groups json)
returns varchar[] as $$
declare 
res varchar[];
begin

  select array_agg(name) from api.cluster 
  where api.cluster.e_group in
    (select value from json_array_elements_text(groups))
    or api.cluster.username = owner
  into res;

  return res;

end
$$ language plpgsql;


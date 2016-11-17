CREATE FUNCTION cluster()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
  cluster_id int;
BEGIN
  INSERT INTO cluster (owner, name, e_group, category, creation_date, expiry_date, instance_type_id, project, description, version, master_cluster_id, state, status)
  VALUES new.owner,
         new.name,
         new.e_group,
         new.category,
         now(),
         expiry_date,
         select type_id from instance_type where instance_type.type=new.instance_type,
         new.project,
         new.description,
         new.version,
         select cluster_id from apiato.cluster where apiato.cluster.name=new.master_name,
         new.state,
         new.status;
RETURN new;
END;
$$;

CREATE TRIGGER apiato_ro.cluster
INSTEAD OF INSERT ON apiato_ro.cluster
FOR EACH ROW
EXECUTE PROCEDURE cluster();
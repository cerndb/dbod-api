job "apiato-{{MODE}}" {
  datacenters = [
    "cern-geneva-a",
#    "cern-geneva-b",
#    "cern-geneva-c"
  ]

  type = "service"

  {% if MODE == 'dev' %}
  {% set pg_port = 'PG_PORT_DEV' %}
  {% set apiato_port = 'APIATO_PORT_DEV' %}
  {% elif MODE == 'qa' %}
  {% set pg_port = 'PG_PORT_QA' %}
  {% set apiato_port = 'APIATO_PORT_QA' %}
  {% else %}
  {% set pg_port = 'PG_PORT_PROD' %}
  {% set apiato_port = 'APIATO_PORT_PROD' %}
  {% endif %}

  group "dbod" {
    task "postgrest" {
      driver = "docker"
      config {
        image = "gitlab-registry.cern.ch/db/dbod/postgrest:latest"
        volumes = [
          "/etc/dia/certificates/:/etc/dia/certificates/",
          "/etc/ssl/certs/:/etc/ssl/certs/"
        ]
        auth {
          username = "diaglab"
          password = "{{ "not-defined" | env_override('DIAGLAB_REGISTRY_TOKEN_RO') }}"
        }
        port_map {
          postgrest_port = "{{ "not-defined" | env_override(pg_port) }}"
        }
        network_mode = "docker_custom_network"
        network_aliases = ["postgrest"]
      }
      resources {
        cpu = 100 # Mhz
        memory = 128 # MB
        network {
          mbits = 10
        }
      }
      env {
        PGRST_DB_URI = "{{ "not-defined" | env_override('PGRST_DB_URI') }}"
        PGRST_DB_ANON_ROLE = "{{ "not-defined" | env_override('PGRST_DB_ANON_ROLE') }}"
        PGRST_DB_SCHEMA = "{{ "not-defined" | env_override('PGRST_DB_SCHEMA') }}"
        PGRST_SERVER_PORT = "{{ "not-defined" | env_override(pg_port) }}"
      }
    }
    task "apiato" {
      driver = "docker"
      config {
        image = "gitlab-registry.cern.ch/db/dbod-api:{{BUILD_MODE}}"
        volumes = [
          "etc:/etc/apiato",
          "/etc/dia/certificates/:/etc/dia/certificates/",
          "/etc/ssl/certs/:/etc/ssl/certs/"
        ]
        auth {
          username = "diaglab"
          password = "{{ "not-defined" | env_override('DIAGLAB_REGISTRY_TOKEN_RO') }}"
        }
        port_map {
          apiato_port = "{{ "not-defined" | env_override(apiato_port) }}"
        }
        network_mode = "docker_custom_network"
        network_aliases = ["apiato"]
      }
      resources {
        cpu = 100 # Mhz
        memory = 128 # MB
        network {
          mbits = 10
          port "apiato_port" {
            static = "{{ "not-defined" | env_override(apiato_port) }}"
          }
        }
      }
      template {
        destination = "etc/apiato.cfg"
        left_delimiter = "@#$%^"
        right_delimiter = "^%$#@"
        data = <<EOH

[server]
port={{ "not-defined" | env_override(apiato_port) }}

[cache]
path=/etc/dbod/cache/metadata.json

[ssl]
hostcert=/etc/dia/certificates/hostcert.pem
hostkey=/etc/dia/certificates/hostkey.pem

[api]
user=dbod-api
pass={{ "not-defined" | env_override('APIATO_PASSWORD') }}

[auth]
admin_group = dbondemand-admin

[logging]
path=/var/log/apiato.log
level=debug
stderr=true
fmt = %(color)s[%(levelname)s %(asctime)s %(module)s:%(lineno)d]%(end_color)s %(message)s
datefmt = %d/%b/%Y:%H:%M:%S %z

[tornado]
debug=true

[postgrest]
rundeck_resources_url=http://postgrest:{{ "not-defined" | env_override(pg_port) }}/rundeck_instances
host_aliases_url=http://postgrest:{{ "not-defined" | env_override(pg_port) }}/host_aliases
host_url=http://postgrest:{{ "not-defined" | env_override(pg_port) }}/host
metadata_url=http://postgrest:{{ "not-defined" | env_override(pg_port) }}/metadata
fim_url=http://postgrest:{{ "not-defined" | env_override(pg_port) }}/fim_data
egroups_url=http://postgrest:{{ "not-defined" | env_override(pg_port) }}/egroups
user_instances_url=http://postgrest:{{ "not-defined" | env_override(pg_port) }}/rpc/get_user_instances
user_clusters_url=http://postgrest:{{ "not-defined" | env_override(pg_port) }}/rpc/get_user_clusters
functional_alias_url=http://postgrest:{{ "not-defined" | env_override(pg_port) }}/functional_aliases

instance_type_url=http://postgrest:{{ "not-defined" | env_override(pg_port) }}/instance_type
instance_url=http://postgrest:{{ "not-defined" | env_override(pg_port) }}/instance
insert_instance_url=http://postgrest:{{ "not-defined" | env_override(pg_port) }}/rpc/insert_instance
delete_instance_url=http://postgrest:{{ "not-defined" | env_override(pg_port) }}/rpc/delete_instance
update_instance_url=http://postgrest:{{ "not-defined" | env_override(pg_port) }}/rpc/update_instance
get_instances_url=http://postgrest:{{ "not-defined" | env_override(pg_port) }}/rpc/get_instances

volume_url=http://postgrest:{{ "not-defined" | env_override(pg_port) }}/volume
insert_volume_url=http://postgrest:{{ "not-defined" | env_override(pg_port) }}/rpc/insert_volume
delete_volume_url=http://postgrest:{{ "not-defined" | env_override(pg_port) }}/rpc/delete_volume
update_volume_url=http://postgrest:{{ "not-defined" | env_override(pg_port) }}/rpc/update_volume

functional_alias_url=http://postgrest:{{ "not-defined" | env_override(pg_port) }}/functional_alias
insert_functional_alias_url=http://postgrest:{{ "not-defined" | env_override(pg_port) }}/rpc/insert_functional_alias
delete_functional_alias_url=http://postgrest:{{ "not-defined" | env_override(pg_port) }}/rpc/delete_functional_alias
update_functional_alias_url=http://postgrest:{{ "not-defined" | env_override(pg_port) }}/rpc/update_functional_alias

attribute_url=http://postgrest:{{ "not-defined" | env_override(pg_port) }}/attribute
instance_attributes_url=http://postgrest:{{ "not-defined" | env_override(pg_port) }}/rpc/get_instance_attributes
instance_attribute_url=http://postgrest:{{ "not-defined" | env_override(pg_port) }}/rpc/get_instance_attribute
insert_instance_attribute_url=http://postgrest:{{ "not-defined" | env_override(pg_port) }}/rpc/insert_instance_attribute
update_instance_attribute_url=http://postgrest:{{ "not-defined" | env_override(pg_port) }}/rpc/update_instance_attribute
delete_instance_attribute_url=http://postgrest:{{ "not-defined" | env_override(pg_port) }}/rpc/delete_instance_attribute
get_attributes_url=http://postgrest:{{ "not-defined" | env_override(pg_port) }}/rpc/get_attributes

cluster_attributes_url=http://postgrest:{{ "not-defined" | env_override(pg_port) }}/cluster_attributes
update_cluster_attribute_url=http://postgrest:{{ "not-defined" | env_override(pg_port) }}/rpc/insert_instance_attribute
update_cluster_attribute_url=http://postgrest:{{ "not-defined" | env_override(pg_port) }}/rpc/update_cluster_attribute
delete_cluster_attribute_url=http://postgrest:{{ "not-defined" | env_override(pg_port) }}/rpc/delete_instance_attribute

volume_type_url=http://postgrest:{{ "not-defined" | env_override(pg_port) }}/volume_type
volume_url=http://postgrest:{{ "not-defined" | env_override(pg_port) }}/volume
insert_volume_url=http://postgrest:{{ "not-defined" | env_override(pg_port) }}/rpc/insert_volume
update_volume_url=http://postgrest:{{ "not-defined" | env_override(pg_port) }}/rpc/update_volume
delete_volume_url=http://postgrest:{{ "not-defined" | env_override(pg_port) }}/rpc/delete_volume
volume_attributes_url=http://postgrest:{{ "not-defined" | env_override(pg_port) }}/volume_attributes
insert_volume_attribute_url=http://postgrest:{{ "not-defined" | env_override(pg_port) }}/rpc/insert_volume_attribute
update_volume_attribute_url=http://postgrest:{{ "not-defined" | env_override(pg_port) }}/rpc/update_volume_attribute
delete_volume_attribute_url=http://postgrest:{{ "not-defined" | env_override(pg_port) }}/rpc/delete_volume_attribute

cluster_type_url=
cluster_url=http://postgrest:{{ "not-defined" | env_override(pg_port) }}/cluster
insert_cluster_url=http://postgrest:{{ "not-defined" | env_override(pg_port) }}/rpc/insert_cluster
delete_cluster_url=http://postgrest:{{ "not-defined" | env_override(pg_port) }}/rpc/delete_cluster
update_cluster_url=http://postgrest:{{ "not-defined" | env_override(pg_port) }}/rpc/update_cluster
get_clusters_url=http://postgrest:{{ "not-defined" | env_override(pg_port) }}/rpc/get_clusters

host_url=http://postgrest:{{ "not-defined" | env_override(pg_port) }}/host
insert_host_url=http://postgrest:{{ "not-defined" | env_override(pg_port) }}/rpc/insert_host
delete_host_url=http://postgrest:{{ "not-defined" | env_override(pg_port) }}/rpc/delete_host
update_host_url=http://postgrest:{{ "not-defined" | env_override(pg_port) }}/rpc/delete_host

job_url=http://postgrest:{{ "not-defined" | env_override(pg_port) }}/job
job_log_url=http://postgrest:{{ "not-defined" | env_override(pg_port) }}/job_log
insert_job_url=http://postgrest:{{ "not-defined" | env_override(pg_port) }}/rpc/insert_job
delete_job_url=http://postgrest:{{ "not-defined" | env_override(pg_port) }}/rpc/delete_job
update_job_url=http://postgrest:{{ "not-defined" | env_override(pg_port) }}/rpc/delete_job
get_jobs_url=http://postgrest:{{ "not-defined" | env_override(pg_port) }}/rpc/get_jobs

instance_state_url=http://postgrest:{{ "not-defined" | env_override(pg_port) }}/enum_instance_state
instance_status_url=http://postgrest:{{ "not-defined" | env_override(pg_port) }}/enum_instance_status
instance_category_url=http://postgrest:{{ "not-defined" | env_override(pg_port) }}/enum_instance_category
job_state_url=http://postgrest:{{ "not-defined" | env_override(pg_port) }}/enum_job_state

[rundeck]
timeout = 15
api_run_job = https://dbod-rundeck.cern.ch/api/14/job/{0}/run?format=json
api_job_output = https://dbod-rundeck.cern.ch/api/14/execution/{0}/output?format=json
api_authorization = {{ "not-defined" | env_override('RUNDECK_API_AUTH') }}

[rundeck-jobs]
backup = 8be1302e-2ed7-486c-8a1f-6e32ea882e08
get-snapshots = c7d19158-9442-4806-9f99-a0ba405ab2b0
list-config-files = 8ab3d01e-f28b-4d66-96e1-2e1037feddad
list-log-files = eb0c96b3-95d1-43a0-afe6-a23b939e0150
serve-file = 6644ab9a-b606-4bdf-9c70-64475b17d8ef
start = 14ead236-f9fd-4e68-9a84-9b897b4bec3f
stop = 28039d3c-c87c-45ed-9fcf-8865839a4bb0

      EOH
      }
    }
  }
}


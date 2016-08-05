-- Use this script when the password to connect to Oracle is changed
ALTER USER MAPPING FOR <dbuser> SERVER <server_name>
    OPTIONS (SET user '<oracle_username>', SET password '<oracle_password>');
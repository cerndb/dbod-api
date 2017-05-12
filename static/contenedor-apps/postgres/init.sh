#!/bin/bash
#
# Bash script for creating DBOD MySQL user accounts on puppet managed installations
#
# Author: rgaspar  Created: 3rd November 2014
set -e
bindir=/usr/bin
socket=/var/run/postgresql
port=5432

cat <<'EOF' > /tmp/dbod-users.sql
-- Owner account
create user admin with password 'pass' createdb createrole;
create database admin with owner = admin;

-- postgres
alter user postgres with password 'superpass';
EOF

if ! [ -f '/tmp/dbod-users.sql' ]; then
    exit 2 # The file could not be created
fi

output=`${bindir}/psql -U postgres -h ${socket} -p ${port} < /tmp/dbod-users.sql #2>&1`
if [[ $output =~ "ERROR" || $? -ne 0 ]]; then
    exit 3 # Problem creating accounts
fi

echo "host all admin 0.0.0.0/0 md5" | tee -a "$PGDATA/pg_hba.conf" > /dev/null

rm /tmp/dbod-users.sql
#exit 0

-- Copyright (C) 2015, CERN
-- This software is distributed under the terms of the GNU General Public
-- Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".
-- In applying this license, CERN does not waive the privileges and immunities
-- granted to it by virtue of its status as Intergovernmental Organization
-- or submit itself to any jurisdiction.

------------------------------------------------
-- Create the structure for the test database --
------------------------------------------------

-- DOD_COMMAND_DEFINITION
CREATE TABLE dod_command_definition (
    command_name varchar(64) NOT NULL,
    type varchar(64) NOT NULL,
    exec varchar(2048),
    category varchar(20),
    PRIMARY KEY (command_name, type, category)
);

-- DOD_COMMAND_PARAMS
CREATE TABLE dod_command_params (
    username varchar(32) NOT NULL,
    db_name varchar(128) NOT NULL,
    command_name varchar(64) NOT NULL,
    type varchar(64) NOT NULL,
    creation_date date NOT NULL,
    name varchar(64) NOT NULL,
    value text,
    category varchar(20),
    PRIMARY KEY (db_name)
);

-- DOD_INSTANCE_CHANGES
CREATE TABLE dod_instance_changes (
    username varchar(32) NOT NULL,
    db_name varchar(128) NOT NULL,
    attribute varchar(32) NOT NULL,
    change_date date NOT NULL,
    requester varchar(32) NOT NULL,
    old_value varchar(1024),
    new_value varchar(1024),
    PRIMARY KEY (db_name)
);

-- DOD_INSTANCES
CREATE TABLE dod_instances (
    username varchar(32) NOT NULL,
    db_name varchar(128) NOT NULL,
    e_group varchar(256),
    category varchar(32) NOT NULL,
    creation_date date NOT NULL,
    expiry_date date,
    db_type varchar(32) NOT NULL,
    db_size int NOT NULL,
    no_connections int,
    project varchar(128),
    description varchar(1024),
    version varchar(128),
    master varchar(32),
    slave varchar(32),
    host varchar(128),
    state varchar(32),
    status varchar(32),
    id int,
    PRIMARY KEY (id)
);

-- DOD_JOBS
CREATE TABLE dod_jobs (
    username varchar(32) NOT NULL,
    db_name varchar(128) NOT NULL,
    command_name varchar(64) NOT NULL,
    type varchar(64) NOT NULL,
    creation_date date NOT NULL,
    completion_date date,
    requester varchar(32) NOT NULL,
    admin_action int NOT NULL,
    state varchar(32) NOT NULL,
    log text,
    result varchar(2048),
    email_sent date,
    category varchar(20),
    PRIMARY KEY (username, db_name, command_name, type, creation_date)
);

-- DOD_UPGRADES
CREATE TABLE dod_upgrades (
    db_type varchar(32) NOT NULL,
    category varchar(32) NOT NULL,
    version_from varchar(128) NOT NULL,
    version_to varchar(128) NOT NULL,
    PRIMARY KEY (db_type, category, version_from)
);

-- VOLUME
CREATE TABLE volume (
    id serial,
    instance_id integer NOT NULL,
    file_mode char(4) NOT NULL,
    owner varchar(32) NOT NULL,
    vgroup varchar(32) NOT NULL,
    server varchar(63) NOT NULL,
    mount_options varchar(256) NOT NULL,
    mounting_path varchar(256) NOT NULL
);

-- HOST
CREATE TABLE host (
    id serial,
    name varchar(63) NOT NULL,
    memory integer NOT NULL
);

-- ATTRIBUTE
CREATE TABLE attribute (
    id serial,
    instance_id integer NOT NULL,
    name varchar(32) NOT NULL,
    value varchar(250) NOT NULL
);

-- Insert test data for instances
INSERT INTO dod_instances (username, db_name, e_group, category, creation_date, expiry_date, db_type, db_size, no_connections, project, description, version, master, slave, host, state, status, id)
VALUES ('user01', 'dbod01', 'testgroupA', 'TEST', now(), NULL, 'MYSQL', 100, 100, 'API', 'Test instance 1', '5.6.17', NULL, NULL, 'host01', 'RUNNING', 1, 1),
       ('user01', 'dbod02', 'testgroupB', 'PROD', now(), NULL, 'PG', 50, 500, 'API', 'Test instance 2', '9.4.4', NULL, NULL, 'host03', 'RUNNING', 1, 2),
       ('user02', 'dbod03', 'testgroupB', 'TEST', now(), NULL, 'MYSQL', 100, 200, 'WEB', 'Expired instance 1', '5.5', NULL, NULL, 'host01', 'RUNNING', 0, 3),
       ('user03', 'dbod04', 'testgroupA', 'PROD', now(), NULL, 'PG', 250, 10, 'LCC', 'Test instance 3', '9.4.5', NULL, NULL, 'host01', 'RUNNING', 1, 4),
       ('user04', 'dbod05', 'testgroupC', 'TEST', now(), NULL, 'MYSQL', 300, 200, 'WEB', 'Test instance 4', '5.6.17', NULL, NULL, 'host01', 'RUNNING', 1, 5);
       
-- Insert test data for volumes
INSERT INTO volume (instance_id, file_mode, owner, vgroup, server, mount_options, mounting_path)
VALUES (1, '0755', 'TSM', 'ownergroup', 'NAS-server', 'rw,bg,hard', '/MNT/data1'),
       (2, '0755', 'TSM', 'ownergroup', 'NAS-server', 'rw,bg,hard', '/MNT/data2'),
       (4, '0755', 'TSM', 'ownergroup', 'NAS-server', 'rw,bg,hard,tcp', '/MNT/data4'),
       (5, '0755', 'TSM', 'ownergroup', 'NAS-server', 'rw,bg,hard', '/MNT/data5');

-- Insert test data for attributes
INSERT INTO attribute (instance_id, name, value)
VALUES (1, 'port', '5501'),
       (2, 'port', '6603'),
       (3, 'port', '5510'),
       (4, 'port', '6601'),
       (5, 'port', '5500');
        
-- Insert test data for hosts
INSERT INTO host (name, memory)
VALUES ('host01', 12),
       ('host02', 24),
       ('host03', 64),
       ('host04', 256);

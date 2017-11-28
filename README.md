# apiato-API

[![Build Status](https://travis-ci.org/cerndb/apiato-api.svg?branch=icot_rundeck)](https://travis-ci.org/cerndb/apiato-api)
[![Coverage Status](https://coveralls.io/repos/github/cerndb/apiato-api/badge.svg?branch=master)](https://coveralls.io/github/cerndb/apiato-api?branch=master)

## Introduction

This repository contains a REST API server which exposes a common and uniform
interface to the CERN DB On Demand service internal database. The objective is
to consolidate the access to the service database and avoid maintaining
database access code in different components (and langugages) which form
part of the service architecture. 

It's implemented using [Tornado](http://www.tornadoweb.org/) and tries to be
as simple as possible.

## Installation for a development environment

There is a dependency for *libpq-dev*, which is required to build the
python *psycopg2* module. This library needs to be installed with the standard 
package manager for your OS.

Afterwards you can clone the repository and install it and its dependencies
in a local virtual environment (this requires the *python-virtualenv* package).

    $ git clone <repo_url>
    $ cd apiato-api
    $ virtualenv venv
    $ source venv/bin/activate
    $ pip install -r requirements.pip
    $ python setup.py install

Now you should be able to start the server by executing:

    $ bin/apiato-api

## Requirements 

### Configuration file
The code expects a configuration file */etc/apiato/api.cfg*. It is also possible to provide
a path for the config file using the argument *-c* or *--config*.

A sample config file can be fount in this repository at: [static/api.cfg](static/api.cfg)

### Database

All sql files required to run the API are included in the *sql* folder. Depending on the 
version you are running you should import the latest *base_schema.sql* file and any
sql files with a higher version number existing in the folder *sql/updates*.

```
psql apiato apiato -f sql/0.90qa-base_schema.sql 
```

The current sql schema from version 0.90 and higher is [0.90qa-base-schema.sql](sql/0.90qa-base-schema.sql).
Importing that sql file should autommatically import all the required scripts. If for
any reason the import doesn't work you can just simply enter the folder **0.90-base_schema**
and manually import the 4 files in numeric order.



### Testing

A new, empty database is required to execute the tests. Import the sql base schema from previous
step to create it.
When the database is ready, we can import all the test data used by the tests to check all the 
functionality:

* Note: Do NOT import this file in a production database, it will DELETE all the existing data!

The file to import is: [apiato/tests/db_test.sql](apiato/tests/db_test.sql).

```
psql apiato apiato -f apiato/tests/db_test.sql
```


Once the file is imported and PostgREST is running on that database, we can run the tests using the 
following command:

```
nosetests -v
```

If the config file is not in the default path **/etc/apiato/api.cfg** we can specify it using the **--config**
argument:

```
nosetests -v -c /path/to/api.cfg
```

#### Migrating from existing database

To migrate from an existing database we can just import the 4 sql files inside the folder **sql/0.90-base_schema/migration** in numeric order.
Please note that the first file should be edited before with the connection details of the existing databases, and this file
should be executed with ADMIN priviledges.

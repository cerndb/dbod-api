# DBOD-API

[![Build Status](https://travis-ci.org/cerndb/dbod-api.svg?branch=icot_rundeck)](https://travis-ci.org/cerndb/dbod-api)
[![Coverage Status](https://coveralls.io/repos/github/cerndb/dbod-api/badge.svg?branch=master)](https://coveralls.io/github/cerndb/dbod-api?branch=master)

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
    $ cd dbod-api
    $ virtualenv venv
    $ source venv/bin/activate
    $ pip install -r requirements.pip
    $ python setup.py install

Now you should be able to start the server by executing:

    $ bin/dbod-api

## Requirements 

### Configuration file
In it's current, very initial version, the code expects a configuration file 
*/etc/dbod/api.cfg* with the following sections and fields:
```
[database]
user=
host=
port=
database=
password=
[ssl]
hostcert=
hostkey=
```

### Database
TODO


# DBOD-API

## Installation for a development environment

There is a dependency for *libpq-dev*. This library needs to be installed with
the standard package manager for your OS.

    $ git clone <repo_url>
    $ cd dbod-api
    $ virtualenv venv
    $ source venv/bin/activate
    $ pip install -r requirements.pip
    $ python setup.py install

    $ bin/dbod-api

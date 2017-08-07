.. DB On Demand API documentation master file, created by
   sphinx-quickstart on Fri Aug  5 10:50:18 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

######################
DB On Demand API
######################

Introduction
================================

The main objetive of the DB On Demand API is to serve as an interface 
between the platform data and all other platform componentes, such as,
at the moment of writing this document:
- The DB On Demand `Web Interface <https://github.com/cerndb/dbod-webapp>`_
- The DB On Demand `Core framework <https://github.com/cerndb/dbod-Core>`_
- A `Rundeck <https://rundeck.org>`_ installation

Setup
^^^^^^^^^^^^^^^^^^^^^^

The DB On Demand platform uses a postgrest database for its backend. In order
to communicate with it it uses `PostgREST <https://postgrest.com>`_.

A basic single node deployment consist of both and instance of **PostgREST** and the DB
On Demand API running on the same machine, with the **PostgREST** listening port not
reachable through the network.


####################
Table of Contents
####################

.. toctree::
    :maxdepth: 3
    :name: mastertoc
    :caption: Table of Contents

    endpoints
    modules




####################
Documentation
####################

Indices and tables
================================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


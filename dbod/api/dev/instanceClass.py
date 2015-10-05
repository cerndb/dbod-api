#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2015, CERN
# This software is distributed under the terms of the GNU General Public
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as Intergovernmental Organization
# or submit itself to any jurisdiction.

from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Instance(Base):
    __tablename__ = 'dod_instances'
    
    ID = Column(Integer, primary_key=True)
    username = Column(String)
    db_name = Column(String)
    e_group = Column(String)
    category = Column(String)
    creation_date = Column(Date)
    expiry_date = Column(Date)
    db_type = Column(String)
    db_size = Column(Integer)
    no_connections = Column(Integer)
    project = Column(String)
    description = Column(String)
    version = Column(String)
    master = Column(String)
    slave = Column(String)
    host = Column(String)
    state = Column(String)
    status = Column(Integer)
    

    def __repr__(self):
        return "<Entity(db_name='%s', username='%s', db_type='%s')>" % (self.db_name, self.username, self.db_type)

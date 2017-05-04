#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2015, CERN
# This software is distributed under the terms of the GNU General Public
# Licence version 3 (GPL Version 3), copied verbatim in the file "LICENSE".
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as Intergovernmental Organization
# or submit itself to any jurisdiction.

"""
Base module with common methods and classes used by another endpoints.
"""

import tornado.web
import base64
import functools
import logging
import requests
import json
import urllib
from os import mkdir, path, listdir
from subprocess import check_output, CalledProcessError
import shlex

from dbod.config import config

# HTTP API status codes
OK = 200
CREATED = 201 # Request fulfilled resulting in creation of new resource
ACCEPTED = 202
NO_CONTENT = 204 # Succesfull delete
NOT_FOUND = 404
UNAUTHORIZED = 401
CONFLICT = 409
BAD_REQUEST = 400
BAD_GATEWAY = 502
SERVICE_UNAVAILABLE = 503

# Basic HTTP Authentication decorator
def http_basic_auth(fun):
    """Decorator for extracting HTTP basic authentication user/password pairs
    from the request headers and matching them to configurated credentials.
    It will generate an HTTP UNAUTHORIZED (Error code 401) if the request is
    not using HTTP basic authentication.

    Example:
        @http_basic_auth
        def get(self, user, pwd)
    """
    @functools.wraps(fun)
    def wrapper(*args, **kwargs):
        """ Decorator wrapper """
        self = args[0]
        try:
            # Try
            auth = self.request.headers.get('Authorization')
            scheme, _, token = auth.partition(' ')
            if scheme.lower() == 'basic':
                # Decode user and password
                user, _, pwd = base64.decodestring(token).partition(':')
                if user == config.get('api','user') and pwd == config.get('api','pass'):
                    return fun(*args, **kwargs)
                else:
                    # Raise UNAUTHORIZED HTTP Error (401)
                    logging.error("Unauthorized access from: %s",
                        self.request.headers)
                    raise tornado.web.HTTPError(UNAUTHORIZED)

            else:
                # We only support basic authentication
                logging.error("Authentication scheme not recognized")
                return "Authentication scheme not recognized"
        except AttributeError:
            # Raise UNAUTHORIZED HTTP Error (401) if the request is not
            # using autentication (auth will be None and partition() will fail
            logging.error("Unauthorized access from: %s",
                self.request.headers)
            raise tornado.web.HTTPError(UNAUTHORIZED)

    return wrapper

# Openstack authentication through keystone
def cloud_auth(component):
    """
    This function can be used as a decorator.
    It is used for authenticating with the container providers and the orchestrators.
    In this case the container provider is *magnum* and the orchestrator *kubernetes*.

    :param component: magnum or kubernetes
    :type component: str
    :return: The calling function with the auth header or the certificates' paths as function parameters
    :raises: 401 UNAUTHORIZED - when the password of the *auth_keystone.json* is not correct
    """
    def keystone_decorator(fun):
        @functools.wraps(fun)
        def wrapper(*args, **kwargs):
            if component == "magnum":
                # header from keystone
                token_header = 'X-Subject-Token'
                keystone_url = config.get(component, 'auth_id_url')
                auth_url = keystone_url + '/auth' + '/tokens'
                auth_json_file = config.get(component,'auth_json')
                try:
                    auth_json = json.load(open(auth_json_file, 'r'))

                    header = {'Content-Type': 'application/json'}
                    response = requests.post(auth_url,
                                             json=auth_json,
                                             headers=header)
                    xtoken = response.headers.get(token_header)
                    if response.ok and xtoken:
                        logging.debug("Token collected for DBoD Pilot Project")
                        kwargs.update({token_header: xtoken})
                        return fun(*args, **kwargs)
                    else:
                        logging.error("No Token or not all the fields provided to access %s with status code: %s" %(component, response.status_code))
                        raise tornado.web.HTTPError(response.status_code)
                except ValueError:
                    logging.error("No JSON format of the authentication file provided for %s." %(component))
                    raise tornado.web.HTTPError(UNAUTHORIZED)
                except KeyError:
                    logging.error("No X-Subject-Token available in headers")
                    logging.debug("Headers of the response from %s: %s" %(component, response.headers))
                    raise tornado.web.HTTPError(UNAUTHORIZED)

            if component == 'kubernetes' and config.get('containers-provider', 'cloud') == 'magnum':
                force = False
                cloud = config.get('containers-provider', 'cloud')
                cluster = kwargs.get('cluster')
                cluster_certs_dir = config.get(cloud, 'cluster_certs_dir') + '/' + cluster

                if path.isdir(cluster_certs_dir):
                    certFiles = set(listdir(cluster_certs_dir))
                    certRequired = set(['config', 'ca.pem', 'key.pem', 'cert.pem'])
                    if certRequired <= certFiles:
                        return fun(*args, **kwargs)
                    else:
                        force = True
                        logging.error("There are certificates missing in %s" %(cluster_certs_dir))
                else:
                    try:
                        # create a directory with all the certificates for future use
                        mkdir(cluster_certs_dir)
                        logging.debug("Creating certs dir in " + cluster_certs_dir)
                    except OSError, e:
                        logging.error("Error while creating certificates directory")
                        logging.error("Return code: %s" %(e.returncode))
                        raise tornado.web.HTTPError(UNAUTHORIZED)

                # take the necessary information from the authentication json file
                auth_json_file = config.get(cloud,'auth_json')
                auth_json = json.load(open(auth_json_file, 'r'))['auth']

                os_user_base = auth_json.get('identity').get('password').get('user')
                username = os_user_base.get('name')
                user_domain_name = os_user_base.get('domain').get('name')
                password = os_user_base.get('password')

                os_project_base = auth_json.get('scope').get('project')
                project_name = os_project_base.get('name')
                project_domain_name = os_project_base.get('domain').get('name')

                auth_url = config.get(cloud,'auth_id_url')
                cmd_prefix = 'magnum --os-username ' + username + \
                             ' --os-user-domain-name ' + user_domain_name + \
                             ' --os-password ' + password + \
                             ' --os-project-name ' + '"'+project_name+'"' + \
                             ' --os-project-domain-name ' + project_domain_name + \
                             ' --os-auth-url ' + auth_url

                cmd = "cluster-config " + cluster
                #cmd_args = ' '.join(args)
                cmd_args = "--dir " + cluster_certs_dir
                if force:
                    cmd_args = cmd_args + " --force"
                cmd_final = cmd_prefix + ' ' + cmd + ' ' + cmd_args
                try:
                    # No way to run this kind of command through the Openstack API
                    check_output(shlex.split(cmd_final))
                    logging.debug("Command %s with args %s ran successfully" %(cmd, cmd_args))
                    return fun(*args, **kwargs)
                except CalledProcessError as e:
                    logging.error("Command %s with args %s failed with return code %s" %(cmd, cmd_args, e.returncode))
                    logging.error("Command failed with output: %s" %(e.output))
                    #return callback(auth_json, cmd, args)
                    raise tornado.web.HTTPError(UNAUTHORIZED)

        return wrapper
    return keystone_decorator

def get_function(composed_url, **auth):
    """
    This function is used to do easily GET requests without checking the results every time.

    :param url: The url the request will be sent to

    :param headers: The value is a *dict*, the token in the header which is used to access openstack through keystone
    :type headers: dict

    or

    :param url: The url the request will be sent to
    :param cert: The value is a *str*, the path to the certificate which is usually used to access kubernetes
    :type cert: dict
    :param key: The value is a str, the path to the private key
    :type key: dict
    :param ca: The value is a str, the path to the certificate authority
    :type ca: dict

    :return: The json data and the status_code
    :rtype: dict, int

    """
    if auth.get('headers'):
        response = requests.get(composed_url,
                                headers=auth.get('headers'))
    elif auth.get('cert') and auth.get('key') and auth.get('ca'):
        response = requests.get(composed_url,
                                cert=(auth.get('cert'), auth.get('key')),
                                verify=auth.get('ca'))
    else:
        return {}, 401

    if response.ok:
        try:
            data = response.json()
        except ValueError:
            return {}, 500
        if data:
            return data, response.status_code
    return {}, response.status_code,

def get_instance_id_by_name(name):
    """Common function to get the ID of an instance by its name."""
    response = requests.get(config.get('postgrest', 'instance_url') + "?db_name=eq." + name)
    if response.ok:
        data = response.json()
        if data:
            return data[0]["id"]
    return None

class DocHandler(tornado.web.RequestHandler):
    """Shows the list of endpoints available in the API"""
    def get(self):
        logging.info("Generating API endpoints doc")
        response = """Please use :
            <p>http://hostname:port/api/v1/instance/NAME</p>
            <p>http://hostname:port/api/v1/instance/alias/NAME</p>
            <p>http://hostname:port/api/v1/host/aliases/HOSTNAME</p>
            <p>http://hostname:port/api/v1/metadata/instance/NAME</p>
            <p>http://hostname:port/api/v1/metadata/host/HOSTNAME</p>
            <p>http://hostname:port/api/v1/rundeck/resources.xml</p>
            <p>http://hostname:port/api/v1/rundeck/job/JOB/NODE</p>"""
        self.set_header("Content-Type", 'text/html')
        self.write(response)

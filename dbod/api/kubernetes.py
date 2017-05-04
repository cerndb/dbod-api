#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2015, CERN
# This software is distributed under the terms of the GNU General Public
# Licence version 3 (GPL Version 3), copied verbatim in the file "LICENSE".
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Kubernetes Module"""

import logging
import json
import yaml
import requests
import tornado.web
from dbod.api.base import *
from dbod.config import config
from os import path, listdir, mkdir, rename
from jinja2 import Environment, FileSystemLoader
from base64 import b64encode

class KubernetesClusters(tornado.web.RequestHandler):
    """
    This is the handler of **(/beta)/kubernetes/<cluster>/<resource>/<name>/<suresource><subname>** endpoint

    Things that are given for the development of this endpoint:

    * There are 2 new sections in the *api.cfg*:
        * *containers-provider*, which includes:
            * the name of the cloud container provider e.g. magnum or native
            * the directory for the applications files
        * *<name of container provider>* which includes:
            * *coe*, the name of the orchestrator
            * *cluster_certs*, the directory where the certificates for accessing the  orchestrator are stored
            * *auth_json*, the path to the json file for authenticating with the container provider
            * *cluster_url*, base url for accessing the container provider
            * *auth_id_url*, base url for authenticating with the container provider
            * *volume_url*, base url for managing volumes of the container provider

    * All the directories defined in the *api.cfg* above have to exist and the user who runs the api has to be able to read-write on them

    * There has to be a folder named *contenedor-apps* which will have to include folders with the supported applications; in this case these are *mysql* and *postgres*.
        * In the folder with the name of the application there has to be the templates folder for:
            * the deployment kubernetes configuration file
            * the service kubernetes configuration file
            * the secret kubernetes configuration file
            * the application's configuration file which will be encoded later to be mounted as a secret
        * In the folder there has to be also the initialization script (init.sql for mysql and init.sh for postgres) which will be encoded and mounted as a secret in kubernetes as well
    """

    headers = {'Content-Type': 'application/json'}
    cloud = config.get('containers-provider', 'cloud')
    coe = config.get(cloud, 'coe')
    kubeApi = ''
    api_response = {'response': []}
    app_specifics = {
            'mysql': {
                'conf_name': 'mysql.cnf',
                'init_name': 'init.sql',
                'port': 5500
                },
            'postgres': {
                'conf_name': 'postgresql.conf',
                'init_name': 'init.sh',
                'port': 6600
                }
            }

    @cloud_auth(coe)
    def get(self, **args):
        logging.debug('Arguments:' + str(self.request.arguments))
        composed_url, cert, key, ca = self._config(args)

        logging.debug("Request to " + composed_url)
        response = requests.get(composed_url, cert=(cert, key), verify=ca)
        if response.ok:
            data = response.json()
            logging.info("response: " + json.dumps(data))
            self.write({'response': data})
        else:
            logging.error("Error in fetching %s 's resources from %s" %(self.coe, composed_url))
            self.set_status(response.status_code)

    @cloud_auth(coe)
    @http_basic_auth
    def post(self, **args):
        logging.debug('Arguments:' + str(self.request.arguments))
        composed_url, cert, key, ca = self._config(args)
        cluster = args.get('cluster')

        app_type = self.get_argument('app_type', None)
        instance_name = self.get_argument('app_name', None)
        volume_type = self.get_argument('vol_type', None)
        if ((app_type == 'mysql' or app_type == 'postgres') and
            (volume_type == 'cinder' or volume_type == 'nfs') and
            instance_name):
            if volume_type == 'nfs':
                # status code 400 if type is nfs and server and path is not defined
                if (not self.get_argument('server_data',None) and
                    not self.get_argument('server_bin',None) and
                    not self.get_argument('path_data',None) and
                    not self.get_argument('path_bin',None)):

                    logging.error("For NFS you need to provide also the server and the path")
                    raise tornado.web.HTTPError(BAD_REQUEST)

            logging.info("Start to create the %s instance %s witg %s volumes"
                    %(app_type, instance_name, volume_type))
            depl, svc = self.app_config(app_type, instance_name, cluster, volume_type)
            logging.debug("depl %s & svc %s" %(depl, svc))
            with open(depl) as fd1, open(svc) as fd2 :
                depl_json = json.load(fd1)
                svc_json = json.load(fd2)
                specs = [svc_json, depl_json]
        else:
            try:
                specs = [json.loads(self.request.body)]
                logging.debug("Creation parameters: %s" %(specs))
            except ValueError:
                logging.error("No JSON object could be decoded from request body")
                logging.error("Or no app_type parameteres in the request body")
                raise tornado.web.HTTPError(BAD_REQUEST)

        #resource = args.get('resource')
        #subresource = args.get('subresource')
        #if specs['kind'] != resource and specs['kind'] != subresource:
        #    logging.warning("Ensure that your request 'kind:%s' is for this endpoint" %(specs['kind']))

        if len(specs) > 1:
            temp = composed_url
            service_args = self.get_resource_args(cluster, 'services', False)
            composed_url, _,_,_ = self._config(service_args)

        for spec in specs:
            logging.debug("Request to post" + composed_url)
            logging.debug("Data to be posted: %s" %(spec))
            response = requests.post(composed_url,
                                     json=spec,
                                     cert=(cert, key),
                                     verify=ca,
                                     headers=self.headers)
            if response.ok:
                data = response.json()
                logging.info("response: " + json.dumps(data))
                self.api_response['response'].append({spec['kind']: data})
            elif response.status_code == 409:
                logging.warning("The name %s in the endpoint %s already exists"
                        %(spec['metadata']['name'],composed_url))
                self.set_status(CONFLICT)
            else:
                logging.error("Error in posting %s 's resources from %s" %(self.coe, composed_url))
                self.set_status(response.status_code)
            if len(specs) > 1:
                composed_url = temp
        self.write(self.api_response)

    @cloud_auth(coe)
    @http_basic_auth
    def delete(self, **args):
        logging.debug('Arguments:' + str(self.request.arguments))
        composed_url, cert, key, ca = self._config(args)
        logging.debug("The url to act upon is: " + composed_url)
        instance_name = args.get('subname')
        if not instance_name:
            if not args.get('subresource'):
                instance_name = args.get('name')
            else:
                logging.error("You have to define the instance name to be deleted in the url")
                raise tornado.web.HTTPError(BAD_REQUEST)

        cluster = args.get('cluster')
        logging.debug("Request to delete " + instance_name)
        app_type = self.get_argument('app_type', None)
        #instance_name = self.get_argument('app_name')
        delete_volumes = self.get_argument('delete_volumes', False)
        delete_service = self.get_argument('delete_service', False)
        force = self.get_argument('force', False)

        if not instance_name or (app_type and app_type != 'mysql' and app_type != 'postgres'):
            logging.error("You have to define the app type and the instance name")
            raise tornado.web.HTTPError(BAD_REQUEST)

        if app_type:
            apps_dir = config.get('containers-provider', 'apps_dir')
            app_conf_dir = apps_dir + '/' + app_type
            instance_dir = app_conf_dir + '/' + instance_name.upper()

        # delete_urls: (url, use_cert=Boolean, method)
        if args.get('subresource') == 'deployments' and app_type:
            deleteit = composed_url + '-depl'
        else:
            deleteit = composed_url
        delete_urls = [(deleteit, True, 'delete')]

        if delete_service:
            service_args = self.get_resource_args(cluster, 'services', False)
            service_url, _,_,_ = self._config(service_args)
            delete_urls.append((service_url + '/' + instance_name + '-svc', True, 'delete'))

        if delete_volumes:
            # Secrets
            secrets_args = self.get_resource_args(cluster, 'secrets', False)
            secrets_url, _,_,_ = self._config(secrets_args)

            #secret_url = composed_url[:changeurl_index+1] + \
            #        '/api/v1/namespaces/default/secrets/' + \
            #        instance_name + '-secret-mysql.cnf'
            conf_name = self.app_specifics[app_type]['conf_name']
            init_name = self.app_specifics[app_type]['init_name']
            delete_urls.append((secrets_url + '/' + instance_name + '-secret-' + conf_name,
                                True, 'delete'))

            delete_urls.append((secrets_url + '/' + instance_name + '-secret-' + init_name,
                                True, 'delete'))

            # Cinder
            # If there is a volume name with the instance name it will be deleted
            project_id, project_name = self.get_project_info()
            volume_url = config.get(self.cloud, 'volume_url')
            volume_project_url = volume_url + '/' + project_id + '/volumes'
            body = '{"os-detach":{}\n}'

            voldata_name = instance_name + '-vol-data'
            volbin_name = instance_name + '-vol-bin'

            len_delete_urls = len(delete_urls)
            data, _ = get_function(volume_project_url, headers=self.headers)
            for vol in data['volumes']:
                if vol['name'] == voldata_name or vol['name'] == volbin_name:
                    url_detach = volume_project_url + '/' + vol['id'] + '/action'
                    delete_urls.append((url_detach, False, 'post'))
                    url_delete = volume_project_url + '/' + vol['id']
                    delete_urls.append((url_delete, False, 'delete'))

            if (len(delete_urls) - len_delete_urls) > 4:
                logging.error("There is a volume name conflict or \
                        previous volumes have not been deleted successfully for %s"
                        %(instance_name))
                raise tornado.web.HTTPError(SERVICE_UNAVAILABLE)

        # Delete if necessary replicasets and remaining non terminating pods
        if force:
            logging.debug("Looking for replicasets and pods leftovers")
            rs_args = self.get_resource_args(cluster, 'replicasets', True)
            rs_url, _,_,_ = self._config(rs_args)
            pods_args = self.get_resource_args(cluster, 'pods', False)
            pods_url, _,_,_ = self._config(pods_args)
            data, _ = get_function(rs_url, cert=cert, key=key, ca=ca)
            if data.get('items'):
                delete_urls.extend([(rs_url + '/' + item['metadata']['name'], True, 'delete')
                                    for item in data['items']
                                     if instance_name in item['metadata']['name']
                                  ])
            data, _ = get_function(pods_url, cert=cert, key=key, ca=ca)
            if data.get('items'):
                delete_urls.extend([(pods_url + '/' + item['metadata']['name'], True, 'delete')
                                    for item in data['items']
                                    if (instance_name in item['metadata']['name'] and
                                        (item['status']['phase'] == 'Running' or 
                                        item['status']['phase'] == 'Pending'))
                                   ])

        logging.debug("URLs to be accessed for deletion: " + str(delete_urls))
        # Delete using the urls from delete_urls
        for url in delete_urls:
            logging.debug("Request to %s %s" %(url[2], url[0]))
            if url[2] == 'post':
                response = requests.post(url[0],
                                         data=body,
                                         headers=self.headers)
                print response.status_code
            if url[1] and url[2] == 'delete':
                response = requests.delete(url[0],
                                           cert=(cert, key),
                                           verify=ca)
            else:
                response = requests.delete(url[0],
                                           headers=self.headers)
            if response.ok or response.status_code == 202:
                #data = response.json()
                #logging.info("response: " + json.dumps(data))
                #self.api_response['response'].append(data)
                logging.info("The resource %s has been %sed successfully" %(url[0],url[2]))
                self.set_status(response.status_code)
            elif response.status_code == 404:
                logging.warning("The resource %s cannot be found" %(url[0]))
                self.set_status(NOT_FOUND)
            else:
                logging.error("Error in deleting %s 's resources from %s" %(self.coe, url[0]))
                self.set_status(response.status_code)
            #self.write(self.api_response)

        if app_type:
            try:
                rename(instance_dir, instance_dir + '.old')
            except OSError as e:
                # e.errno: 39 Directory not empty
                if e.errno == 39:
                    logging.warning("%s dir cannot be renamed because %s.old already exists" %(instance_name,instance_name))
                    logging.warning("You shoud delete manually %s" %(instance_dir))
                    self.set_status(ACCEPTED)
                else:
                    logging.error("The directory %s is not registered for %s" %(instance_dir, instance_name))
                    logging.error("Return code: %s" %(e))
                    self.set_status(NOT_FOUND)

    def _config(self, args):
        cluster_name = args.get('cluster')
        resource = args.get('resource')
        ident = args.get('name')
        subresource = args.get('subresource')
        subname = args.get('subname')
        isBeta = args.get('beta',True)
        cluster_certs_dir = config.get(self.cloud, 'cluster_certs_dir') + '/' + cluster_name

        if not self.kubeApi:
            self.kubeApi = self._api_master(cluster_name)
        if self.request.uri.split('/')[3] == 'beta' and isBeta:
            apiVersion = 'apis/extensions/v1beta1'
        else:
            apiVersion = 'api/v1'
        #kubeApi = kubeList[0]
        composed_url = self.kubeApi + '/' + apiVersion
        if resource:
            composed_url = composed_url + '/' + resource
            if ident:
                composed_url = composed_url + '/' + ident
                if subresource:
                    composed_url = composed_url + '/' + subresource
                    if subname:
                        composed_url = composed_url + '/' + subname
        cert = cluster_certs_dir + '/cert.pem'
        key = cluster_certs_dir + '/key.pem'
        ca = cluster_certs_dir + '/ca.pem'
        return composed_url, cert, key, ca

    @cloud_auth(cloud)
    def _api_master(self, cluster_name, **args):
        token_header = 'X-Subject-Token'
        auth_header = 'X-Auth-Token'

        if auth_header not in self.headers.keys():
            xtoken = {auth_header: args.get(token_header)}
            self.headers.update(xtoken)

        url = config.get(self.cloud, 'cluster_url')
        composed_url = url + '/' + 'clusters' + '/' + cluster_name
        data, status_code = get_function(composed_url, headers=self.headers)
        if status_code == 200:
            kubeApi = data['api_address']
            logging.debug("Kubernetes master(s) api: " + str(kubeApi))
            return kubeApi
        else:
            logging.error("Error fetching cloud's resources in this endpoint: " + composed_url)
            raise tornado.web.HTTPError(status_code)

    def app_config(self, app_type, instance_name, cluster_name, volume_type):
        # TODO try to initiate mysql through a bash file for consistency
        instance_port = self.app_specifics[app_type]['port']
        conf_name = self.app_specifics[app_type]['conf_name']

        apps_dir = config.get('containers-provider', 'apps_dir')
        app_conf_dir = apps_dir + '/' + app_type
        templates_dir = app_conf_dir + '/templates'

	logging.info("Create new '%s' in cluster '%s'" %(app_type, cluster_name))
        if path.isdir(app_conf_dir) and path.isdir(templates_dir):
            confFiles = set(listdir(app_conf_dir))
            templateFiles = set(listdir(templates_dir))
            conf_required = set(['init.sql', 'templates'])
            template_required = set([app_type + '-cnf.template', app_type + '-depl.json.template',
                                     app_type + '-secret.json.template', app_type + '-secret.yaml.template',
                                     app_type + '-svc.json.template'])
            if conf_required > confFiles or template_required > templateFiles:
                logging.error("Not all conf files of %s were found in %s" %(app_type, app_conf_dir))
                raise tornado.web.HTTPError(SERVICE_UNAVAILABLE)
        else:
            logging.error("The %s dir '%s' and its templates do not exist" %(app_type, app_conf_dir))
            raise tornado.web.HTTPError(BAD_REQUEST)

        logging.info("Creating %s configuration files from '%s' templates" %(instance_name, app_type))
        instance_dir = app_conf_dir + '/' + instance_name.upper()

        if not path.isdir(instance_dir):
            try:
                mkdir(instance_dir)
                logging.debug("The instance conf dir has created: %s" %(instance_dir))
            except OSError, e:
                logging.error("Error while creating %s directory %s" %(instance_dir,e))
                logging.error("Return code: %s" %(e.returncode))
                raise tornado.web.HTTPError(SERVICE_UNAVAILABLE)
        #else:
        #    logging.error("Directory already exists check if there is an instance \
        #                   with the same name or if it's not deleted completely")

        loader = FileSystemLoader(templates_dir)
        templates = Environment(loader=loader)
        configuration = {'app_type': app_type,
                         'instance_name': instance_name,
                         'instance_port': instance_port
                        }

	filename = instance_dir + '/' + conf_name
        conf = templates.get_template(app_type + '-cnf.template').render(configuration)
        self._write(conf, filename)
	logging.debug("%s %s conf file is ready" %(filename, app_type))

        volume_data = None
        volume_bin = None
        volume_data, volume_bin = self.cloud_volume_creation(app_conf_dir, app_type, instance_name, templates, cluster_name, volume_type)

        configuration.update(self.get_volume_config(volume_type, volume_data, volume_bin))

	filename = instance_dir + '/' + 'depl.json'
        controller_json = templates.get_template(app_type + '-depl.json.template').render(configuration)
        self._write(controller_json, filename)
	logging.debug("%s controller conf file is ready" %(filename))
        returnBack = [filename]

        filename = instance_dir + '/' + 'svc.json'
        service_json = templates.get_template(app_type + '-svc.json.template').render(configuration)
        self._write(service_json, filename)
	logging.debug("%s service conf file is ready" %(filename))
        returnBack.append(filename)

        return returnBack


    def cloud_volume_creation(self, app_conf_dir, app_type, instance_name, templates, cluster_name, volume_type):
        # TODO separate secrets with cinder volumes
        conf_name = self.app_specifics[app_type]['conf_name']
        init_name = self.app_specifics[app_type]['init_name']

        conf_file = app_conf_dir + '/' + instance_name.upper() + '/' + conf_name
        instance_dir = app_conf_dir + '/' + instance_name.upper()
        init_file = app_conf_dir + '/' + init_name
        volume_url = config.get(self.cloud, 'volume_url')
        auth_id_url = config.get(self.cloud, 'auth_id_url')
	logging.info("Create volumes for '%s' instance '%s'" %(app_type, instance_name))

        project_id, project_name = self.get_project_info()

        secrets_args = self.get_resource_args(cluster_name, 'secrets', False)
        secret_url, cert, key, ca = self._config(secrets_args)
        volume_project_url = volume_url + '/' + project_id + '/volumes'

        exists_cnf = self.check_ifexists(instance_name+'-secret-' + app_type + '.cnf',
                                         secret_url, cert=cert, key=key, ca=ca)
        exists_init = self.check_ifexists(instance_name+'-secret-init.sql',
                                          secret_url, cert=cert, key=key, ca=ca)
        if not exists_cnf and not exists_init:
            # Secrets
            logging.info("Volumes will be created for project: %s" %(project_name))

            secret64 = ''
            with open(conf_file) as conf:
                secret64 = b64encode(conf.read())
            configuration = {'secret64': secret64,
                             'filename': conf_name,
                             'instance_name': instance_name
                            }
            kube_filename = instance_dir + '/' + 'secretconf.json'
            conf_template = app_type + '-secret.json.template'
            secretconf = templates.get_template(conf_template).render(configuration)
            self._write(secretconf, kube_filename)
            _ = self.postjson(secret_url, ('metadata', 'selfLink'), 'Secretconf',
                          filename=kube_filename,
                          cert=cert,
                          key=key,
                          ca=ca)
            logging.debug("%s conf file for secret volume has been created" %(kube_filename))

            secret64 = ''
            with open(init_file) as conf:
                secret64 = b64encode(conf.read())
            configuration = {'secret64': secret64,
                             'filename': init_name,
                             'instance_name': instance_name
                            }
            kube_filename = app_conf_dir + '/' + 'secretinit.json'
            secretconf = templates.get_template(conf_template).render(configuration)
            self._write(secretconf, kube_filename)
            _ = self.postjson(secret_url, ('metadata', 'selfLink'), 'Secretinit',
                              filename=kube_filename,
                              cert=cert,
                              key=key,
                              ca=ca)
            logging.debug("%s conf file for secret volume has been created" %(kube_filename))
            secret64 = ''
        else:
            logging.warning("Secret volume %s exists: %s and %s exists: %s"
                            %(instance_name+'-secret-' + app_type + '.cnf',
                              exists_cnf,
                              instance_name+'-secret-init.sql',
                              exists_init)
                           )

        if volume_type == 'nfs':
            return None, None

        # Continue if volume_type is cinder
        logging.debug("Check the %s if there are volume leftovers with the same name" %(volume_project_url))
        data, _ = get_function(volume_project_url, headers=self.headers)
        exist_volume = [instance_name+'-vol-data' in vol['name'] or instance_name+'-vol-bin' in vol['name']
                        for vol in data['volumes']]

        if exist_volume.count(True) == 0:
            # Cinder volumes
            volconf={
                      "volume": {
                        #"availability_zone": null,
                        #"source_volid": null,
                        #"multiattach ": false,
                        #"snapshot_id": null,
                        #"imageRef": null,
                        #"volume_type": null,
                        #"metadata": {},
                        #"source_replica": null,
                        #"consistencygroup_id": null,
                        "size": 1,
                        "name": instance_name + '-vol-data',
                        "description": instance_name + '-voldata'
                        }
                    }
            logging.debug("Volume conf: %s" %(volconf))
            voldata = self.postjson(volume_project_url, ('volume','id'), 'Voldata',
                                    jsondata=volconf)
            logging.debug("Volume data %s has been created" %(volconf['volume']['name']))

            volconf['volume']['name'] = instance_name + '-vol-bin'
            volconf['volume']['description'] = instance_name + '-volbin'
            volbin = self.postjson(volume_project_url, ('volume','id'), 'Volbin',
                                   jsondata=volconf)
            logging.debug("Volume data %s has been created" %(volconf['volume']['name']))
	    return voldata, volbin
        elif exist_volume.count(True) == 2:
            logging.info("Instance's volume names are found and will be reused")
            if 'vol_data' in data['volumes'][exist_volume.index(True)]['name']:
                voldata = data['volumes'][exist_volume.index(True)]['id']
                volbin = data['volumes'][exist_volume.index(True, exist.index(True)+1)]['id']
            else:
                volbin = data['volumes'][exist_volume.index(True)]['id']
                voldata = data['volumes'][exist_volume.index(True, exist_volume.index(True)+1)]['id']
            return voldata, volbin
        else:
                logging.error("Volume %s exists: %s and %s exists: %s"
                                %(instance_name+'_vol_data',
                                  instance_name+'_vol_data' in data['volumes'][0].values(),
                                  instance_name+'_vol_bin',
                                  instance_name+'_vol_bin' in data['volumes'][0].values())
                           )
                logging.error("There is a volume name conflict or \
                        previous volumes have not been deleted successfully for %s" %(instance_name))
                raise tornado.web.HTTPError(SERVICE_UNAVAILABLE)

    def get_project_info(self):
        auth_id_url = config.get(self.cloud, 'auth_id_url')
	project_url = auth_id_url + '/auth' + '/projects'
	logging.debug("Get project id from %s" %(project_url))
        data, status_code = get_function(project_url, headers=self.headers)
        if status_code == 200 and data:
            project_id = data['projects'][0]['id']
            project_name = data['projects'][0]['name']
            return project_id, project_name
        else:
            logging.error("Cannot access '%s' with status code %s" %(auth_id_url+'/auth'+'/projects', status_code))
            raise tornado.web.HTTPError(status_code)

    def get_resource_args(self,cluster_name, resource, isBeta):
        resource_args = {'cluster': cluster_name,
                        'resource': 'namespaces',
                        'name': 'default',
                        'subresource': resource,
                        'beta': isBeta
                       }
        return resource_args

    def get_volume_config(self, volume_type, voldata, volbin):
        if volume_type == 'nfs':
            return {'volume_type': volume_type,
                    'volume_ident': 'path',
                    'volume_ident_data': self.get_argument('path_data'),
                    'volume_ident_bin': self.get_argument('path_bin'),
                    'volume_attr': 'server',
                    'volume_attr_data': self.get_argument('server_data'),
                    'volume_attr_bin': self.get_argument('server_bin')
                   }
        elif volume_type == 'cinder':
            return {'volume_type': volume_type,
                    'volume_ident': 'volumeID',
                    'volume_ident_data': voldata,
                    'volume_ident_bin': volbin,
                    'volume_attr': 'fsType',
                    'volume_attr_data': 'ext4',
                    'volume_attr_bin': 'ext4'
                   }

    def postjson(self, composed_url, getBackfield, response_name,  **args):
	filename = args.get('filename')
	cert = args.get('cert')
	key = args.get('key')
	ca = args.get('ca')
	jsondata = args.get('jsondata')
	logging.debug("Loading to Kubernetes volume configurations")

	if filename:
	    logging.debug("Load %s" %(filename))
	    with open(filename) as fd:
		try:
		    jsonconf = json.load(fd)
		except:
		    logging.error("The file %s is not in json format" %(filename))
		    raise tornado.web.HTTPError(SERVICE_UNAVAILABLE)
	elif isinstance(jsondata, dict):
	    logging.debug("Load json %s" %(jsondata))
	    jsonconf = jsondata
	else:
	    jsonconf = None

	logging.debug("Post data to: %s" %(composed_url))

	if cert and key and ca:
	   response = requests.post(composed_url, cert=(cert, key), verify=ca, json=jsonconf)
	else:
           response = requests.post(composed_url, json=jsonconf, headers=self.headers)

        if response.ok:
           #data = response.json()
           data = response.json()[getBackfield[0]][getBackfield[1]]
           logging.info("Volume response: " + data)
           self.api_response['response'].append({response_name: data})
	   return data
        elif response.status_code == 409:
           logging.warning("The secret in %s already exists" %(composed_url))
           return 'Use the existing secret with the same name'
        else:
            logging.error("Error in posting %s 's resources from %s" %(self.coe, composed_url))
            raise tornado.web.HTTPError(response.status_code)

    def _write(self, template, path):
        with open(path, "wb") as output:
            output.write(template)

    def check_ifexists(self, name, url, **args):
        cert = args.get('cert')
        key = args.get('key')
        ca = args.get('ca')
        composed_url = url + '/' + name
        if cert and key and ca:
            response = requests.get(composed_url, cert=(cert, key), verify=ca)
        else:
            response = requests.get(composed_url, headers=self.headers)
        if response.ok:
            return True
        elif response.status_code == 404:
            return False
        else:
            logging.error("Error in checking %s 's endpoint from %s" %(self.coe, composed_url))
            raise tornado.web.HTTPError(response.status_code)


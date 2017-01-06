import boto.ec2
from boto.exception import EC2ResponseError
import xmltodict
import tempfile
from urllib.parse import urlparse

from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver

import logging
logging.getLogger('boto').setLevel(logging.ERROR)

from amon.apps.servers.models import cloud_server_model
from amon.apps.cloudservers.models import cloud_credentials_model


def sync_credentials(credentials=None):
    if credentials == None:
        return 

    provider_name = credentials.get('service')
    credentials_id = credentials.get('_id')


    if provider_name == 'vultr':
        result = sync_vultr(credentials=credentials)

    if provider_name == 'amazon':
        result = sync_amazon(credentials=credentials)

    if provider_name == 'linode':
        result = sync_linode(credentials=credentials)

    if provider_name == 'digitalocean':
        result = sync_digitalocean(credentials=credentials)

    if provider_name == 'google':
        result = sync_google(credentials=credentials)

    if provider_name == 'rackspace':
        result = sync_rackspace(credentials=credentials)
    

    cloud_credentials_model.unset_error(credentials_id=credentials_id)
    cloud_credentials_model.update_last_sync(credentials_id=credentials_id)

    error = result.get('error')
    instance_list = result.get('instances')


    # Everything is OK. Save these servers. 
    if error == False:
        cloud_server_model.save(instances=instance_list, credentials=credentials)
    else:
        cloud_credentials_model.update(data={'error': error}, id=credentials_id, provider_id=provider_name)
    




# Apache libcloud is not complete - doesn't get size / region
def sync_vultr(credentials=None):
    result = {
        'instances': [],
        'error': False
    }

    auth = get_driver(Provider.VULTR)

    api_key = credentials.get('api_key')
    driver = auth(api_key)

    try:
        nodes = driver.list_nodes()
    except Exception as e:
        result['error'] = str(e)
        nodes = None

    if nodes:
        for node in nodes:
            node_details = {
                'name': node.name,
                'instance_id': node.id,
                'public_ips': node.public_ips,
                'provider': 'vultr',
                'credentials_id': credentials['_id'],
                'credentials': credentials.get("name", "production"),
                'temp_tags': "vultr"
            }
            result['instances'].append(node_details)

    return result


def sync_linode(credentials=None):
    result = {
        'instances': [],
        'error': False
    }


    api_key = credentials.get('api_key')
    auth = get_driver(Provider.LINODE)

    driver = auth(api_key)

    try:
        nodes = driver.list_nodes()
    except Exception as e:
        result['error'] = str(e)
        nodes = None

    if nodes:
        for node in nodes:
            node_details = {
                'name': node.name,
                'instance_id': node.id,
                'public_ips': node.public_ips,
                'provider': "linode",
                'credentials_id': credentials['_id'],
                'credentials': credentials.get("name", "production"),
                'temp_tags': "linode"
            }
            result['instances'].append(node_details)

    return result


def sync_rackspace(credentials=None):
    result = {
        'instances': [],
        'error': False
    }

    username = credentials.get('username')
    api_key = credentials.get('api_key')
    regions = credentials.get('regions')
    regions = regions.split(",")

    auth = get_driver(Provider.RACKSPACE)


    for region in regions:
        driver = auth(username, api_key, region=region)

        try:
            nodes = driver.list_nodes()
        except Exception as e:
            result['error'] = str(e)
            nodes = None

        if nodes:
            for node in nodes:

                node_details = {
                    'name': node.name,
                    'instance_id': node.id,
                    'public_ips': node.public_ips,
                    'provider': "rackspace",
                    'credentials_id': credentials['_id'],
                    'credentials': credentials.get("name", "production"),
                    'temp_tags': "{0}".format(region)
                }
                result['instances'].append(node_details)

    return result



def sync_amazon(credentials=None):
    result = {
        'instances': [],
        'error': False
    }

    regions = credentials.get('regions', [])
    secret_key = credentials.get('secret_key')
    access_key = credentials.get('access_key')
    regions = regions.split(",")

    for region in regions:
        conn = boto.ec2.connect_to_region(region,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key)

        if conn:
            try:
                instances_for_region = conn.get_all_instances()
            except EC2ResponseError as e:
                error_dict = xmltodict.parse(e[2])
                try:
                    result['error'] =  error_dict['Response']['Errors']['Error']['Message']
                except:
                    result['error'] = "AWS error"



                instances_for_region = None


            if instances_for_region:
                instances = [i for r in instances_for_region for i in r.instances]

                for inst in instances:
                    name_tag = inst.tags.get('Name', '')
                    name = name_tag if len(name_tag) > 0 else inst.id

                    instance_dict = {
                        "instance_id": inst.id,
                        "state": inst.state,
                        "name": name,
                        "region": inst.region.name,
                        "type": inst.instance_type,
                        "architecture": inst.architecture,
                        "ip_address": inst.ip_address,
                        "provider": "amazon",
                        "pem_key": inst.key_name,
                        'credentials_id': credentials['_id'],
                        'credentials': credentials.get("name", "production"),
                        "tags": dict(inst.tags)     # Convert to dict, else is a Boto tag list
                    }

                    if inst.state != 'terminated':
                        result['instances'].append(instance_dict)

    return result



def sync_digitalocean(credentials=None):
    result = {
        'instances': [],
        'error': False
    }
    token = credentials.get('token')

    auth = get_driver(Provider.DIGITAL_OCEAN)
    driver = auth(token)

    try:
        nodes = driver.list_nodes()
    except Exception as e:
        result['error'] = str(e)
        nodes = None

    if nodes:
        for node in nodes:
            node_details = {
                'name': node.name,
                'instance_id': node.id,
                'public_ips': node.public_ips,
                'provider': "digitalocean",
                'credentials_id': credentials['_id'],
                'credentials': credentials.get("name", "production"),
                'region': node.extra.get("region", {}).get('slug'),
                'size': node.extra.get('size_slug')
            }

            result['instances'].append(node_details)


    return result


def sync_google(credentials=None):
    result = {
        'instances': [],
        'error': False
    }

    client_id = credentials.get('email')
    project_id = credentials.get('project_id')
    pem_file = credentials.get('file')

    auth = get_driver(Provider.GCE)
    driver = None
    with tempfile.NamedTemporaryFile() as temp:
        temp.write(pem_file.read())
        temp.flush()
        try:
            driver = auth(client_id, temp.name, project=project_id, auth_type='SA')
        except Exception as e:
            result['error'] = str(e)

    nodes = None
    if driver:
        try:
            nodes = driver.list_nodes()
        except Exception as e:
            result['error'] = str(e)

    if nodes:
        for node in nodes:

            try:
                machine_type = node.extra.get('machineType')
                machine_type_url = urlparse(machine_type)
                machine_type_url_list = machine_type_url.path.split('/')
                type = machine_type_url_list[-1]
            except:
                type = ''


            node_details = {
                'name': node.name,
                'instance_id': node.id,
                'public_ips': node.public_ips,
                'provider': "google",
                'credentials_id': credentials['_id'],
                'credentials': credentials.get("name", "production"),
                'zone': node.extra.get('zone', {}).name,
                'type': type
            }
            result['instances'].append(node_details)


    return result

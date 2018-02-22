from amon.apps.core.basemodel import BaseModel
from amon.utils import generate_random_string

from amon.utils.haiku import generate_haiku_name

from amon.apps.processes.models import process_model
from amon.apps.devices.models import interfaces_model, volumes_model
from amon.apps.tags.models import tags_model, tag_groups_model
from amon.utils.dates import unix_utc_now


class ServerModel(BaseModel):

    def __init__(self):
        super(ServerModel, self).__init__()
        self.collection = self.mongo.get_collection('servers')
        self.data_collection = self.mongo.get_collection('system_data')


    def server_exists(self, name):
        result = self.collection.find({"name": name}).count()

        return result


    def get_or_create_by_machine_id(
            self,
            machine_id=None,
            hostname=None,
            check_every=60,
            keep_data=30,
            instance_id=None,
            tags=[]):

        server = self.collection.find_one({"key": machine_id})  # Randomly generated

        instance_id = "" if instance_id == None else instance_id
        name = hostname if hostname else generate_haiku_name()

        # keep_data - in days
        # check_every - in seconds
        # settings/forms/data retention
        data = {
            "name": name,
            "key": machine_id,
            "check_every": check_every,
            "keep_data": keep_data,
            "date_created": unix_utc_now(),
            "tags": tags
        }

        # Bare metal servers
        if server == None and len(instance_id) == 0:
            self.collection.insert(data)
            server = self.collection.find_one({"key": machine_id})

        # Cloud servers
        if len(instance_id) > 0:
            server = self.collection.find_one({"instance_id": instance_id})

            # Cloud server synced and found
            if server is not None:
                data = {"key": machine_id}
                self.collection.update({"instance_id": instance_id}, {"$set": data}, upsert=True)
            else:
                data["key"] = machine_id
                data["instance_id"] = instance_id

                self.collection.insert(data)
                server = self.collection.find_one({"key": machine_id})

        self.collection.ensure_index([('name', self.desc)], background=True)
        self.collection.ensure_index([('tags', self.desc)], background=True)
        self.collection.ensure_index([('key', self.desc)], background=True)
        self.collection.ensure_index([('last_check', self.desc)], background=True)
        self.collection.ensure_index([('account_id', self.desc)], background=True)
        self.collection.ensure_index([('instance_id', self.desc)], background=True)

        return server

    def get_by_ids(self, id_list=None):
        result = []
        _ids = [self.object_id(x) for x in id_list]

        query = self.collection.find({'_id': {"$in": _ids}})
        for r in query:
            result.append(r)  # Expects list

        return result

    # Tags is a list
    def get_with_tags(self, tags=None):
        result = []
        tags = [self.object_id(x) for x in tags]

        query = self.collection.find({'tags': {"$in": tags}})
        for r in query:
            result.append(r)  # Expects list

        return result


    def get_tags(self, server=None):
        result = []
        tags = server.get('tags', None)
        if tags:
            result = [tags_model.get_by_id(x) for x in tags]
            result = list(filter(lambda x: x is not None, result))  # Remove non existing tags

        return result


    def add(self, name, account_id=None, check_every=60, keep_data=30, tags=[], key=None):
        server_key = key if key else generate_random_string(size=32)

        # keep_data - in days
        # check_every - in seconds
        # settings/forms/data retention
        data = {"name": name,
             "key": server_key,
              "account_id": account_id,
              "check_every": check_every,
              "keep_data": keep_data,
              "date_created": unix_utc_now(),
              "tags": tags}

        self.collection.insert(data)

        self.collection.ensure_index([('tags', self.desc)], background=True)
        self.collection.ensure_index([('key', self.desc)], background=True)
        self.collection.ensure_index([('name', self.desc)], background=True)
        self.collection.ensure_index([('last_check', self.desc)], background=True)
        self.collection.ensure_index([('account_id', self.desc)], background=True)
        self.collection.ensure_index([('instance_id', self.desc)], background=True)

        return server_key


    # TODO
    # Refactor this method to avoid confusion
    def get_active_last_five_minutes(self, account_id=None, count=None):
        five_minutes_ago = unix_utc_now() - 300
        params = {"last_check": {"$gte": five_minutes_ago}}

        if account_id:
            params['account_id'] = account_id

        result = self.collection.find(params)

        if count:
            result = result.count()

        return result

    def get_all_ids(self):

        id_list = []
        result = self.collection.find()

        if result.clone().count() > 0:
            for r in result:
                _id = str(r.get("_id"))
                id_list.append(_id)


        return id_list

    def get_all(self, account_id=None):
        server_list = []

        count = self.collection.find().count()

        if count == 0:
            return None
        else:
            result = self.collection.find(sort=[("name", self.asc), ("last_check", self.asc)])

            for server in result:
                server['tags'] = self.get_tags(server=server)
                server_list.append(server)


        return server_list

    def get_servers_count(self, account_id):
        if account_id:
            count = self.collection.find().count()

            return count
        else:
            return 0

    def get_server_by_key(self, key):
        params = {'key': key}

        return self.collection.find_one(params)

    def delete_data(self, server_id=None, soft=None):
        server_id = self.object_id(server_id)
        params = {'server_id': server_id}


        process_params = {'server': server_id}
        processes = self.mongo.get_collection('processes')
        processes.remove(process_params)

        volumes = self.mongo.get_collection('volumes')
        volumes.remove(params)

        interfaces = self.mongo.get_collection('interfaces')
        interfaces.remove(params)


        plugins_col = self.mongo.get_collection('plugins')
        plugin_gauges_col = self.mongo.get_collection('plugin_gauges')
        plugins_for_server = plugins_col.find(params)

        for p in plugins_for_server:
            plugin_gauges_col.remove({'plugin_id': p['_id']})

        # Soft delete - deletes process names, plugin names, network and disk volumes. 
        # Leaves the data which already has TTL and will be automatically deleted according to the 'Keep data' option
        if soft == False:
            process_data_collection = process_model.data_collection
            process_data_collection.remove(params)

            system_data_collection = self.data_collection
            system_data_collection.remove(params)


            volume_data_collection = volumes_model.get_data_collection()
            volume_data_collection.remove(params)

            interface_data_collection = interfaces_model.get_data_collection()
            interface_data_collection.remove(params)


    
    def delete(self, id, soft=None):
        server_id = self.object_id(id)

        if server_id:

            # Enforce default delete mode
            if soft == None:
                server = self.get_by_id(server_id)
                keep_data = server.get('keep_data', 3600)
                soft = True if keep_data < 3600 else False # Delete only data kept forever

            self.delete_data(server_id=server_id, soft=soft)
            self.collection.remove(server_id)



    def cleanup(self, server, date_before=None):
        process_data_collection = process_model.data_collection
        params = {"t": {"$lte": date_before}, 'server_id': server['_id']}
        process_data_collection.remove(params)

        system_params = {"time": {"$lte": date_before}}
        system_data_collection = self.data_collection
        system_data_collection.remove(system_params)

        volume_data_collection = volumes_model.get_data_collection()
        volume_data_collection.remove(params)

        interfaces_data_collection = interfaces_model.get_data_collection()
        interfaces_data_collection.remove(params)


class CloudServerModel(BaseModel):

    def __init__(self):
        super(CloudServerModel, self).__init__()
        self.collection = self.mongo.get_collection('servers')


    def delete_servers_for_credentials(self, credentials_id=None):
        params = {'credentials_id': credentials_id}

        result = self.collection.find(params)

        for r in result:
            server_model.delete(r['_id'])

        self.collection.remove(params)


    def update_server(self, data=None, account_id=None):
        instance_id = data['instance_id']

        result = self.collection.find_one({"instance_id": instance_id})

        if result == None:
            data['key'] = generate_random_string(size=32)
            data['account_id'] = account_id

        self.collection.update({"instance_id": instance_id}, {"$set": data}, upsert=True)

    def delete_all_for_provider(self, credentials_id=None):
        params = {'credentials_id': credentials_id}

        return self.collection.remove(params)

    def get_all_for_provider(self, credentials_id=None):
        params = {'credentials_id': credentials_id}

        return self.collection.find(params)


    def get_instance_ids_list(self, credentials_id=None, account_id=None):

        instance_list = []
        all_servers_for_provider = self.get_all_for_provider(credentials_id=credentials_id)

        if all_servers_for_provider.clone().count() > 0:
            for s in all_servers_for_provider:
                instance_id = s.get("instance_id")
                if instance_id:
                    instance_list.append(instance_id)

        return instance_list


    def diff_instance_ids(self, new_instances=None, old_instances=None):
        # This method should return a list with all the instances that have to be removed
        return list(set(old_instances) - set(new_instances))


    def delete_instances(self, instance_ids_list=None):

        if len(instance_ids_list) > 0:
            for i in instance_ids_list:
                server = self.collection.find_one({"instance_id": i})
                server_model.delete(server['_id'])

    def save(self, instances=None, credentials=None):
        credentials_id = credentials.get('_id')
        old_instances = self.get_instance_ids_list(credentials_id=credentials_id)

        if len(instances) > 0:
            new_instances = [i['instance_id'] for i in instances]
            instance_diff = self.diff_instance_ids(new_instances=new_instances, old_instances=old_instances)
            self.delete_instances(instance_ids_list=instance_diff)

            for instance in instances:
                synced_tags = instance.get('tags')

                # Reset the tags
                instance['tags'] = []

                # Amazon tags example: {u'application': u'rails', u'type': u'dbserver'}
                if type(synced_tags) is dict:
                    for group, tag in synced_tags.items():
                        group_id = tag_groups_model.get_or_create_by_name(group)
                        _id = tags_model.get_or_create(name=tag, group_id=group_id)
                        instance['tags'].append(_id)


                generated_tags_list = ['provider', 'type', 'region', 'zone', 'size', 'credentials']
                for auto_tag in generated_tags_list:
                    value = instance.get(auto_tag)
                    if value != None:
                        group_id = tag_groups_model.get_or_create_by_name(auto_tag)
                        _id = tags_model.get_or_create(name=value, group_id=group_id)
                        instance['tags'].append(_id)


                self.update_server(data=instance)
        else:
            # Empty list, clear out all instances for this provider
            self.delete_all_for_provider(credentials_id=credentials_id)


        self.collection.ensure_index('instance_id', background=True)
        self.collection.ensure_index('credentials_id', background=True)



server_model = ServerModel()
cloud_server_model = CloudServerModel()

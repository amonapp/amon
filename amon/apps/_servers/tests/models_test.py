import unittest
from time import time
from nose.tools import eq_
from amon.apps.servers.models import (
    ServerModel,
    cloud_server_model
)

from amon.apps.devices.models import interfaces_model, volumes_model
from amon.apps.processes.models import process_model
from amon.apps.system.models import system_model
from amon.apps.tags.models import tags_model, tag_groups_model
from amon.apps.cloudservers.models import cloud_credentials_model

now = int(time())
minute_ago = (now-60)
two_minutes_ago = (now-120)
five_minutes_ago = (now-300)


class ServerModelTest(unittest.TestCase):

    def setUp(self):
        self.model = ServerModel()
        self.collection = self.model.mongo.get_collection('servers')


    def _cleanup(self):
        self.collection.remove()
        tags_model.collection.remove()
        tag_groups_model.collection.remove()


    def get_or_create_by_machine_id_test(self):
        self._cleanup()
        self.collection.insert({"name" : "cloud-server", "key": "somekeyhere", "instance_id": "150"})
        self.model.get_or_create_by_machine_id(instance_id="150", machine_id="cloudkey")

        result = self.collection.find_one()

        
        assert result["key"] == "cloudkey"
        assert result["name"] == "cloud-server"

        self._cleanup()
        self.collection.insert({"name" : "test", "key": "somekeyhere", "instance_id": ""})
        
        self.model.get_or_create_by_machine_id(instance_id="", machine_id="somekeyhere")

        result = self.collection.find_one()
        assert result["key"] == "somekeyhere"
        assert result["name"] == "test"


        self._cleanup()        


    def get_all_with_tags_test(self):
        self._cleanup()

        tags = {'rds': 'value', 'ebs': 'volume'}
        tags_list = tags_model.create_and_return_ids(tags)

        self.collection.insert({"name" : "test", "tags": tags_list})
    
        result = self.model.get_with_tags(tags=[tags_list[0]])

        assert len(result) == 1

        result = self.model.get_with_tags(tags=tags_list)

        assert len(result) == 1

        self._cleanup()

        tags = {'rds': 'value', 'ebs': 'volume', 'region': 'uswest-1', 'provider': 'amazon'}
        tags_list = tags_model.create_and_return_ids(tags)

        self.collection.insert({"name" : "test", "tags": tags_list})


        result = self.model.get_with_tags(tags=[tags_list[0], tags_list[1], tags_list[2]])

        assert len(result) == 1

        result = self.model.get_with_tags(tags=tags_list)

        assert len(result) == 1
    

    def check_server_exists_test(self):
        self.collection.remove()
        self.collection.insert({"name" : "test"})

        result = self.model.server_exists('test')
        eq_(result, 1)

        self.collection.remove()


    def update_server_test(self):
        self.collection.remove()
        self.collection.insert({"name" : "test"})
        server = self.collection.find_one()

        self.model.update({"name": "test_updated", "default": 1 }, server['_id'])

        result = self.collection.find_one()
        eq_(result['name'],'test_updated')

        self.collection.remove()


    def add_server_test(self):
        self.collection.remove()

        self.model.add('test')

        result = self.collection.find_one()
        eq_(result['name'],'test')
        if result['key']:
            assert True

        self.collection.remove()

    
    def get_server_test(self):
        self.collection.remove()
        self.collection.insert({"name" : "test"})
        server = self.collection.find_one()

        result = self.model.get_by_id(server['_id'])
        eq_(result['name'],'test')
        eq_(result['_id'],server['_id'])

        self.collection.remove()


    

    def get_active_last_five_minutes_test(self):
        self.collection.remove()
        

        for i in range(0, 100):
            self.collection.insert({"name" : "test", 'last_check': now-i})

        result = self.model.get_active_last_five_minutes(count=True)

        eq_(result, 100)

        self.collection.remove()

        for i in range(0, 100):
            self.collection.insert({"name" : "test", 'last_check': five_minutes_ago-i})

        result = self.model.get_active_last_five_minutes(count=True)
        eq_(result, 0)


    def get_server_by_key_test(self):
        self.collection.remove()
        self.collection.insert({"name" : "test", "key": "test_me"})
        server = self.collection.find_one()

        result = self.model.get_server_by_key('test_me')
        eq_(result['name'],'test')
        eq_(result['key'],'test_me')
        eq_(result['_id'],server['_id'])

        self.collection.remove()


    def delete_server_test(self):
        self.collection.remove()
        self.collection.insert({"name" : "test", "key": "test_me"})
        server = self.collection.find_one()

        self.model.delete(server['_id'])

        result = self.collection.count()
        eq_(result,0)

        self.collection.remove()


    def get_all_servers_test(self):
        self.collection.remove()
        for i in range(0, 1000):
            name = "test-{0}".format(i)
            key = "testkey-{0}".format(i)
            self.collection.insert({"name" : name, "key": key, "last_check": minute_ago})

        result = self.model.get_all()
        eq_(len(result), 1000)

        self.collection.remove()



    


    def cleanup_test(self):
        self.collection.remove()
        self.collection.insert({"name" : "testserver", "key": "test_me"})

        
        server = self.collection.find_one()
        date_before = 100

        process_collection = process_model.data_collection
        process_collection.remove()

        system_collection = system_model.data_collection
        system_collection.remove()

        interface_collection = interfaces_model.get_data_collection()
        interface_collection.remove()

        volume_collection = volumes_model.get_data_collection()
        volume_collection.remove()
        
        for i in range(0, date_before):
            process_collection.insert({'i' : 'test', 't': i, 'server_id': server['_id']})
            system_collection.insert({'i' : 'test', 'time': i, 'server_id': server['_id']})
            interface_collection.insert({'i' : 'test', 't': i, 'server_id': server['_id']})
            volume_collection.insert({'i' : 'test', 't': i, 'server_id': server['_id']})


        params = {'server_id': server['_id']}
        self.model.cleanup(server, date_before=date_before)

        process_entries = process_collection.find(params).count()
        eq_(process_entries, 0)

        system_entries = system_collection.find(params).count()
        eq_(system_entries, 0)

        interface_entries = interface_collection.find(params).count()
        eq_(interface_entries, 0)

        volume_entries = volume_collection.find(params).count()
        eq_(volume_entries, 0)

        system_collection.remove()
        process_collection.remove()
        interface_collection.remove()
        volume_collection.remove()


        entries = interface_collection.find().count()
        eq_(entries, 0)

        for i in range(0, 300):
            process_collection.insert({'i' : 'test', 't': i, 'server_id': server['_id']})
            system_collection.insert({'i' : 'test', 'time': i, 'server_id': server['_id']})
                
            interface_collection.insert({'i' : 'test', 't': i, 'server_id': server['_id']})
            volume_collection.insert({'i' : 'test', 't': i, 'server_id': server['_id']})



        process_collection.ensure_index('server_id', background=True)
        process_collection.ensure_index('t', background=True)
        system_collection.ensure_index('time', background=True)
        system_collection.ensure_index('server_id', background=True)
        interface_collection.ensure_index('t', background=True)
        interface_collection.ensure_index('server_id', background=True)
        volume_collection.ensure_index('t', background=True)
        volume_collection.ensure_index('server_id', background=True)

        self.model.cleanup(server, date_before=date_before)

        process_entries = process_collection.find(params).count()
        eq_(process_entries, 199)

        for p in process_collection.find(sort=[('t', self.model.asc)]):
            assert p['t'] > date_before
            
        
        system_entries = system_collection.find(params).count()
        eq_(system_entries, 199)

        for p in system_collection.find(sort=[('time', self.model.asc)]):
            assert p['time'] > date_before
        

        entries = interface_collection.find(params).count()
        eq_(entries, 199)

        for p in interface_collection.find(sort=[('t', self.model.asc)]):
            assert p['t'] > date_before
            
        entries = volume_collection.find(params).count()
        eq_(entries, 199)

        for p in volume_collection.find(sort=[('t', self.model.asc)]):
            assert p['t'] > date_before


        process_collection.drop()
        system_collection.drop()
        interface_collection.drop()
        volume_collection.drop()



class CloudServerModelTest(unittest.TestCase):

    def setUp(self):
        self.collection = cloud_server_model.mongo.get_collection('servers')

    def _cleanup(self):
        self.collection.remove()
        tags_model.collection.remove()
        cloud_credentials_model.collection.remove()


    def update_cloud_server_test(self):
        self._cleanup()

        s = self.collection


        s.remove()
        s.insert({"account_id": 1, "name" : "test", "key": "server_key_test", "instance_id": 2})

        result = s.find_one()
        eq_(result['instance_id'], 2)
        

        data = {'instance_id': 2, 'provider': 'amazon'}
        cloud_server_model.update_server(data)

        result = s.find_one()
        eq_(result['provider'], 'amazon')


        # Create new server if it does not exists
        self.collection.remove()

        data = {"name":"create_server", 'instance_id': 3}
        cloud_server_model.update_server(data, account_id=1)


        result = s.find_one()
        assert(result['key'])
        eq_(result['instance_id'], 3)
        eq_(result['account_id'], 1)
        
        self._cleanup()

    def delete_servers_for_credentials_test(self):
        self._cleanup()

        credentials_id = "test_credentials"
        
        
        self.collection.insert({"account_id": 1, "name" : "test", "key": "server_key_test", "credentials_id": credentials_id})
        server = self.collection.find_one()

        eq_(server['credentials_id'], 'test_credentials')
        cloud_server_model.delete_servers_for_credentials(credentials_id=credentials_id)
        

        result = self.collection.find().count()
        eq_(result, 0)

        self._cleanup()


    def delete_all_for_credentials_test(self):
        self._cleanup()

        
        data = {'name': 'test', 'token': 'test-token'}
        credentials_id = cloud_credentials_model.save(data=data, provider_id='digitalocean')

        for i in range(5):
            self.collection.insert({"account_id": 1, "name" : "test", "key": "server_key_test", "credentials_id": credentials_id})
        
        cloud_server_model.delete_all_for_provider(credentials_id=credentials_id)


        result = self.collection.find().count()
        eq_(result, 0)
        

        self._cleanup()

    def get_all_for_credentials_test(self):
        self._cleanup()

        credentials_id = "test_credentials"

        for i in range(5):
            self.collection.insert({"account_id": 1, "name" : "test", "key": "server_key_test", "credentials_id": credentials_id})
        
        result = cloud_server_model.get_all_for_provider(credentials_id=credentials_id)

        eq_(result.count(), 5)
        

        self._cleanup()



    def get_instance_ids_list_test(self):
        self._cleanup()

        credentials_id = "test_credentials"

        for i in range(5):
    

            self.collection.insert({"account_id": 1, "name" : "test", 
                "key": "server_key_test", 
                "credentials_id": credentials_id,
                "instance_id": "instance_id_{0}".format(i)
            })
        
        result = cloud_server_model.get_instance_ids_list(credentials_id=credentials_id)

        eq_(sorted(result), [u'instance_id_0', u'instance_id_1', u'instance_id_2', u'instance_id_3', u'instance_id_4'] )    

        self._cleanup()



    def diff_instance_ids_test(self):
        old_instances = ['test', 'test1', 'test2']
        new_instances = ['somethingnew', 'test1']

        result =  cloud_server_model.diff_instance_ids(old_instances=old_instances, new_instances=new_instances)

        eq_(sorted(result), ['test', 'test2']) # These have to be removed
    

    def save_test(self):
        self._cleanup()

        credentials_id = "test_credentials"


        data = {'name': 'test', 'token': 'test-token'}
        credentials_id = cloud_credentials_model.save(data=data, provider_id='digitalocean')
        credentials = cloud_credentials_model.collection.find_one()

        # Empty list 
        instance_list = []

        cloud_server_model.save(instances=instance_list, credentials=credentials)

        result = self.collection.find() 
        eq_(result.count(), 0)

        # Normal list 
        for i in range(5):
            instance = {
                'name': 'test', 
                'instance_id': "instance_id_{0}".format(i), 
                'provider': "rackspace",
                'credentials_id': credentials_id,
                'region': 'eu-west1',
                'type': 't1-micro'

            }

            instance_list.append(instance)


        cloud_server_model.save(instances=instance_list, credentials=credentials)

        result = self.collection.find() 

        for r in result.clone():

            assert len(r['tags']) == 3
            for tag in r['tags']:
                tag_object = tags_model.get_by_id(tag)
        
                name = tag_object.get('name')
                group = tag_object.get('group', {}).get('name')
                assert name in ['rackspace', 'eu-west1', 't1-micro']
                assert group in ['region', 'provider', 'type']
            
            eq_(r['credentials_id'], credentials_id)

        eq_(result.count(), 5)


        self._cleanup()

        # Filter and delete some old instances
        for i in range(4):
            self.collection.insert({
                "account_id": 1,
                "name": "test",
                "key": "server_key_test",
                "credentials_id": credentials_id,
                "instance_id": "instance_id_{0}".format(i)
            })

        result = self.collection.find().count()
        eq_(result, 4)

        # Check if duplicate tags are being saved
        for i in ['rackspace', 'bla']:
            tags_model.get_or_create_by_name(name=i)

        instance_list = []
        for i in range(5, 10):
            instance = {
                'name': 'test',
                'instance_id': i,
                'provider': "rackspace",
                'credentials_id': credentials_id,
            }

            instance_list.append(instance)


        cloud_server_model.save(instances=instance_list, credentials=credentials)

        result = self.collection.find()
        eq_(result.count(), 5)

        for r in result:
            for tag in r['tags']:
                tag_object = tags_model.get_by_id(tag)

                assert tag_object['name'] in ['rackspace', 'bla']

            self.assertTrue(r['key'])
            assert r['instance_id'] <= 10
            assert r['instance_id'] >= 5


        # Filter and delete all instances, the instance list is empty 
        instance_list = []
        cloud_server_model.save(instances=instance_list, credentials=credentials)
        
        result = self.collection.find()
        eq_(result.count(), 0)

        self._cleanup()
        
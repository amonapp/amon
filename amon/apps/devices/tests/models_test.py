import unittest
from nose.tools import eq_

from amon.apps.devices.models import volumes_model, interfaces_model

class DevicesModelTest(unittest.TestCase):

    def setUp(self):
        self.collection = volumes_model.mongo.get_collection('volumes')
        self.servers_collection = volumes_model.mongo.get_collection('servers')

        self.servers_collection.insert({"name" : "test"})
        self.server = self.servers_collection.find_one()
        self.server_id = self.server['_id']


    def _cleanup(self):
        self.collection.remove()

        data_collection = volumes_model.get_data_collection(server_id=self.server_id)
        data_collection.remove()

        data_collection = interfaces_model.get_data_collection(server_id=self.server_id)
        data_collection.remove()


    def rename_keys_test(self):
        original_dict = {'inbound': 1, 'outbound': 2, 't':1, 'server_id': 4}
        new_keys = {'inbound': 'i', 'outbound': 'o'}

        result = interfaces_model.rename_keys(original_dict, new_keys)

        eq_(result, {'i': 1, 'o': 2, 't': 1, 'server_id': 4})



    def tearDown(self):
        self.servers_collection.remove()

    def get_by_name_test(self):
        self._cleanup()

        volumes_model.get_or_create(server_id=self.server_id, name='test')
        result = volumes_model.get_by_name(server=self.server, name='test')


        eq_(result['name'], 'test')
        eq_(result['server_id'], self.server['_id'])


        self._cleanup()

    def get_check_for_timestamp_test(self):
        self._cleanup()
        volumes_model.get_or_create(server_id=self.server_id, name='sda1')

        for i in range(0, 10):
            volume_data = {
                'sda1': {"used" : "19060", "percent" : "41", "free" : "27527", "total": 62}
            }

            volumes_model.save_data(server=self.server, data=volume_data, time=i)


        result = volumes_model.get_check_for_timestamp(self.server, 5)


        eq_(result['sda1']['t'], 5)

        self._cleanup()



    def get_all_for_server_test(self):
        self._cleanup()


        volumes_model.get_or_create(server_id=self.server_id, name='test')
        volumes_model.get_or_create(server_id=self.server_id, name='test1')
        volumes_model.get_or_create(server_id=self.server_id, name='test2')

        result = volumes_model.get_all_for_server(server_id=self.server_id)

        eq_(result.count(), 3)

        self._cleanup()

    def get_data_collection_test(self):
        result = volumes_model.get_data_collection()

        eq_(result.name, "volume_data")


    def get_or_create_test(self):
        self._cleanup()

        volumes_model.get_or_create(server_id=self.server_id, name='test')

        total_devices = self.collection.find().count()
        eq_(total_devices, 1)

        volume = volumes_model.get_or_create(server_id=self.server_id, name='test')

        eq_(volume['name'], 'test')
        eq_(volume['server_id'], self.server_id)


        total_devices = self.collection.find().count()
        eq_(total_devices, 1)

        self._cleanup()


    def save_disk_data_test(self):
        self._cleanup()

        data_collection = volumes_model.get_data_collection(server_id=self.server_id)


        device_id = volumes_model.get_or_create(server_id=self.server_id, name='sda1')
        volume_data = {
            'sda1': {"used" : "19060", "percent" : "41", "free" : "27527", "total": 62}
        }

        volumes_model.save_data(server=self.server, data=volume_data, time=1)



        for r in data_collection.find():
            eq_(r['device_id'], device_id['_id'])
            eq_(r['percent'], '41')
            eq_(r['used'], "19060")
            eq_(r['t'], 1)

        golang_data = [{"name":"sda1","path":"/","fstype":"ext2/ext3","total":"36236.00",
        "free":"3194.00","used":"31282.00","percent":86.33}]

        data_collection.remove()

        volumes_model.save_data(server=self.server, data=golang_data, time=1)
        for r in data_collection.find():
            eq_(r['device_id'], device_id['_id'])
            eq_(r['percent'], 86.33)
            eq_(r['used'], "31282.00")
            eq_(r['t'], 1)

    
        self._cleanup()


    def save_network_data_test(self):
        self._cleanup()

        data_collection = interfaces_model.get_data_collection(server_id=self.server_id)


        device_id = interfaces_model.get_or_create(server_id=self.server_id, name='eth1')
        network_data = {
            'eth1': {"inbound" : 991, "outbound" : 22, }
        }

        interfaces_model.save_data(self.server, network_data, time=1)

        for r in data_collection.find():
            eq_(r['device_id'], device_id['_id'])
            eq_(r['i'], 991)
            eq_(r['o'], 22)
            eq_(r['t'], 1)

        self._cleanup()

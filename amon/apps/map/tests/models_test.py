import unittest
from time import time
from amon.apps.servers.models import server_model
from amon.apps.map.models import map_model
from amon.apps.devices.models import interfaces_model, volumes_model
from amon.apps.processes.models import process_model
from amon.apps.system.models import system_model
from amon.apps.tags.models import tags_model, tag_groups_model

now = int(time())
minute_ago = (now - 60)
two_minutes_ago = (now - 120)
five_minutes_ago = (now - 300)


class MapModelTest(unittest.TestCase):

    def setUp(self):
        pass

    def _cleanup(self):
        server_model.collection.remove()
        system_model.data_collection.remove()
        process_model.data_collection.remove()
        process_model.collection.remove()

        interfaces_model.collection.remove()
        interfaces_model.get_data_collection().remove()

        volumes_model.collection.remove()
        volumes_model.get_data_collection().remove()
        tags_model.collection.remove()


    def get_fields_test(self):
        self._cleanup()
        
        result = map_model.get_fields()

        assert len(result) != 0


    def group_by_test(self):
        self._cleanup()

        tags = [
            'provider:digitalocean',
            'provider:amazon',
            'region:lon1',
        ]
        tags_object_ids = tags_model.create_and_return_ids(tags)

        server = server_model.get_or_create_by_machine_id(
            tags=tags_object_ids,
            machine_id=1
        )

        provider_group = tag_groups_model.get_or_create_by_name('provider')

        data = {
            'max_value': 59,
            'sorted_data': [{
                'last_check': 100,
                'value': 59,
                'field': 'system:memory.used_percent',
                'server': server,
                'unit': '%',
            }]
        }

        result = map_model.group_by(
            group_id=provider_group,
            data=data.copy()
        )
        assert set(result.keys()) == set(['not_in_group', 'digitalocean', 'amazon'])
        assert len(result['digitalocean']['sorted_data']) == 1
        assert len(result['not_in_group']['sorted_data']) == 0
        
        new_tags = [
            'size:1gb',
            'distro:ubuntu',
            'size:2gb'
        ]
        tags_object_ids = tags_model.create_and_return_ids(new_tags)

        provider_group = tag_groups_model.get_or_create_by_name('size')

        result = map_model.group_by(
            group_id=provider_group,
            data=data.copy()
        )
        assert set(result.keys()) == set(['not_in_group', '1gb', '2gb'])
        assert len(result['1gb']['sorted_data']) == 0
        assert len(result['2gb']['sorted_data']) == 0
        assert len(result['not_in_group']['sorted_data']) == 1



    def sort_by_test_system_data(self):
        self._cleanup()

        for i in range(10):
            data = {
                'name': 'system-server-{0}'.format(i),
                'last_check': 100
            }
            server_id = server_model.collection.insert(data.copy())

            cpu_dict = {"time": 100,
                "server_id": server_id,
                "cpu": {"system": i, "idle": "91.15"},
                 "memory": {
                    "used_percent": 50 + i,
                    "swap_used_mb": 9,
                    "total_mb": 497,
                    "free_mb": 12,
                    "swap_used_percent": 1,
                    "swap_free_mb": 1015,
                    "used_mb": 485,
                    "swap_total_mb": 1024
                },
                "loadavg": {
                    "cores": 1,
                    "fifteen_minutes": i + 1,
                    "five_minutes": 0.01,
                    "minute": 0
                },
            }
            system_model.data_collection.insert(cpu_dict)

        result = map_model.sort_by(field='system:cpu.system')
        assert len(result['sorted_data']) == 10
        for i, r in enumerate(result['sorted_data']):
            assert r['value'] == (9 - i)

        assert result['max_value'] == 9


        result = map_model.sort_by(field='system:memory.used_percent')
        assert len(result['sorted_data']) == 10
        assert result['sorted_data'][0]['value'] == 59
        assert result['max_value'] == 59


        result = map_model.sort_by(field='system:loadavg.fifteen_minutes')
        assert len(result['sorted_data']) == 10
        assert result['sorted_data'][0]['value'] == 10
        assert result['max_value'] == 10


    def sort_by_test_process_data(self):
        self._cleanup()


        for i in range(10):
            data = {
                'name': 'process-server-{0}'.format(i),
                'last_check': 100
            }
            server_id = server_model.collection.insert(data.copy())

            process = {
                'name': 'amonagent',
                'server': server_id,
                'last_check': 100,
            }
            process_id = process_model.collection.insert(process.copy())

            process_dict = {
                "server_id": server_id,
                "t": 100,
                "data": [{
                    "c": i + 1,
                    "m": i + 101,
                    "n": "amonagent",
                    "p": process_id,
                    "r": 0.17,
                    "w": 0.0
                }]
            }
            process_model.data_collection.insert(process_dict.copy())

        result = map_model.sort_by(field='process:amonagent.cpu')
        assert len(result['sorted_data']) == 10
        assert result['sorted_data'][0]['value'] == 10
        assert result['sorted_data'][0]['unit'] == '%'
        assert result['max_value'] == 10

        result = map_model.sort_by(field='process:amonagent.memory')
        assert len(result['sorted_data']) == 10
        assert result['sorted_data'][0]['value'] == 110
        assert result['sorted_data'][0]['unit'] == 'MB'
        assert result['max_value'] == 110


        result = map_model.sort_by(field='process:nontexisting.no')
        assert len(result['sorted_data']) == 10
        assert result['sorted_data'][0]['value'] == 0
        assert result['sorted_data'][0]['unit'] == ''
        assert result['max_value'] == 0


    def test_sort_by_volume_data(self):
        self._cleanup()
        
        for i in range(10):
            data = {
                'name': 'volume-server-{0}'.format(i),
                'last_check': 100
            }
            server_id = server_model.collection.insert(data.copy())

            for v in range(5):

                volume = {
                    'name': 'sda-{0}'.format(v),
                    'server_id': server_id,
                    'last_update': 100,
                }
                volume_id = volumes_model.collection.insert(volume.copy())


                volume_data_dict = {
                    "server_id": server_id,
                    "device_id": volume_id,
                    "percent": i + v + 10,
                    "t": 100
                    
                }
                volumes_model.get_data_collection().insert(volume_data_dict.copy())

        result = map_model.sort_by(field='disk:disk.used_percent')
    
        assert len(result['sorted_data']) == 10
        assert result['sorted_data'][0]['value'] == 23  # 10 + 9 + 4
        assert result['sorted_data'][0]['unit'] == '%'
        

    def test_sort_by_iface_data(self):
        self._cleanup()


        for i in range(10):
            data = {
                'name': 'iface-server-{0}'.format(i),
                'last_check': 100
            }
            server_id = server_model.collection.insert(data.copy())

            for v in range(5):

                device_data = {
                    'name': 'eth{0}'.format(v),
                    'server_id': server_id,
                    'last_update': 100,
                }
                device_id = interfaces_model.collection.insert(device_data.copy())


                data_dict = {
                    "server_id": server_id,
                    "device_id": device_id,
                    "i": i + v + 100,
                    "t": 100
                    
                }
                interfaces_model.get_data_collection().insert(data_dict.copy())

        result = map_model.sort_by(field='network:network.inbound')
    
        assert len(result['sorted_data']) == 10
        assert result['sorted_data'][0]['value'] == 113  # 100 + 9 + 4
        assert result['sorted_data'][0]['unit'] == 'kb/s'

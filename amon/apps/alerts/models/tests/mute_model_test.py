import unittest

from amon.apps.alerts.models import alert_mute_servers_model
from amon.apps.servers.models import server_model
from amon.apps.tags.models import tags_model


class MuteModelTest(unittest.TestCase):

    def setUp(self):
        pass



    def tearDown(self):
        alert_mute_servers_model.collection.remove()
        server_model.collection.remove()


    def _cleanup(self):
        self.tearDown()


    def test_check_if_server_is_muted(self):
        self._cleanup()

        tags_model.get_or_create_by_name('test_tag')
        tag = tags_model.collection.find_one()

        server_model.add('name', account_id=1, tags=[tag['_id']])
        server = server_model.collection.find_one()
        
        # First check, plain server_id
        data = {
            'server': server['_id'],
            'period': 0
        }

        alert_mute_servers_model.save(data)

        result = alert_mute_servers_model.check_if_server_is_muted(server=server)
        assert result == True

        # Second check, all servers, no tags
        alert_mute_servers_model.collection.remove()

        data = {
            'server': 'all',
            'period': 0
        }

        alert_mute_servers_model.save(data)

        result = alert_mute_servers_model.check_if_server_is_muted(server=server)
        assert result == True


        # Third check, all servers, different tag
        alert_mute_servers_model.collection.remove()

        tags_model.get_or_create_by_name('global_tag')
        global_tag = tags_model.collection.find_one({'name': 'global_tag'})

        data = {
            'server': 'all',
            'tags': [global_tag['_id']],
            'period': 0
        }
        alert_mute_servers_model.save(data)

        result = alert_mute_servers_model.check_if_server_is_muted(server=server)
        assert result == False


        # Check all servers with server_tag included
        alert_mute_servers_model.collection.remove()

        data = {
            'server': 'all',
            'tags': [tag['_id']],
            'period': 0
        }
        alert_mute_servers_model.save(data)

        result = alert_mute_servers_model.check_if_server_is_muted(server=server)
        assert result == True
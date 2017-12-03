import json
import os

from django.test.client import Client
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
User = get_user_model()

from amon.apps.servers.models import server_model
from amon.apps.system.models import system_model
from amon.apps.processes.models import process_model
from amon.apps.devices.models import interfaces_model, volumes_model
from amon.apps.plugins.models import plugin_model
from amon.apps.alerts.models import alerts_model

from amon.apps.cloudservers.models import cloud_credentials_model


class TestCoreApi(TestCase):

    def setUp(self):
        self.c = Client()
        self.user = User.objects.create_user(password='qwerty', email='foo@test.com')
        self.c.login(username='foo@test.com', password='qwerty')


    def tearDown(self):
        self.c.logout()
        self.user.delete()


    def _cleanup(self):
        server_model.collection.remove()
        system_model.data_collection.remove()
        process_model.data_collection.remove()
        interfaces_model.collection.remove()
        volumes_model.collection.remove()
        plugin_model.collection.remove()
        alerts_model.collection.remove()
        cloud_credentials_model.collection.remove()

    def test_with_user_data(self):
        self._cleanup()

        alerts_model.add_initial_data()

        current_directory = os.path.abspath(os.path.dirname(__file__))
        agentdata = os.path.join(current_directory, 'agentdata.json')
        data = open(agentdata).read()

        url = reverse('api_system')
        response = self.c.post(url, data, content_type='application/json')

        assert server_model.collection.find().count() == 1
        assert system_model.data_collection.find().count() == 1
        assert process_model.data_collection.find().count() == 1
        assert volumes_model.collection.find().count() == 1
        assert interfaces_model.collection.find().count() == 1
        assert plugin_model.collection.find().count() == 1

    def test_get_or_create_server_view(self):
        self._cleanup()


        # Default, non cloud servers
        data = {"host": {
            "host": "debian-jessie",
            "machineid": "25e1f5e7b26240109d199892e468d529",
            "server_key": "",
            "distro": {
                "version": "8.2",
                "name": "debian"
            },
            "ip_address": "10.0.2.15",
            "instance_id": ""
        }}

        url = reverse('api_system')
        # data = open(JSON_PATH).read()
        self.c.post(url, json.dumps(data), content_type='application/json')

        assert server_model.collection.find().count() == 1
        server = server_model.collection.find_one()

        assert server['name'] == 'debian-jessie'
        assert server['key'] == '25e1f5e7b26240109d199892e468d529'

        self._cleanup()

        # Not synced cloud server
        data = {"host": {
            "host": "debian-jessie",
            "machineid": "25e1f5e7b26240109d199892e468d529",
            "server_key": "",
            "distro": {
                "version": "8.2",
                "name": "debian"
            },
            "ip_address": "10.0.2.15",
            "instance_id": "100"
        }}

        url = reverse('api_system')
        self.c.post(url, json.dumps(data), content_type='application/json')

        assert server_model.collection.find().count() == 1
        server = server_model.collection.find_one()

        assert server['name'] == 'debian-jessie'
        assert server['key'] == '25e1f5e7b26240109d199892e468d529'
        assert server['instance_id'] == '100'

    def test_system_data_view(self):
        self._cleanup()

        current_directory = os.path.abspath(os.path.dirname(__file__))
        agentdata = os.path.join(current_directory, 'agentdata.json')
        data = open(agentdata).read()

        url = reverse('api_system')
        self.c.post(url, data, content_type='application/json')

        assert server_model.collection.find().count() == 1
        assert system_model.data_collection.find().count() == 1
        assert process_model.data_collection.find().count() == 1
        assert volumes_model.collection.find().count() == 1
        assert interfaces_model.collection.find().count() == 1
        assert plugin_model.collection.find().count() == 1


    def stress_test_system_data_view(self):
        self._cleanup()

        current_directory = os.path.abspath(os.path.dirname(__file__))
        agentdata = os.path.join(current_directory, 'agentdata.json')
        data = open(agentdata).read()

        url = reverse('api_system')
        for i in range(10):
            self.c.post(url, data, content_type='application/json')

        assert server_model.collection.find().count() == 1

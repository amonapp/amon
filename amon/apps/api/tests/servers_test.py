from django.test.client import Client
from django.test import TestCase
from django.urls import reverse
from nose.tools import *
from amon.apps.servers.models import server_model
import json
from django.contrib.auth import get_user_model
User = get_user_model()


class TestServersApi(TestCase):

    def setUp(self):
        self.c = Client()
        self.user = User.objects.create_user(password='qwerty', email='foo@test.com')
        self.c.login(username='foo@test.com', password='qwerty')


    def tearDown(self):
        self.c.logout()
        self.user.delete()


    def _cleanup(self):
        server_model.collection.remove()


    def test_add_servers(self):
        self._cleanup()

        url = reverse('api_servers_create')
        
        # Just the name,
        data = {'name': 'testserver'}
        response = self.c.post(url, json.dumps(data), content_type='application/json')

        response = json.loads(response.content.decode('utf-8'))

        assert response['status'] == 201 # Created
        assert response['name'] == 'testserver'

        assert response['server_key']


        self._cleanup()

        # Invalid key 
        data = {'name': 'testserver', 'key': 'BlaBla'}
        response = self.c.post(url, json.dumps(data), content_type='application/json')

        response = json.loads(response.content.decode('utf-8'))

        assert response['status'] == 422  # Invalid key
        assert response['error']

        self._cleanup()
        
        # Valid key
        # d3vopqnzdnm677keoq3ggsgkg5dw94xg
        data = {'name': 'testserver', 'key': 'd3vopqnzdnm677keoq3ggsgkg5dw94xg'}
        response = self.c.post(url, json.dumps(data), content_type='application/json')

        response = json.loads(response.content.decode('utf-8'))

        assert response['status'] == 201  # Created
        assert response['name'] == 'testserver'

        assert response['server_key'] == data['key']

        # Check for unique keys
        data = {'name': 'testserver_one', 'key': 'd3vopqnzdnm677keoq3ggsgkg5dw94xg'}
        response = self.c.post(url, json.dumps(data), content_type='application/json')

        response = json.loads(response.content.decode('utf-8'))

        assert response['status'] == 201 # Created
        assert response['name'] == 'testserver'

        assert response['server_key'] == data['key']


    def test_list_servers(self):
        self._cleanup()

        url = reverse('api_servers_list')

        response = self.c.get(url)
        response = json.loads(response.content.decode('utf-8'))

        
        assert len(response['servers']) == 0


        for i in range(0, 10):
            server_model.add('test')
        

        response = self.c.get(url)
        response = json.loads(response.content.decode('utf-8'))

        assert len(response['servers']) == 10
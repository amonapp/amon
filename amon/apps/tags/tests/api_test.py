import json

from django.test.client import Client
from django.test import TestCase
from django.core.urlresolvers import reverse


from django.contrib.auth import get_user_model


from amon.apps.tags.models import tags_model
from amon.apps.servers.models import server_model

User = get_user_model()


class TestTagsApi(TestCase):

    def setUp(self):
        self.c = Client()
        self.user = User.objects.create_user(password='qwerty', email='foo@test.com')
        self.c.login(username='foo@test.com', password='qwerty')


    def tearDown(self):
        self.c.logout()
        self.user.delete()


    def _cleanup(self):
        server_model.collection.remove()
        tags_model.collection.remove()




    def test_ajax_get_tags(self):
        self._cleanup()

        tags = {'rds': 'value', 'ebs': 'volume'}
        tags_model.create_and_return_ids(tags)

        url = reverse('api_tags_get_tags')
        response = self.c.get(url)
        response = json.loads(response.content.decode('utf-8'))

        assert len(response) == 2

        for i in response:
            assert i['group'] in ['rds', 'ebs']
            assert i['text'] in ['rds:value', 'ebs:volume']


    def test_ajax_get_tags_list(self):
        self._cleanup()

        tags = {'rds': 'value', 'ebs': 'volume'}
        result = tags_model.create_and_return_ids(tags)

        assert len(result) == 2
    
        tags_ids_to_string =  ','.join(map(str, result))

        url = reverse('api_tags_get_tags_list')

        url = "{0}?tags={1}".format(url, tags_ids_to_string)
        response = self.c.get(url)

        response = json.loads(response.content.decode('utf-8'))
        
        assert len(response) == 2

        for i in response:
            assert i['name'] in ['value', 'volume']
            assert i['full_name'] in ['rds.value', 'ebs.volume']


    def test_ajax_get_tags_for_server(self):
        self._cleanup()

    def test_ajax_get_only_server_tags(self):
        self._cleanup()

        # Create unassigned tags
        tags = {'rds': 'value', 'ebs': 'volume'}
        tags_model.create_and_return_ids(tags)

        # Create a server with tags
        data = {'name': 'testserver_one', 'key': 'd3vopqnzdnm677keoq3ggsgkg5dw94xg', 'tags': ['provider:digitalocean', "nyc1"]}
        url = reverse('api_servers_create')
        response = self.c.post(url, json.dumps(data),  content_type='application/json')

        # Create a server with tags
        data = {'name': 'testserver_one_one', 'key': 'd3vopqnzdnm677keoq3ggsgkg5dw94xg', 'tags': ['provider:digitalocean', "nyc1"]}
        url = reverse('api_servers_create')
        response = self.c.post(url, json.dumps(data),  content_type='application/json')

        # Create a server with no tags
        data = {'name': 'testserver_two', 'key': 'd3vopqnzdnm677keoq3ggsgkg5dw94dg',}
        url = reverse('api_servers_create')
        response = self.c.post(url, json.dumps(data),  content_type='application/json')

        url = reverse('api_tags_only_server_tags')
        response = self.c.get(url)



        response = json.loads(response.content.decode('utf-8'))
        # provider:digitalocean, nyc1
        assert len(response) == 2
            
        for r in response:
            assert r['text'] in ['nyc1', 'provider:digitalocean']

from django.test.client import Client
from django.test import TestCase
from django.urls import reverse
from nose.tools import *
from amon.apps.tags.models import tags_model, tag_groups_model
import json
from django.contrib.auth import get_user_model
User = get_user_model()
from amon.apps.api.utils import dict_from_cursor


class TestTagsApi(TestCase):

    def setUp(self):
        self.c = Client()
        self.user = User.objects.create_user(password='qwerty', email='foo@test.com')
        self.c.login(username='foo@test.com', password='qwerty')


    def tearDown(self):
        self.c.logout()
        self.user.delete()


    def _cleanup(self):
        tags_model.collection.remove()
        tag_groups_model.collection.remove()

    def test_add_tag(self):
        self._cleanup()

        url = reverse('api_tags_create')

        data = {'name': 'test'}
        response = self.c.post(url, json.dumps(data),  content_type='application/json')

        response = json.loads(response.content.decode('utf-8'))
        assert response['tag']['name'] == 'test'

        self._cleanup()
        group_id = tag_groups_model.get_or_create_by_name(name='testgroup')
        group = tag_groups_model.get_by_id(group_id)
        

        group_dict = dict_from_cursor(group, keys=['_id', 'name'])

        data = {'name': 'test', 'group': group_dict}
        response = self.c.post(url, json.dumps(data),  content_type='application/json')

        response = json.loads(response.content.decode('utf-8'))

        assert response['tag']['name'] == 'test'

        assert response['tag']['group']['id'] == str(group['_id'])


    def test_update_tag(self):
        self._cleanup()

        url = reverse('api_tags_create')
        update_url = reverse('api_tags_update')

        data = {'name': 'test'}
        response = self.c.post(url, json.dumps(data),  content_type='application/json')

        response = json.loads(response.content.decode('utf-8'))
        assert response['tag']['name'] == 'test'


        data = {'name': 'updatetest', 'id': response['tag']['id']}
        response = self.c.post(update_url, json.dumps(data),  content_type='application/json')

        response = json.loads(response.content.decode('utf-8'))
        assert response['status'] == 200
from django.test.client import Client
from django.test import TestCase

from django.urls import reverse
from django.conf import settings

from amon.apps.servers.models import server_model, cloud_server_model

from django.contrib.auth import get_user_model
User = get_user_model()

from amon.apps.cloudservers.models import cloud_credentials_model


class TestCloudServersApi(TestCase):

    def setUp(self):
        self.c = Client()
        self.user = User.objects.create_user(password='qwerty', email='foo@test.com')
        self.c.login(username='foo@test.com', password='qwerty')


    def tearDown(self):
        self.c.logout()
        self.user.delete()


    def _cleanup(self):
        server_model.collection.remove()
        cloud_credentials_model.collection.remove()


    def test_get_instance_key(self):
        self._cleanup()

        data = {"access_key": settings.AMAZON_ACCESS_KEY, "secret_key": settings.AMAZON_SECRET_KEY, "regions": 'eu-west-1'}


        credentials_id = cloud_credentials_model.save(data=data, provider_id='amazon')

        valid_credentials = cloud_credentials_model.get_by_id(credentials_id)


        instance_id = "instance_id_test"
        instance_list = []
        instance = {
            'name': 'test',
            'instance_id': instance_id,
            'provider': "amazon",
            'credentials_id': credentials_id,
            'credentials': 'production',
            'region': 'eu-west1',
            'type': 't1-micro',
            'key': 'testserver-key'

        }

        instance_list.append(instance)
        cloud_server_model.save(instances=instance_list, credentials=valid_credentials)
        server = server_model.collection.find_one()
        key = server.get('key')

        url = reverse('api_cloudservers_get_server_key', kwargs={'provider_id': 'amazon'}, )
        url = "{0}?instance_id={1}".format(url, instance_id)

        response = self.c.get(url)
        assert response.content.decode('utf-8') == key

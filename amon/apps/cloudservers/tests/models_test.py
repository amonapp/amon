import unittest
from nose.tools import * 

from django.contrib.auth import get_user_model
User = get_user_model()
from amon.apps.cloudservers.models import cloud_credentials_model
from amon.utils.security import AESCipher


class CloudServersModelTest(unittest.TestCase):

    def setUp(self):
        self.user = User.objects.create_user(password='qwerty', email='foo@test.com')
        self.account_id = 1

        self.cypher = AESCipher()
        


    def tearDown(self):
        self.user.delete()
        User.objects.all().delete()

        

    def _cleanup(self):
        cloud_credentials_model.collection.remove()
        

    
    def save_digitalocean_test(self):
        self._cleanup()

        data = {'name': 'test', 'token': 'test-token'}

        cloud_credentials_model.save(data=data, provider_id='digitalocean')


        result = cloud_credentials_model.collection.find_one() 

        assert self.cypher.decrypt(result['token']) == 'test-token'


    def save_amazon_test(self):
        self._cleanup()

        data = {'name': 'test', 'access_key': 'test-token', 'secret_key': 'super_secret'}

        cloud_credentials_model.save(data=data.copy(), provider_id='amazon')

        result = cloud_credentials_model.collection.find_one()

        assert self.cypher.decrypt(result['access_key']) == data['access_key']
        assert self.cypher.decrypt(result['secret_key']) == data['secret_key']


    def save_google_test(self):
        self._cleanup()

        data = {'name': 'test', 'email': 'test-token@example.com', 'project_id': 'super_secret'}

        cloud_credentials_model.save(data=data.copy(), provider_id='google')


        result = cloud_credentials_model.collection.find_one() 


        assert self.cypher.decrypt(result['email']) == data['email']
        assert self.cypher.decrypt(result['project_id']) == data['project_id']



    def save_linode_test(self):
        self._cleanup()

        data = {'name': 'test', 'api_key': 'test-token', 'client_id': 'super_secret'}

        cloud_credentials_model.save(data=data.copy(), provider_id='linode')


        result = cloud_credentials_model.collection.find_one() 

        assert self.cypher.decrypt(result['api_key']) == data['api_key']
        assert self.cypher.decrypt(result['client_id']) == data['client_id']


    def save_rackspace_test(self):
        self._cleanup()

        data = {'name': 'test', 'username': 'test-token', 'api_key': 'super_secret'}

        cloud_credentials_model.save(data=data.copy(), provider_id='rackspace')


        result = cloud_credentials_model.collection.find_one() 

        assert self.cypher.decrypt(result['username']) == data['username']
        assert self.cypher.decrypt(result['api_key']) == data['api_key']




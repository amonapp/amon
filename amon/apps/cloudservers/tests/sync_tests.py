import unittest
from nose.tools import eq_ 

from django.contrib.auth import get_user_model
User = get_user_model()
from django.conf import settings

from amon.utils.dates import unix_utc_now
from amon.apps.servers.models import server_model

from amon.apps.cloudservers.apicalls import sync_credentials
from amon.apps.cloudservers.models import cloud_credentials_model



class IntegrationsTest(unittest.TestCase):

    def setUp(self):
        User.objects.all().delete()
        self.user = User.objects.create_user(password='qwerty', email='foo@test.com')

        self.account_id = 1


        self.valid_data = {
            'rackspace': {"username": "martinrusev", "api_key": settings.RACKSPACE_API_KEY, "regions": 'dfw'}, 
            'amazon': {"access_key": settings.AMAZON_ACCESS_KEY, "secret_key": settings.AMAZON_SECRET_KEY, "regions": 'eu-west-1'},
            'digitalocean': {"token": settings.DIGITALOCEAN_TOKEN},
            'linode': {"api_key": settings.LINODE_API_KEY},
            'vultr': {'api_key': settings.VULTR_API_KEY}
        }

        self.invalid_data = {
            'rackspace': {"username": "example"},
            'amazon': {"access_key": "example"},
            'digitalocean': {"token": "example"},
            'linode': {"api_key": "example"},
            'vultr': {"api_key": "example"}
        }


    def tearDown(self):
        self.user.delete()
        

    def _cleanup(self):
        server_model.collection.remove()    
        cloud_credentials_model.collection.remove()    
        

    def test_rackspace_sync(self):
        self._cleanup()

        self._cloud_sync(provider_id='rackspace')


    def test_digitalocean_sync(self):
        self._cleanup()

        self._cloud_sync(provider_id='digitalocean')

    def test_amazon_sync(self):
        self._cleanup()

        self._cloud_sync(provider_id='amazon')


    def test_linode_sync(self):
        self._cleanup()

        self._cloud_sync(provider_id='linode')


    def test_vultr_sync(self):
        self._cleanup()

        self._cloud_sync(provider_id='vultr')


    def _cloud_sync(self, provider_id=None):
        valid_dict = self.valid_data[provider_id]
        invalid_dict = self.invalid_data[provider_id]
    

        credentials_id = cloud_credentials_model.save(data=valid_dict, provider_id=provider_id)

        valid_credentials = cloud_credentials_model.get_by_id(credentials_id)
        
        now = unix_utc_now() - 5 # Just in case, the case could pass in less then a second
        sync_credentials(credentials=valid_credentials)

        entry = cloud_credentials_model.get_by_id(credentials_id)

        assert entry['last_sync'] > now

        # for r in server_model.get_all():
        #     eq_(r['provider'], 'rackspace')
        #     eq_(r['credentials'], entry['_id'])

    
        # Invalid credentials
        cloud_credentials_model.update(data=invalid_dict, id=credentials_id, provider_id=provider_id)


        invalid_credentials = cloud_credentials_model.get_by_id(credentials_id)


        now = unix_utc_now()-5 
        sync_credentials(credentials=invalid_credentials)
        entry = cloud_credentials_model.get_by_id(credentials_id)


        assert entry['error']
        assert entry['last_sync'] > now

from django.test.client import Client
from django.core.urlresolvers import reverse
from django.test import TestCase
from nose.tools import *

from django.contrib.auth import get_user_model
User = get_user_model()
from amon.apps.dashboards.models import dashboard_model


class TestDashboardUrls(TestCase):

    def setUp(self):
        User.objects.all().delete()
        
        self.c = Client()
        self.user = User.objects.create_user(password='qwerty', email='foo@test.com')
        


        self.c.login(username='foo@test.com', password='qwerty')
        self.account_id = 1

        self.collection = dashboard_model.collection
        self.servers_collection = dashboard_model.mongo.get_collection('servers')

        self.servers_collection.insert({"name" : "test"})
        self.server = self.servers_collection.find_one()
        self.server_id = self.server['_id']

    def tearDown(self):
        self.servers_collection.remove()
        self.collection.remove()

        self.c.logout()
        self.user.delete()
        


    def _cleanup(self):
        self.collection.remove()
        

    def test_dashboards(self):
        self._cleanup()

        for i in range(5):
            self.collection.insert({'test': 1, 'server': i, 'account_id':self.account_id})


        url = reverse('dashboards')    
        response = self.c.get(url)

        assert response.status_code == 200
        assert len(response.context['dashboards_data']) == 5

        # Test the urls
        

        
        self._cleanup()


    def test_edit_dashboard(self):
        self._cleanup()

        dashboard_id = self.collection.insert({'server': 'test', 'account_id':self.account_id})

        url = reverse('edit_dashboard', kwargs={'dashboard_id': dashboard_id})    
        response = self.c.get(url)
        assert response.status_code == 200

        self._cleanup()


    def test_delete_dashboard(self):
        self._cleanup()

        dashboard_id = self.collection.insert({'server': 'test', 'account_id':self.account_id})

        assert self.collection.find().count() == 1

        url = reverse('delete_dashboard', kwargs={'dashboard_id': dashboard_id})    
        response = self.c.get(url)
        assert response.status_code == 302

        assert self.collection.find().count() == 0

        self._cleanup()



    def test_public_dashboard(self):
        self._cleanup()

        dashboard_id = self.collection.insert({'server': 'test', 'account_id':self.account_id})

        url = reverse('public_dashboard', kwargs={'dashboard_id': dashboard_id, 'account_id': self.account_id})    
        response = self.c.get(url)
            
        # Default - not shared
        assert response.status_code == 404

        dashboard_model.update({'shared': True}, dashboard_id)
        response = self.c.get(url)

        assert response.status_code == 200


        self._cleanup()

        

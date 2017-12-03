from django.test.client import Client
from django.urls import reverse
from django.test import TestCase
from nose.tools import *

from django.contrib.auth import get_user_model
User = get_user_model()

from amon.apps.servers.models import server_model
from amon.apps.alerts.models import alert_mute_servers_model

from amon.utils.dates import unix_utc_now


class TestMuteForm(TestCase):

    def setUp(self):
        self.c = Client()
        User.objects.all().delete()
        self.user = User.objects.create_user(password='qwerty', email='foo@test.com')
        self.c.login(username='foo@test.com', password='qwerty')


    def tearDown(self):
        self.c.logout()
        User.objects.all().delete()
    
    def _cleanup(self):
        server_model.collection.remove()
        alert_mute_servers_model.collection.remove()


    def test_mute(self):
        self._cleanup()

        url = reverse('alerts_mute_servers')

        response = self.c.post(url,{
            'server': 'all', 
            'period': 1,
        })

        result = alert_mute_servers_model.collection.find_one()
        

        assert result['expires_at_utc'] == unix_utc_now()+3600

        self._cleanup()


        response = self.c.post(url,{
            'server': 'all', 
            'period': 0,
        })

        result = alert_mute_servers_model.collection.find_one()

        assert result.get('expires_at_utc') == None
        






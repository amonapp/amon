from django.test.client import Client
from django.core.urlresolvers import reverse
from django.test import TestCase
from nose.tools import *


from django.contrib.auth import get_user_model
User = get_user_model()
from amon.apps.settings.models import data_retention_model


class TestDataRetention(TestCase):

    def setUp(self):
        self.c = Client()
        self.user = User.objects.create_user(password='qwerty', email='foo@test.com')
        self.c.login(username='foo@test.com', password='qwerty')

    def tearDown(self):
        self.c.logout()
        User.objects.all().delete()


    def test_data_retention_form(self):
        url = reverse('settings_data')

    
        response = self.c.post(url, {'check_every': 60, 'keep_data': 30})

        
        result = data_retention_model.get_one()

        assert result['check_every'] == 60
        assert result['keep_data'] == 30



        response = self.c.post(url, {'check_every': 300, 'keep_data': 60})

        result = data_retention_model.get_one()

        assert result['check_every'] == 300
        assert result['keep_data'] == 60



from django.test.client import Client
from django.core.urlresolvers import reverse
from django.test import TestCase
from nose.tools import *

from django.contrib.auth import get_user_model
User = get_user_model()
from amon.apps.account.models import user_preferences_model



class TestProfileForms(TestCase):

    def setUp(self):
        self.c = Client()
        self.user = User.objects.create_user(password='qwerty', email='foo@test.com')
        self.c.login(username='foo@test.com', password='qwerty')


    def tearDown(self):
        self.c.logout()
        User.objects.all().delete()




    def test_update_profile(self):
        url = reverse('view_profile')

        # Test profile update with the same email - Nothing happens
        response = self.c.post(url, {'email': 'foo@test.com', 'timezone': 'UTC',})


        self.assertRedirects(response, reverse('view_profile'), status_code=302)

        user_preferences = user_preferences_model.get_preferences(user_id=self.user.id)

        assert user_preferences['timezone'] == 'UTC'
        


        response = self.c.post(url, {'email': 'foo@test.com', 'timezone': 'Europe/Sofia',})

        user_preferences = user_preferences_model.get_preferences(user_id=self.user.id)

        assert user_preferences['timezone'] == 'Europe/Sofia'


        # Test profile update with the same email
        response = self.c.post(url, {'email': 'network-operations@maynardnetworks.com',  'timezone': 'UTC'})

        self.assertRedirects(response, reverse('view_profile'), status_code=302)


        updated_user = User.objects.get(id=self.user.id)

        assert updated_user.email == 'network-operations@maynardnetworks.com'


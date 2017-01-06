from django.test.client import Client
from django.core.urlresolvers import reverse
from django.test import TestCase
from nose.tools import *

from django.contrib.auth import get_user_model
User = get_user_model()
from amon.apps.notifications.models import notifications_model

class TestNotifications(TestCase):

    def setUp(self):
        self.c = Client()
        self.user = User.objects.create_user(password='qwerty', email='foo@test.com')



        self.c.login(username='foo@test.com', password='qwerty')

    def tearDown(self):
        self.c.logout()
        self.user.delete()
        notifications_model.collection.remove()

    def _cleanup(self):
        notifications_model.collection.remove()

    def test_add_url(self):

        self._cleanup()

        url = reverse('notifications_add', kwargs={"provider_id": "pushover"})

        response = self.c.post(url,{
            'name': 'default',
            'user_key': 'somekey',
            'application_api_key': 'some'
        })


        self.assertRedirects(response, reverse('notifications_edit', kwargs={'provider_id': 'pushover'}))
        assert notifications_model.collection.find().count() == 1


        result = notifications_model.collection.find_one()

        edit_url = reverse('notifications_edit', kwargs={"provider_id": "pushover", 'notification_id': result['_id']})
        response = self.c.post(edit_url,{
            'name': 'default',
            'user_key': 'changed_user_key',
            'application_api_key': 'changed_data'
        })


        self.assertRedirects(response, reverse('notifications_edit', kwargs={'provider_id': 'pushover', 'notification_id': result['_id']}))
        assert notifications_model.collection.find().count() == 1

        for r in notifications_model.collection.find():
            assert r['application_api_key'] == 'changed_data'
            assert r['user_key'] == 'changed_user_key'

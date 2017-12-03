from django.test.client import Client
from django.urls import reverse
from django.test import TestCase
from nose.tools import *


from django.contrib.auth import get_user_model
User = get_user_model()


from amon.apps.users.forms import InviteForm
from amon.apps.users.models import invite_model


class TestInvite(TestCase):

    def setUp(self):
        self.c = Client()
        self.user = User.objects.create_user(password='qwerty', email='foo@test.com')
        self.c.login(username='foo@test.com', password='qwerty')

    def tearDown(self):
        self.c.logout()
        self.user.delete()
        invite_model.collection.remove()


    def test_invite(self):

        form_data = {'email': 'foo@test.com'}
        form = InviteForm(data=form_data, user=self.user)

        self.assertEqual(form.is_valid(), False) # Can't invite yourself error


        form_data = {'email': 'foo1@test.com'}
        form = InviteForm(data=form_data, user=self.user)

        self.assertEqual(form.is_valid(), True) 
        form.save()


        form_data = {'email': 'foo1@test.com'}
        form = InviteForm(data=form_data, user=self.user,)

        self.assertEqual(form.is_valid(), False) # Duplicate invitation 


        result = invite_model.collection.find().count()

        assert result == 1
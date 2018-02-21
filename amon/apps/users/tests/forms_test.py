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



class TestUser(TestCase):

    def test_forgotten_password_form(self):
        self._cleanup()

        url = reverse('forgotten_password')


        response = self.c.post(url, {'email': self.email})

        assert response.context['form'].errors

        # Create user and reset password
        self.user = User.objects.create_user(password='qwerty', email=self.email)
        response = self.c.post(url, {'email': self.email})

        # assert forgotten_pass_tokens_model.collection.find().count() == 1

        response = self.c.post(url, {'email': self.email})

        # assert forgotten_pass_tokens_model.collection.find().count() == 1

    
    def test_reset_password_form(self):
        self._cleanup()
        self.user = User.objects.create_user(self.email, 'qwerty')

        # Generate token
        url = reverse('forgotten_password')
        response = self.c.post(url, {'email': self.email})
        assert forgotten_pass_tokens_model.collection.find().count() == 1
        token = forgotten_pass_tokens_model.collection.find_one()
        

        url = reverse("reset_password", kwargs={'token': token['token']})
        response = self.c.post(url, {'password': 'newpass', 'repeat_password': 'newpasssssss'})

        assert response.context['form'].errors
        
        url = reverse("reset_password", kwargs={'token': token['token']})
        response = self.c.post(url, {'password': 'newpass', 'repeat_password': 'newpass'})

        self.assertFalse(self.c.login(email=self.email, password='qwerty'))
        self.assertTrue(self.c.login(email=self.email, password='newpass'))
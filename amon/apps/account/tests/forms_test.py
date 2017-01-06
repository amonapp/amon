from django.test.client import Client
from django.core.urlresolvers import reverse
from django.test import TestCase
from nose.tools import *

from django.contrib.auth import get_user_model
from amon.apps.account.models import user_preferences_model, forgotten_pass_tokens_model

User = get_user_model()


class TestAccountForms(TestCase):

    def setUp(self):
        self.c = Client()
        self.email = "network-operations@something.com"

    def tearDown(self):
        User.objects.all().delete()
        

    def _cleanup(self):
        User.objects.all().delete()
        forgotten_pass_tokens_model.collection.remove()

    def test_create_admin_user(self):
        url = reverse('create_admin_user')

        response = self.c.post(url, {'email': self.email, 'password': '123456'})

        
        user = User.objects.get(email=self.email)
        eq_(user.email, self.email)
        eq_(user.is_superuser, True)

    def test_forgotten_password_form(self):
        self._cleanup()

        url = reverse('forgotten_password')


        response = self.c.post(url, {'email': self.email})

        assert response.context['form'].errors

        # Create user and reset password
        self.user = User.objects.create_user(password='qwerty', email=self.email)
        response = self.c.post(url, {'email': self.email})

        assert forgotten_pass_tokens_model.collection.find().count() == 1

        response = self.c.post(url, {'email': self.email})

        assert forgotten_pass_tokens_model.collection.find().count() == 1

    
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


class TestProfileForms(TestCase):

    def setUp(self):
        self.c = Client()
        self.user = User.objects.create_user(password='qwerty', email='foo@test.com')
        self.c.login(email='foo@test.com', password='qwerty')


    def tearDown(self):
        self.c.logout()
        User.objects.all().delete()
    
    def test_update_password(self):
        url = reverse('change_password')

        # Test password update with wrong current password
        response = self.c.post(url, {'current_password': 'wrongoldpass',
            'new_password': '123456'})

            
        errors = dict(response.context['form'].errors.items())

        assert 'current_password' in errors


        updated_user = User.objects.get(id=self.user.id)
    
        assert_true(updated_user.check_password('qwerty'))

        # Test password update
        response = self.c.post(url, {'current_password': 'qwerty', 'new_password': '123456'})

        self.assertRedirects(response, reverse('view_profile'))

        updated_user = User.objects.get(id=self.user.id)
        assert_true(updated_user.check_password('123456'))


    def test_update_profile(self):
        url = reverse('view_profile')

        # Test profile update with the same email - Nothing happens
        response = self.c.post(url, {'email': 'foo@test.com', 'timezone': 'UTC'})


        self.assertRedirects(response, reverse('view_profile'), status_code=302)

        user_preferences = user_preferences_model.get_preferences(user_id=self.user.id)

        assert user_preferences['timezone'] == 'UTC'
        


        response = self.c.post(url, {'email': 'foo@test.com', 'timezone': 'Europe/Sofia'})

        user_preferences = user_preferences_model.get_preferences(user_id=self.user.id)

        assert user_preferences['timezone'] == 'Europe/Sofia'


        # Test profile update with the same email
        response = self.c.post(url, {'email': 'network-operations@maynardnetworks.com', 'timezone': 'UTC'})

        self.assertRedirects(response, reverse('view_profile'), status_code=302)


        updated_user = User.objects.get(id=self.user.id)

        assert updated_user.email == 'network-operations@maynardnetworks.com'


from django.test.client import Client
from django.core.urlresolvers import reverse
from django.test import TestCase
from nose.tools import *

from django.contrib.auth import get_user_model
User = get_user_model()


from amon.apps.users.models import invite_model
from amon.apps.notifications.mail.models import email_model


class TestUsersViews(TestCase):

    def setUp(self):
        self.c = Client()

        self.user = User.objects.create_user(password='qwerty', email='foo@test.com')
        self.user.is_superuser = True
        self.user.save()
        self.c.login(username='foo@test.com', password='qwerty')
        email_model.save_email_settings({'sent_from': 'test@example.com'})

    def tearDown(self):
        self.c.logout()
        self.user.delete()
        User.objects.all().delete()
        email_model.collection.remove()
        

    def _cleanup(self):
        invite_model.collection.remove()

    def test_send_invite(self):
        self._cleanup()

        email = 'invite@test.com'


        url = reverse('view_users')    
        response = self.c.post(url, {'email':email})

        self.assertRedirects(response, reverse('view_users'))
        
        result = invite_model.collection.find().count()

        assert result == 1


    def test_revoke_access(self):
        self._cleanup()
        email = 'revoke@test.com'

        new_user = User.create_user('revoke', 'qwerty', email=email)

        url = reverse('users_revoke_access', kwargs={'user_id': str(new_user.id)})
        response = self.c.get(url)


        assert User.objects.filter(email__iexact=email).count() == 0
        



    def test_confirm_invite(self):
        self._cleanup()
        email = 'confirm@test.com'

        url = reverse('view_users')    
        response = self.c.post(url, {'email':email})

        
        result = invite_model.collection.find_one()
        
        
        url = reverse('users_confirm_invite', 
            kwargs={'invitation_code': result['invitation_code']})
        response = self.c.post(url, {'password':'qwerty'})

        invited_user = User.objects.get(email__iexact=email)

        assert invited_user

        
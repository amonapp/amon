# from django.test.client import Client
# from django.core.urlresolvers import reverse
# from django.test import TestCase
# from nose.tools import *

# from django.contrib.auth import get_user_model
User = get_user_model()


# class TestIntegrationsUrls(TestCase):

#     def setUp(self):
#         self.c = Client()
#         self.user = User.objects.create_user(password='qwerty', email='foo@test.com')
#         self.c.login(username='foo@test.com', password='qwerty')

#     def tearDown(self):
#         self.c.logout()
#         self.user.delete()

        
        

#     def test_integrations_url(self):
#         url = reverse('integrations')    
#         response = self.c.get(url)

#         assert response.status_code == 200



#     def test_integrations_amazon_url(self):
#         url = reverse('integrations_amazon')    
#         response = self.c.get(url)

#         assert response.status_code == 200


#     def test_integrations_digitalocean_url(self):
#         url = reverse('integrations_digitalocean')    
#         response = self.c.get(url)

#         assert response.status_code == 200


#     def test_integrations_linode_url(self):
#         url = reverse('integrations_linode')    
#         response = self.c.get(url)

#         assert response.status_code == 200


#     def test_integrations_rackspace_url(self):
#         url = reverse('integrations_rackspace')    
#         response = self.c.get(url)

#         assert response.status_code == 200


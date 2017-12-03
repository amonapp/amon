from django.test.client import Client
from django.test import TestCase
from django.urls import reverse
from nose.tools import *

from django.contrib.auth import get_user_model
User = get_user_model()
from amon.apps.servers.models import server_model


class TestServerViews(TestCase):

    def setUp(self):
        User.objects.all().delete()


        self.c = Client()
        self.user = User.objects.create_user(password='qwerty', email='foo@test.com')    
        
        self.c.login(username='foo@test.com', password='qwerty')


    def tearDown(self):
        self.c.logout()
        self.user.delete()

        server_model.collection.remove()


    def all_servers_test(self):
    
        url = reverse('servers')    
        response = self.c.get(url)

        assert response.status_code == 200

    def add_server_test(self):
        server_model.collection.remove()

        url = reverse('add_server')

        response = self.c.get(url)

        assert response.status_code == 200

        response = self.c.post(url, {'name': 'test', 'check_every': 60,'keep_data': 30})
        
        created_server = server_model.collection.find_one()

        eq_(created_server['name'], 'test')

        response_url = "{0}#{1}".format(reverse('servers'), created_server['_id'])
        self.assertRedirects(response, response_url)

        server_model.collection.remove()

    def edit_server_test(self):

        server_model.collection.remove()
        server_model.collection.insert({'name': 'test' , 'check_every': 60,'keep_data': 30, "key": "test"})


        server = server_model.collection.find_one()

        url = reverse('edit_server', kwargs={'server_id': server['_id']})
        response = self.c.get(url)


        assert response.status_code == 200


        response = self.c.post(url, {'name': 'changetest', 'check_every': 300,'keep_data': 30})
        
        
        updated_server = server_model.collection.find_one()
        self.assertRedirects(response, reverse('servers'))

        eq_(updated_server['name'], 'changetest')
        eq_(updated_server['check_every'], 300)
        
        
        server_model.collection.remove()


    def delete_server_test(self):

        server_model.collection.remove()
        server_model.collection.insert({'name': 'test'})


        server = server_model.collection.find_one()

        url = reverse('delete_server', kwargs={'server_id': server['_id']})
        response = self.c.get(url)

        self.assertRedirects(response, reverse('servers'))

        deleted_server = server_model.collection.find().count()
        eq_(deleted_server, 0)
        

        
        server_model.collection.remove()
        

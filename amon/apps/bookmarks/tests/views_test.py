from django.test.client import Client
from django.urls import reverse
from django.test import TestCase
from nose.tools import *

from django.contrib.auth import get_user_model
User = get_user_model()
from amon.apps.tags.models import tags_model, tag_groups_model
from amon.apps.bookmarks.models import bookmarks_model


class TestBookmarks(TestCase):

    def setUp(self):
        self.c = Client()
        self.user = User.objects.create_user(password='qwerty', email='foo@test.com')
        

        
        self.c.login(username='foo@test.com', password='qwerty')

    def tearDown(self):
        self.c.logout()
        self.user.delete()



    def _cleanup(self):
        tags_model.collection.remove()
        tag_groups_model.collection.remove()
        bookmarks_model.collection.remove()
        
    


    def add_delete_bookmark_test(self):
        self._cleanup()

        url = reverse('bookmarks_add')
        tags = {'provider': 'digitalocean', 'credentials': 'production'}
    
        
        tag_ids = [str(x) for x in tags_model.create_and_return_ids(tags)]
        tag_ids_str = ",".join(tag_ids)

        form_data = {'name': 'test', 'tags': tag_ids_str, 'type': 'server'}


        response = self.c.post(url, form_data)


        assert response.status_code == 302
        assert bookmarks_model.collection.find().count() == 1



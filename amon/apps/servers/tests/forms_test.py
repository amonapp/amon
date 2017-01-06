from django.test import TestCase
from nose.tools import *


from amon.apps.servers.models import server_model
from amon.apps.servers.forms import ServerForm
from amon.apps.tags.models import tags_model

class TestAddServerForm(TestCase):


    def setUp(self):
        tags_model.collection.remove()
        server_model.collection.remove()


    def tearDown(self):
        tags_model.collection.remove()
        server_model.collection.remove()

        
    def test_form(self):
        tags_string = u'tag1, tag2'
        updated_tags = u'tag1, tag2, tag3'
        form_data = {'name': 'test', 'check_every': 60,'keep_data': 30,
        'tags':tags_string}


        form = ServerForm(data=form_data)
        self.assertEqual(form.is_valid(), True)

        form.save()
        assert tags_model.collection.find().count() == 2

        tags = tags_model.get_tags_ids(tags_string=tags_string)
        server = server_model.collection.find_one()

        assert server.get('tags') == tags
        

        form_data = {'name': 'test', 'check_every': 60,'keep_data': 30,
        'tags':updated_tags}

        form = ServerForm(data=form_data, server=server)
        self.assertEqual(form.is_valid(), True)

        form.save()
        assert tags_model.collection.find().count() == 3

        tags_list = [x.strip() for x in updated_tags.split(',')]

        for r in tags_model.collection.find():
            assert r['name'] in tags_list


        updated_tags_ids = tags_model.get_tags_ids(tags_string=updated_tags)
        server = server_model.collection.find_one()

        assert server.get('tags') == updated_tags_ids
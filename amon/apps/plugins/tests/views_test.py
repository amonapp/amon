from django.test.client import Client
from django.test import TestCase
from django.core.urlresolvers import reverse
from nose.tools import *
import json

from django.contrib.auth import get_user_model
User = get_user_model()
from amon.apps.servers.models import server_model
from amon.apps.plugins.models import plugin_model
from amon.apps.plugins.helpers import flat_to_tree_dict_helper, replace_underscore_with_dot_helper


class TestPluginViews(TestCase):

    def setUp(self):
        self.c = Client()
        self.user = User.objects.create_user(password='qwerty', email='foo@test.com')
        

        self.account_id = 1

        self.c.login(username='foo@test.com', password='qwerty')

        server_model.add('testserver', account_id=self.account_id)
        self.server = server_model.collection.find_one()


    def tearDown(self):
        self.c.logout()
        self.user.delete()
        User.objects.all().delete()
        

        server_model.collection.remove()


    def view_plugins_test(self):
        url = reverse('view_plugins', kwargs={'server_id': self.server['_id']})    

        response = self.c.get(url)

        assert response.status_code == 200


    def view_plugin_with_id(self):
        plugin = plugin_model.get_or_create(name='test1', server_id=self.server['_id'])
        url = reverse('view_plugins', kwargs={'server_id': self.server['_id']})    
        url = "&plugin_id={0}".format(plugin['_id'])

        response = self.c.get(url)

        assert response.status_code == 200


    def _cleanup(self):
        gauges_collection = plugin_model._get_gauges_data_collection()
        gauges_collection.remove()


        plugin_model.collection.remove()


    def ajax_get_gauge_data_after_test(self):

        self._cleanup()

        plugin = plugin_model.get_or_create(name='test1', server_id=self.server['_id'])     

        for i in range(0, 100):
            data = {'t': i, 'count.first': 2, 'count.second': 4, 'count.third': 5}
            plugin_model.save_gauges(data=data, plugin=plugin, time=i)
        
        gauge = plugin_model.get_gauge_by_name(name='count', plugin=plugin)
            
        url = reverse('ajax_get_gauge_data_after')
        url = "{0}?gauge={1}&timestamp=30&enddate=59".format(url, gauge['_id'])

        response = self.c.get(url)

        to_json = json.loads(response.content.decode('utf-8'))

        assert to_json['last_update']
        assert to_json['now_local']

        data = to_json['data']

        eq_(len(data), 3)

        for i in data:
            assert i['name'] in ['second', 'third', 'first']
            assert len(i['data']) == 30
        
        self._cleanup()
    



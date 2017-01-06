from django.test.client import Client
from django.test import TestCase
from nose.tools import *
from nose.tools import nottest

from django.contrib.auth import get_user_model
User = get_user_model()

from amon.apps.api.utils import throttle_status, parse_statsd_data
from amon.utils.dates import unix_utc_now


from amon.apps.servers.models import server_model

class TestThrottle(TestCase):

    def setUp(self):
        self.c = Client()
        self.user = User.objects.create_user(password='qwerty', email='foo@test.com')
        

    def tearDown(self):
        server_model.collection.remove()
        self.user.delete()


    def _cleanup(self):
        server_model.collection.remove()




    def throttle_check_period_test(self):
        self._cleanup()

        buffer_period = 15 # For collectd

        # No data - first check
        server_key = server_model.add('test_name', account_id=1, check_every=60)
        server = server_model.get_server_by_key(server_key)
    

        result = throttle_status(server=server)

        assert result.allow == True

        self._cleanup()


        now = unix_utc_now()

    
        server_key = server_model.add('test_name', account_id=1, check_every=60)
        server = server_model.get_server_by_key(server_key)

        data = {'last_check': now-61}
        server_model.update(data, server['_id'])
        server = server_model.get_server_by_key(server_key)
        

        result = throttle_status(server=server)

        assert result.allow == True


        last_check_plus_buffer = now-54+buffer_period
        
        data = {'last_check': last_check_plus_buffer}
        server_model.update(data, server['_id'])
        server = server_model.get_server_by_key(server_key)
        
        result = throttle_status(server=server)

        assert result.allow == False

        self._cleanup()



        server_key = server_model.add('test_name', account_id=1, check_every=300)
        server = server_model.get_server_by_key(server_key)

        data = {'last_check': now-301}
        server_model.update(data, server['_id'])
        server = server_model.get_server_by_key(server_key)
        

        result = throttle_status(server=server)

        assert result.allow == True

        self._cleanup()


class TestParseStatsD(TestCase):

    
    def parse_data_test(self):

        # First try, ignore derive, only gauges are permitted 
        data =  [{
          u'dstypes':[
             u'derive',
             u'derive'
          ],
          u'plugin':u'disk',
          u'dsnames':[
             u'read',
             u'write'
          ],
          u'interval':10.0,
          u'host':u'ubuntu',
          u'values':[
             2048,
             0
          ],
          u'time':1424265912.232,
          u'plugin_instance':u'sda2',
          u'type_instance':u'',
          u'type':u'disk_octets'
        },]

        result = parse_statsd_data(data)

        assert result == {}


        data =  [{
          u'dstypes':[
             u'gauge',
             u'gauge'
          ],
          u'plugin':u'disk',
          u'dsnames':[
             u'read',
             u'write'
          ],
          u'interval':10.0,
          u'host':u'ubuntu',
          u'values':[
             2048,
             0
          ],
          u'time':1424265912.232,
          u'plugin_instance':u'sda2',
          u'type_instance':u'',
          u'type':u'disk_octets'
        },]


        result = parse_statsd_data(data)

        assert result == {'collectd.disk': {'sda2.write': 0, 'sda2.read': 2048}}


        data =  [{
          u'dstypes':[
             u'gauge',
             u'gauge'
          ],
          u'plugin':u'disk',
          u'dsnames':[
             u'read',
             u'write'
          ],
          u'interval':10.0,
          u'host':u'ubuntu',
          u'values':[
             2048,
             0
          ],
          u'time':1424265912.232,
          u'plugin_instance':u'',
          u'type_instance':u'',
          u'type':u'disk_octets'
        },]


        result = parse_statsd_data(data)
        
        assert result == {'collectd.disk': {'write': 0, 'read': 2048}}

        data = [ {
          u'dstypes':[
             u'gauge'
          ],
          u'plugin':u'processes',
          u'dsnames':[
             u'value'
          ],
          u'interval':10.0,
          u'host':u'ubuntu',
          u'values':[
             501
          ],
          u'time':1424265912.297,
          u'plugin_instance':u'',
          u'type_instance':u'sleeping',
          u'type':u'ps_state'
        }]

        result = parse_statsd_data(data)
    
        assert result == {'collectd.processes': {'processes.value': 501,}}
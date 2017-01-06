import unittest
from nose.tools import *
from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
User = get_user_model()
from amon.apps.servers.models import server_model
from amon.apps.plugins.models import plugin_model
from amon.apps.plugins.helpers import flat_to_tree_dict_helper, replace_underscore_with_dot_helper

class PluginsModelTest(unittest.TestCase):

    def setUp(self):
        self.user = User.objects.create_user(password='qwerty', email='foo@test.com')


        self.account_id = 1

        server_model.collection.remove()

        server_key = server_model.add('test', account_id=self.account_id)

        self.server = server_model.get_server_by_key(server_key)
        self.server_id = self.server['_id']



    def tearDown(self):
        self.user.delete()
        User.objects.all().delete()



    def _cleanup(self):
        plugin_model.collection.remove()
        counters_collection = plugin_model._get_counters_collection()
        counters_collection.remove()

        gauges_collection = plugin_model._get_gauges_data_collection()
        gauges_collection.remove()

    def get_errors_collection_test(self):
        self._cleanup()
        result = plugin_model._get_error_collection()

        eq_(result.name, "plugin_errors")


    def get_counters_collection_test(self):
        self._cleanup()
        result = plugin_model._get_counters_collection()

        eq_(result.name, "plugin_counters_data")


    def get_gauges_data_collection_test(self):
        self._cleanup()
        result = plugin_model._get_gauges_data_collection()

        eq_(result.name, "plugin_gauges_data")



    def get_all_unique_gauge_keys_test(self):
        self._cleanup()

        plugin = plugin_model.get_or_create(name='test1', server_id=self.server['_id'])

        data = {'t': 1, 'count.count_key': 2, 'second.second_key': 4, 'more.more_key': 5}

        plugin_model.save_gauges(plugin=plugin, data=data, time=1)


        result = plugin_model.get_all_unique_gauge_keys_list()

        assert set(result) == set(['test1.count.count_key' ,'test1.second.second_key', 'test1.more.more_key'])


    def get_global_data_after_test(self):
        self._cleanup()



    def get_or_create_plugin_test(self):
        self._cleanup()

        plugin = plugin_model.get_or_create(name='test1', server_id=self.server['_id'])

        eq_(plugin['name'], 'test1')


    def get_gauge_keys_for_server_test(self):
        self._cleanup()

        plugin = plugin_model.get_or_create(name='test1', server_id=self.server['_id'])

        data = {'t': 1, 'count.count_key': 2, 'second.second_key': 4, 'more.more_key': 5}

        plugin_model.save_gauges(plugin=plugin, data=data, time=1)


        result = plugin_model.get_gauge_keys_for_server(server_id=self.server['_id'])


        assert len(result) == 3 # count, second, more
        for r in result:
            assert r['plugin']['_id'] == plugin['_id']
            for key in r['gauge']['keys']:
                assert key in ['count_key', 'second_key', 'more_key']


    def get_plugins_for_server_test(self):
        self._cleanup()


        for i in range(0, 5):
            plugin_model.collection.insert({'name': 'test{0}'.format(i), 'server_id': self.server['_id'] })

        result = plugin_model.get_for_server(server_id=self.server['_id'])

        eq_(result.clone().count(), 5)

        for r in result.clone():
            valid_names = ['test0', 'test1', 'test2', 'test3', 'test4']
            assert r['name'] in valid_names


    def get_gauges_test(self):
        self._cleanup()

        plugin = plugin_model.get_or_create(name='test1', server_id=self.server['_id'])

        data = {'t': 1, 'count.test': 2, 'second.test': 4, 'more.tests': 5 }

        plugin_model.save_gauges(plugin=plugin, data=data, time=1)


        result = plugin_model.get_gauges_list(plugin=plugin)

        self.assertCountEqual(result, ['count', 'second', 'more'])


        self._cleanup()


    def upsert_gauges_test(self):
        self._cleanup()

        plugin = plugin_model.get_or_create(name='test1', server_id=self.server['_id'])

        gauges_data = {'t': 1, 'count.test': 2, 'second.test': 4, 'more.tests': 5 }

        plugin_model.upsert_gauges(plugin=plugin, gauges=gauges_data)

        plugin = plugin_model.get_or_create(name='test1', server_id=self.server['_id'])


        result = plugin_model.get_gauges_list(plugin=plugin) # Excludes t and plugin_id
        self.assertCountEqual(result, ['count', 'second', 'more'])


        data = {'t': 1, 'count.test': 2, 'second.test': 4, 'more.tests': 5, 'evenmore.test':2 }
        result = plugin_model.upsert_gauges(plugin, gauges=data) # Excludes t and plugin_id


        result = plugin_model.get_gauges_list(plugin=plugin) # Excludes t and plugin_id
        self.assertCountEqual(result, ['count', 'second', 'evenmore' ,'more'])



        data = {'t': 1, 'count.test': 2, 'second.test': 4}
        result = plugin_model.upsert_gauges(plugin, gauges=data) # Excludes t and plugin_id


        result = plugin_model.get_gauges_list(plugin=plugin) # Excludes t and plugin_id
        self.assertCountEqual(result, ['count', 'second', 'evenmore' ,'more'])

        self._cleanup()

    def get_gauge_keys_test(self):
        self._cleanup()

        plugin = plugin_model.get_or_create(name='test1', server_id=self.server['_id'])



        data = {'t': 1, 'count.first': 2, 'count.second': 4, 'count.third': 5, }
        plugin_model.save_gauges(data=data, plugin=plugin, time=1)

        gauge = plugin_model.get_gauge_by_name(name='count', plugin=plugin)

        result = plugin_model.get_gauge_keys(gauge=gauge)

        self.assertCountEqual(result, [u'second', u'third', u'first'])


        self._cleanup()



        data = {'t': 1, 'countsecond': 2}
        plugin_model.save_gauges(data=data, plugin=plugin, time=1)

        gauge = plugin_model.get_gauge_by_name(name='countsecond', plugin=plugin)


        result = plugin_model.get_gauge_keys(gauge=gauge)

        self.assertCountEqual(result, [u'value'])



    def get_gauge_data_test(self):
        self._cleanup()


        plugin = plugin_model.get_or_create(name='test1', server_id=self.server['_id'])


        gauges_collection = plugin_model._get_gauges_data_collection()

        for i in range(0, 100):
            data = {'t': i, 'count.first': 11, 'count.second': 22, 'count.third': 33 }
            plugin_model.save_gauges(data=data, plugin=plugin, time=i)

        gauge = plugin_model.get_gauge_by_name(name='count', plugin=plugin)


        result = plugin_model.get_gauge_data_after(timestamp=0, enddate=29, gauge=gauge)

        eq_(len(result), 3)   # first, second, third


        for i in result:
            assert i['name'] in ['first', 'second', 'third']
            assert len(i['data']) == 30

            for point in i['data']:
                assert point['y'] in [33, 22, 11]


        self._cleanup()

        for i in range(0, 100):
            data = {'t': i, 'count': 2}
            plugin_model.save_gauges(data=data, plugin=plugin, time=i)

        result = plugin_model.get_gauge_data_after(timestamp=0, enddate=29,  gauge=gauge)

        eq_(len(result),1 )  # count

        count = result[0]

        eq_(count['name'], 'value') # Single value
        eq_(len(count['data']), 30)



        self._cleanup()


    def get_counters_test(self):
        self._cleanup()

        plugin = plugin_model.get_or_create(name='test1', server_id=self.server['_id'])


        counters_collection = plugin_model._get_counters_collection()
        data = {'t': 1, 'count.test': 2, 'second.test': 4, 'more.tests': 5 }
        formated_data = flat_to_tree_dict_helper(data)
        formated_data['plugin_id'] = plugin['_id']
        formated_data['server_id'] = self.server_id

        counters_collection.insert(formated_data)

        result = plugin_model.get_counters(server=self.server, plugin=plugin) # Excludes t and plugin_id
        eq_(result, {u'count': {u'test': 2}, u'second': {u'test': 4}, u't': 1, u'more': {u'tests': 5}})

        self._cleanup()


    def save_counters_test(self):
        self._cleanup()

        plugin = plugin_model.get_or_create(name='test1', server_id=self.server['_id'])

        counter_data = {
            u'rows.inserted': 4, u'rows.updated': 6, u'rows.deleted': 4,
            u'rows.returned': 1832119, u'rows.fetched': 680425,
            u'xact.rollbacks': 0, u'xact.commits': 26869,
            u'performance.disk_read': 170, u'performance.buffer_hit': 1711069
        }


        plugin_model.save_counters(data=counter_data, plugin=plugin, server=self.server)

        collection = plugin_model._get_counters_collection()

        for r in collection.find():
            self.assertEqual(sorted(r.keys()), sorted([u'server_id', u'rows', u't', u'xact', u'performance', u'plugin_id', u'_id']))

            rows = r['rows']

            eq_(r['plugin_id'], plugin['_id'])
            self.assertTrue(r['t'], int)

            self.assertEqual(rows, {u'deleted': 4, u'inserted': 4, u'updated': 6, u'fetched': 680425, u'returned': 1832119})

            rows = r['xact']
            self.assertEqual(rows, {u'commits': 26869, u'rollbacks': 0})

            rows = r['performance']
            self.assertEqual(rows, {u'buffer_hit': 1711069, u'disk_read': 170})


        # Test duplicates - the counters should be only a single entry in the collection
        collection.remove()
        for i in range(0, 10):
            plugin_model.save_counters(data=counter_data, plugin=plugin, server=self.server)

        result = collection.find().count()
        eq_(result, 1)

        self._cleanup()


    def flatten_plugin_data_test(self):
        self._cleanup()

        data = {u'custom': {u'custom.ping.amoncx': {u'gauges': {u'ping.amoncx.lookup_time': 0.126, u'ping.amoncx.connect_time': 0.167, u'ping.amoncx.total': 0.502}},
            u'custom.requests': {u'gauges': {u'requests.max': 263, u'requests.per_second': 188}},
            u'custom.connections': {u'gauges': {u'connections.error': 18, u'connections.active': 181}}},
            'sensu': {u'sensu.iostat': {u'gauges': {u'avg-cpu.pct_nice': u'0', u'sda.wkB_per_s': u'0'}}},
            u'apache': {u'gauges': {u'requests.request_per_second': 0.0144365, u'workers.idle': 9}}}

        formated_data = plugin_model.flatten_plugin_data(data)
        keys = formated_data.keys()

        assert 'custom.ping.amoncx' in keys
        assert 'custom.requests' in keys
        assert 'custom.connections' in keys
        assert 'apache' in keys
        assert 'sensu.iostat' in keys

        assert 'sensu' not in keys
        assert 'custom' not in keys


    def format_telegraf_to_amon_test(self):
        self._cleanup()

        expires_at = datetime.utcnow()+timedelta(hours=24)

        data = [
            {u'metric': u'memcached.get.hits', u'metrics': [[1447751280.0, 120.0]]},
            {u'metric': u'memcached.get.misses', u'metrics': [[1447751280.0, 50.0]]},
            {u'metric': u'memcached.evictions', u'metrics': [[1447751280.0, 0]]},
            {u'metric': u'memcached.limit.maxbytes', u'metrics': [[1447751280.0, 67108864.0]]}
        ]


        formated_data = plugin_model.format_telegraf_to_amon(data=data, server=self.server, expires_at=expires_at)
        assert formated_data == {u'memcached': {'gauges': {u'get.misses': 50.0, u'limit.maxbytes': 67108864.0, u'evictions': 0, u'get.hits': 120.0}}}


        # Telegraf 0.10
        data_telegraf_010 = [

            {u'metric': u'diskio_read.time', u'metrics': [[1455923510.0, 108644]]}, 
            {u'metric': u'diskio_reads', u'metrics': [[1455923510.0, 134188]]}, 
            {u'metric': u'diskio_write.bytes', u'metrics': [[1455923510.0, 35673124864.0]]}, 
            {u'metric': u'diskio_write.time', u'metrics': [[1455923510.0, 8670312.0]]}, 
            {u'metric': u'diskio_writes', u'metrics': [[1455923510.0, 5914627.0]]}, 
            {u'metric': u'diskio_io.time', u'metrics': [[1455923510.0, 306176]]}, 
            {u'metric': u'diskio_read.bytes', u'metrics': [[1455923510.0, 2282908672.0]]}, 
            {u'metric': u'diskio_write.bytes', u'metrics': [[1455923510.0, 35673124864.0]]}, 
            {u'metric': u'diskio_write.time', u'metrics': [[1455923510.0, 8670312.0]]}, 
            {u'metric': u'diskio_writes', u'metrics': [[1455923510.0, 5914627.0]]}, 
            {u'metric': u'diskio_io.time', u'metrics': [[1455923510.0, 306148]]}, 
            {u'metric': u'diskio_read.bytes', u'metrics': [[1455923510.0, 2281174016.0]]},
            {u'metric': u'diskio_read.time', u'metrics': [[1455923510.0, 108612]]}, 
            {u'metric': u'diskio_reads', u'metrics': [[1455923510.0, 133763]]}, 
            {u'metric': u'diskio_read.bytes', u'metrics': [[1455923510.0, 10240]]}, 
            {u'metric': u'diskio_read.time', u'metrics': [[1455923510.0, 0]]},
            {u'metric': u'diskio_reads', u'metrics': [[1455923510.0, 4]]}, 
            {u'metric': u'diskio_write.bytes', u'metrics': [[1455923510.0, 0]]},
            {u'metric': u'diskio_write.time', u'metrics': [[1455923510.0, 0]]}, 
            {u'metric': u'diskio_writes', u'metrics': [[1455923510.0, 0]]}, 
            {u'metric': u'diskio_io.time', u'metrics': [[1455923510.0, 0]]}, 
            {u'metric': u'diskio_reads', u'metrics': [[1455923510.0, 242]]}, 
            {u'metric': u'diskio_write.bytes', u'metrics': [[1455923510.0, 0]]}, 
            {u'metric': u'diskio_write.time', u'metrics': [[1455923510.0, 0]]}, 
            {u'metric': u'diskio_writes', u'metrics': [[1455923510.0, 0]]}, 
            {u'metric': u'diskio_io.time', u'metrics': [[1455923510.0, 24]]}, 
            {u'metric': u'diskio_read.bytes', u'metrics': [[1455923510.0, 991232]]},
            {u'metric': u'diskio_read.time', u'metrics': [[1455923510.0, 24]]}, 
            {u'metric': u'ping_average.response.ms', u'metrics': [[1455923510.0, 2.097]]}, 
            {u'metric': u'ping_packets.received', u'metrics': [[1455923510.0, 1]]}, 
            {u'metric': u'ping_packets.transmitted', u'metrics': [[1455923510.0, 1]]}, 
            {u'metric': u'ping_percent.packet.loss', u'metrics': [[1455923510.0, 0]]}

        ]

        formated_data = plugin_model.format_telegraf_to_amon(data=data_telegraf_010, server=self.server, expires_at=expires_at)

        valid_keys =  [u'ping_percent', u'diskio_write', u'diskio_read', u'diskio_writes',
             u'ping_average', u'diskio_reads', u'diskio_io', u'ping_packets']

        for k in formated_data.keys():
            assert k in valid_keys
        


    def save_gauges_test(self):
        self._cleanup()


        expires_at = datetime.utcnow()+timedelta(hours=24)


        plugin = plugin_model.get_or_create(name='test1', server_id=self.server['_id'])
        gauge_data = {
            u'performance.cpu_load': 1.08719, u'performance.busy_workers': 117.0,
            u'performance.idle_workers': 523.0, u'net.bytes': 86855934115.0,
            u'requests.per.second': 140.7, u'net.hits': 35534902.0
        }

        plugin_model.save_gauges(data=gauge_data, plugin=plugin, time=1, expires_at=expires_at)

        collection = plugin_model._get_gauges_data_collection()

        gauges = plugin_model.get_gauges_cursor(plugin=plugin)

        gauges_dict = {}
        for g in gauges:
            gauges_dict[str(g['_id'])] = g['name']


        for r in collection.find():
            gauge_id = str(r['gauge_id'])

            gauge_name = gauges_dict[gauge_id]
            assert gauge_name in ['net', 'performance', 'requests']
            self.assertTrue(r['t'], int)
            self.assertEqual(r['expires_at'].date(), expires_at.date())

            if gauge_name == 'net':
                self.assertCountEqual(r.keys(), [u't', u'hits', u'bytes', u'gauge_id', u'_id', 'expires_at'])

                self.assertEqual(r['hits'], 35534902.0)
                self.assertEqual(r['bytes'], 86855934115.0)

            elif gauge_name == 'performance':

                self.assertCountEqual(r.keys(), [u't', u'cpu_load', u'busy_workers', u'idle_workers', u'gauge_id', u'_id', 'expires_at'])

                self.assertEqual(r['cpu_load'],  1.08719)
                self.assertEqual(r['busy_workers'], 117.0)
                self.assertEqual(r['idle_workers'], 523.0)

            elif gauge_name == 'requests':

                self.assertCountEqual(r.keys(), [u't', u'per_second', u'gauge_id', u'_id', 'expires_at'])

                self.assertEqual(r['per_second'],  140.7)


        self._cleanup()


    def delete_gauges_test(self):
        self._cleanup()

        plugin = plugin_model.get_or_create(name='test1', server_id=self.server['_id'])
        gauge_data = {u'performance.cpu_load': 1.08719, u'performance.busy_workers': 117.0,}

        for i in range(0, 10):
            plugin_model.save_gauges(data=gauge_data, plugin=plugin)

        collection = plugin_model._get_gauges_data_collection()

        result = collection.find().count()
        eq_(result, 10)

        plugin_model.delete_gauges(plugin=plugin)
        result = collection.find().count()


        eq_(result, 0)

        self._cleanup()


    def get_check_for_timestamp_test(self):

        self._cleanup()

        gauges_collection = plugin_model._get_gauges_data_collection()
        plugin = plugin_model.get_or_create(name='test1', server_id=self.server['_id'])
        plugin_with_error = plugin_model.get_or_create(name='error1', server_id=self.server['_id'])

        for i in range(0, 100):
            data = {'t': i, 'count.first': 2, 'count.second': 4, 'count.third': 5 }
            formated_data = flat_to_tree_dict_helper(data)
            formated_data['plugin_id'] = plugin['_id']
            formated_data['server_id'] = self.server_id

            gauges_collection.insert(formated_data)


        error_data = {'plugin_id': plugin_with_error['_id'], 'server_id': self.server_id,
        't': 10, 'error': 'Argghh'}
        error_collection = plugin_model._get_error_collection()
        error_collection.insert(error_data)

        result = plugin_model.get_check_for_timestamp(self.server, 10)


        for r in result:
            assert r['name'] in ['test1', 'error1']

        self._cleanup()



    def delete_counters_test(self):
        self._cleanup()

        plugin = plugin_model.get_or_create(name='test1', server_id=self.server['_id'])
        gauge_data = {u'performance.cpu_load': 1.08719, u'performance.busy_workers': 117.0,}

        for i in range(0, 10):
            plugin_model.save_counters(data=gauge_data, plugin=plugin, server=self.server)

        collection = plugin_model._get_counters_collection()

        result = collection.find().count()
        eq_(result, 1)

        plugin_model.delete_counters(server=self.server, plugin=plugin)
        result = collection.find().count()
        eq_(result, 0)

        self._cleanup()


    def get_table_data_collection_test(self):
        self._cleanup()

        plugin = plugin_model.get_or_create(name='test1', server_id=self.server['_id'])

        result = plugin_model._get_table_data_collection(plugin=plugin, table_name='testme')

        eq_(result.name, "plugin_test1_testme_data")



    def get_save_table_data_test(self):
        self._cleanup()

        plugin = plugin_model.get_or_create(name='nginx', server_id=self.server['_id'])
        data = {
            'headers': [u'visitors', u'hits', u'bytes', u'percent', u'data'],
            'data': [
                [1, 34, 0, 3.91, u'/static/css/screen.css'],
                [1, 34, 0, 3.91, u'/static/js/libs/libs.min.js'],
                [1, 33, 0, 3.8, u'/static/css/chart.css']
            ]
        }
        plugin_model.save_table_data(data=data, server=self.server,
            plugin=plugin,
            table_name='requests',
            find_by_string='data')

        data_collection = plugin_model._get_table_data_collection(plugin=plugin, table_name='requests')

        assert data_collection.find().count() == 3

        result = plugin_model.get_table_data(server=self.server,
                plugin=plugin,
                table_name='requests')

        assert set(result['header']) == set(data['headers'])
        assert result['data'].count() == 3


        # Check if it doesnt create duplicates
        plugin_model.save_table_data(data=data, server=self.server,
            plugin=plugin,
            table_name='requests',
            find_by_string='data')

        assert data_collection.find().count() == 3


        data_collection.remove()
        plugin_model.collection.remove()
        # Check for the harders - sql queries

        plugin = plugin_model.get_or_create(name='mysql', server_id=self.server['_id'])
        data_collection = plugin_model._get_table_data_collection(plugin=plugin, table_name='slow_queries')
        data_collection.remove()

        data = {'headers': ['query_time', 'rows_sent', 'rows_examined', 'lock_time', 'db', 'query', 'start_time'],
        'data': [
            [3.0, 1, 0, 0.0, 'wordpress', 'select BENCHMARK(500000000, EXTRACT(YEAR FROM NOW()))', '2015-04-22 23:50:40'],
            [12.0, 1, 0, 0.0, 'wordpress', 'select BENCHMARK(5000000, EXTRACT(YEAR FROM NOW()))', '2015-04-22 23:00:22']
        ]
        }

        plugin_model.save_table_data(data=data, server=self.server,
            plugin=plugin,
            table_name='slow_queries',
            find_by_string='query',
            unique_hash=True)

        assert data_collection.find().count() == 2

        result = plugin_model.get_table_data(server=self.server,
                plugin=plugin,
                table_name='slow_queries',
                additional_ignore_keys=['unique_hash'])

        assert set(result['header']) == set(data['headers'])
        assert result['data'].count() == 2


        data = {'headers': ['query_time', 'rows_sent', 'rows_examined', 'lock_time', 'db', 'query', 'start_time'],
        'data': [
            [3.0, 1, 0, 0.0, 'wordpress', 'select BENCHMARK(500000000, EXTRACT(YEAR FROM NOW()))', '2015-04-22 23:50:40'],
            [12.0, 1, 0, 0.0, 'wordpress', 'select BENCHMARK(5000000, EXTRACT(YEAR FROM NOW()))', '2015-04-22 23:00:22']
        ]
        }

        plugin_model.save_table_data(data=data, server=self.server,
            plugin=plugin,
            table_name='slow_queries',
            find_by_string='query',
            unique_hash=True)

        assert data_collection.find().count() == 2

        result = plugin_model.get_table_data(server=self.server,
                plugin=plugin,
                table_name='slow_queries',
                additional_ignore_keys=['unique_hash'])

        assert set(result['header']) == set(data['headers'])
        assert result['data'].count() == 2

        self._cleanup()

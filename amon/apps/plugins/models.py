from amon.apps.core.basemodel import BaseModel
from amon.utils.charts import colors, select_colors
from amon.apps.plugins.helpers import flat_to_tree_dict_helper, replace_underscore_with_dot_helper
from amon.utils.dates import utc_unixtime_to_localtime, unix_utc_now
from amon.apps.plugins.utils import create_unique_hash, get_find_by_string_param, sort_header

class PluginModel(BaseModel):

    def __init__(self):
        super(PluginModel, self).__init__()
        self.collection = self.mongo.get_collection('plugins')
        self.gauge_collection = self.mongo.get_collection('plugin_gauges')


    def _get_counters_collection(self):
        collection = self.mongo.get_collection("plugin_counters_data")

        return collection

    def _get_gauges_data_collection(self,):
        collection = self.mongo.get_collection("plugin_gauges_data")

        return collection


    def _get_table_data_collection(self, plugin=None, table_name=None):
        name = plugin.get('name')
        collection_name = "plugin_{plugin}_{table_name}_data".format(plugin=name, table_name=table_name)
        collection = self.mongo.get_collection(collection_name)

        return collection


    def _get_error_collection(self,):
        collection = self.mongo.get_collection("plugin_errors")

        return collection


    def get_all_unique_gauge_keys_list(self):
        unique_list = []
        result = []

        query = self.get_all()

        for r in query:
            plugin_name = r.get('name')

            if plugin_name not in unique_list:
                gauges = self.get_gauges_cursor(plugin=r)
                for gauge in gauges:
                    gauge_name = gauge.get('name')
                    names = ["{0}.{1}.{2}".format(plugin_name, gauge_name, x) for x in gauge['keys']]
                    result.append(names)


                unique_list.append(plugin_name)

        result = [val for sublist in result for val in sublist]
        return result

    def get_last_check(self, server=None, plugin=None):

        plugin_gauges = self.get_gauges_cursor(plugin=plugin)
        data_collection = self._get_gauges_data_collection()

        time = None
        checks_list = []
        for gauge in plugin_gauges:

            params = {'gauge_id': gauge['_id']}
            result = data_collection.find_one(params, sort=[('t', self.desc)])
            if result:
                checks_list.append(result['t'])


        if len(checks_list) > 0:
            time = max(checks_list)


        return time

    def get_first_check(self, server=None, plugin=None):
        plugin_gauges = self.get_gauges_cursor(plugin=plugin)
        data_collection = self._get_gauges_data_collection()

        time = None

        checks_list = []
        for gauge in plugin_gauges:
            params = {'gauge_id': gauge['_id']}
            result = data_collection.find_one(params, sort=[('t', self.asc)])
            if result:
                checks_list.append(result['t'])

        if len(checks_list) > 0:
            time = min(checks_list)

        return time


    def get_or_create(self, name=None, server_id=None):
        params = {"server_id": server_id, "name": name}
        params = self.keys_to_mongoid(params, ['server_id', ])
        result = super(PluginModel, self).get_or_create(params)

        self.collection.ensure_index([('server_id', self.desc)], background=True)

        return result


    # Used in notifications/generator
    def get_by_name_and_server_id(self, name=None, server_id=None):
        params = {"server_id": server_id, "name": name}
        params = self.keys_to_mongoid(params, ['server_id', ])

        result = self.collection.find_one(params)

        return result

    def get_gauge_by_name_and_plugin_id(self, name=None, plugin=None):

        params = {"plugin_id": plugin['_id'], "name": name}


        result = self.gauge_collection.find_one(params)

        return result




    def get_gauge_keys_for_server(self, server_id=None):
        result = []
        server_id = self.object_id(server_id)

        if server_id:
            plugins = self.get_for_server(server_id=server_id)
            for p in plugins:
                plugin_gauges = self.get_gauges_cursor(plugin=p)
                for gauge in plugin_gauges:
                    gauge_keys = gauge.get('keys', [])
                    for key in gauge_keys:
                        gauge_dict = {
                            'plugin': p,
                            'gauge': gauge,
                            'key': key
                        }

                        result.append(gauge_dict)

        return result


    def get_for_server(self, server_id=None, last_check_after=None):
        result = None

        server_id = self.object_id(server_id)

        if server_id:
            params = {"server_id": server_id}

            if last_check_after:
                params['last_check'] = {"$gte": int(last_check_after)}

            result = self.collection.find(params)

        return result

    # Make sure gauges are with unique names
    #
    #  Data structure - plugin_gauges
    #
    # {'plugin_id': 1, 'name': 'gauge_unique_name'}
    #
    # plugin_gauges_data, multiple keys:
    #
    #     {'gauge_id': 1, 'read': 1, 'write': 5, 'time': 100} - keys, everything except gauge_id and time
    #
    # for a single key ->
    #
    #     {'gauge_id': 1, 'value': 1, 'time': 100}
    #
    def upsert_gauges(self, plugin=None, gauges=None):

        # Example data - {'t': 1, 'count.test': 2, 'second.test': 4, 'more.tests': 5 }
        formated_data = flat_to_tree_dict_helper(gauges)

        excluded_keys = ['_id', 't', 'plugin_id', 'server_id','expires_at']
        filtered_gauges = list((key) for key in formated_data.keys() if key not in excluded_keys)

        for g in filtered_gauges:
            gauge_params = {'name': g, 'plugin_id': plugin['_id']}
            result = self.gauge_collection.find_one(gauge_params)
            if result == None:
                self.gauge_collection.insert(gauge_params)


    def get_gauges_cursor(self, plugin=None):
        gauges = self.gauge_collection.find({'plugin_id': plugin['_id']})
        return gauges

    def get_gauges_key_list(self, plugin=None):
        gauge_keys = []

    def get_gauges_list(self, plugin=None):
        gauge_list = []
        gauge_cursor = self.get_gauges_cursor(plugin=plugin)

        for g in gauge_cursor:
            gauge_list.append(g.get('name'))

        return gauge_list


    def get_gauge_by_id(self, gauge_id=None,):
        params = {'_id': gauge_id}
        params = self.keys_to_mongoid(params, ['_id', ])

        return self.gauge_collection.find_one(params)


    def get_gauge_by_name(self, plugin=None, name=None):
        params = {'plugin_id': plugin['_id'], 'name': name}

        return self.gauge_collection.find_one(params)


    def get_or_create_gauge_by_name(self, plugin=None, name=None, keys=None):
        result = None
        params = {'plugin_id': plugin['_id'], 'name': name}

        result = self.gauge_collection.find_one(params)
        if result == None:
            self.gauge_collection.insert(params)

            result = self.gauge_collection.find_one(params)

        if result:
            self.gauge_collection.update(params, {"$set": {"keys": keys}}, upsert=True)

        self.gauge_collection.ensure_index([('plugin_id', self.desc)], background=True)


        return result

    def get_gauge_keys(self, gauge=None):
        gauge_keys = None
        data_collection = self._get_gauges_data_collection()

        params = {'gauge_id': gauge['_id']}

        plugin_data = data_collection.find_one(params, sort=[('t', self.desc)])



        excluded_keys = ['_id', 't', 'gauge_id', 'expires_at']

        if plugin_data:
            gauge_keys = list((key) for key in plugin_data.keys() if key not in excluded_keys)

        return gauge_keys



    def _get_gauge_data_after_query(self, timestamp, gauge=None):
        data_collection = self._get_gauges_data_collection()

        params = {
            "t": {"$gte": int(timestamp)},
            "gauge_id": gauge['_id'],
        }

        query = data_collection.find(params).sort('t', self.asc)

        return query




    def _get_gauge_data_for_period_query(self, timestamp=None, enddate=None, gauge=None):
        data_collection = self._get_gauges_data_collection()

        params = {
            "t": {"$gte": int(timestamp),"$lte": int(enddate)},
            "gauge_id": gauge['_id'],
        }

        query = data_collection.find(params).sort('t', self.asc)

        return query


    def get_global_data_after(self, timestamp=None, metric=None, filtered_servers=None, timezone='UTC'):
        gauge = metric.get('gauge')
        key = metric.get('key')
        plugin = metric.get('plugin')

        keys = {}

        data_lists = {}
        for server in filtered_servers:
            server_id = str(server['_id'])
            keys[server_id] = server.get('name')
            data_lists[server_id] = []

        plugins = self.collection.find({'name': plugin})

        for p in plugins:
            p_server_id = str(p.get('server_id'))
            server_list = data_lists.get(p_server_id)


            result = None
            gauge_cursor = self.get_gauge_by_name(plugin=p, name=gauge)
            if gauge_cursor != None:
                if key in gauge_cursor.get('keys'):
                    result = self._get_gauge_data_after_query(timestamp, gauge=gauge_cursor)

            if result:
                for r in result:
                    time = utc_unixtime_to_localtime(r['t'], tz=timezone)
                    value = r.get(key, None)
                    server_list.append({"x": time, "y": value})

        series = []

        for server, server_name in keys.items():
            _index = keys.keys().index(server)
            data = [] if len(data_lists[server]) == 0 else data_lists[server]
            chart_colors = select_colors(_index)

            result = {
                'name': server_name,
                'data': data
            }

            result.update(chart_colors)

            if len(data) > 0:
                series.append(result)


        return series


    def get_gauge_data_after(self, enddate=None, timestamp=None, gauge=None, timezone='UTC'):

        if enddate:
            result = self._get_gauge_data_for_period_query(timestamp=timestamp, enddate=enddate, gauge=gauge)
        else:
            result = self._get_gauge_data_after_query(timestamp, gauge=gauge)


        gauge_keys = self.get_gauge_keys(gauge=gauge)


        series = []
        gauge_dict = {}

        # Search and iterate over the data only if there are gauge keys
        if gauge_keys:
            for key in gauge_keys:
                gauge_dict[key] = []

            for r in result:
                time = utc_unixtime_to_localtime(r['t'], tz=timezone)


                for key in gauge_keys:
                    value = r.get(key, 0)
                    if not value:
                        value = r.get('value', 0)

                    gauge_dict[key].append({"x": time, "y": value})

            # Eliminate empty lines
            for key in gauge_keys:
                y_axis_sum = sum([x.get('y', 0) for x in gauge_dict[key]])
                if y_axis_sum == 0:
                    gauge_dict[key] = []


            for i, key in enumerate(gauge_keys):
                data = [] if len(gauge_dict[key]) == 0 else gauge_dict[key]

                result = {
                    'color': colors[i],
                    'name': replace_underscore_with_dot_helper(key),
                    'data': data
                }

                if len(data) > 0:
                    series.append(result)


        return series


    def get_counters(self, server=None, plugin=None):
        collection = self._get_counters_collection()


        params = {'plugin_id': plugin['_id'], 'server_id': server['_id']}
        result = collection.find_one(params)


        if result != None:
            try:
                del result['_id']
                del result['plugin_id']
                del result['server_id']
                del result['k']
            except:
                pass


        result = replace_underscore_with_dot_helper(result)


        return result

    def save_counters(self, data=None, server=None, plugin=None, time=None):
        if data is None:
            return

        formated_data = flat_to_tree_dict_helper(data)
        collection = self._get_counters_collection()

        if len(formated_data) > 0:
            params = {'plugin_id': plugin['_id'], 'server_id': server['_id']}
            collection.remove(params)

            formated_data['plugin_id'] = plugin['_id']
            formated_data['server_id'] = server['_id']
            formated_data['t'] = time if time else unix_utc_now()

            collection.insert(formated_data)

            collection.ensure_index([('server_id', self.desc)], background=True)
            collection.ensure_index([('plugin_id', self.desc)], background=True)


    def save_gauges(self, data=None, plugin=None, time=None, expires_at=None):
        if data is None:
            return

        formated_data = flat_to_tree_dict_helper(data)
        collection = self._get_gauges_data_collection()

        excluded_keys = ['_id', 't', 'gauge_id', 'expires_at']

        for key, value in formated_data.items():
            if key not in excluded_keys:
                gauge_data = {}

                gauge_keys = []
                if type(value) is dict:
                    gauge_keys = list(value.keys())  # Python 3.5
                gauge = self.get_or_create_gauge_by_name(plugin=plugin, name=key, keys=gauge_keys)

                if type(value) is dict:
                    gauge_data.update(value)  # Multiple keys {"read":1, "write":3, 'waiting': 5}
                else:
                    gauge_data['value'] = value  # Just the value, : 1

                gauge_data['t'] = time
                gauge_data['gauge_id'] = gauge['_id']
                gauge_data['expires_at'] = expires_at

                collection.insert(gauge_data)
                collection.ensure_index([('gauge_id', self.desc)], background=True)
                collection.ensure_index([('t', self.desc)], background=True)

                collection.ensure_index([('expires_at', 1)], expireAfterSeconds=0)


    def delete(self, plugin=None, server=None):
        self.delete_gauges(plugin=plugin)
        self.delete_counters(plugin=plugin, server=server)
        super(PluginModel, self).delete(plugin['_id'])

    def delete_gauges(self, plugin=None):
        collection = self._get_gauges_data_collection()

        gauges = self.gauge_collection.find({'plugin_id': plugin['_id']})

        for g in gauges:
            params = {'gauge_id': g['_id']}
            collection.remove(params)


    def delete_counters(self, server=None, plugin=None):
        collection = self._get_counters_collection()
        params = {'plugin_id': plugin['_id'], 'server_id': server['_id']}

        collection.remove(params)


    def save_error(self, data=None, server=None, plugin=None, time=None):
        collection = self._get_error_collection()

        params = {'plugin_id': plugin['_id'], 'server_id': server['_id']}

        collection.remove(params)
        params['t'] = time if time else unix_utc_now()
        params['error'] = data
        collection.insert(params)

        collection.ensure_index([('server_id', self.desc)], background=True)
        collection.ensure_index([('plugin_id', self.desc)], background=True)
        collection.ensure_index([('t', self.desc)], background=True)


    def save_table_data(self, data=None, server=None, plugin=None,
        find_by_string=None,
        table_name=None,
        unique_hash=False):

        if data is None:
            return

        collection = self._get_table_data_collection(plugin=plugin, table_name=table_name)
        params = {'plugin_id': plugin['_id'], 'server_id': server['_id']}
        header_row = data.get('headers')
        table_data = data.get('data')

        if header_row is None or table_data is None:
            return

        for row in data.get('data'):
            result = dict(zip(header_row, row))

            name = result.get(find_by_string)
            update_params = {find_by_string: name}


            # Converts SQL queries to MD5 for faster search and identification
            if unique_hash:
                unique_hash = create_unique_hash(name)
                result['unique_hash'] = unique_hash
                update_params = {"unique_hash": unique_hash}


            result['last_update'] = unix_utc_now()
            result.update(params)
            collection.update(update_params, {"$set": result}, upsert=True)

        # find_by_string is different for different datasets - ns, name, data, table_name, etc
        if unique_hash:
            collection.ensure_index([('unique_hash', self.desc)], background=True)
        else:
            collection.ensure_index([(find_by_string, self.desc)], background=True)


        collection.ensure_index([('last_update', self.desc)], background=True)
        collection.ensure_index([('server_id', self.desc)], background=True)
        collection.ensure_index([('plugin_id', self.desc)], background=True)



    def get_table_data(self, server=None,
        plugin=None,
        additional_ignore_keys=None,
        table_name=None):

        collection = self._get_table_data_collection(plugin=plugin, table_name=table_name)

        result = {
            'header': [],
            'data': []
        }

        params = {'plugin_id': plugin['_id'], 'server_id': server['_id']}

        query = collection.find(params).sort('last_update', self.desc)

        ignored_keys = ['plugin_id','_id', 'server_id', 'last_update']
        if additional_ignore_keys:
            ignored_keys.extend(additional_ignore_keys)

        if query.clone().count() > 0:
            try:
                # Get headers
                keys = list(set(query[0].keys()) - set(ignored_keys))
            except:
                keys = False

            keys = sort_header(keys)

            if keys:
                result['header'] = keys
                result['data'] = [element for element in query]

        return result



    # This is needed for the golang agent - sensu and custom plugins
    def flatten_plugin_data(self, data=None):
        formatted_dict = data.copy()
        for name, dict in data.items():

            # Flatten dictionary for sensu and custom plugins
            if name in ["custom", "sensu", "telegraf"]:
                formatted_dict.update(dict.copy())

                try:
                    del formatted_dict[name]
                except:
                    pass


        return formatted_dict



    def format_telegraf_to_amon(self, server=None, name=None, data=None, time=None, expires_at=None):
        # Format data
        plugin_data = {}
        for m in data:
            metric = m.get('metric')
            metrics = m.get('metrics', {})
            
            try:
                # diskio_read.time
                plugin_name, gauge_name = metric.split('.', 1)
            except:
                plugin_name = metric
                gauge_name = "value"
                gauge = "value"
                # diskio_reads

            if len(metrics) > 0:
                value = metrics[0][1]  # u'metrics': [[1447751280.0, 120.0]]

            # Check if the dict exist
            exists = plugin_data.get(plugin_name)
            if not exists:
                plugin_data[plugin_name] = {'gauges': {}}

            plugin_data[plugin_name]['gauges'][gauge_name] = value
        
        return plugin_data

    def save_data(self, server=None, name=None, data=None, time=None, expires_at=None):

        plugin = self.get_or_create(name=name, server_id=server['_id'])

        counters = data.get('counters', {})
        gauges = data.get('gauges', {})
        error = data.get('error')

        # Additional data list
        plugin_table_data = ['slow_queries',
            'tables_size',
            'index_hit_rate',
            'not_found',
            'requests'
        ]

        for t in plugin_table_data:
            table_data = data.get(t)
            if table_data:
                unique_hash = True if t in ['slow_queries'] else False
                find_by_string = get_find_by_string_param(name=name, table_data_type=t)

                plugin_model.save_table_data(
                    data=table_data,
                    server=server,
                    plugin=plugin,
                    find_by_string=find_by_string,
                    unique_hash=unique_hash,
                    table_name=t
                )
                self.update({'last_check': time}, plugin['_id'])


        if error:
            self.save_error(data=error, plugin=plugin, server=server, time=time)
        else:
            if gauges:
                self.save_gauges(data=gauges, plugin=plugin, time=time, expires_at=expires_at)

            if counters:
                self.save_counters(data=counters, plugin=plugin, server=server, time=time)


            self.update({'last_check': time}, plugin['_id'])

            self.collection.ensure_index([('last_check', self.desc)], background=True)

        return plugin


    def get_check_for_timestamp(self, server, timestamp):
        result = []

        errors_collection = self._get_error_collection()

        all_plugins = self.get_for_server(server_id=server['_id'])
        result = []


        for plugin in all_plugins:

            params = {'t': timestamp, 'plugin_id': plugin['_id']}
            error = errors_collection.find_one(params)
            error_message = error.get('error') if error else None

            last_check = plugin.get('last_check', 0)

            #  Add 5 minutes buffer
            if (last_check + 300) < timestamp:
                error = True

            plugin_dict = {
                'name': plugin.get('name'),
                'id': plugin.get('_id'),
                'error': error,
                'error_message':error_message,
                'last_check': last_check
            }
            result.append(plugin_dict)

        return result


plugin_model = PluginModel()

from operator import itemgetter
from django.urls import reverse

from amon.apps.core.basemodel import BaseModel
from amon.apps.api.utils import generate_api_key
from amon.utils.dates import unix_utc_now

from amon.templatetags.charts import yaxis
from amon.apps.processes.models import process_model
from amon.apps.servers.models import server_model
from amon.apps.system.models import system_model
from amon.apps.plugins.models import plugin_model
from amon.apps.devices.models import volumes_model, interfaces_model
from amon.apps.tags.models import tags_model
from amon.apps.healthchecks.models import health_checks_model


class DashboardModel(BaseModel):

    def __init__(self):
        super(DashboardModel, self).__init__()
        self.collection = self.mongo.get_collection('dashboards')


    def create(self, data=None):
        result = self.insert(data)

        return result

    def get_all(self, account_id=None):
        result = None

        if account_id:
            params = {'account_id': account_id}
            result = super(DashboardModel, self).get(params=params)

        return result


class DashboardMetricsModel(BaseModel):

    def __init__(self):
        super(DashboardMetricsModel, self).__init__()
        self.collection = self.mongo.get_collection('dashboard_metrics')


    def get_or_create_metric(self, data=None):
        result = None

        process_id = data.get('process_id', '')
        plugin_id = data.get('plugin_id')
        metric_id = data.get('metric_id')
        healthcheck_id = data.get('healthcheck_id')
        dashboard_id = data.get('dashboard_id')
        metric_type = data.get('metric_type')  # Global metrics all have this


        data['unique_id'] = generate_api_key()
        data['metric_type'] = 'system' if process_id == '' else 'process'

        data['metric_type'] = 'plugin' if plugin_id else data['metric_type']
        data['metric_type'] = 'healthcheck' if healthcheck_id else data['metric_type']


        # Check for global metrics here
        if metric_type in ['system_global', 'process_global', 'plugin_global']:
            data['metric_type'] = metric_type
            data = self.remove_keys(data, ['server_id', 'process_id', 'plugin_id'])

        data = self.keys_to_mongoid(data=data, keys=['server_id', 'process_id',
            'dashboard_id', 'plugin_id', 'metric_id', 'gauge_id', 'healthcheck_id'])


        if dashboard_id:
            result = super(DashboardMetricsModel, self).get_or_create(data)

            self.collection.ensure_index([('account_id', self.desc)], background=True)
            self.collection.ensure_index([('server_id', self.desc)], background=True)
            self.collection.ensure_index([('process_id', self.desc)], background=True)
            self.collection.ensure_index([('plugin_id', self.desc)], background=True)
            self.collection.ensure_index([('healthcheck_id', self.desc)], background=True)

        return result


    # Global
    def get_all_metrics(self, account=None):
        data = []

        process_checks = ['cpu', 'memory']
        system_additional_checks = {'memory': 'used_percent', 'disk': 'percent'}


        system_keys = system_model.keys.copy()
        try:
            system_keys.pop('windows_cpu')
            system_keys.pop('memory')
            system_keys.pop('disk')
        except:
            pass

        for check, metric_list in system_keys.items():
            for metric in metric_list:
                key = metric.key

                # Overwrite keys for better visual presentation
                if check == 'network':
                    key = 'inbound' if metric.key == 'i' else 'outbound'

                name = "{0}.{1}".format(check, key)
                _id = "check:{0}.key:{1}.metric_type:system_global".format(check, metric.key)
                data.append([_id, name, 'System metrics'])

        for check, key in system_additional_checks.items():
            name = "{0}.percent".format(check)
            _id = "check:{0}.key:{1}.metric_type:system_global".format(check, key)
            data.append([_id, name, 'System metrics'])

        for p in process_model.get_all_unique():
            for check in process_checks:
                name = "{0}.{1}".format(p, check)
                _id = "check:{0}.key:{1}.metric_type:process_global".format(check, p)
                data.append([_id, name, 'Process Metrics'])


        for el in plugin_model.get_all_unique_gauge_keys_list():
            append = True
            try:
                plugin, gauge, key = el.split('.')
            except:
                append = False

            if append:
                _id = "plugin:{0}.gauge:{1}.key:{2}.metric_type:plugin_global".format(plugin, gauge, key)
                name = "{0}.{1}.{2}".format(plugin, gauge, key)

                data.append([_id, name, 'Plugin Metrics'])

        return data


    def get_server_metrics(self, account_id=None, server_id=None):
        data = []
        constants = ['cpu', 'memory', 'loadavg', 'network']
        process_charts = ['cpu', 'memory']

        processes = process_model.get_all_for_server(server_id)
        plugins = plugin_model.get_for_server(server_id=server_id)
        volumes = volumes_model.get_all_for_server(server_id=server_id)
        interfaces = interfaces_model.get_all_for_server(server_id=server_id)

        for v in volumes:
            name = "Disk.{0}".format(v['name'])
            _id = "server_id:{0}.check:disk.device_id:{1}".format(server_id, v['_id'])
            data.append([_id, name, 'System metrics'])

        for v in interfaces:
            name = "Adapter.{0}".format(v['name'])
            _id = "server_id:{0}.check:network.device_id:{1}".format(server_id, v['_id'])
            data.append([_id, name, 'System metrics'])

        for check in constants:
            name = "{0}".format(check.title())
            _id = "server_id:{0}.check:{1}".format(server_id, check)
            data.append([_id, name, 'System metrics'])

        for p in processes:
            for check in process_charts:
                name = "{0}.{1}".format(p['name'], check)
                _id = "server_id:{0}.process_id:{1}.check:{2}".format(server_id, p['_id'], check)
                data.append([_id, name, 'Process Metrics'])

        for p in plugins:
            gauges = plugin_model.get_gauges_cursor(plugin=p)
            for g in gauges:
                name = "{0}.{1}".format(p.get('name'), g.get('name'))
                _id = "server_id:{0}.plugin_id:{1}.gauge_id:{2}.check:plugin".format(server_id, p['_id'], g['_id'])
                data.append([_id, name, 'Plugin Metrics'])

        data = sorted(data, key=itemgetter(1))

        return data


    def get_all(self, account_id=None, dashboard_id=None, public=None):

        result_list = []
        query = []
        params = {'dashboard_id': dashboard_id}
        params = self.keys_to_mongoid(data=params, keys=['dashboard_id'])

        if dashboard_id:
            query = super(DashboardMetricsModel, self).get(params=params)

        utc_now = unix_utc_now()

        for metric in query:
            mongo_id = metric.get('_id')
            server_id = metric.get('server_id')
            metric_type = metric.get('metric_type')
            unique_id = metric.get('unique_id')
            check = metric.get('check')
            order = metric.get('order', 0)

            tags = metric.get('tags', [])
            tags_list = tags_model.get_list_of_tags(tags_list=tags, to_dict=True)

            server = server_model.get_by_id(server_id)
            process = process_model.get_by_id(metric.get('process_id'))
            plugin = plugin_model.get_by_id(metric.get('plugin_id'))
            gauge = plugin_model.get_gauge_by_id(gauge_id=metric.get('gauge_id'))

            volume = volumes_model.get_by_id(metric.get('device_id'))
            interface = interfaces_model.get_by_id(metric.get('device_id'))

            healthcheck_metric = health_checks_model.get_by_id(metric.get('healthcheck_id'))

            append = False

            unit = yaxis(check)
            if metric_type == 'system_global' and check == 'memory':
                unit = "%"
            if metric_type == 'system_global' and check == 'disk':
                unit = '%'

            if public:
                url = reverse('public_dashboard_metric', kwargs={"metric_id": mongo_id})
            else:
                url = reverse('dashboard_metric', kwargs={"metric_id": mongo_id})

            result = {
                'id': mongo_id,
                'unique_id': unique_id,
                'metric_type': metric_type,
                'url': url,
                'utcnow': utc_now,
                'name': '',
                'unit': unit,
                'tags': tags_list,
                'order': order
            }

            if server:
                result.update({'server_id': server_id, 'type': 'server_metric','server_name' :server.get('name')})


                if metric_type == 'system':
                    result['name'] = "{0}".format(check)
                    if volume:
                        result['name'] = u"{0}.{1}".format(result['name'], volume['name'])

                    if interface:
                        result['name'] = u"{0}.{1}".format(result['name'], interface['name'])

                    append = True


                elif metric_type == 'process' and process:
                    process_name = process.get('name')
                    result['name'] = u"{0}.{1}".format(process_name, check)
                    result['process_id'] = process['_id']
                    append = True

                elif metric_type == 'plugin' and plugin and gauge:
                    result['name'] = u"{0}.{1}".format(plugin.get('name'), gauge.get('name'))

                    result['plugin_id'] = plugin['_id']

                    result['gauge_id'] = gauge['_id']
                    append = True

                result['name'] = u"{0}.{1}".format(server.get('name'), result['name'])


            elif healthcheck_metric:
                result['healthcheck'] = healthcheck_metric
                result['healthcheck_id'] = healthcheck_metric.get('_id')
                try:
                    del result['healthcheck']['_id']
                    del result['healthcheck']['server_id']
                    del result['healthcheck']['tags']
                    del result['healthcheck']['file_id']  # Custom scripts
                except:
                    pass

                result['type'] = 'healthcheck'
                append = True

            else:
                key = metric.get('key')
                # Overwrite keys for better visual presentation
                if check == 'network':
                    key = 'inbound' if key == 'i' else 'outbound'

                result['name'] = u"{0}.{1}".format(check, key)
                append = True


            if metric_type == 'plugin_global':
                result['name'] = u'{0}.{1}.{2}'.format(metric.get('plugin'), metric.get('gauge'), metric.get('key'))
                append = True

            result = self.mongoid_to_str(result, ['server_id', 'id', 'process_id', 'plugin_id', 'metric_id', 'gauge_id', 'healthcheck_id',])

            if append:
                result_list.append(result)


        from operator import itemgetter
        sorted_list = sorted(result_list, key=itemgetter('order')) 

        return sorted_list


    def get_all_grouped_by_server_name(self, account_id=None, dashboard_id=None):
        all_metrics = self.get_all(account_id=account_id, dashboard_id=dashboard_id)


        server_ids = [m.get('server_id') for m in all_metrics if m.get('server_id')]  # Don't add app metrics here
        server_ids = list(set(server_ids))


        metrics_dict = {'server_metrics': {}, "app_metrics": [], "global_metrics": []}
        server_dict = {}
        for i in server_ids:
            server_dict[i] = {
                'metrics': [],
                'name': ""
            }

        for metric in all_metrics:

            server_id = metric.get('server_id', False)
            server_name = metric.get('server_name')
            metric_type = metric.get('metric_type')

            if metric_type == 'application':
                metrics_dict['app_metrics'].append(metric)
            elif metric_type in ['system_global', 'process_global', 'plugin_global']:
                metrics_dict['global_metrics'].append(metric)

            elif server_id:
                server_dict[server_id]['metrics'].append(metric)
                server_dict[server_id]['name'] = server_name

        metrics_dict['server_metrics'] = server_dict

        return metrics_dict


    def delete_all(self, account_id=None, dashboard_id=None):
        params = {'account_id': account_id, 'dashboard_id': dashboard_id}
        params = self.keys_to_mongoid(data=params, keys=['dashboard_id'])

        if account_id and dashboard_id:
            self.collection.remove(params)

    def update_order(self, dashboard_id=None, new_order=None):
        if type(new_order) is list:
            for order, elem in enumerate(new_order):
                _id = self.object_id(elem)
                self.collection.update({"_id": _id}, {"$set": {'order': order}}, upsert=True)

            self.collection.ensure_index([('order', self.desc)], background=True)

dashboard_model = DashboardModel()
dashboard_metrics_model = DashboardMetricsModel()

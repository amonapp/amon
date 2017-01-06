from amon.apps.core.basemodel import BaseModel

from amon.apps.processes.models import process_model
from amon.apps.plugins.models import plugin_model

from amon.apps.devices.models import volumes_model
from amon.apps.devices.models import interfaces_model



class AlertsAPIModel(BaseModel):

    def __init__(self):
        super(AlertsAPIModel, self).__init__()


    def get_selected_metric(self, alert=None):
        selected_metric = ''

        rule_type = alert.get('rule_type')
        check = alert.get('metric')

        if rule_type in ['process', 'uptime',]:
            process = alert.get('process')
            selected_metric = "{0}.{1}".format(process['name'], check)
        elif rule_type in ['global', 'system']:
            selected_metric = check
            
            # Append volumes / interfaces if needed
            volume_interface = alert.get('interface', False)
            if volume_interface == False:
                volume_interface = alert.get('volume', False)
            
            if volume_interface:
                selected_metric = "{0}.{1}".format(selected_metric, volume_interface)
            
        elif rule_type == 'plugin':
            plugin = alert.get('plugin')
            gauge = alert.get('gauge')
            key = alert.get('key')
            selected_metric = "{0}.{1}.{2}".format(plugin['name'], gauge['name'], key)
        elif rule_type == 'process_global':
            process = alert.get('process')
            selected_metric = "{0}.{1}".format(process, check)
        elif rule_type == 'plugin_global':
            plugin = alert.get('plugin')
            gauge = alert.get('gauge')
            key = alert.get('key')
            selected_metric = "{0}.{1}.{2}".format(plugin, gauge, key)

        return selected_metric

    def get_global_metrics(self):
        data = []
        system_alerts = ['CPU', 'Memory', 'Loadavg', 'Disk', 'Network/inbound', 'Network/outbound', 'Not Sending Data']
        process_checks = ['cpu', 'memory', 'down']


        for metric in system_alerts:
            spaceless_metric = metric.replace(" ", "")
            _id = "server:all.metric:{0}.rule_type:global".format(spaceless_metric)
            data.append({'value': _id, 'name': metric, 'metric': metric})

        for p in process_model.get_all_unique():
            for check in process_checks:
                name = "{0}.{1}".format(p, check)
                _id = "server:all.process:{0}.metric:{1}.rule_type:process_global".format(p, check)
                data.append({'value': _id, 'name': name, 'metric': check})

        for el in plugin_model.get_all_unique_gauge_keys_list():
            append = True
            try:
                plugin, gauge, key = el.split('.')
            except:
                append = False

            if append:
                _id = "server:all.plugin:{0}.gauge:{1}.key:{2}.rule_type:plugin_global".format(plugin, gauge, key)
                name = "{0}.{1}.{2}".format(plugin, gauge, key)

                data.append({'value': _id, 'name': name, 'metric': 'plugin'})



        return data

    def get_server_metrics(self, server_id=None):
        data = []
        system_alerts = ['CPU', 'Memory', 'Loadavg', 'Disk', 'Network/inbound', 'Network/outbound', 'Not Sending Data']
        process_alerts = ['CPU', 'Memory', 'Down']

        processes = process_model.get_all_for_server(server_id)
        plugin_gauges = plugin_model.get_gauge_keys_for_server(server_id)
        volumes = volumes_model.get_all_for_server(server_id)
        interfaces = interfaces_model.get_all_for_server(server_id)


        for metric in system_alerts:
            spaceless_metric = metric.replace(" ", "")
            _id = "server:{0}.metric:{1}.rule_type:system".format(server_id, spaceless_metric)
            data.append({'value': _id, 'name': metric, 'metric': metric})

            if metric == 'Disk':
                for volume in volumes.clone():
                    name = "Disk.{0}".format(volume.get('name'))
                    _id = "server:{0}.metric:Disk.rule_type:system.volume:{1}".format(server_id, volume.get('name'))
                    data.append({'value': _id, 
                        'name': name, 
                        'metric': metric, 
                    })

            if metric.startswith('Network'):
                for interface in interfaces.clone():
                    name = "{0}.{1}".format(metric, interface.get('name'))
                    _id = "server:{0}.metric:{1}.rule_type:system.interface:{2}".format(server_id, metric, interface.get('name'))
                    data.append({
                        'value': _id, 
                        'name': name, 
                        'metric': metric,
                    })



        if processes:
            for p in processes:
                for metric in process_alerts:
                    name = "{0}.{1}".format(p['name'], metric)
                    rule_type = 'process' if metric != 'Down' else 'uptime'
                    _id = "server:{0}.process:{1}.metric:{2}.rule_type:{3}".format(server_id, p['_id'], metric, rule_type)
                    data.append({'value': _id, 'name': name, 'metric': metric})

        if len(plugin_gauges) > 0:
            for g in plugin_gauges:
                plugin = g.get('plugin')
                gauge = g.get('gauge')
                key = g.get('key')


                name = "{0}.{1}.{2}".format(plugin['name'], gauge['name'], key)
                _id = "server:{0}.plugin:{1}.gauge:{2}.key:{3}.rule_type:plugin".format(
                    server_id,
                    plugin['_id'],
                    gauge['_id'],
                    key
                )
                data.append({'value': _id, 'name': name})

        return data
import collections

from amon.apps.core.basemodel import BaseModel
from amon.apps.servers.models import server_model
from amon.apps.system.models import system_model
from amon.apps.devices.models import volumes_model, interfaces_model
from amon.apps.processes.models import process_model
from amon.apps.tags.models import tag_groups_model, tags_model

from amon.apps.servers.utils import filter_tags


class MapModel(BaseModel):

    def __init__(self):
        super(MapModel, self).__init__()


    def _get_device_stats(self, value=None, data=None):
        all_data = [0, ]
        metric_map = {'used_percent': 'percent', 'inbound': 'i', 'outbound': 'o'}

        value_in_dict = metric_map.get(value, False)
        if value_in_dict == False:
            value_in_dict = value

        for _, d in data.items():
            d = {} if d == None else d
            metric_value = d.get(value_in_dict, 0)
            metric_value = float(metric_value)

            all_data.append(metric_value)

        v = max(all_data)
        
        return v

    def group_by(self, group_id=None, data=None):

        tags_for_group = tags_model.get_for_group(group_id)
        group = tag_groups_model.get_by_id(group_id)

        grouped_servers = collections.OrderedDict()
        if tags_for_group.clone().count() > 0:
            
            server_ids_in_groups = []
            for tag in tags_for_group:
                
                tag_name = tag.get('name')
                grouped_servers[tag_name] = {
                    'sorted_data': [],
                    'max_value': data['max_value']
                }
                for s in data['sorted_data']:
                    server = s.get('server')
                    server_id = str(server.get('_id'))
                    tag_id = str(tag.get("_id"))
                    append_server = filter_tags(server, tag_id)

                    if append_server:
                        server_ids_in_groups.append(server_id)
                        grouped_servers[tag_name]['sorted_data'].append(s)

            # Add servers with no groups
            grouped_servers['not_in_group'] = {
                'sorted_data': [],
                'max_value': data['max_value']
            }

            for s in data['sorted_data']:
                server = s.get('server')
                server_id = str(server.get('_id'))
                if server_id not in server_ids_in_groups:
                    grouped_servers['not_in_group']['sorted_data'].append(s)

        return grouped_servers


    def sort_by(self, field=None):
        all_servers = server_model.get_all()
        metric_type, metric_block = field.split(":")
        name, value = metric_block.split('.')
        
        all_data = []
        calculate_max_list = []

        unit_dict = {
            'cpu': "%", 
            'memory': 'MB',
            'used_percent': "%",
            'network': 'kb/s',
            'swap_used_percent': "%",
        }

        if not all_servers:
            return

        for s in all_servers:
            v = 0
            last_check = s.get('last_check', 0)

                
            if metric_type == 'disk' or metric_type == 'network':
                if metric_type == 'disk':
                    device_data = volumes_model.get_check_for_timestamp(s, last_check)
                else:
                    device_data = interfaces_model.get_check_for_timestamp(s, last_check)
    
                v = self._get_device_stats(value=value, data=device_data)
    
            
            elif metric_type == 'process':
                process = process_model.get_by_name_and_server_id(server_id=s['_id'], name=name)
                value_in_dict = 'c' if value == 'cpu' else 'm'
                
                if process:
                    process_data = process_model.get_check_for_timestamp(server=s, timestamp=process.get('last_check'))

                    if process_data:
                        for p in process_data.get('data', []):
                            if p.get('p') == process.get('_id'):
                                v = p.get(value_in_dict, 0)

            else:
                system_data = system_model.get_check_for_timestamp(s, last_check)
                metric_dict = system_data.get(name, {})
                v = metric_dict.get(value, 0)
                    
            

            unit = unit_dict.get(name, "")

            # Overwrite, if you find an alternative unit
            alterative_unit = unit_dict.get(value, False)
            if alterative_unit:
                unit = alterative_unit

            server_data = {
                'server': s,
                'last_check': last_check,
                'unit': unit,
                'value': v,
                'field': field
            }

            calculate_max_list.append(v)
            all_data.append(server_data)


        all_data = sorted(all_data, key=lambda k: k['value'], reverse=True)

        result = {
            'sorted_data': all_data,
            'max_value': max(calculate_max_list)
        }
    

        return result




    def get_fields(self):
        system_fields = [
            ('system:cpu.system', 'cpu.system'),
            ('system:cpu.user', 'cpu.user'),
            ('system:cpu.steal', 'cpu.steal'),
            ('system:cpu.iowait', 'cpu.iowait'),
            ('system:loadavg.minute', 'loadavg.minute'),
            ('system:loadavg.five_minutes', 'loadavg.five_minutes'),
            ('system:loadavg.fifteen_minutes', 'loadavg.fifteen_minutes'),
            ('system:memory.used_mb', 'memory.used_mb'),
            ('system:memory.used_percent', 'memory.used_percent'),
            ('system:memory.free_mb', 'memory.free_mb'),
            ('system:memory.total_mb', 'memory.total_mb'),
            ('system:memory.swap_free_mb', 'memory.swap_free_mb'),
            ('system:memory.swap_used_percent', 'memory.swap_used_percent'),
            ('system:memory.swap_total_mb', 'memory.swap_total_mb'),
            ('network:network.inbound', 'network.inbound'),
            ('network:network.outbound', 'network.outbound'),
            ('disk:disk.total', 'disk.total'),
            ('disk:disk.free', 'disk.free'),
            ('disk:disk.used_percent', 'disk.used_percent'),
        ]

        process_fields = []
        for p in process_model.get_all_unique():
            process_cpu = "{0}.cpu".format(p)
            process_memory = "{0}.memory".format(p)
            cpu_tuple = ("process:{0}".format(process_cpu), process_cpu)
            memory_tuple = ("process:{0}".format(process_memory), process_memory)

            process_fields.append(cpu_tuple)
            process_fields.append(memory_tuple)

        process_fields = sorted(process_fields, key=lambda k: k[0])
        system_fields.extend(process_fields)

        return system_fields


map_model = MapModel()
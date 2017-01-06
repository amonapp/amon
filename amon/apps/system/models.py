import collections
from amon.apps.core.basemodel import BaseModel
from amon.apps.servers.models import server_model
from amon.apps.devices.models import interfaces_model, volumes_model

from amon.utils.charts import select_colors
from amon.utils.dates import utc_unixtime_to_localtime, unix_utc_now

class SystemModel(BaseModel):

    def __init__(self):
        super(SystemModel, self).__init__()
        self.metric_tuple = collections.namedtuple('Metric', 'key, name')
        self.data_collection = self.mongo.get_collection('system_data')


        self.keys = {
            'windows_cpu': [
                self.metric_tuple('idle', 'Idle'),
                self.metric_tuple('system', 'System'),
                self.metric_tuple('user', 'User'),
            ],
            'cpu': [
                self.metric_tuple('idle', 'Idle'),
                self.metric_tuple('system', 'System'),
                self.metric_tuple('user', 'User'),
                self.metric_tuple('iowait', 'IOWait'),
                self.metric_tuple('steal', 'Steal'),
            ],
            'memory': [
                self.metric_tuple('used_mb', 'Used memory'),
                self.metric_tuple('total_mb', 'Total memory'),

            ],
            'loadavg': [
                self.metric_tuple('minute', '1 minute'),
                self.metric_tuple('five_minutes', '5 minutes'),
                self.metric_tuple('fifteen_minutes', '15 minutes'),
            ],
            'disk': [
                self.metric_tuple('used', 'Used'),
                self.metric_tuple('total', 'Total')

            ],
            'network': [
                self.metric_tuple('i', 'Inbound'),
                self.metric_tuple('o', 'Outbound')
            ]

        }

    # Used in Dashboards, soon in Alerts
    def get_keys_list(self):
        keys_list = []
        for key, metric_list in system_model.keys.items():
            if key != 'windows_cpu':
                for metric in metric_list:
                    keys_list.append(metric.key)

        return keys_list


    def generate_charts(self, result=None, keys=None, check=None, timezone='UTC'):
        keys_length = len(keys)
        data_lists = []
        data_lists = [[] for i in range(keys_length)]

        for r in result:
            time = r.get('time') if r.get('time') else r.get('t')
            time = utc_unixtime_to_localtime(time, tz=timezone)


            for i in range(keys_length):
                data = r.get(check) if r.get(check) else r

                key = keys[i].key

                value = data.get(key)  # Gets to the specific key -> cpu: {'steal': 4}
                value = self.format_float(value)

                data_lists[i].append({"x": time, "y": value})


        series = []


        for i in range(keys_length):
            data = [] if len(data_lists[i]) == 0 else data_lists[i]
            chart_colors = select_colors(i)

            metric_type = {
                'name': keys[i].name,
                'data': data,
                'unit': '%'

            }
            metric_type.update(chart_colors)
            series.append(metric_type)


        return series


    def get_global_data_after(self, timestamp=None, key=None, enddate=None, check=None, timezone='UTC', filtered_servers=None):
        params = {"time": {"$gte": int(timestamp)}}

        if enddate:
            params['time']["$lte"] = int(enddate)

        keys = {}

        data_lists = {}
        for server in filtered_servers:
            server_id = str(server['_id'])
            keys[server_id] = server.get('name')
            data_lists[server_id] = []

        server_ids_list = [x.get('_id') for x in filtered_servers]
        params['server_id'] = {"$in": server_ids_list}

        result = self.data_collection.find(params).sort('time', self.asc)

        for r in result:
            r_server_id = str(r['server_id'])
            time = r.get('time', 0)
            time = utc_unixtime_to_localtime(time, tz=timezone)

            key = 'used_percent' if check == 'memory' else key

            value = r.get(check, {}).get(key, 0)

            value = self.format_float(value)


            server_list = data_lists.get(r_server_id)
            server_list.append({"x": time, "y": value})

            # Dont display empty lines
            y_axis_sum = sum([x.get('y', 0) for x in data_lists[r_server_id]])
            if y_axis_sum == 0:
                data_lists[r_server_id] = []

        series = []

        for key, name in keys.items():
            _index = list(keys.keys()).index(key)
            data = [] if len(data_lists[key]) == 0 else data_lists[key]
            chart_colors = select_colors(_index)

            metric_type = {
                'name': name,
                'data': data
            }
            metric_type.update(chart_colors)

            if len(data) > 0:
                series.append(metric_type)


        return series


    def get_global_device_data_after(self, timestamp=None, enddate=None, check=None, key=None, timezone="UTC", filtered_servers=None):
        params = {"t": {"$gte": int(timestamp)}}

        if enddate:
            params['t']["$lte"] = int(enddate)

        keys = {}
        series = []
        data_lists = {}
        datamodel = volumes_model if check == 'disk' else interfaces_model
        devices = datamodel.get_all_for_servers_list(servers=filtered_servers)

        for device in devices:
            data_collection = datamodel.get_data_collection()
            params['device_id'] = device['_id']
            result = data_collection.find(params).sort('t', self.asc)

            if result.clone().count() > 0:
                device_server_id = device['server_id']
                device_server = None
                for server in filtered_servers:
                    if server['_id'] == device_server_id:
                        device_server = server

                # Server exists
                if device_server != None:
                    _id = str(device['_id'])
                    keys[_id] = u"{server}.{device}".format(server=device_server.get('name', ""), device=device.get('name'))
                    data_lists[_id] = []

                    for r in result:
                        time = utc_unixtime_to_localtime(r.get('t', 0), tz=timezone)
                        value = r.get(key, 0)
                        value = self.format_float(value)
                        data_lists[_id].append({"x": time, "y": value})


                # Dont display empty lines
                y_axis_sum = sum([x.get('y', 0) for x in data_lists[_id]])
                if y_axis_sum == 0:
                    data_lists[_id] = []


        for _id, name in keys.items():
            _index = list(keys.keys()).index(_id)
            data = [] if len(data_lists[_id]) == 0 else data_lists[_id]
            chart_colors = select_colors(_index)

            metric_type = {
                'name': name,
                'data': data,
            }
            metric_type.update(chart_colors)

            if len(data) > 0:
                series.append(metric_type)


        return series


    def get_data_after(self, timestamp=None, enddate=None, server=None, check=None, timezone='UTC'):
        params = {"time": {"$gte": int(timestamp)}, 'server_id': server['_id']}


        if enddate:
            params['time']["$lte"] = int(enddate)


        result = self.data_collection.find(params).sort('time', self.asc)


        keys = []
        if check in ['cpu', 'memory', 'loadavg']:
            keys = self.keys.get(check)

            distro = server.get('distro')
            if type(distro) is dict:
                name = distro.get('name')
                if name == 'windows' and check == 'cpu':
                    keys = self.keys.get('windows_cpu')


        series = self.generate_charts(result=result, timezone=timezone, check=check, keys=keys)

        return series


    def get_device_data_after(self, timestamp=None, enddate=None, server=None, check=None, device_id=None, timezone="UTC"):
        params = {"t": {"$gte": int(timestamp)}, 'server_id': server['_id']}

        if enddate:
            params['t']["$lte"] = int(enddate)


        keys = []

        if check in ['disk', 'network']:
            datamodel = volumes_model if check == 'disk' else interfaces_model
            device = datamodel.get_by_id(device_id)
            collection = datamodel.get_data_collection()

            keys = self.keys.get(check)
            if device:
                params['device_id'] = device['_id']


        result = collection.find(params).sort('t', self.asc)


        series = self.generate_charts(result=result, timezone=timezone, keys=keys, check=check)

        return series





    def get_first_check_date(self, server=None):
        """
        Used in the Javascript calendar - doesn't permit checks for dates before this date
        Also used to display no data message in the system tab
        """
        params = {'server_id': server['_id']}
        start_date = self.data_collection.find_one(params, sort=[("time", self.asc)])

        if start_date is not None:
            start_date = start_date.get('time', 0)
        else:
            start_date = 0

        return start_date



    def save_data(self, server=None, data=None, time=None, expires_at=None):
        server_id = server['_id']
        time = time if time else unix_utc_now()

        volumes_model.save_data(server=server, data=data.get('disk'), time=time, expires_at=expires_at)
        interfaces_model.save_data(server=server, data=data.get('network'), time=time, expires_at=expires_at)

        server_meta = {
            'last_check': time,
            'uptime': data.get('uptime', ""),
        }
        server_model.update(server_meta, server_id)

        cleaned_data_dict = dict([(k, v) for k,v in data.items() if k not in ['disk', 'network']])
        cleaned_data_dict['time'] = time
        cleaned_data_dict['server_id'] = server['_id']

        cleaned_data_dict["expires_at"] = expires_at

        self.data_collection.insert(cleaned_data_dict)

        self.data_collection.ensure_index([('time', self.desc)], background=True)
        self.data_collection.ensure_index([('server_id', self.desc)], background=True)
        self.data_collection.ensure_index([('expires_at', 1)], expireAfterSeconds=0)


    def get_check_for_timestamp(self, server, timestamp):
        timestamp = int(timestamp)
        server_id = server['_id']
        params = {'server_id': server_id, 'time':timestamp}

        result = self.data_collection.find_one(params)

        system_check = result if result != None else {}


        return system_check


system_model = SystemModel()

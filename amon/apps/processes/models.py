import collections

import operator
from django.core.urlresolvers import reverse


from amon.apps.core.basemodel import BaseModel
from amon.utils.charts import colors, select_colors
from amon.utils.dates import utc_unixtime_to_localtime, unix_utc_now

class ProcessModel(BaseModel):

    def __init__(self):
        super(ProcessModel, self).__init__()
        self.collection = self.mongo.get_collection('processes')
        self.data_collection = self.mongo.get_collection('process_data')
        self.ignored_processes_collection = self.mongo.get_collection('ignored_processes')

        self.metric_tuple = collections.namedtuple('Metric', 'key, name')

        self.keys = {
            'cpu':  [
                self.metric_tuple('c', 'CPU'),
            ], 
            'memory': [
                self.metric_tuple('m', 'Memory'), 
            ],
            'io': [
                self.metric_tuple('r', 'Read'), 
                self.metric_tuple('w', 'Write')
            ],

        }


    def is_ignored(self, fragment):
        ignore_list = ['indicator', 'unity', 'gnome', 'zeitgeist', 'notify', 'hud', 'colord',
            'whoopsie', 'bluetooth', 'ubuntu', 'gtk', 'watchdog', 'bdi', 'jbd',
             'kworker', 'flush', 'vbox', 'upstart', 'ksoftirqd', 'irq', 'dbus',
             'migration', 'sh', 'ssh', 'nautilus', 'compiz', 'update', 'at-spi',
             'telepathy', 'mission', 'network', 'cupsd', 'pulseaudio', 'gvfs', 
             'udevd', 'dnsmasq', 'init', 'zsh', 'polkit', 'bamfdaemon', 
             'modem', 'pid', 'console', 'dconf', 'gconf', 'mount', 'dhclient', 'su', 'du', 'df', 'apt',
             'sort', 'sleep', 'goa', 'plugin', 'kthreadd', 'kswap', 'khung', 'launc',
             'udisks', 'deja', 'cat', 'gdu', 'nm-', 'avahi', 'rtkit', 'accounts', 'acpid',
              'atd', 'getty', 'system-', 'lightdm', 'geoclue-master' ,'upowerd' ,'dropbox', 'System Idle Process']
        
        lower_case = fragment.lower()
        
        return any(lower_case.startswith(w) for w in ignore_list)

    def whitelist_process(self, fragment):
            white_list = ['apache', 'mysql', 'postgres', 'nginx', 'redis-server', 'supervisord']
            
            return any(fragment.startswith(w) for w in white_list)

    def get_ignored_processes_for_timestamp(self, server_id=None, time=None):
        params = {"server_id": server_id, "t": time}

        return self.ignored_processes_collection.find(params)

    def get_by_name_and_server_id(self, server_id=None, name=None):
        server_id = self.object_id(server_id)
        params = {"server": server_id, "name": name}

        result = self.collection.find_one(params)

        return result

    def get_or_create(self, server_id=None, name=None):
        server_id = self.object_id(server_id)
        params = {"server": server_id, "name": name}
        result = super(ProcessModel, self).get_or_create(params)

        self.collection.ensure_index([('server', self.desc)], background=True)
        self.collection.ensure_index([('name', self.desc)], background=True)
        
        return result    


    def save_data(self, server=None, data=None, time=None, expires_at=None):

        time = time if time else unix_utc_now()

        if type(data) == list:
            formated_data = {}
            # New agent, format data
            # the legacy format will be removed in the future and this is going to be the default
            for process in data:
                name = process.get('name')

                # Check if this already exists
                exists = formated_data.get(name, False)
                if exists:
                    existing_memory = formated_data[name].get('memory_mb')
                    current_iteration_memory = process.get('memory_mb')

                    # Overwrite
                    if existing_memory < current_iteration_memory:
                        formated_data[name] = process

                else:
                    formated_data[name] = process


            data = formated_data
        
        ignored_cpu_value = float(0)
        ignored_memory = float(0)
        ignored_processes = []
        process_data = []
        ignored_data = {}
        total_processes = len(data.items())    
        total_cpu = 0
        total_memory = 0

        all_processes = self.get_all_for_server(server['_id'])

        all_processes_dict = {}
        for p in all_processes:
            process_name = p.get('name', None)
            if process_name:
                all_processes_dict[process_name] = p.get('_id')

        # {'process': {'cpu': 10, 'memory_mb': 10, 'kb_read': 10}}
        for name, value in data.items():
            cpu_value = self.format_float(value['cpu'])
            memory_value = self.format_float(value['memory_mb'])

            try:
                read_value = self.format_float(value['kb_read'])
                write_value = self.format_float(value['kb_write'])
            except:
                read_value = 0
                write_value = 0

            process_id = all_processes_dict.get(name)

            if process_id == None:
                if self.is_ignored(name):
                    ignored_cpu_value = ignored_cpu_value+cpu_value
                    ignored_memory = ignored_memory+memory_value
                    ignored_data = {"name": name, "c": cpu_value, "m": memory_value}
                    name = "{0}::{1}::{2}".format(name, cpu_value, memory_value)
                    ignored_processes.append(name)
                else:
                    process_id = self.collection.insert({'server': server['_id'], "name": name })

            
            if process_id and (cpu_value+memory_value) > 2:
                process_dict = {
                    "n": name,
                    "p": process_id,
                    "c": cpu_value, 
                    "m": memory_value,
                    "r": read_value,
                    "w": write_value
                }
                process_data.append(process_dict)
                self.update({'last_check': time}, process_id)
                self.collection.ensure_index([('last_check', self.asc)], background=True)


            if (ignored_memory+ignored_cpu_value) > 0:
                ignored_data = { 
                    'm': self.format_float(ignored_memory),
                    'c': self.format_float(ignored_cpu_value)                
                }

            total_memory = total_memory+memory_value
            total_cpu = total_cpu+cpu_value


        user_processes = int(total_processes-len(ignored_processes))

        process_data_by_cpu = sorted(process_data, key=lambda k: k['c'], reverse=True)
        process_data_by_memory = sorted(process_data, key=lambda k: k['m'], reverse=True)
        
        if len(process_data_by_cpu) < 3:
            top_cpu =  process_data_by_cpu[0:]
            top_memory = process_data_by_memory[0:]
        else:
            top_cpu =  process_data_by_cpu[0:3]
            top_memory = process_data_by_memory[0:3]


        process_data_dict = {
                "t": time,
                "server_id": server['_id'],
                "data": process_data,
                "expires_at": expires_at,
                "total_processes": total_processes,
                "user_processes": user_processes,
                "total_cpu": self.format_float(total_cpu),
                "total_memory": self.format_float(total_memory),
                "top_cpu": top_cpu,
                "top_memory": top_memory,
        }    
        
        self.data_collection.insert(process_data_dict)
        self.data_collection.ensure_index([('t', self.asc)], background=True)
        self.data_collection.ensure_index([('server_id', self.asc)], background=True)


        self.data_collection.ensure_index([('expires_at', 1)], expireAfterSeconds=0)


        # Delete old data 
        self.ignored_processes_collection.remove({'t': {"$lt": time}, 'server_id': server['_id']})


        self.ignored_processes_collection.insert({
            "t": time,
            "server_id": server['_id'], 
            "total_cpu": ignored_data.get('c'),
            "total_memory": ignored_data.get('m'),
            "data": sorted(ignored_processes),

        })

        self.ignored_processes_collection.ensure_index([('t', self.asc)], background=True)
        self.ignored_processes_collection.ensure_index([('server_id', self.asc)], background=True)


        
        return process_data_dict


    def get_all_unique(self):
        result = self.collection.distinct("name")

        return result


    def get_all_for_server(self, server_id, last_check_after=None):
        result = None

        server_id = self.object_id(server_id)

        if server_id:
            params = {"server": server_id}

            if last_check_after:
                params['last_check'] = {"$gte": int(last_check_after)}

            result = self.collection.find(params).sort('name', self.asc)
        
        return result


    def _get_data_for_period_query(self, date_from, enddate, server):
        params = {"t": {"$gte": int(date_from), "$lte": int(enddate)}}
        if server:
            params['server_id'] = server['_id']


        result = self.data_collection.find(params).sort('t', self.asc)

        return result


    def _get_data_after_query(self, timestamp, server):
        params = {"t": {"$gte": int(timestamp)}}
        if server:
            params['server_id'] = server['_id']

        result = self.data_collection.find(params).sort('t', self.asc)

        return result


    def generate_charts(self,  keys=None, result=None, check=None, timezone='UTC', process=None):
        

        keys_length = len(keys)
        data_lists = []
        data_lists = [[] for i in range(keys_length)]
        

        for r in result:
            data = r.get('data', [])
            for d in data:
                if d['p'] == process['_id']:
                    time = utc_unixtime_to_localtime(r['t'], tz=timezone)

                    for i in range(keys_length):
                        key = keys[i].key

                        value = d.get(key)
                        value = self.format_float(value)

                        data_lists[i].append({ "x": time, "y": value})
                        
                    
                    for i in range(keys_length):
                        # Dont display empty lines
                        data_lists[i] = self.clear_y_axis(data=data_lists[i])


        series = []

        for i in range(keys_length):
            data = [] if len(data_lists[i]) == 0 else data_lists[i]
            metric_type =  {
                'color': colors[i],
                'name': keys[i].name,
                'data': data
                
            }
            series.append(metric_type)

        return series


    def get_global_data_after(self, timestamp=None, enddate=None, key=None, timezone='UTC', check=None, filtered_servers=None):
        keys = {}
        data_lists = {}
        process_ids_list = []
        series = []
        server_ids_list = [x.get('_id') for x in filtered_servers]


        filter_proceses_params = {'name': key, 'server': {"$in": server_ids_list}}
        all_processes = self.collection.find(filter_proceses_params)
        for process in all_processes:
            process_id = str(process['_id'])
            name = ''
            server = filter(lambda x: x['_id'] == process['server'], filtered_servers)
            if len(server) > 0:
                name = server[0].get('name')
            
        
            keys[process_id] = name
            data_lists[process_id] = []
            process_ids_list.append(process_id)


        params = {"t": {"$gte": int(timestamp)}}
        if enddate:
            params['t']["$lte"] = int(enddate)
        params['server_id'] = {"$in": server_ids_list}

        
        result = self.data_collection.find(params).sort('t', self.asc)
        for r in result:
            time = r.get('time') if r.get('time') else r.get('t')
            
            time = utc_unixtime_to_localtime(time, tz=timezone)

            data = r.get('data', [])
            for d in data:
                process_id = str(d['p'])
                if process_id in process_ids_list:
                    time = utc_unixtime_to_localtime(r['t'], tz=timezone)
                    key = 'c' if check == 'cpu' else 'm'

                    value = d.get(key)
                    value = self.format_float(value)

                    data_lists[process_id].append({ "x": time, "y": value})


        for key, name in keys.items():
            _index =  keys.keys().index(key)
            data = [] if len(data_lists[key]) == 0 else data_lists[key]
            chart_colors = select_colors(_index)

            metric_type =  {
                'name': name,
                'data': data
                
            }
            metric_type.update(chart_colors)

            if len(data) > 0:
                series.append(metric_type)    
    

        return series


    def get_data_after(self, timestamp=None, enddate=None, server=None, process=None, timezone='UTC', check=None):
        if enddate:
            result = self._get_data_for_period_query(timestamp, enddate, server)
        else:
            result = self._get_data_after_query(timestamp, server)


        keys = []
        if check in ['cpu', 'memory', 'io']:
            keys = self.keys.get(check)

    
        series = self.generate_charts(result=result, timezone=timezone, check=check, process=process, keys=keys)

        return series
                    


    ## TODO - Analyze all the data for period instead of just getting the last value
    def get_top_consumers_for_period(self, date_from=None, date_to=None, server=None, metric_type='cpu'):
        process_data = None

        result = self.data_collection.find_one({"t":{"$lte": int(date_to)}, 'server_id': server['_id']})

        if result != None:
            data = result['data']
            
            metric_type_key = 'c' if metric_type == 'cpu' else 'm'

            data_with_process_names = []
            for d in data:
                process = self.get_by_id(d['p'])
                d['name'] = process.get('name', None)
                data_with_process_names.append(d)
                
            process_data = reversed(sorted(data_with_process_names, key=operator.itemgetter(metric_type_key)))
            

        return process_data



    """
    Used in the Javascript calendar - doesn't permit checks for dates before this date
    Also used to display no data message in the system tab
    """
    def get_first_check_date(self, server=None):
        params = {'server_id': server['_id']}

        start_date = self.data_collection.find_one(params, sort=[("t", self.asc)])

        if start_date is not None:
            start_date = start_date.get('t', 0)
        else:
            start_date = 0
        
        return start_date


    def get_check_for_timestamp(self, server=None, timestamp=None):
        params = {'t': timestamp, 'server_id': server['_id']}
        return self.data_collection.find_one(params)


    def get_process_check(self, server, timestamp):
        timestamp = int(timestamp)
        process_dict = {}
        processes_data_list = []
    
        process_data = self.data_collection.find_one({'t': timestamp, 'server_id': server['_id']})
        process_list = self.get_all_for_server(server['_id'])
        

        url = reverse('view_process', kwargs={"server_id": server['_id']})

        for p in process_list:
            pid = str(p['_id'])

            process_dict[pid] = p.get('name')
            
        
        data = process_data.get('data')

        if data:
            for process in data:
                _id = str(process.get('p'))
                
                processes_data_list.append({
                    'id': _id, 
                    'name': process_dict.get(_id),
                    'memory': process['m'],
                    'cpu': process['c'],
                    'io': "{0}KB | {1}".format(process['r'],process['w']),
                    'url': "{0}?process={1}".format(url, _id)
                })

        

        return processes_data_list


    def get_ignored_process_check(self, server, timestamp):
        result = []
        process_dict = {}
        timestamp = int(timestamp)
        ignored_processes = self.ignored_processes_collection.find_one({"t":{"$gte": int(timestamp)}, 'server_id': server['_id']}) 

        data = None
        if ignored_processes:
            data = ignored_processes.get('data')

        url = reverse('ajax_monitor_process')


        if data:
            for d in data:
                try:
                    name, cpu, memory = d.split('::')
                except:
                    name, cpu, memory = None, None, None

                
                process_dict = {
                    'name': name,
                    'cpu': cpu, 
                    'memory': memory,
                    'io': 0,
                    'url': "{0}?server_id={1}&name={2}".format(url, server['_id'], name)
                }
                result.append(process_dict)

        return result

process_model = ProcessModel()
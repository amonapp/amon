class SystemAlerts(object):

    def __init__(self):
        self.alerts = {}

    def check(self, data=None, rules=None, server=None):
        if rules:
            for rule in rules:
                if rule['metric'] == 'CPU':
                    cpu_data = data.get('cpu', None)
                    if cpu_data:
                        self.check_cpu(rule, data['cpu'])

                elif rule['metric'] == 'Memory':
                    memory_data = data.get('memory', None)
                    if memory_data:
                        self.check_memory(rule, data['memory'])

                elif rule['metric'] == 'Loadavg':
                    load_data = data.get('loadavg', None)
                    if load_data:
                        self.check_loadavg(rule, data['loadavg'])

                elif rule['metric'] == 'Disk':
                    disk_data = data.get('disk', None)
                    if disk_data:
                        self.check_disk(rule, data['disk'])
                elif rule['metric'] in ['Network/inbound', 'Network/outbound']:
                    network_data = data.get('network', None)
                    if network_data:
                        self.check_network(rule, data['network'])

        if len(self.alerts) > 0:
            alerts = self.alerts
            self.alerts = {}

            return alerts
        else:
            return False



    def check_memory(self, rule, data):

        trigger = False
        # Calculate rules with MB

        metric_type = rule.get('metric_type')


        if rule['metric_type'] == 'MB':
            used_memory = float(data['used_mb'])
        else:
            used_memory = float(data['used_percent'])

        if rule['above_below'] == 'above':
            if used_memory > float(rule['metric_value']):
                trigger = True

        if rule['above_below'] == 'below':
            if used_memory < float(rule['metric_value']):
                trigger = True

        alert = {"value": used_memory , "rule": str(rule['_id']),
                 "metric_type": metric_type,
                 "trigger": trigger}


        if alert:
            try:
                len(self.alerts['memory'])
                self.alerts['memory'].append(alert)
            except:
                self.alerts['memory'] = [alert]

            return True

    def check_cpu(self, rule, data):
        last = data.get('last', None)
        if last:
            return False

        trigger = False

        # Utitlization show total cpu usage
        utilization = float(100) - float(data['idle'])

        if rule['above_below'] == 'above':
            if float(rule['metric_value']) < utilization:
                trigger = True

        if rule['above_below'] == 'below':
            if float(rule['metric_value']) > utilization:
                trigger = True

        alert = {"value": utilization , "rule": str(rule['_id']), "trigger": trigger}



        if alert:
            try:
                len(self.alerts['cpu'])
                self.alerts['cpu'].append(alert)
            except:
                self.alerts['cpu'] = [alert]

            return True

    def check_loadavg(self, rule, data):
        last = data.get('last', None)
        if last:
            return False

        trigger = False
        value_to_compare = 0
        values = [float(data['minute']), float(data['five_minutes']), float(data['fifteen_minutes'])]

        value_to_compare = float(sum(values)) / len(values) if len(values) > 0 else float('nan')


        if rule['above_below'] == 'above':
            if float(rule['metric_value']) < value_to_compare:
                trigger = True

        if rule['above_below'] == 'below':
            if float(rule['metric_value']) > value_to_compare:
                trigger = True


        alert = {"value": value_to_compare ,
             "rule": str(rule['_id']),
            'trigger': trigger
        }

        if alert:
            try:
                len(self.alerts['loadavg'])
                self.alerts['loadavg'].append(alert)
            except:
                self.alerts['loadavg'] = [alert]

            return True


    # Internal - checks a single volume
    def _check_volume(self, volume_data, rule, volume):

        trigger = False

        used = volume_data['percent'] if rule['metric_type'] == "%" else volume_data['used']
        metric_type = '%' if rule['metric_type'] == '%' else 'MB'

        # Convert the data value to MB
        if isinstance(used, str):
            if 'G' in used:
                used = used.replace('G','')
                used = float(used) * 1024
            elif 'MB' in used:
                used = used.replace('MB','')
            elif 'M' in used:
                used = used.replace('M', '')


        used = float(used)

        # Convert the rule value to MB if necessary
        if rule['metric_type'] == 'GB':
            metric_value = float(rule['metric_value']) * 1024
        else:
            metric_value = float(rule['metric_value'])

        if rule['above_below'] == 'above':
            if metric_value < used:
                trigger = True

        if rule['above_below'] == 'below':
            if metric_value > used:
                trigger = True

        alert = {
            "value": used , 
            "rule": str(rule['_id']),
            'metric_type': metric_type,
            'volume': volume,
            "trigger": trigger
        }

        return alert

    def check_disk(self, rule, data):
        # New golang agent [{"name": sda1, used: 100, free: 100}]
        # Format to the old format {"sda1": {"used": 100, "free": 100}}
        if type(data) is list:
            data = self._format_golang_device_data(data=data)


        last = data.get('last', None)

        if last:
            return False

        volumes = []
        single_volume = rule.get('volume', None)

        if single_volume:
            volumes.append(single_volume)
        else:
            volumes = data.keys()

        if len(volumes) > 0:
            # ["sda1": {'used': '', "free": }]
            for volume in volumes:
                volume_data = data.get(volume, False)

                if volume_data:
                    alert = self._check_volume(volume_data, rule, volume)
                    disk_alerts = self.alerts.get('disk', [])

                    if len(disk_alerts) == 0:
                        self.alerts['disk'] = [alert]
                    else:
                        self.alerts['disk'].append(alert)

            return True


    # Internal - checks a single volume
    def _check_interface(self, data, rule, iface):

        trigger = False

        rule_type = rule.get('metric').lower()

        if rule_type == 'network/inbound':
            value_to_compare = data.get('inbound')
        elif rule_type == 'network/outbound':
            value_to_compare = data.get('outbound')

        metric_value = float(rule['metric_value'])
        value_to_compare = float(value_to_compare)

        if rule['above_below'] == 'above':
            if metric_value < value_to_compare:
                trigger = True

        if rule['above_below'] == 'below':
            if metric_value > value_to_compare:
                trigger = True

        alert = {
            "value": value_to_compare,
            "rule": str(rule['_id']),
            'interface': iface,
            "trigger": trigger
        }

        return alert



    def check_network(self, rule, data):

        # New golang agent [{"name": sda1, used: 100, free: 100}]
        # Format to the old format {"sda1": {"used": 100, "free": 100}}
        if type(data) is list:
            data = self._format_golang_device_data(data=data)

        last = data.get('network', None)

        if last:
            return False

        single_interface = rule.get('interface', None)

        interfaces = []
        if single_interface:
            interfaces.append(single_interface)
        else:
            interfaces = data.keys()

        if len(interfaces) > 0:
            # ["eth1": {'inbound': '', "inbound": }]
            for iface in interfaces:
                interface_data = data.get(iface, False)

                if interface_data:
                    alert = self._check_interface(interface_data, rule, iface)
                    network_alerts = self.alerts.get('network', [])

                    if len(network_alerts) == 0:
                        self.alerts['network'] = [alert]
                    else:
                        self.alerts['network'].append(alert)

            return True


    def _format_golang_device_data(self, data=None):
        formatted_data = {}
        for device in data:
            name = device.get("name")
            if name:
                formatted_data[name] = device

        return formatted_data



system_alerts = SystemAlerts()

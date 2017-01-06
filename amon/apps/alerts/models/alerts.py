from django.conf import settings

from amon.apps.core.basemodel import BaseModel
from amon.apps.notifications.models import notifications_model
from amon.apps.tags.models import tags_model
from amon.apps.processes.models import process_model
from amon.apps.servers.models import server_model
from amon.apps.plugins.models import plugin_model

from amon.apps.devices.models import volumes_model
from amon.apps.devices.models import interfaces_model

from amon.utils.dates import unix_utc_now

from amon.apps.alerts.models.alertshistory import AlertHistoryModel



class AlertsModel(BaseModel):

    def __init__(self):
        super(AlertsModel, self).__init__()
        self.collection = self.mongo.get_collection('alerts')
        self.alert_history_model = AlertHistoryModel()



    def add_initial_data(self, recipient=None):

        count = self.collection.find().count()

        if count == 0:
            email_recepients = [str(recipient)] if recipient else []
            default_alert = {
                "above_below": "above",
                "email_recepients": email_recepients,
                "rule_type": "global",
                "server": "all",
                "account_id": settings.ACCOUNT_ID,
                "period": 300,
            }



            # Disk alert
            disk_alert = {'metric': 'Disk', 'metric_value': 80, 'metric_type': "%"}
            disk_alert_dict = dict(list(default_alert.items()) + list(disk_alert.items()))
            self.collection.insert(disk_alert_dict)

            # Memory alert
            memory_alert = {'metric': 'Memory', 'metric_value': 80, 'metric_type': "%"}
            memory_alert_dict = dict(list(default_alert.items()) + list(memory_alert.items()))
            self.collection.insert(memory_alert_dict)

            # CPU alert
            cpu_alert = {'metric': 'CPU', 'metric_value': 80, 'metric_type': "%"}
            cpu_alert_dict = dict(list(default_alert.items()) + list(cpu_alert.items()))
            self.collection.insert(cpu_alert_dict)



    def get_process_check(self, collection=None, time=None):
        collection = self.mongo.get_collection(collection)
        params = {'t': time}
        return collection.find_one(params)


    def save(self, data):
        data['period'] = int(data.get('period', 1))

        mongo_keys = ['process', 'plugin', 'gauge', 'custom_metric_id', 'server']
        for key in mongo_keys:
            value = data.get(key, None)
            if value:
                try:
                    data[key] = self.mongo.get_object_id(data[key])
                except:
                    pass

        self.collection.insert(data)
        self.collection.ensure_index([('metric', self.desc)])
        self.collection.ensure_index([('server', self.desc)])
        self.collection.ensure_index([('rule_type', self.desc)])
        self.collection.ensure_index([('plugin', self.desc)])
        self.collection.ensure_index([('account_id', self.desc)])


    def _get_notifications(self, alert):
        notifications_list = []
        notifications = alert.get('notifications', None)
        if notifications:

            for x in notifications:
                split_provider_id = x.split(':')  # email:id
                if len(split_provider_id) == 2:  # New format, ignore old ['hipchat', 'something']
                    _id = split_provider_id[1]
                    result = notifications_model.get_by_id(_id)
                    notifications_list.append(result)

        return notifications_list

    def _get_tags(self, alert):
        tags = []
        alert_tags = alert.get('tags', None)
        if alert_tags:
            tags = [tags_model.get_by_id(x) for x in alert_tags]

        return tags


    def get_by_id(self, alert_id, recipients_dict=True):
        alert_id = self.mongo.get_object_id(alert_id)
        alert = self.collection.find_one({"_id": alert_id})
        rule_type = alert.get('rule_type')

        # Return a full dictionary with recipients instead of list
        if recipients_dict is True:
            alert['notifications'] = self._get_notifications(alert)


        process = alert.get('process')
        if process and rule_type != 'process_global':
            alert['process'] = process_model.get_by_id(process)


        plugin = alert.get('plugin', None)
        gauge = alert.get('gauge', None)
        if plugin and gauge and rule_type != 'plugin_global':
            alert['plugin'] = plugin_model.get_by_id(plugin)
            alert['gauge'] = plugin_model.get_gauge_by_id(gauge)

        return alert

    def update(self, data, id):
        object_id = self.mongo.get_object_id(id)
        server = data.get('server', None)
        if server != 'all':
            data['server'] = self.mongo.get_object_id(server)

        data['period'] = int(data.get('period'))

        self.collection.update({"_id": object_id}, {"$set": data}, upsert=True)



    def get_global_alerts_with_notifications(self, all_servers=None, account_id=None, limit=5, include_all_types=None):
        rules_list = self.get_global_alerts(account_id=account_id, include_all_types=include_all_types)
        rules_with_notifications = []
        if len(rules_list) > 0:
            for rule in rules_list:

                rule['total_triggers'] = self.alert_history_model.count_notifications(alert_id=rule['_id'])
                rule['last_trigger'] = self.alert_history_model.get_last_trigger(alert_id=rule['_id'])

                rules_with_notifications.append(rule)

        return rules_with_notifications



    def _get_alert_tags(self, alert):
        alert['tags'] = self._get_tags(alert)

        return alert

    # Used both on the front and in the API
    def get_global_alerts(self, account_id=None, include_all_types=None):
        params = {"rule_type": {"$in": ["global"]}}

        if include_all_types is True:
            params['rule_type'] = {"$in": ["global", 'process_global', 'plugin_global']}

        alerts = self.collection.find(params).count()
        alerts_list = []

        if alerts > 0:
            alerts = self.collection.find(params)

            for alert in alerts:
                alert['notifications'] = self._get_notifications(alert)
                alert = self._get_alert_tags(alert)
                alerts_list.append(alert)

        return alerts_list

    # Used internally in the alert checker
    def get_alerts_for_metric(self, metric=None):
        params = {'custom_metric_id': metric.get('_id')}

        result = self.collection.find(params)

        return result


    # Used internally in the alert checker
    def get_alerts_for_plugin(self, plugin=None):
        rules_list = []
        params = {'plugin': plugin.get('_id')}

        result = self.collection.find(params)

        if result.clone().count() > 0:
            for rule in result:

                rule['gauge_data'] = plugin_model.get_gauge_by_id(rule['gauge'])
                rules_list.append(rule)

        return rules_list


    # Used for the not sending data only at the moment
    def get_alerts_not_sending_data(self, metric=None):
        params = {"metric": 'NotSendingData'}
        alerts_list = []

        result = self.collection.find(params)

        if result.clone().count() > 0:
            for rule in result:
                rule['notifications'] = self._get_notifications(rule)
                server = rule.get('server')
                if server:
                    rule['server_data'] = [server_model.get_by_id(server)]

                    if rule['rule_type'] == 'global':
                        rule['server_data'] = server_model.get_all()

                alerts_list.append(rule)

        return alerts_list

    def get_alerts(self, type=None, server=None, limit=None):
        params = {"rule_type": type}

        if server:
            params['server'] = server['_id']


        rules_list = []
        rules = self.collection.find(params).count()

        if rules > 0:
            rules = self.collection.find(params)

            rules_list = []
            for rule in rules:
                process_id = rule.get('process', None)
                if process_id:
                    rule['process_data'] = process_model.get_by_id(process_id)

                plugin_id = rule.get('plugin', None)
                gauge_id = rule.get('gauge', None)
                if plugin_id and gauge_id:
                    rule['plugin_data'] = plugin_model.get_by_id(plugin_id)
                    rule['gauge_data'] = plugin_model.get_gauge_by_id(gauge_id)


                if server:
                    rule['server'] = server
                # Check if the rule is for specific server and get the data
                else:
                    rule_server = rule.get('server', False)
                    server_id = self.object_id(rule_server)
                    if server_id:
                        rule['server'] = server_model.get_by_id(rule_server)


                tags = rule.get('tags', False)
                if tags:
                    rule = self._get_alert_tags(rule)

                rule['notifications'] = self._get_notifications(rule)

                rule['last_trigger'] = self.alert_history_model.get_last_trigger(alert_id=rule['_id'])
                rule['total_triggers'] = self.alert_history_model.count_notifications(alert_id=rule['_id'])

                rules_list.append(rule)

        return rules_list



    def delete(self, server_id=None, alert_id=None):
        self.alert_history_model.clear(server_id=server_id, alert_id=alert_id)
        super(AlertsModel, self).delete(alert_id)

    def delete_server_alerts(self, server_id):
        params = {"server": server_id}  # Could be object ID or all
        self.collection.remove(params)

    def delete_metric_alerts(self, metric_id):
        metric_id = self.object_id(metric_id)
        self.collection.remove({"custom_metric_id": metric_id})


    def save_notsendingdata_occurence(self, alert=None):
        time = unix_utc_now()

        data = {
            "value": 1,
            "time": time,
            "trigger": True
        }

        server_id = alert['server']['_id']

        self.alert_history_model.save(alert=alert, server_id=server_id, data=data)


    def save_healtcheck_occurence(self, trigger=None, server_id=None):
        time = trigger.get('time', None)
        alert_id = trigger.get('alert_id')
        trigger_state = trigger.get('trigger', False)
        health_checks_data_id = trigger.get("health_checks_data_id")

        # For the test suite, add an option to overwrite time
        if time is None:
            time = unix_utc_now()

        data = {
            "value": 1,
            "time": time,
            "trigger": trigger_state,
            "health_checks_data_id": health_checks_data_id  # Save a reference to the actual result
        }

        alert = self.get_by_id(alert_id)

        self.alert_history_model.save(alert=alert, server_id=server_id, data=data)


    def save_uptime_occurence(self, alert, data=None):
        time = unix_utc_now()

        data = {
            "value": 1,
            "time": time,
            "trigger": True
        }

        server_id = alert['server']['_id']

        self.alert_history_model.save(alert=alert, server_id=server_id, data=data)

    # Custom metrics, plugins, processes
    def save_occurence(self, alert, server_id=None):
        alert_id = alert.get('alert_id')
        alert_on = alert.get('value', None)
        trigger = alert.get('trigger', False)
        alert_on = "{0:.2f}".format(float(alert_on))

        time = alert.get('time', None)

        if time is None:
            time = unix_utc_now()

        data = {
            "value": float(alert_on),
            "time": time,
            "trigger": trigger
        }

        alert = self.get_by_id(alert_id)

        # Global alerts here
        if server_id:
            self.alert_history_model.save(alert=alert, server_id=server_id, data=data)
        else:
            self.alert_history_model.save(alert=alert, data=data)


    def _server_tags_in_alert(self, server=None, alert=None):
        check = True
        server_tags = server.get('tags', [])

        server_tags = [str(x) for x in server_tags]
        alert_tags = alert.get('tags', [])

        if len(alert_tags) > 0:
            check = any(t in alert_tags for t in server_tags)

        return check


    # System alerts
    def save_system_occurence(self, alerts, server_id=None):

        server = server_model.get_by_id(server_id)

        # Format: {'cpu': [{'value': 2.6899999999999977, 'rule': '4f55da92925d75158d0001e0'}}]}
        for key, values_list in alerts.items():
            for value in values_list:
                data = {}

                save_to_db = False
                alert_on = value.get('value', None)
                trigger = value.get('trigger', False)
                rule_id = value.get('rule', None)
                time = value.get('time', None)

                if time is None:
                    time = unix_utc_now()

                alert_on = "{0:.2f}".format(float(alert_on))

                alert = self.get_by_id(rule_id)

                data = {"value": float(alert_on),
                        "time": time,
                        "trigger": trigger}

                if key == 'disk':
                    volume = value.get('volume', None)
                    volume_data = volumes_model.get_by_name(server, volume)
                    if volume_data:
                        data['volume'] = volume_data.get('_id', None)

                if key == 'network':
                    interface = value.get('interface', None)
                    interface_data = interfaces_model.get_by_name(server, interface)
                    if interface_data:
                        data['interface'] = interface_data.get('_id', None)

                server_id = self.mongo.get_object_id(server_id)

                # Check for tagged global alerts
                alert_server = alert.get('server')
                if alert_server == 'all':
                    if self._server_tags_in_alert(server=server, alert=alert):
                        save_to_db = True
                else:
                    save_to_db = True

                if save_to_db:
                    self.alert_history_model.save(alert=alert, server_id=server_id, data=data)


    def mute(self, alert_id):
        alert_id = self.mongo.get_object_id(alert_id)
        result = self.collection.find_one({"_id": alert_id})
        current_mute = result.get('mute', None)

        toggle = False if current_mute is True else True

        self.collection.update({"_id": alert_id}, {"$set": {"mute": toggle}})


    def get_mute_state(self, account_id=None, mute=None):
        alerts = self.get_all(account_id)

        state_list = []
        for a in alerts.clone():
            state_list.append(a.get('mute', False))

        state = True if len(state_list) > state_list.count(True) else False
        state = mute if mute != None else state

        return state


    def mute_all(self, account_id=None, mute=None):
        alerts = self.get_all(account_id=account_id)

        state = self.get_mute_state(account_id=account_id, mute=mute)


        for alert in alerts:
            self.collection.update({"_id": alert['_id']}, {"$set": {"mute": state}})


    def get_all(self, account_id=None):

        return self.collection.find()

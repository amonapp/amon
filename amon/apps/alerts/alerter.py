from amon.apps.alerts.checkers.system import system_alerts
from amon.apps.alerts.checkers.process import process_alerts
from amon.apps.alerts.checkers.plugin import plugin_alerts
from amon.apps.alerts.checkers.healthcheck import healthcheck_alert_checker
from amon.apps.alerts.models import alerts_model

from amon.apps.plugins.models import plugin_model
from amon.apps.processes.models import process_model

from amon.utils.dates import unix_utc_now


class Alerter(object):

    def check_tags(self, server=None, rule=None):
        valid_rule = True

        server_tags = server.get('tags', [])
        server_tags = [str(t) for t in server_tags]

        tags = rule.get('tags', [])
        tags = [str(t) for t in tags]

        # Check tags first
        if len(server_tags) > 0 and len(tags) > 0:
            valid_rule = set(tags).issubset(server_tags)

        return valid_rule

class ServerAlerter(Alerter):

    def check(self, data, server):
        alerts = False
        account_id = server.get('account_id', None)


        # System alerts
        rules = alerts_model.get_alerts(type='system', server=server)
        if rules:
            alerts = system_alerts.check(data=data, rules=rules, server=server)

            if alerts:
                alerts_model.save_system_occurence(alerts, server_id=server['_id'])


        # Global rules
        global_rules = alerts_model.get_global_alerts(account_id=account_id)
        if global_rules:
            alerts = system_alerts.check(data=data, rules=global_rules, server=server)
            if alerts:
                alerts_model.save_system_occurence(alerts, server_id=server['_id'])

        return alerts  # For the test suite


class ProcessAlerter(Alerter):


    def check_rule_and_save(self, process_data_dict=None, rule=None, process_id=None, server_id=None):
        process_data = next((item for item in process_data_dict if item["p"] == process_id), None)
        if process_data:
            alert = process_alerts.check(process_data, rule)

            if alert:
                alerts_model.save_occurence(alert, server_id=server_id)


    def check(self, data, server):
        process_data_dict = data.get('data', None)

        rules = alerts_model.get_alerts(type='process', server=server)
        if len(rules) + len(process_data_dict) > 0:
            for rule in rules:
                process_id = rule['process']
                self.check_rule_and_save(process_id=process_id, rule=rule, process_data_dict=process_data_dict, server_id=server['_id'])


        # Global alerts
        rules = alerts_model.get_alerts(type='process_global')
        if len(rules) + len(process_data_dict) > 0:
            all_processes = process_model.get_all_for_server(server['_id'])
            for rule in rules:
                valid_rule = self.check_tags(server=server, rule=rule)

                if valid_rule:
                    process_name = rule.get('process')
                    process_id = None
                    # Check if this server has a process with this name
                    for p in all_processes.clone():
                        if p.get('name') == process_name:
                            process_id = p.get('_id')

                    if process_id:
                        self.check_rule_and_save(process_id=process_id, rule=rule, process_data_dict=process_data_dict, server_id=server['_id'])


class PluginAlerter(Alerter):

    def check(self, data=None, plugin=None, server=None):
        plugin_data = data.get('gauges', None)

        rules = alerts_model.get_alerts_for_plugin(plugin=plugin)

        if len(rules) > 0:
            for rule in rules:
                alert = plugin_alerts.check(data=plugin_data, rule=rule)

                if alert:
                    alerts_model.save_occurence(alert)


        # Global alerts
        rules = alerts_model.get_alerts(type='plugin_global')
        if len(rules) > 0:
            all_plugins = plugin_model.get_for_server(server_id=server['_id'])
            for rule in rules:
                valid_rule = self.check_tags(server=server, rule=rule)

                if valid_rule:
                    plugin_name = rule.get('plugin')
                    plugin_id = None

                    # Check if this server has a plugin with this name
                    for p in all_plugins.clone():
                        if p.get('name') == plugin_name:
                            plugin_id = p.get('_id')

                    if plugin_id:
                        alert = plugin_alerts.check(data=plugin_data, rule=rule)

                        if alert:
                            alerts_model.save_occurence(alert, server_id=server['_id'])




class UptimeAlerter(object):

    def check(self, data, server):
        process_data_dict = data.get('data', None)

        rules = alerts_model.get_alerts(type='uptime', server=server)

        if len(rules) + len(process_data_dict) > 0:
            for rule in rules:
                process_id = rule['process']

                process_data = next((item for item in process_data_dict if item["p"] == process_id), None)

                # Process is down
                if not process_data:
                    alerts_model.save_uptime_occurence(rule, data=process_data)


class NotSendingDataAlerter(object):

    def check(self):
        time_now = unix_utc_now()

        alerts = alerts_model.get_alerts_not_sending_data()
        for alert in alerts:
            period = alert.get('period')
            for server in alert.get('server_data'):
                last_check = server.get('last_check')

                # Skip all the servers with no agent installed
                if last_check != None:
                    since_last_check = time_now - last_check  # 65 seconds, 60 seconds sleep, 5 seconds to collect
                    if since_last_check > (period + 10):  # Trigger alert, add 10 seconds buffer
                        alert['server'] = server
                        alerts_model.save_notsendingdata_occurence(alert=alert)


class HealthCheckAlerter(object):

    def check(self, data=None, server=None):

        alerts = alerts_model.get_alerts(type='health_check')
        for alert in alerts:
            # Data is list 
            for d in data:
                trigger = healthcheck_alert_checker.check(data=d, rule=alert)
                # Will scan all the data, check for relevancy and then check the specific entry
                if trigger:
                    alerts_model.save_healtcheck_occurence(trigger=trigger, server_id=server['_id'])



server_alerter = ServerAlerter()
process_alerter = ProcessAlerter()
uptime_alerter = UptimeAlerter()
plugin_alerter = PluginAlerter()
health_check_alerter = HealthCheckAlerter()
notsendingdata_alerter = NotSendingDataAlerter()

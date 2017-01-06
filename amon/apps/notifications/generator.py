import logging

from amon.apps.alerts.models import alerts_model, alerts_history_model, alert_mute_servers_model
from amon.apps.servers.models import server_model
from amon.apps.processes.models import process_model
from amon.apps.plugins.models import plugin_model
from amon.apps.devices.models import volumes_model
from amon.apps.devices.models import interfaces_model
from amon.apps.healthchecks.models import health_checks_results_model, health_checks_model
from amon.utils import AmonStruct
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)

def generate_message(notification=None):
    message = 'Amon - Test Notification'
    
    if notification:
        alert_type = notification.alert.get('rule_type')
        template = False

        if alert_type in ['process', 'process_global']:
            template = "process_alert.txt"
        elif alert_type == 'uptime':
            template = "uptime_alert.txt"
        elif alert_type in ['system', 'global']:
            template = "system_alert.txt"
        elif alert_type in ['plugin', 'plugin_global']:
            template = "plugin_alert.txt"
        elif alert_type == 'notsendingdata': 
            template = "notsending_alert.txt"
        elif alert_type == 'health_check':
            template = "health_check_alert.txt"
            

        if template:
            try:
                message = render_to_string(template,  {'notification': notification})
            except Exception as e:
                logger.exception('Can not generate notification')

    return message

def generate_notifications():
    notifications_list = []

    unsent_alerts = alerts_history_model.get_unsent()

    for trigger in unsent_alerts.get('data'):    

        result = AmonStruct() 
        result.global_mute = False
        
        metadata = None
        timezone = 'UTC'
        
        try:
            alert = alerts_model.get_by_id(trigger['alert_id'])
        except:
            alert = None # Deleted alert here


        if alert:
            rule_type = alert.get('rule_type', 'system')
            metric_type = alert.get('metric', None)
        else:
            rule_type = 'alert-does-not-exist'

        
        if rule_type in ['global', 'process_global', 'plugin_global', 'process', 'system', 'plugin', 'uptime', 'health_check']:

            if rule_type in ['global', 'process_global', 'plugin_global', 'health_check']:
                server_id = trigger.get('server_id')
            else:
                server_id = alert.get('server')
            
            if server_id:
                server = server_model.get_by_id(server_id)
                result.server = server
                result.global_mute = alert_mute_servers_model.check_if_server_is_muted(server=server)


            if metric_type:
                metric_type =  metric_type.lower()
            
            if metric_type in ['cpu', 'memory', 'loadavg']:
                trigger_period_from = trigger['from']
                trigger_period_to = trigger['time']

                metric_type = 'cpu' if metric_type == 'loadavg' else metric_type # Get CPU top consumers for Load average

                if server:
                    metadata = process_model.get_top_consumers_for_period(date_from=trigger_period_from,
                    date_to=trigger_period_to, server=server, metric_type=metric_type)

            # Overwrite rule_type for the new type
            if metric_type == 'notsendingdata':
                alert['rule_type'] = 'notsendingdata'
            
            if metric_type == 'disk':
                volume_id = trigger.get('volume')
                metadata = volumes_model.get_by_id(volume_id)


            if metric_type in ['network/inbound', 'network/outbound']:
                interface_id = trigger.get('interface')
                metadata = interfaces_model.get_by_id(interface_id)


            if rule_type == 'process_global':
                process_name = alert.get('process')
                result.process = process_model.get_by_name_and_server_id(server_id=server_id, name=process_name)

            if rule_type == 'plugin_global':
                gauge_name = alert.get('gauge')
                plugin_name = alert.get('plugin')
                result.plugin = plugin_model.get_by_name_and_server_id(server_id=server_id, name=plugin_name)
                result.gauge = plugin_model.get_gauge_by_name_and_plugin_id(plugin=result.plugin, name=gauge_name)


            # Process and Uptime alerts
            if rule_type == 'process' or rule_type == 'uptime':
                process_dict = alert.get('process')
                if process_dict:
                    result.process = process_model.get_by_id(process_dict.get('_id'))

            if rule_type == 'plugin':
                result.plugin = alert.get('plugin')
                result.gauge = alert.get('gauge')

            if rule_type == 'health_check':
                health_check_result_id = trigger.get('health_checks_data_id')
                health_check_result = health_checks_results_model.get_by_id(health_check_result_id)

                if type(health_check_result) is dict:
                    health_check_id = health_check_result.get('check_id')
                    health_check = health_checks_model.get_by_id(health_check_id)
                    result.healthcheck = health_check

                result.health_check_result = health_check_result
                

        
        if alert:
            result.alert = alert
            result.metadata = metadata
            result.timezone = timezone
            result.trigger = trigger
            result.mute = alert.get('mute', False) # Shortcut

            notifications_list.append(result)

    return notifications_list
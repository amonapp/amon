import logging

from django.template.loader import render_to_string
from django.conf import settings
from amon.utils.dates import datetimeformat_local

logger = logging.getLogger(__name__)

def compile_notsendingdata_email(notification=None):    
    n = notification

    html_content = render_to_string('notsendingdata_alert.html', {
        'alert': n.alert,
        'trigger': n.trigger,
        'server': n.server,
        'timezone': n.timezone, 
        'domain_url': settings.HOST,
        'notification': n
    })

    server_name = n.server.get('name', None)
    last_check=n.server.get('last_check')
    if last_check:
        last_check = datetimeformat_local(last_check)
    
    subject = ''
    subject = 'Server: {server} has not sent data since {last_check} '.format(
        server=server_name, 
        last_check=last_check
    )


    result = {
        'html_content': html_content,
        'subject': subject,
    }

    return result

def compile_uptime_email(notification=None):    
    n = notification

    html_content = render_to_string('process_uptime_alert.html', {
        'alert': n.alert,
        'process': n.process,
        'trigger': n.trigger,
        'server': n.server,
        'timezone': n.timezone, 
        'domain_url': settings.HOST
    })

    process_name = n.process.get('name', None)
    server_name = n.server.get('name', None)
    

    subject = ''
    subject = 'Server: {server} / {process} is Down'.format(
        server=server_name, 
        process=process_name,
    )

    result = {
        'html_content': html_content,
        'subject': subject,
    }

    return result

    
def compile_plugin_email(notification=None):
    n = notification
    html_content = render_to_string('plugin_alert.html', {
        'alert': n.alert,
        'plugin': n.plugin,
        'gauge': n.gauge,
        'trigger': n.trigger,
        'server': n.server,
        'timezone': n.timezone,
        'domain_url': settings.HOST
    })

    
    plugin_name = n.plugin.get('name', None)
    server_name = n.server.get('name', None)
    gauge_name = n.gauge.get('name', '')
    
    above_below_value = ">" if n.alert.get('above_below') == 'above' else "<"
    subject = ''
    subject = 'Server: {server} - {plugin}.{gauge_name}.{key} {above_below} {metric_value} (Current value: {current})'.format(
        server=server_name, 
        plugin=plugin_name,
        gauge_name=gauge_name,
        key=n.alert.get('key'),
        above_below=above_below_value,
        metric_value=n.alert.get('metric_value'),
        current=n.trigger.get('average_value')
    )

    result = {
        'html_content': html_content,
        'subject': subject,
    }

    return result    

    
def compile_process_email(notification=None):
    n = notification
    html_content = render_to_string('process_alert.html', {
        'alert': n.alert,
        'process': n.process,
        'trigger': n.trigger,
        'server': n.server,
        'timezone': n.timezone,
        'domain_url': settings.HOST
    })

    
    metric = n.alert.get('metric')
    process_name = n.process.get('name', None)
    server_name = n.server.get('name', None)
    
    above_below_value = ">" if n.alert.get('above_below') == 'above' else "<"
    subject = ''
    subject = 'Server: {server} - {process}/{metric} {above_below} {metric_value}{metric_type} alert (Current value: {current}{metric_type})'.format(
        server=server_name, 
        process=process_name,
        metric=metric,
        above_below=above_below_value,
        metric_value=n.alert.get('metric_value'),
        current=n.trigger.get('average_value'),
        metric_type=n.alert.get('metric_type', '')
    )

    result = {
        'html_content': html_content,
        'subject': subject,
    }

    return result


def compile_system_email(notification=None):
    n = notification
    
    try:
        html_content = render_to_string('system_alert.html', {
            'alert': n.alert,
            'trigger': n.trigger,
            'server': n.server,
            'metadata': n.metadata,
            'timezone': n.timezone,
            'domain_url': settings.HOST
        })
    except Exception as e:
        logger.exception("Can't compile system email")

    check = n.alert.get('metric')
    above_below_value = ">" if n.alert.get('above_below') == 'above' else "<"


    try:
        meta = n.metadata.get('name', '')
        meta = "{0}/".format(meta)  # eth1/100kbs, sda1/100MB
    except:
        meta = ''

    subject = 'Server: {server} - {check}  {above_below} {metric_value}{metric_type} alert (Current value: {meta}{current}{metric_type})'.format(
        server=n.server.get('name', None),
        check=check,
        above_below=above_below_value,
        metric_value=n.alert.get('metric_value'),
        current=n.trigger.get('average_value'),
        metric_type=n.alert.get('metric_type', ''),
        meta=meta
    )

    result = {
        'html_content': html_content,
        'subject': subject,
    }

    return result

def compile_health_check_email(notification=None):
    n = notification


    # Alert with param 
    param = n.alert.get('param')
    if not param:
        # Global alerts, get the param value from the health check itself
        param = n.healthcheck.get('params', "")
    param = "" if param == False else param

    try:
        html_content = render_to_string('health_check_alert.html', {
            'alert': n.alert,
            'trigger': n.trigger,
            'server': n.server,
            'timezone': n.timezone,
            'domain_url': settings.HOST,
            'notification': n,
            'param': param
        })
    except Exception as e:
        logger.exception("Can't compile health check alert email")

    

    subject = 'Server: {server} - {command}{param} status is {status}'.format(
        server=n.server.get('name', None),
        command=n.alert.get('command'),
        param=param,
        status=n.alert.get('status', "").upper()
    )

    result = {
        'html_content': html_content,
        'subject': subject
    }

    return result
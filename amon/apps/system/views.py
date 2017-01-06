from datetime import datetime

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

from amon.apps.servers.models import server_model
from amon.apps.devices.models import volumes_model
from amon.apps.system.models import system_model
from amon.apps.plugins.models import plugin_model
from amon.apps.processes.models import process_model

from amon.utils.dates import (
    datetime_to_unixtime,
    dateformatcharts_local
)

from amon.utils.charts import get_disk_unit


@login_required
def system_view(request, server_id):
    enddate = request.GET.get('enddate')
    charts = request.GET.get('charts', 'all')

    duration = request.GET.get('duration', 10800)
    duration = int(duration)

    server = server_model.get_by_id(server_id)
    tags = server_model.get_tags(server=server)
    if tags:
        server['tags'] = tags

    first_check_date = system_model.get_first_check_date(server)


    now_unix = datetime_to_unixtime(request.now)
    max_date = now_unix * 1000

    if enddate:
        date_to = int(enddate)
    else:
        date_to = now_unix

    date_from = date_to - int(duration)

    data_url = reverse('ajax_get_data_after')
    data_url = "{0}?server_id={1}".format(data_url, server.get('_id'))

    charts_metadata = {
        'cpu': {'id': 'cpu', 'check': 'cpu', 'name': 'CPU', 'url': data_url, },
        'loadavg': {'id': 'loadavg', 'check': 'loadavg', 'name': 'Load Average','url': data_url},
        'memory': {'id': 'memory', 'check': 'memory', 'name': 'Memory', 'url': data_url, 'type': 'area'},
        'network': [
            {'id': 'network.inbound', 'check': 'network.inbound', 'name': 'Network - KB/s Received', 'url': data_url, 'unit': 'kb/s'},
            {'id': 'network.outbound', 'check': 'network.outbound', 'name': 'Network - KB/s Sent', 'url': data_url, 'unit': 'kb/s'}
        ]
    }

    if charts == 'all':
        active_checks = ['cpu', 'memory', 'loadavg', 'disk', 'network']
    else:
        active_checks = [charts]

    selected_charts = []
    for check in active_checks:
        if check in ['network']:
            chart_meta = charts_metadata.get(check)
            for i in chart_meta:
                selected_charts.append(i)
        elif check != 'disk':
            chart_meta = charts_metadata.get(check)
            selected_charts.append(chart_meta)


    volumes = volumes_model.get_all_for_server(server_id)
    if 'disk' in active_checks:

        unit = get_disk_unit(server)

        for device in volumes.clone():
            device_id, name = device.get('_id'), device.get('name')
            url = "{0}&device_id={1}".format(data_url, device_id)
            meta = {'id': device_id, 'check': 'disk', 'name': name, 'url': url , 'unit': unit}

            last_update = device.get('last_update')
            if last_update > date_from:
                selected_charts.append(meta)


    all_plugins = plugin_model.get_for_server(server_id=server['_id'], last_check_after=date_from)
    all_processes = process_model.get_all_for_server(server_id, last_check_after=date_from)

    breadcrumb_url = reverse('server_system', kwargs={'server_id': server['_id']})
    breadcrumb_url = "{0}?charts={1}".format(breadcrumb_url, charts)

    return render_to_response('system/view.html', {
        "enddate": enddate,
        "duration": duration,
        "all_processes": all_processes,
        "all_plugins": all_plugins,
        "now": now_unix,
        "charts":charts,
        "selected_charts" : selected_charts,
        "date_from" : date_from,
        "date_to" : date_to,
        "first_check_date" : first_check_date,
        "server" : server,
        "max_date" : max_date,
        "server_id": server_id,
        "breadcrumb_url": breadcrumb_url
    },
    context_instance=RequestContext(request))


def get_global_system_data_after(timestamp=None, check=None, key=None, enddate=None, timezone='UTC', filtered_servers=None):
    data = []
    now = datetime.utcnow()

    active_checks = ['memory', 'loadavg', 'cpu', 'disk', 'network']
    if check in active_checks and timestamp:

        if check in ['disk', 'network']:
            data = system_model.get_global_device_data_after(timestamp=timestamp,
                enddate=enddate,
                timezone=timezone,
                check=check,
                key=key,
                filtered_servers=filtered_servers
            )
        else:
            data = system_model.get_global_data_after(timestamp=timestamp,
                    enddate=enddate,
                    check=check,
                    key=key,
                    timezone=timezone,
                    filtered_servers=filtered_servers
                )

    try:
        now_local = dateformatcharts_local(datetime_to_unixtime(now), tz=timezone)
    except:
        now_local = False

    response = {
        'data': data,
        'last_update': datetime_to_unixtime(now),
        'now_local': now_local,
        'chart_type': 'line',
    }

    return response

def get_system_data_after(server_id=None, timestamp=None, check=None, enddate=None, timezone='UTC', device_id=None):

    server = server_model.get_by_id(server_id)
    data = []
    now = datetime.utcnow()

    active_checks = ['memory', 'loadavg', 'cpu', 'disk', 'network.inbound', 'network.outbound']
    if check in active_checks and timestamp:

        if check in ['network.inbound', 'network.outbound']:
            key = 'i' if check == 'network.inbound' else 'o'

            filtered_servers = [server]
            data = system_model.get_global_device_data_after(timestamp=timestamp,
                enddate=enddate,
                filtered_servers=filtered_servers,
                key=key,
                timezone=timezone,
                check='network'
            )


        elif check == 'disk':
            data = system_model.get_device_data_after(timestamp=timestamp, enddate=enddate, server=server, timezone=timezone,
            check=check, device_id=device_id)
        else:
            data = system_model.get_data_after(timestamp=timestamp, enddate=enddate, server=server, check=check, timezone=timezone)

    try:
        now_local = dateformatcharts_local(datetime_to_unixtime(now), tz=timezone)
    except:
        now_local = False


    response = {
        'data': data,
        'last_update': datetime_to_unixtime(now),
        'now_local': now_local,
        'chart_type': 'line'
    }

    return response

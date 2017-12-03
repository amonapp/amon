from datetime import datetime

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from amon.apps.system.common_models import *


from amon.utils.dates import (
    datetime_to_unixtime,
    dateformatcharts_local
)

from rest_framework.decorators import api_view
from rest_framework.response import Response


@login_required
def view_process(request, server_id):

    enddate = request.GET.get('enddate')
    process_id = request.GET.get('process', None)

    server = server_model.get_by_id(server_id)
    tags = server_model.get_tags(server=server)
    if tags:
        server['tags'] = tags

    first_check_date = process_model.get_first_check_date(server)

    duration = request.GET.get('duration', 10800)
    duration = int(duration)


    now_unix = datetime_to_unixtime(request.now)
    max_date = now_unix * 1000

    if enddate:
        date_to = int(enddate)
    else:
        date_to = now_unix

    date_from = date_to - int(duration)


    process = process_model.get_by_id(process_id)

    all_processes = process_model.get_all_for_server(server_id, last_check_after=date_from)
    all_plugins = plugin_model.get_for_server(server_id=server['_id'], last_check_after=date_from)


    data_url = reverse('ajax_get_process_data_after')
    data_url = "{0}?server_id={1}&process={2}".format(data_url, server.get('_id'), process_id)

    selected_charts = [
        {'id': 'cpu', 'check': 'cpu', 'name': 'CPU', 'url': data_url},
        {'id': 'memory', 'check': 'memory', 'name': 'Memory', 'url': data_url},
        {'id': 'io', 'check': 'io', 'name': 'I/O', 'url': data_url}
    ]


    breadcrumb_url = reverse('view_process', kwargs={'server_id': server['_id']})
    breadcrumb_url = "{0}?process={1}".format(breadcrumb_url, process_id)

    return render(request, 'processes/view.html', {
        "selected_charts": selected_charts,
        "enddate": enddate,
        "duration": duration,
        "all_plugins": all_plugins,
        "all_processes":all_processes,
        "now": now_unix,
        "first_check_date": first_check_date,
        "process":process,
        "date_from":date_from,
        "date_to":date_to,
        "server":server,
        "max_date":max_date,
        "breadcrumb_url": breadcrumb_url
    })


def get_global_process_data_after(key=None, timestamp=None, check=None, enddate=None, timezone='UTC', filtered_servers=None):
    now = datetime.utcnow()
    data = []

    active_checks = ['memory', 'cpu', 'io']
    if check in active_checks and timestamp:
        data = process_model.get_global_data_after(timestamp=timestamp,
            enddate=enddate,
            key=key,
            timezone=timezone,
            check=check,
            filtered_servers=filtered_servers
    )

    try:
        now_local = dateformatcharts_local(datetime_to_unixtime(now), tz=timezone)
    except:
        now_local = False

    response = {
        'data': data,
        'last_update': datetime_to_unixtime(now),
        'now_local': now_local
    }

    return response


def get_process_data_after(process_id=None, server_id=None, timestamp=None, check=None, enddate=None, timezone='UTC'):
    now = datetime.utcnow()
    server = server_model.get_by_id(server_id)
    process = process_model.get_by_id(process_id)

    data = []

    active_checks = ['memory', 'cpu', 'io']
    if check in active_checks and timestamp:
        data = process_model.get_data_after(timestamp=timestamp, enddate=enddate,
            server=server, timezone=timezone, process=process,check=check)

    try:
        now_local = dateformatcharts_local(datetime_to_unixtime(now), tz=timezone)
    except:
        now_local = False

    response = {
        'data': data,
        'last_update': datetime_to_unixtime(now),
        'now_local': now_local
    }

    return response



@login_required
@api_view(['GET'])
def ajax_get_data_after(request):
    process_id = request.GET.get('process')
    server_id = request.GET.get('server_id')
    timestamp = request.GET.get('timestamp')
    check = request.GET.get('check', None)
    enddate = request.GET.get('enddate')

    response = get_process_data_after(process_id=process_id,
        server_id=server_id, timestamp=timestamp,
        timezone=request.timezone, enddate=enddate,
        check=check)


    return Response(response)



@login_required
@api_view(['GET'])
def ajax_monitor_process(request):
    data = {}


    process_name = request.GET.get('name')
    server_id = request.GET.get('server_id')

    server = server_model.get_by_id(server_id)

    result = process_model.get_or_create(server_id=server['_id'], name=process_name)

    if result:
        data = {"Response": "OK"}

    return Response(data)


@login_required
@api_view(['GET'])
def ajax_get_data_for_timestamp(request):
    data = {}


    server_id = request.GET.get('server_id')
    timestamp = request.GET.get('timestamp')


    server = server_model.get_by_id(server_id)
    result = process_model.get_process_check(server, timestamp)


    data['data'] = result

    return Response(data)



@login_required
@api_view(['GET'])
def ajax_get_ignored_data_for_timestamp(request):
    data = {}


    server_id = request.GET.get('server_id')
    timestamp = request.GET.get('timestamp')


    server = server_model.get_by_id(server_id)
    result = process_model.get_ignored_process_check(server, timestamp)

    data['data'] = result

    return Response(data)

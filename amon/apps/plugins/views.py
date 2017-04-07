from amon.apps.core.views import *
from amon.apps.system.common_models import *
from datetime import datetime

from amon.utils.dates import (
    datetime_to_unixtime,
    dateformatcharts_local
)


from rest_framework.decorators import api_view
from rest_framework.response import Response

@login_required
def view_plugins(request, server_id):
    plugin_id = request.GET.get('plugin')
    enddate = request.GET.get('enddate')

    duration = request.GET.get('duration', 10800)
    duration = int(duration)

    server = server_model.get_by_id(server_id)
    tags = server_model.get_tags(server=server)
    if tags:
        server['tags'] = tags
        
    plugin = plugin_model.get_by_id(plugin_id)

    selected_charts = []
    custom_metrics = {}
    include_template = False
    gauges = None
    counters = None
    nodata = False
    first_check_date = False

    if plugin:

        name = plugin.get('name')
        first_check_date = plugin_model.get_first_check(server=server, plugin=plugin)
        gauges = plugin_model.get_gauges_cursor(plugin=plugin)
        counters = plugin_model.get_counters(plugin=plugin, server=server)

        plugin_model.get_table_data(plugin=plugin, server=server, table_name='slow_queries')


        if name in ['postgres', 'postgresql', 'mongo', 'mysql', 'nginx', 'apache']:
            include_template = name

            table_metrics = ['slow_queries', 'tables_size', 'index_hit_rate', 'not_found', 'requests']
            for metric in table_metrics:
                additional_ignore_keys = ['unique_hash'] if metric == 'slow_queries' else []
                additional_ignore_keys = ['full_name'] if metric == 'tables_size' else additional_ignore_keys     # Mysql

                custom_metrics[metric] = plugin_model.get_table_data(plugin=plugin,
                    server=server,
                    table_name=metric,
                    additional_ignore_keys=additional_ignore_keys)


        # Display no data for selected plugin message, list - meaning no cursor object
        if isinstance(gauges, list) and counters == None:
            nodata = True

        else:
            data_url = reverse('ajax_get_gauge_data_after')

            for g in gauges:
                gauge_name = g.get('name')
                gauge_id = g.get('_id')

                gauge_url = "{0}?gauge={1}".format(data_url, gauge_id)

                gauge_data = {'id': gauge_id, 'check': gauge_name, 'name':gauge_name, 'url': gauge_url}
                selected_charts.append(gauge_data)




    now_unix = datetime_to_unixtime(request.now)
    max_date = now_unix * 1000

    if enddate:
        date_to = int(enddate)
    else:
        date_to = now_unix

    date_from = date_to - int(duration)


    all_plugins = plugin_model.get_for_server(server_id=server['_id'], last_check_after=date_from)
    all_processes = process_model.get_all_for_server(server_id, last_check_after=date_from)


    breadcrumb_url = reverse('view_plugins', kwargs={'server_id': server['_id']})
    breadcrumb_url = "{0}?plugin={1}".format(breadcrumb_url, plugin_id)


    return render(request, 'plugins/view.html', {
        "custom_metrics": custom_metrics,  # containers, slow queries, etc
        "include_template": include_template,
        "enddate": enddate,
        "duration": duration,
        "date_from":date_from,
        "date_to":date_to,
        "nodata": nodata,
        "server": server,
        "plugin": plugin,
        "selected_charts": selected_charts,
        "counters": counters,
        "all_plugins": all_plugins,
        "all_processes": all_processes,
        "now": now_unix,
        "max_date": max_date,
        "first_check_date": first_check_date,
        "breadcrumb_url": breadcrumb_url
    })


# Use in Public methods, does not require login
def get_plugin_data_after(plugin_id=None, timestamp=None, gauge_id=None, enddate=None, timezone='UTC'):
    now = datetime.utcnow()

    gauge = plugin_model.get_gauge_by_id(gauge_id=gauge_id)

    data = plugin_model.get_gauge_data_after(enddate=enddate, timestamp=timestamp, gauge=gauge, timezone=timezone)

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



def get_global_plugin_data_after(metric=None, timestamp=None, check=None, enddate=None, timezone='UTC', filtered_servers=None):
    now = datetime.utcnow()


    data = plugin_model.get_global_data_after(
        timestamp=timestamp,
        metric=metric,
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
        'now_local': now_local
    }

    return response

@login_required
@api_view(['GET'])
def ajax_get_gauge_data_after(request):
    timestamp = request.GET.get('timestamp')
    enddate = request.GET.get('enddate')
    gauge_id = request.GET.get('gauge')


    response = get_plugin_data_after(timestamp=timestamp, timezone=request.timezone, enddate=enddate, gauge_id=gauge_id)

    return Response(response)

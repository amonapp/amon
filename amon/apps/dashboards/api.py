from amon.apps.servers.models import server_model
from django.contrib.auth.decorators import login_required
from amon.apps.dashboards.models import dashboard_model, dashboard_metrics_model
from rest_framework.decorators import api_view
from rest_framework.response import Response


from amon.apps.system.views import get_system_data_after, get_global_system_data_after
from amon.apps.processes.views import get_process_data_after, get_global_process_data_after
from amon.apps.plugins.views import get_plugin_data_after, get_global_plugin_data_after


@api_view(['GET'])
def public_dashboard_metric(request, metric_id=None):
    timestamp = request.GET.get('timestamp')
    dashboard_metric = dashboard_metrics_model.get_by_id(metric_id)

    server_id = dashboard_metric.get('server_id')
    process_id = dashboard_metric.get('process_id')
    plugin_id = dashboard_metric.get('plugin_id')
    metric_type = dashboard_metric.get('metric_type')
    check = dashboard_metric.get('check')

    # App metrics here
    tags = dashboard_metric.get('tags', [])

    filtered_servers = server_model.get_all()
    if len(tags) > 0:
        filtered_servers = server_model.get_with_tags(tags=tags)

    response = {}
    if metric_type == 'system':
        response = get_system_data_after(timestamp=timestamp, server_id=server_id,
        check=check)
    elif metric_type == 'process':
        response = get_process_data_after(timestamp=timestamp, server_id=server_id,
            process_id=process_id, check=check)
    elif metric_type == 'plugin':
        gauge_id = dashboard_metric.get('gauge_id')
        response = get_plugin_data_after(timestamp=timestamp,
            plugin_id=plugin_id, gauge_id=gauge_id)
    elif metric_type == 'system_global':
        key = dashboard_metric.get('key')  # loadavg.minute
        response = get_global_system_data_after(timestamp=timestamp, check=check, key=key, filtered_servers=filtered_servers)
    elif metric_type == 'process_global':
        key = dashboard_metric.get('key')  # loadavg.minute
        response = get_global_process_data_after(timestamp=timestamp, check=check, key=key, filtered_servers=filtered_servers)
    elif metric_type == 'plugin_global':
        response = get_global_plugin_data_after(timestamp=timestamp, metric=dashboard_metric, filtered_servers=filtered_servers)


    return Response(response)


@login_required
@api_view(['GET'])
def dashboard_metric(request, metric_id=None):
    return public_dashboard_metric(request, metric_id=metric_id)


@login_required
@api_view(['POST'])
def edit_dashboard(request, dashboard_id):
    data = request.data

    dashboard_model.update(data, dashboard_id)

    response = {
        'response': [],
    }

    return Response(response)


@login_required
@api_view(['POST'])
def add_metric(request, dashboard_id):
    data = request.data

    check = data.get('check')
    metric_type = data.get('metric_type')

    valid_checks = ['cpu', 'memory', 'loadavg', 'network', 'disk', 'plugin', 'metric', 'healthcheck']
    result = None
    add_metric = False

    # Check if the metric/server exists and belongs to the same account
    if check in valid_checks:
        add_metric = True

    if metric_type in ['process_global', 'plugin_global', 'system_global']:
        add_metric = True

    if add_metric:
        data['account_id'] = request.account_id
        data['dashboard_id'] = dashboard_id
        result = dashboard_metrics_model.get_or_create_metric(data=data)


    response = 'Created' if result else 'Error'

    response = {
        'response': response,
    }

    return Response(response)


@login_required
@api_view(['POST'])
def reorder_metrics(request, dashboard_id):
    data = request.data

    new_order = data.get('new_order')
    result = None
    
    if type(new_order) is list:
        dashboard_metrics_model.update_order(dashboard_id=dashboard_id, new_order=new_order)
        result = True

    response = 'Metrics Order Updated' if result else 'Error'

    response = {
        'response': response,
    }

    return Response(response)

@login_required
@api_view(['POST'])
def remove_metric(request):
    data = request.data
    metric_id = data.get('metric_id')

    response = {'Response': 'OK'}
    dashboard_metrics_model.delete(metric_id)

    response = {
        'response': response,
    }

    return Response(response)


@login_required
@api_view(['GET'])
def get_all_metrics(request, dashboard_id):
    all_metrics = dashboard_metrics_model.get_all(account_id=request.account_id, dashboard_id=dashboard_id)

    response = {
        'data': all_metrics,
    }

    return Response(response)


# Used in edit dashboard, select server - dropdown menu
@login_required
@api_view(['POST', 'GET'])
def get_server_metrics(request):

    data = request.data
    server_id = data.get('server_id')

    if server_id == 'all':
        metrics = dashboard_metrics_model.get_all_metrics()
    else:
        metrics = dashboard_metrics_model.get_server_metrics(account_id=request.account_id, server_id=server_id)


    response = {
        'data': metrics,
    }

    return Response(response)

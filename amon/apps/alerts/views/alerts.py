from amon.apps.core.views import *


from amon.apps.servers.models import server_model
from amon.apps.alerts.models import alerts_model, alerts_history_model, alerts_api_model
from amon.apps.alerts.forms import AlertForm, EditAlertForm, MuteForm
from amon.apps.tags.models import tags_model
from amon.apps.notifications.models import notifications_model

@login_required
def all(request):

    all_servers = server_model.get_all(account_id=request.account_id)

    alerts = []
    
    if all_servers:
        for server in all_servers:
            types = ['system', 'process', 'uptime', 'plugin']
            for alert_type in types:
                result = alerts_model.get_alerts(type=alert_type, server=server)
                if result:
                    [alerts.append(x) for x in result]

    
    global_alerts = alerts_model.get_global_alerts_with_notifications(all_servers=all_servers, account_id=request.account_id, include_all_types=True)
    if global_alerts:
        [alerts.append(x) for x in global_alerts]

    global_health_check_alerts = alerts_model.get_alerts(type='health_check')
    if global_health_check_alerts:
        [alerts.append(x) for x in global_health_check_alerts]
    

    return render_to_response('alerts/all.html', {
        "alerts": alerts,
        "all_servers": all_servers,
        "server_metrics": settings.SERVER_METRICS,
        "common_metrics": settings.COMMON_METRICS,
        "total_alerts": len(alerts),
    },
    context_instance=RequestContext(request))


@login_required
def add_alert(request):
    all_servers = server_model.get_all(account_id=request.account_id)
    tags = tags_model.get_all()
    notifications = notifications_model.get_all_formated()

    if request.method == 'POST':
        form = AlertForm(request.POST, all_servers=all_servers)
        if form.is_valid():
            data = form.cleaned_data
            metric = data.get('metric')
            
            metric_dict = dict(item.split(":") for item in metric.split("."))

            form_data = {
                "metric_type": request.POST.get('metric_type'),
                "tags": request.POST.getlist('tags'),
                "notifications": request.POST.getlist('notifications'),
                "rule_type": metric_dict.get('rule_type'), 
                "account_id": request.account_id,
            }

            form_data = dict(list(form_data.items()) + list(metric_dict.items()))
            del data['metric']

            data.update(form_data)
            alerts_model.save(data)
            return redirect(reverse('alerts'))
    else:
        form = AlertForm(all_servers=all_servers)
    
    return render_to_response('alerts/add.html', {
        "common_metrics": settings.COMMON_METRICS,
        "form": form,
        'tags': tags,
        'notifications': notifications,
        "all_servers": all_servers
    },
    context_instance=RequestContext(request))    


@login_required
def edit_alert(request, alert_id):

    all_servers = server_model.get_all(account_id=request.account_id)
    alert = alerts_model.get_by_id(alert_id, recipients_dict=False)
    tags = tags_model.get_all()
    server = alert.get('server', None)  # If the alert is for specific server, it could be global

    notifications = notifications_model.get_all_formated()

    selected_metric = alerts_api_model.get_selected_metric(alert=alert)

    if request.method == 'POST':
        form = EditAlertForm(request.POST, all_servers=all_servers)
        if form.is_valid():
            data = form.cleaned_data

            form_data = {
                "tags": request.POST.getlist('tags', None),
                "metric_value": data.get('metric_value'),
                "above_below": data.get('above_below'),
                "period": data.get('period'),
                "server": server,
                "metric_type": request.POST.get('metric_type'),
                "notifications": request.POST.getlist('notifications')
            }

            alerts_model.update(form_data, alert_id)
            return redirect(reverse('alerts'))
    else:
        form = EditAlertForm(all_servers=all_servers, initial={
            'metric_value': alert['metric_value'],
            'period': alert['period'],
            'server':server,
            "above_below": alert['above_below'],
        })

    # TODO - Fix that angular bug sometime
    metric_types = ''
    metric = alert.get('metric')
    if metric:
        metric = metric.lower()
        metric_types = ["%"] if metric == 'cpu' else []
        metric_types = ["%", "MB"] if metric == 'memory' else metric_types
        metric_types = ["%", "MB", "GB"] if metric == 'disk' else metric_types
        metric_types = ["KB/s"] if metric in ['network/inbound', 'network/outbound'] else metric_types

    
    return render_to_response('alerts/edit.html', {
        "server": server, 
        'tags': tags,
        "alert": alert,
        "form": form,
        "selected_metric": selected_metric,
        "notifications": notifications,
        "metric_types": metric_types,
    },
    context_instance=RequestContext(request))


@login_required
def delete_alert(request, alert_id):
    alert = alerts_model.get_by_id(alert_id)
    rule_type = alert.get('rule_type', None)

    if rule_type in ['process_global', 'plugin_global', 'global', 'health_check']:
        all_servers = server_model.get_all()

        if all_servers:
            for server in all_servers:
                server_id = server.get('_id')
                alerts_model.delete(server_id=server_id, alert_id=alert_id)
        else:
            alerts_model.delete(alert_id=alert_id)
    else:
        server_id = alert.get('server', None)
        alerts_model.delete(server_id=server_id, alert_id=alert_id)
    
    return redirect(reverse('alerts'))


@login_required
def clear_triggers(request, alert_id):
    alerts_history_model.clear(alert_id=alert_id)

    messages.add_message(request, messages.INFO, 'Triggers deleted.')

    return redirect(reverse('alerts'))


@login_required
def history(request, alert_id):
    data = {}
    alert = alerts_model.get_by_id(alert_id)


    notifications = alerts_history_model.get_notifications_list(alert_id=alert['_id'], limit=100)
    
    return render_to_response('alerts/history.html', {
        'notifications': notifications,
        'alert': alert,
        'data': data
    },
    context_instance=RequestContext(request))


@login_required
def history_health_check(request, alert_id):
    data = {}
    alert = alerts_model.get_by_id(alert_id)

    notifications = alerts_history_model.get_notifications_list(alert_id=alert['_id'], limit=100)
    
    return render_to_response('alerts/history.html', {
        'notifications': notifications,
        'alert': alert,
        'data': data
    },
    context_instance=RequestContext(request))


@login_required
def history_system(request, alert_id):
    alert = alerts_model.get_by_id(alert_id)
    server = server_model.get_by_id(alert['server'])

    page = request.GET.get('page', 1)
    page = int(page)

    skip = 0
    if page > 1:
        skip = 100 * (page - 1)

    total = alerts_history_model.count_notifications(alert_id=alert['_id'])
    
    on_page = 100
    if total > on_page:
        total_pages = total/on_page
    else:
        total_pages = 1

    total_pages = range(total_pages)

    notifications = alerts_history_model.get_notifications_list(alert_id=alert['_id'], limit=100, skip=skip)

    return render_to_response('alerts/history.html', {
        'notifications': notifications,
        'alert': alert,
        'server': server,
        "total_pages": total_pages,
        "page": page
    },
    context_instance=RequestContext(request))


@login_required
def ajax_alert_triggers(request, alert_id=None):
    alert = alerts_model.get_by_id(alert_id)

    notifications = alerts_history_model.get_notifications_list(alert_id=alert['_id'], limit=5)

    return render_to_response('alerts/ajax_history.html', {
        "notifications": notifications,
        "rule": alert
    },
    context_instance=RequestContext(request))

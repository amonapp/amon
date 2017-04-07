from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.http import Http404

from amon.apps.dashboards.models import dashboard_model, dashboard_metrics_model
from amon.apps.servers.models import server_model
from amon.apps.healthchecks.models import health_checks_model

from amon.utils.dates import (
    datetime_to_unixtime,
)


@login_required
def index(request):
    dashboards = dashboard_model.get_all(account_id=request.account_id)
    dashboards_data = []

    if dashboards.clone().count() > 0:

        for d in dashboards:
            metrics = dashboard_metrics_model.get_all_grouped_by_server_name(account_id=request.account_id, dashboard_id=d['_id'])

            dashboards_data.append({
                'metrics': metrics,
                'dashboard': d
            })

    return render(request, 'dashboards/all.html', {
        "dashboards_data": dashboards_data
    })


@login_required
def create_dashboard(request):
    data = {'name': '', 'account_id': request.account_id}
    dashboard_id = dashboard_model.create(data=data)

    url = reverse('edit_dashboard', kwargs={'dashboard_id': dashboard_id})
    return redirect(url)


def _fill_metrics_arrays(all_metrics=None):
    charts_list = []
    health_checks_list = []
    for m in all_metrics:
        metric_type = m.get('type')
        if metric_type == 'healthcheck':
            check_id = m.get('healthcheck_id')
            server = None
            if check_id:
                check = health_checks_model.get_by_id(check_id)
                server = server_model.get_by_id(check.get('server_id', None))

            if server != None:
                check['server'] = server
                health_checks_list.append(check)
        else:
            charts_list.append(m)

    return {
        'charts': charts_list,
        'health_checks': health_checks_list
    }


def public_dashboard(request, account_id, dashboard_id):
    enddate = request.GET.get('enddate')
    duration = request.GET.get('duration', 1800)
    duration = int(duration)

    now_unix = datetime_to_unixtime(request.now)
    max_date = now_unix * 1000

    if enddate:
        date_to = int(enddate)
    else:
        date_to = now_unix

    date_from = date_to - int(duration)

    dashboard = dashboard_model.get_by_id(dashboard_id)

    public = dashboard.get('shared', False)
    if public == False:
        raise Http404


    all_metrics = dashboard_metrics_model.get_all(
        dashboard_id=dashboard_id,
        public=public)

    all_existing_server_ids = server_model.get_all_ids()

    metrics_array = _fill_metrics_arrays(all_metrics=all_metrics)
    
    return render(request, 'dashboards/public.html', {
        "account_id": account_id,
        "duration": duration,
        "health_checks": metrics_array['health_checks'],
        "selected_charts": metrics_array['charts'],
        "date_from" : date_from,
        "date_to" : date_to,
        "now": now_unix,
        "max_date": max_date,
        "dashboard": dashboard,
        "enddate": enddate,
        "all_existing_server_ids": all_existing_server_ids
    })

@login_required
def view_dashboard(request, dashboard_id):
    enddate = request.GET.get('enddate')
    duration = request.GET.get('duration', 1800)
    duration = int(duration)

    now_unix = datetime_to_unixtime(request.now)
    max_date = now_unix * 1000

    if enddate:
        date_to = int(enddate)
    else:
        date_to = now_unix

    date_from = date_to - int(duration)

    all_dashboards = dashboard_model.get_all(account_id=request.account_id)
    all_existing_server_ids = server_model.get_all_ids()
    dashboard = dashboard_model.get_by_id(dashboard_id)
    all_metrics = dashboard_metrics_model.get_all(account_id=request.account_id, dashboard_id=dashboard_id)


    metrics_array = _fill_metrics_arrays(all_metrics=all_metrics)


    if len(all_metrics) == 0:
        messages.add_message(request, messages.INFO, 'To view this dashboard add at least 1 metric')
        return redirect(reverse('edit_dashboard', kwargs={'dashboard_id': dashboard_id}))

    return render(request, 'dashboards/view.html', {
        "all_dashboards": all_dashboards,
        "duration": duration,
        "selected_charts": metrics_array['charts'],
        "health_checks": metrics_array['health_checks'],
        "date_from" : date_from,
        "date_to" : date_to,
        "now": now_unix,
        "max_date": max_date,
        "dashboard": dashboard,
        "enddate": enddate,
        "all_existing_server_ids": all_existing_server_ids
    })


@login_required
def delete_dashboard(request, dashboard_id):

    dashboard_metrics_model.delete_all(account_id=request.account_id, dashboard_id=dashboard_id)
    dashboard_model.delete(dashboard_id)

    url = reverse('dashboards')

    return redirect(url)


@login_required
def edit_dashboard(request, dashboard_id):
    dashboard = dashboard_model.get_by_id(dashboard_id)

    all_servers = server_model.get_all(account_id=request.account_id)
    all_healthchecks = health_checks_model.get_all()

    return render(request, 'dashboards/edit.html', {
        "dashboard": dashboard,
        "all_servers": all_servers,
        "all_healthchecks": all_healthchecks
    })


@login_required
def reorder_dashboard(request, dashboard_id):
    dashboard = dashboard_model.get_by_id(dashboard_id)

    return render(request, 'dashboards/reorder.html', {
        "dashboard": dashboard,
    })
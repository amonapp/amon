from amon.apps.core.views import *


from amon.apps.servers.models import server_model
from amon.apps.alerts.models import alerts_model
from amon.apps.alerts.forms import HealthCheckAlertForm, EditHealthCheckAlertForm
from amon.apps.tags.models import tags_model
from amon.apps.notifications.models import notifications_model


@login_required
def add_alert(request):
    all_servers = server_model.get_all()
    tags = tags_model.get_all()
    notifications = notifications_model.get_all_formated()

    if request.method == 'POST':
        form = HealthCheckAlertForm(request.POST, all_servers=all_servers)
        if form.is_valid():
            data = form.cleaned_data

            form_data = {
                "command": request.POST.get('command'),
                "param": request.POST.get('param'), 
                "tags": request.POST.getlist('tags'),
                "notifications": request.POST.getlist('notifications'),
                "rule_type": "health_check", 
            }

            data.update(form_data)
            alerts_model.save(data)
            return redirect(reverse('alerts'))
    else:
        form = HealthCheckAlertForm(all_servers=all_servers)
    
    return render(request, 'alerts/add_healthcheck.html', {
        "form": form,
        'tags': tags,
        'notifications': notifications,
        "all_servers": all_servers
    })    


@login_required
def edit_alert(request, alert_id):

    all_servers = server_model.get_all(account_id=request.account_id)
    alert = alerts_model.get_by_id(alert_id, recipients_dict=False)
    tags = tags_model.get_all()
    server = alert.get('server', None) # If the alert is for specific server, it could be global

    selected_command = " ".join([alert.get("command", ""), alert.get('params', "")])

    notifications = notifications_model.get_all_formated()

    if request.method == 'POST':
        form = EditHealthCheckAlertForm(request.POST, all_servers=all_servers)
        if form.is_valid():
            data = form.cleaned_data

            form_data = {
                "tags": request.POST.getlist('tags', None),
                "status": data.get('status'),
                "period": data.get('period'),
                "server": server,
                "notifications": request.POST.getlist('notifications')
            }

            alerts_model.update(form_data, alert_id)
            return redirect(reverse('alerts'))
    else:
        form = EditHealthCheckAlertForm(
            all_servers=all_servers, 
            initial={
                'period': alert['period'],
                'server':server,
                "status": alert['status'],
        })


    
    return render(request, 'alerts/edit_healthcheck.html', {
        "server": server, 
        'tags': tags,
        "alert": alert,
        "form": form,    
        "selected_command": selected_command,
        "notifications": notifications,
    })    

from amon.apps.core.views import *


from amon.apps.alerts.models import alerts_model
from amon.apps.alerts.forms import MuteForm
from amon.apps.alerts.models import alert_mute_servers_model


@login_required
def mute(request, alert_id):
    alerts_model.mute(alert_id)    

    return redirect(reverse('alerts'))


@login_required
def mute_all(request):
    alerts_model.mute_all(account_id=request.account_id)
    

    return redirect(reverse('alerts'))


@login_required
def mute_servers(request):
    all_muted = alert_mute_servers_model.get_all()

    if request.method == 'POST':
        form = MuteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('alerts_mute_servers'))
    else:
        form = MuteForm()
    

    return render(request, 'alerts/mute.html', {
        "form": form,
        "all_muted": all_muted
    })

@login_required
def unmute_server(request, mute_id):
    alert_mute_servers_model.delete(mute_id)
    return redirect(reverse('alerts_mute_servers'))
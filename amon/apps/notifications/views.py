from django.shortcuts import render
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from amon.apps.notifications.forms import (
    PushoverForm,
    PagerDutyForm,
    VictorOpsForm,
    OpsGenieForm,
    SlackForm,
    TelegramForm,
    HipChatForm,
    EmailForm,
    WebHookForm
)
from amon.apps.notifications.models import notifications_model
from amon.apps.notifications.pushover.sender import send_pushover_notification
from amon.apps.notifications.pagerduty.sender import send_pagerduty_notification
from amon.apps.notifications.victorops.sender import send_victorops_notification
from amon.apps.notifications.opsgenie.sender import send_opsgenie_notification
from amon.apps.notifications.slack.sender import send_slack_notification
from amon.apps.notifications.telegram.sender import send_telegram_notification
from amon.apps.notifications.hipchat.sender import send_hipchat_notification
from amon.apps.notifications.webhooks.sender import _send_webhook
from amon.apps.notifications.mail.sender import send_test_email

PROVIDERS = {
    'pushover': PushoverForm,
    'pagerduty': PagerDutyForm,
    'victorops': VictorOpsForm,
    'opsgenie': OpsGenieForm,
    'slack': SlackForm,
    'telegram': TelegramForm,
    'hipchat': HipChatForm,
    'email': EmailForm,
    'webhook': WebHookForm
}

@login_required
def view(request):
    return render(request, 'notifications/view.html', {
    })


@login_required
def delete(request, provider_id=None, notification_id=None):
    notifications_model.delete(notification_id)

    return redirect(reverse('notifications_edit', kwargs={'provider_id': provider_id}))


@login_required
def add(request, provider_id=None):
    all_for_provider = notifications_model.get_all_for_provider(provider_id=provider_id)

    provider_form = PROVIDERS.get(provider_id, False)

    if not provider_form:
        return redirect(reverse('notifications_all'))

    if request.method == "POST":
        form = provider_form(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            notifications_model.save(data=data, provider_id=provider_id)

            messages.add_message(request, messages.INFO, '{0} settings updated'.format(provider_id.title()))
            return redirect(reverse('notifications_edit', kwargs={'provider_id': provider_id}))
    else:
        form = provider_form()

    return render(request, 'notifications/view.html', {
        "form": form,
        "provider_id": provider_id,
        "add_form": True,
        "all_for_provider": all_for_provider
    })



@login_required
def edit(request, provider_id=None, notification_id=None):
    provider_data = notifications_model.get_by_id(notification_id)

    all_for_provider = notifications_model.get_all_for_provider(provider_id=provider_id)

    provider_form = PROVIDERS.get(provider_id, False)

    if not provider_form:
        return redirect(reverse('notifications_all'))

    if request.method == "POST":
        form = provider_form(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            notifications_model.update(data=data, id=notification_id)

            if 'test' in request.POST:
                redirect_url = reverse('notifications_test', kwargs={'provider_id': provider_id, 'notification_id': notification_id})

            else:
                redirect_url = reverse('notifications_edit', kwargs={'provider_id': provider_id, 'notification_id': notification_id})

            messages.add_message(request, messages.INFO, '{0} settings updated'.format(provider_id.title()))

            return redirect(redirect_url)
    else:
        form = provider_form(provider_data=provider_data)

    return render(request, 'notifications/view.html', {
        "form": form,
        "provider_id": provider_id,
        "provider_data": provider_data,
        "all_for_provider": all_for_provider,
        "notification_id": notification_id
    })



@login_required
def test(request, provider_id=None, notification_id=None):

    auth = notifications_model.get_by_id(notification_id)

    message = 'Test Notification'

    if provider_id == 'pushover':
        send_pushover_notification(message=message, auth=auth)
    elif provider_id == 'pagerduty':
        send_pagerduty_notification(message=message, auth=auth)
    elif provider_id == 'victorops':
        send_victorops_notification(message=message, auth=auth)
    elif provider_id == 'opsgenie':
        send_opsgenie_notification(message=message, auth=auth)
    elif provider_id == 'slack':
        send_slack_notification(message=message, auth=auth)
    elif provider_id == 'telegram':
        send_telegram_notification(message=message, auth=auth)
    elif provider_id == 'hipchat':
        send_hipchat_notification(message=message, auth=auth)
    elif provider_id == 'webhook':
        _send_webhook(auth=auth, data={"message": message})
    elif provider_id == 'email':
        emails = [auth.get('email')]
        send_test_email(emails=emails)
    else:
        return redirect(reverse('notifications_all'))

    messages.add_message(request, messages.INFO, 'Sending test notification to {0}'.format(provider_id.title()))

    return redirect(reverse('notifications_edit', kwargs={'provider_id': provider_id, 'notification_id': notification_id}))

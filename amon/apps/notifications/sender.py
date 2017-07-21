from amon.apps.notifications.generator import generate_notifications
from amon.apps.notifications.generator import generate_message

from amon.apps.notifications.mail.sender import send_notification_email
from amon.apps.notifications.webhooks.sender import send_webhook_notification
from amon.apps.notifications.pushover.sender import send_pushover_notification
from amon.apps.notifications.victorops.sender import send_victorops_notification
from amon.apps.notifications.pagerduty.sender import send_pagerduty_notification
from amon.apps.notifications.opsgenie.sender import send_opsgenie_notification
from amon.apps.notifications.slack.sender import send_slack_notification
from amon.apps.notifications.telegram.sender import send_telegram_notification
from amon.apps.notifications.hipchat.sender import send_hipchat_notification

from amon.apps.alerts.models import alerts_history_model

def send_notifications():
    notifications_to_send = generate_notifications()
    for n in notifications_to_send:
        if n.mute != True and n.global_mute != True:
            message = generate_message(notification=n)

            notify = n.alert.get('notifications', [])
            
            # Collect all emails
            emails_list = []
            for x in notify:
                email = x.get('email')
                if email:
                    emails_list.append(email)
            
            if len(emails_list) > 0:
                send_notification_email(notification=n, emails=emails_list)

            for provider_auth in notify:
                provider = provider_auth.get('provider_id')
                
                if provider == 'pushover':
                    send_pushover_notification(message=message, auth=provider_auth)
                if provider == 'opsgenie':
                    send_opsgenie_notification(message=message, auth=provider_auth)
                if provider == 'pagerduty':
                    send_pagerduty_notification(message=message, auth=provider_auth)
                if provider == 'victorops':
                    send_victorops_notification(message=message, auth=provider_auth)
                if provider == 'slack':
                    send_slack_notification(message=message, auth=provider_auth)
                if provider == 'telegram':
                    send_telegram_notification(message=message, auth=provider_auth)
                if provider == 'hipchat':
                    send_hipchat_notification(message=message, auth=provider_auth)
                if provider == 'webhook':
                    send_webhook_notification(notification=n, auth=provider_auth, message=message)
        

        alerts_history_model.mark_as_sent(n.trigger['_id'])

    return notifications_to_send # For the remote command execute
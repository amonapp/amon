from amon.apps.notifications.models import notifications_model


def active_notification_providers_list():

    providers = ['pagerduty', 'opsgenie', 'pushover','victorops']
    active_list = []

    for provider_id in providers:
        result =  notifications_model.get_for_provider(provider_id=provider_id)

        if result != None:
            active_list.append(provider_id)

    return active_list

import requests
import json

from amon.apps.notifications.models import notifications_model

def send_opsgenie_notification(message=None, auth=None):
    sent = False
    url = "https://api.opsgenie.com/v2/alerts"
    headers = {
        'Authorization': 'GenieKey '+ auth.get('api_key'),
        'Content-Type': 'application/json'
    }

    # Message is limited to 130 chars
    data = {
            'message': message,
        }

    data = json.dumps(data)
    error = None

    try:
        r = requests.post(url, data=data, timeout=5, headers=headers)
    except Exception as e:
        error = e

    return error
import requests
import json


def send_slack_notification(message=None, auth=None):
    sent = False

    url = auth.get('webhook_url')
    
    data = {'text': message}

    data = json.dumps(data)
    error = None
    try:
        r = requests.post(url, data=data, timeout=5)
    except Exception as e:
        error = e

    return error
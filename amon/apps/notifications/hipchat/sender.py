import requests
import json


def send_hipchat_notification(message=None, auth=None):
    sent = False

    url = auth.get('url')
    color = auth.get('color', 'gray')

    data = {'message': message, "message_format": "text", "color": color, "notify": "true"}
    headers = {
        "content-type": "application/json"
    }
    data = json.dumps(data)
    error = None
    
    try:
        r = requests.post(url, data=data, timeout=5, headers=headers)
    except Exception as e:
        error = e

    return error
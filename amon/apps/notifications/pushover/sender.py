import requests


def send_pushover_notification(message=None, auth=None):
    url = "https://api.pushover.net/1/messages.json"

    data = {
        'token': auth.get('application_api_key'),
        'user': auth.get('user_key'),
        'message': message
    }

    error = None
    try:
        r = requests.post(url, data=data, timeout=5)
    except Exception as e:
        error = e

    return error